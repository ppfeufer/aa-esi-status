"""
The models
"""

# Standard Library
import uuid
from datetime import timedelta
from typing import Any

# Django
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# AA ESI Status
from esistatus.app_settings import ESISTATUS_SHOW_HISTORY_THRESHOLD


class EsiStatus(models.Model):
    """
    Model to store (and retain) ESI endpoint status snapshots.

    This model now combines the previous `EsiStatus` and `History` models: each
    row represents a snapshot of the ESI status at a given timestamp. The most
    recent snapshot can be obtained via the default ordering.
    """

    # UUID primary key for snapshot rows
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Timestamp of the snapshot
    timestamp = models.DateTimeField(
        help_text=_("The timestamp of the status entry."),
        auto_now_add=True,
        # default=timezone.now,
        db_index=True,
    )

    # Fields from the original EsiStatus model
    compatibility_date = models.CharField(
        help_text=_("The ESI compatibility date."), max_length=10
    )

    esi_name = models.CharField(
        help_text=_(
            "The name ESI is currently going by. "
            "The three letters have never once meant the same thing twice."
        ),
        max_length=250,
        null=True,
        blank=True,
    )

    status_data = models.JSONField(
        help_text=_("The ESI status data."), null=True, blank=True
    )

    total_endpoints = models.PositiveIntegerField(
        help_text=_("Total number of ESI endpoints."), default=0
    )

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("ESI Endpoint Status")
        verbose_name_plural = _("ESI Endpoint Statuses")
        # Order by timestamp descending by default and add an index for faster queries
        ordering = ["-timestamp"]
        indexes = [models.Index(fields=["timestamp"])]

    @classmethod
    def get_latest_status_data(cls) -> dict:
        """
        Get the latest status data from the most recent snapshot.

        :return: The latest status data.
        :rtype: dict
        """

        latest_snapshot = cls.objects.order_by("-timestamp").first()

        if latest_snapshot:
            return {
                "total_endpoints": latest_snapshot.total_endpoints,
                "esi_status": latest_snapshot.status_data,
                "compatibility_date": latest_snapshot.compatibility_date,
                "esi_name": latest_snapshot.esi_name,
                "timestamp": latest_snapshot.timestamp,
                "id": latest_snapshot.pk,
            }

        return {}

    @classmethod
    def get_history(cls) -> list[dict[str, Any]]:
        """
        Get the history of ESI status snapshots for the last ESISTATUS_HISTORY_SHOW hours.

        :return: A list of dictionaries for historical snapshots (most recent first).
        :rtype: list[dict]
        """

        history_threshold = timezone.now() - timedelta(
            hours=ESISTATUS_SHOW_HISTORY_THRESHOLD
        )

        entries = (
            cls.objects.filter(timestamp__gte=history_threshold)
            .order_by("-timestamp")
            .values(
                "timestamp",
                "total_endpoints",
                "status_data",
                "compatibility_date",
                "esi_name",
            )
        )

        history_list: list[dict[str, Any]] = []

        def safe_count(status_map: dict, key: str) -> int:
            """
            Safely retrieve the count for a given status key from the provided status mapping.

            :param status_map: The status mapping to inspect
            :param key: The status key (e.g. "OK")
            :return: The integer count (0 if missing/malformed)
            """

            val = status_map.get(key)

            if isinstance(val, dict):
                return int(val.get("count", 0) or 0)

            # If val is None or not a dict, it's malformed -> 0
            return 0

        for entry in entries:
            # Ensure status_data is a dict; if it's missing, None, or malformed
            # (e.g. not a mapping), treat it as an empty mapping so subsequent
            # .get calls are safe.
            raw_status = entry.get("status_data")

            if not isinstance(raw_status, dict):
                status: dict = {}
            else:
                status = raw_status

            ok = safe_count(status, "OK")
            degraded = safe_count(status, "Degraded")
            down = safe_count(status, "Down")
            recovering = safe_count(status, "Recovering")
            unknown = safe_count(status, "Unknown")

            history_list.append(
                {
                    "ok": ok,
                    "degraded": degraded,
                    "down": down,
                    "recovering": recovering,
                    "unknown": unknown,
                    "timestamp": entry.get("timestamp"),
                    "total_endpoints": entry.get("total_endpoints"),
                    "compatibility_date": entry.get("compatibility_date"),
                    "esi_name": entry.get("esi_name"),
                }
            )

        return history_list
