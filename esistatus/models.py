"""
The models
"""

# Standard Library
import uuid
from typing import Any

# Django
from django.db import models
from django.utils.translation import gettext_lazy as _


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
        help_text=_("The timestamp of the history entry."),
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
        Get the history of ESI status snapshots.

        :return: A list of dictionaries for historical snapshots (most recent first).
        :rtype: list[dict]
        """

        entries = cls.objects.order_by("-timestamp").values(
            "timestamp",
            "total_endpoints",
            "status_data",
            "compatibility_date",
            "esi_name",
        )

        history_list: list[dict[str, Any]] = []

        for entry in entries:
            status = entry.get("status_data") or {}

            # Use .get with defaults to guard against missing keys / unexpected shapes
            ok = status.get("OK", {}).get("count", 0)
            degraded = status.get("Degraded", {}).get("count", 0)
            down = status.get("Down", {}).get("count", 0)
            recovering = status.get("Recovering", {}).get("count", 0)
            unknown = status.get("Unknown", {}).get("count", 0)

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
