"""
Unit tests for the EsiStatus model and its methods.
"""

# Standard Library
from datetime import timedelta
from unittest.mock import patch

# Django
from django.utils import timezone

# AA ESI Status
from esistatus import models as esistatus_models
from esistatus.tests import BaseTestCase


class EsiStatusModelTestCase(BaseTestCase):
    """
    Test cases for the EsiStatus model methods.
    """

    def test_get_latest_status_data_returns_most_recent_snapshot(self):
        """
        Test that get_latest_status_data returns the most recent snapshot based on timestamp.

        :return:
        """

        older = esistatus_models.EsiStatus.objects.create(
            compatibility_date="2024-01-01",
            esi_name="old",
            status_data={"OK": {"count": 1}},
            total_endpoints=1,
        )
        newer = esistatus_models.EsiStatus.objects.create(
            compatibility_date="2024-01-02",
            esi_name="new",
            status_data={"OK": {"count": 5}},
            total_endpoints=5,
        )

        now = timezone.now()
        esistatus_models.EsiStatus.objects.filter(pk=older.pk).update(
            timestamp=now - timedelta(hours=2)
        )
        esistatus_models.EsiStatus.objects.filter(pk=newer.pk).update(
            timestamp=now - timedelta(hours=1)
        )

        latest = esistatus_models.EsiStatus.get_latest_status_data()

        self.assertEqual(latest["total_endpoints"], 5)
        self.assertEqual(latest["esi_status"]["OK"]["count"], 5)
        self.assertEqual(latest["compatibility_date"], "2024-01-02")
        self.assertEqual(latest["esi_name"], "new")


class EsiStatusHistoryTestCase(BaseTestCase):
    """
    Test cases for the get_history method of the EsiStatus model.
    """

    def test_get_latest_status_data_returns_empty_when_no_snapshots(self):
        """
        Test that get_latest_status_data returns an empty dictionary when there are no snapshots.

        :return:
        """

        esistatus_models.EsiStatus.objects.all().delete()

        latest = esistatus_models.EsiStatus.get_latest_status_data()

        self.assertEqual(latest, {})

    def test_get_history_filters_by_threshold_and_parses_counts(self):
        """
        Test that get_history filters snapshots based on the threshold and correctly parses the counts.

        :return:
        """

        with patch.dict(
            esistatus_models.__dict__, {"ESISTATUS_SHOW_HISTORY_THRESHOLD": 3}
        ):
            now = timezone.now()

            recent = esistatus_models.EsiStatus.objects.create(
                compatibility_date="2024-01-01",
                esi_name="recent",
                status_data={"OK": {"count": 7}, "Down": {"count": 2}},
                total_endpoints=9,
            )
            old = esistatus_models.EsiStatus.objects.create(
                compatibility_date="2023-12-01",
                esi_name="old",
                status_data={"OK": {"count": 3}},
                total_endpoints=3,
            )

            esistatus_models.EsiStatus.objects.filter(pk=recent.pk).update(
                timestamp=now - timedelta(hours=1)
            )
            esistatus_models.EsiStatus.objects.filter(pk=old.pk).update(
                timestamp=now - timedelta(hours=5)
            )

            history = esistatus_models.EsiStatus.get_history()

            self.assertTrue(any(h["esi_name"] == "recent" for h in history))
            self.assertTrue(all(h["esi_name"] != "old" for h in history))

            rec = next(h for h in history if h["esi_name"] == "recent")
            self.assertEqual(rec["ok"], 7)
            self.assertEqual(rec["down"], 2)

    def test_get_history_handles_missing_or_malformed_status_data(self):
        """
        Test that get_history handles missing or malformed status_data gracefully, returning 0 counts.

        :return:
        """

        with patch.dict(
            esistatus_models.__dict__, {"ESISTATUS_SHOW_HISTORY_THRESHOLD": 24}
        ):
            now = timezone.now()

            missing = esistatus_models.EsiStatus.objects.create(
                compatibility_date="2024-01-01",
                esi_name="missing",
                status_data={},
                total_endpoints=0,
            )

            malformed = esistatus_models.EsiStatus.objects.create(
                compatibility_date="2024-01-01",
                esi_name="malformed",
                status_data={"OK": None, "Down": 5},
                total_endpoints=5,
            )

            esistatus_models.EsiStatus.objects.filter(pk=missing.pk).update(
                timestamp=now - timedelta(hours=1)
            )
            esistatus_models.EsiStatus.objects.filter(pk=malformed.pk).update(
                timestamp=now - timedelta(hours=2)
            )

            history = esistatus_models.EsiStatus.get_history()

            m = next(h for h in history if h["esi_name"] == "missing")
            mf = next(h for h in history if h["esi_name"] == "malformed")

            self.assertEqual(m["ok"], 0)
            self.assertEqual(m["down"], 0)
            self.assertEqual(mf["ok"], 0)
            self.assertEqual(mf["down"], 0)

    def test_get_history_returns_zero_for_none_status_data(self):
        """
        Test that get_history returns zero counts for entries with None status_data.

        :return:
        """

        with patch.dict(
            esistatus_models.__dict__, {"ESISTATUS_SHOW_HISTORY_THRESHOLD": 24}
        ):
            now = timezone.now()
            none_status = esistatus_models.EsiStatus.objects.create(
                compatibility_date="2024-01-01",
                esi_name="none_status",
                status_data=None,
                total_endpoints=0,
            )
            esistatus_models.EsiStatus.objects.filter(pk=none_status.pk).update(
                timestamp=now - timedelta(hours=1)
            )

            history = esistatus_models.EsiStatus.get_history()
            entry = next(h for h in history if h["esi_name"] == "none_status")

            self.assertEqual(entry["ok"], 0)
            self.assertEqual(entry["down"], 0)
            self.assertEqual(entry["degraded"], 0)
            self.assertEqual(entry["recovering"], 0)
            self.assertEqual(entry["unknown"], 0)
