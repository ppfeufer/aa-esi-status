"""
Management command to populate the database with dummy ESI status history.

Creates datapoints for a given number of hours (default 24) at a given
interval in minutes (default 1). Intended for development and testing.

The produced status_data uses the same shape as produced by the real
collector so views and charts can render it.

{
    "OK": {"endpoints": {...}, "count": int, "percentage": "x.xx%"},
    "Degraded": {...},
    "Down": {...},
    "Recovering": {...},
    "Unknown": {...}
}
"""

# Standard Library
import random
import uuid
from collections.abc import Iterable
from datetime import datetime as _dt
from datetime import timedelta

# Django
from django.core.management.base import BaseCommand
from django.utils import timezone

# AA ESI Status
from esistatus.models import EsiStatus
from esistatus.tasks import (
    _get_esi_name_for_compatibility_date,
    _get_esi_status_json,
    _get_latest_compatibility_date,
)


class Command(BaseCommand):
    """
    Management command to populate the database with dummy ESI status history.
    """

    help = (
        "Fill the database with dummy ESI status history for a timespan. "
        "Default: 24 hours of data at 1-minute resolution."
    )

    @staticmethod
    def _get_total_endpoints() -> int:
        """
        Get the total number of ESI endpoints based on the latest compatibility date.

        :return: Total number of ESI endpoints
        """

        latest_compat = _get_latest_compatibility_date()
        total = 0

        if latest_compat:
            esi_json = _get_esi_status_json(compatibility_date=latest_compat)

            if isinstance(esi_json, dict) and "routes" in esi_json:
                total = len(esi_json.get("routes", []))

        return total

    total_endpoints: int = _get_total_endpoints()

    @staticmethod
    def _format_pct(n: int, total: int) -> str:
        """
        Format a percentage string with two decimal places. If total is zero, return "0.00%".

        :param n: The numerator value for the percentage calculation.
        :param total: The denominator value for the percentage calculation.
        :return: A string representing the percentage with two decimal places.
        """

        if total > 0:
            percentage = (n / total) * 100
        else:
            percentage = 0.0

        return f"{percentage:.2f}%"

    def _generate_status_data_and_total(  # pylint: disable=too-many-locals
        self: "Command", total_endpoints: int
    ) -> tuple[dict, int]:
        """
        Generate a dictionary representing the status data for ESI endpoints, along with the total number of endpoints.

        :param total_endpoints: The total number of ESI endpoints.
        :return: A tuple containing the status data dictionary and the total number of endpoints.
        """

        # total_endpoints = self.total_endpoints

        # Base probabilities
        p_ok, p_degraded, p_down, p_recovering, p_unknown = (
            0.85,
            0.08,
            0.04,
            0.02,
            0.01,
        )

        # Slight randomness
        p_ok += random.uniform(-0.03, 0.02)
        p_degraded += random.uniform(-0.02, 0.02)
        p_down += random.uniform(-0.01, 0.01)

        total_p = p_ok + p_degraded + p_down + p_recovering + p_unknown
        p_ok /= total_p
        p_degraded /= total_p
        p_down /= total_p
        p_recovering /= total_p
        p_unknown /= total_p

        ok_count = int(total_endpoints * p_ok)
        degraded_count = int(total_endpoints * p_degraded)
        down_count = int(total_endpoints * p_down)
        recovering_count = int(total_endpoints * p_recovering)

        unknown_count = max(
            0,
            total_endpoints
            - (ok_count + degraded_count + down_count + recovering_count),
        )

        status_data = {
            "Unknown": {
                "endpoints": {},
                "count": unknown_count,
                "percentage": self._format_pct(unknown_count, total_endpoints),
            },
            "OK": {
                "endpoints": {},
                "count": ok_count,
                "percentage": self._format_pct(ok_count, total_endpoints),
            },
            "Degraded": {
                "endpoints": {},
                "count": degraded_count,
                "percentage": self._format_pct(degraded_count, total_endpoints),
            },
            "Down": {
                "endpoints": {},
                "count": down_count,
                "percentage": self._format_pct(down_count, total_endpoints),
            },
            "Recovering": {
                "endpoints": {},
                "count": recovering_count,
                "percentage": self._format_pct(recovering_count, total_endpoints),
            },
        }

        return status_data, total_endpoints

    @staticmethod
    def _confirm_and_clear(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        stdout,
        earliest,
        now,
        hours: int,
        interval: int,
        points: int,
        batch_size: int,
        total_endpoints: int,
        clear_existing: bool,
        no_input: bool,
    ) -> bool:
        """
        Confirm with the user before proceeding and optionally clear existing rows in the specified time range.

        :param stdout: The standard output stream for writing messages.
        :param earliest: The earliest timestamp for the generated data.
        :param now: The current timestamp for the generated data.
        :param hours: The number of hours for which to generate data.
        :param interval: The interval in minutes between generated datapoints.
        :param points: The total number of datapoints to generate.
        :param batch_size: The number of objects to create per bulk_create batch.
        :param total_endpoints: The total number of ESI endpoints.
        :param clear_existing: Whether to clear existing rows in the specified time range.
        :param no_input: Whether to skip the confirmation prompt.
        :return: True if the operation should proceed, False otherwise.
        """

        stdout.write(
            "About to generate ESI status dummy data with the following parameters:"
        )
        stdout.write(f"  Hours: {hours}")
        stdout.write(f"  Interval (minutes): {interval}")
        stdout.write(f"  Datapoints (total): {points}")
        stdout.write(f"  Time range: {earliest.isoformat()} -> {now.isoformat()}")
        stdout.write(f"  Batch size: {batch_size}")
        stdout.write(f"  Total endpoints count: {total_endpoints}")
        stdout.write("  Insert method: Django ORM bulk_create")
        stdout.write(
            f"  Clear existing rows in range: {'Yes' if clear_existing else 'No'}"
        )

        if no_input:
            stdout.write("Skipping confirmation prompt (--no-input); proceeding.")
        else:
            try:
                answer = (
                    input("Proceed and modify the database? [y/N]: ").strip().lower()
                )
            except EOFError:
                stdout.write("No input available; aborting.")

                return False

            if answer not in ("y", "yes"):
                stdout.write("Aborted by user. No changes made.")

                return False

        if clear_existing:
            deleted = EsiStatus.objects.filter(
                timestamp__gte=earliest, timestamp__lte=now
            ).delete()

            stdout.write(f"Cleared existing rows in range: {deleted[0]} deleted")

        return True

    def _esi_status_batches(  # pylint: disable=too-many-locals
        self: "Command",
        points: int,
        now,
        interval: int,
        total_endpoints: int,
        batch_size: int,
    ) -> Iterable[list[EsiStatus]]:
        """
        Generate batches of EsiStatus objects for the specified number of points, interval, and total endpoints.

        :param points: The total number of datapoints to generate.
        :param now: The current timestamp for the generated data.
        :param interval: The interval in minutes between generated datapoints.
        :param total_endpoints: The total number of ESI endpoints.
        :param batch_size: The number of objects to create per bulk_create batch.
        :return: An iterable of lists of EsiStatus objects.
        """

        batch: list[EsiStatus] = []
        latest_compat = _get_latest_compatibility_date()
        esi_name = _get_esi_name_for_compatibility_date(
            compatibility_date=latest_compat
        )

        # Use integer epoch arithmetic to avoid subtle tz/datetime rounding
        # differences that can result in nearly identical timestamps. Compute
        # second-precision epoch and subtract whole minutes (in seconds).
        try:
            now_epoch = int(now.timestamp())
        except Exception:  # pylint: disable=broad-except
            # Fallback: if now has no timestamp (very unlikely), fall back to
            # arithmetic using timedelta.
            now_epoch = int(timezone.now().timestamp())

        for i in range(points):
            minutes_back = (points - 1 - i) * interval
            ts_seconds = now_epoch - (minutes_back * 60)
            ts = _dt.fromtimestamp(ts_seconds, tz=now.tzinfo).replace(
                second=0, microsecond=0
            )

            status_data, total_endpoints = self._generate_status_data_and_total(
                total_endpoints
            )

            obj = EsiStatus(
                timestamp=ts,
                compatibility_date=latest_compat,
                esi_name=esi_name,
                status_data=status_data,
                total_endpoints=total_endpoints,
            )

            # Pre-generate and assign the UUID primary key so instances can be
            # identified later when we perform an ORM-only bulk_update to set
            # the precise timestamp values. Assigning the uuid here ensures
            # the in-memory instance has a primary key before bulk_create.
            obj.uuid = uuid.uuid4()

            batch.append(obj)

            if len(batch) >= batch_size:
                yield batch

                batch = []

        if batch:
            yield batch

    def add_arguments(self, parser) -> None:
        """
        Add command-line arguments for the management command.

        :param parser: The argument parser to which the command-line arguments will be added.
        :return: None
        """

        parser.add_argument(
            "--hours",
            type=int,
            default=24,
            help="Number of hours to generate (default: 24).",
        )
        parser.add_argument(
            "--interval",
            type=int,
            default=1,
            help="Interval between datapoints in minutes (default: 1).",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=500,
            help="How many objects to create per bulk_create batch.",
        )
        parser.add_argument(
            "--clear-existing",
            action="store_true",
            dest="clear_existing",
            help="Clear existing EsiStatus rows in the generated time range before inserting.",
        )
        parser.add_argument(
            "--no-input",
            action="store_true",
            dest="no_input",
            help="Don't prompt for confirmation; print the summary and proceed.",
        )

    def handle(  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        self, *_, **options
    ) -> None:
        """
        Handle the management command to generate dummy ESI status history.

        :param _: Positional arguments (not used).
        :param options: Command-line options and their values.
        :return: None
        """

        hours = options.get("hours", 24)
        interval = options.get("interval", 1)
        batch_size = options.get("batch_size", 500)

        if hours <= 0:
            self.stderr.write("--hours must be > 0")

            return

        if interval <= 0:
            self.stderr.write("--interval must be > 0")

            return

        total_minutes = int(hours * 60)
        points = (total_minutes + interval - 1) // interval

        now = timezone.now().replace(second=0, microsecond=0)

        self.stdout.write(
            f"Generating {points} datapoints ending at {now.isoformat()} (every {interval} minute(s), {hours} hours total)"
        )

        total_endpoints = self.total_endpoints
        clear_existing = bool(options.get("clear_existing", False))
        no_input = bool(options.get("no_input", False))

        if points > 0:
            earliest = now - timedelta(minutes=(points - 1) * interval)
        else:
            earliest = now

        proceed = self._confirm_and_clear(
            self.stdout,
            earliest,
            now,
            hours,
            interval,
            points,
            batch_size,
            total_endpoints,
            clear_existing,
            no_input,
        )

        if not proceed:
            return

        created_count = 0

        for batch in self._esi_status_batches(
            points=points,
            now=now,
            interval=interval,
            total_endpoints=total_endpoints,
            batch_size=batch_size,
        ):
            loop_number = (created_count // batch_size) + 1

            self.stdout.write(
                f"Processing batch {loop_number}/{(points + batch_size - 1) // batch_size} (Batch size: {len(batch)})..."
            )

            # Insert the batch using Django ORM bulk_create (ORM-only, no raw SQL).
            # We then explicitly set the intended per-row timestamps using
            # ORM operations to ensure auto_now_add or DB defaults don't leave
            # identical insertion timestamps for all rows.
            try:
                # Capture the intended timestamps separately because Django's
                # bulk_create may populate or mutate in-memory instances with
                # DB defaults (including auto_now_add fields). Preserve the
                # original intended timestamp values in a mapping keyed by
                # uuid so we can reliably write them back after insertion.
                intended_ts_map = {str(obj.uuid): obj.timestamp for obj in batch}

                EsiStatus.objects.bulk_create(batch, batch_size=batch_size)
            except Exception as exc:  # pylint: disable=broad-except
                self.stderr.write(f"ORM bulk_create failed ({exc})")

                raise

            # Ensure each created row has the intended timestamp using ORM-only
            # updates. We first attempt a QuerySet.update(), which is a single
            # UPDATE per object. If that reports 0 affected rows, fall back to
            # a re-query + save(update_fields=[...]) which issues a SELECT then
            # an UPDATE via the ORM. This remains ORM-only and robust across
            # backends.
            updated_total = 0

            for obj in batch:
                try:
                    intended_ts = intended_ts_map.get(str(obj.uuid))
                    affected = 0

                    if intended_ts is not None:
                        affected = EsiStatus.objects.filter(uuid=obj.uuid).update(
                            timestamp=intended_ts
                        )

                    if affected:
                        updated_total += affected

                        continue

                    # Fallback: re-query the created row and save the timestamp
                    row = EsiStatus.objects.filter(uuid=obj.uuid).first()
                    if row:
                        # Use the preserved intended timestamp when saving.
                        row.timestamp = intended_ts_map.get(
                            str(obj.uuid), obj.timestamp
                        )

                        row.save(update_fields=["timestamp"])

                        updated_total += 1
                    else:
                        self.stderr.write(
                            f"Failed to locate created row for uuid {obj.uuid}"
                        )
                except Exception as exc:  # pylint: disable=broad-except
                    self.stderr.write(
                        f"Failed to update timestamp for {obj.uuid}: {exc}"
                    )

            created_count += len(batch)

            self.stdout.write(f"Created {created_count} objects (batch)")

        self.stdout.write(
            self.style.SUCCESS(f"Created {created_count} dummy EsiStatus rows.")
        )
