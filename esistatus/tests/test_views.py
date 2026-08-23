"""
Test the apps' views
"""

# Standard Library
from datetime import timedelta
from unittest import mock
from unittest.mock import MagicMock, patch

# Django
from django.http import HttpResponse
from django.test import RequestFactory
from django.utils import timezone

# AA ESI Status
from esistatus import models as esistatus_models
from esistatus.tests import BaseTestCase
from esistatus.views import (
    _render_esi_status,
    ajax_dashboard_widget,
    ajax_esi_status,
    dashboard_widget,
    index,
)

MODULE: str = "esistatus.views"


class TestDashboardWidget(BaseTestCase):
    """
    Test the dashboard widget
    """

    def test_renders_dashboard_widget_for_superuser(self):
        """
        Test that a superuser sees the ESI status widget

        :return:
        :rtype:
        """

        request = mock.Mock()
        request.user.is_superuser = True

        with mock.patch(MODULE + ".render_to_string") as mock_render:
            dashboard_widget(request)

            mock_render.assert_called_once_with(
                template_name="esistatus/dashboard-widget.html", request=request
            )

    def test_returns_empty_string_for_non_superuser(self):
        """
        Test that a normal user does not see the ESI status widget

        :return:
        :rtype:
        """

        request = mock.Mock()
        request.user.is_superuser = False

        result = dashboard_widget(request)

        self.assertEqual(result, "")


class TestAjaxEsiStatus(BaseTestCase):
    """
    Test the AJAX ESI Status view
    """

    def test_returns_esi_status_with_compat_date(self):
        """
        Test that the AJAX ESI status view returns ESI status with compatibility date

        :return:
        :rtype:
        """

        with mock.patch(MODULE + "._render_esi_status") as mock_render_esi:
            mock_render_esi.return_value = HttpResponse()

            response = ajax_esi_status(request=mock.Mock())

            mock_render_esi.assert_called_once_with(
                request=mock.ANY,
                template_name="esistatus/partials/index/esi-status.html",
                with_compat_date=True,
            )
            self.assertEqual(response, mock_render_esi.return_value)

    def test_handles_empty_esi_status_gracefully(self):
        """
        Test that the AJAX ESI status view handles empty ESI status gracefully

        :return:
        :rtype:
        """

        with mock.patch(MODULE + "._render_esi_status") as mock_render_esi:
            mock_render_esi.return_value = HttpResponse()

            response = ajax_esi_status(request=mock.Mock())

            mock_render_esi.assert_called_once_with(
                request=mock.ANY,
                template_name="esistatus/partials/index/esi-status.html",
                with_compat_date=True,
            )
            self.assertEqual(response, mock_render_esi.return_value)


class TestAjaxEsiStatusDasboardWidget(BaseTestCase):
    """
    Test the AJAX ESI Status view for the dashboard widget
    """

    def test_renders_dashboard_widget_with_esi_status(self):
        """
        Test that the AJAX dashboard widget view renders ESI status

        :return:
        :rtype:
        """

        with mock.patch(MODULE + "._render_esi_status") as mock_render_esi:
            mock_render_esi.return_value = HttpResponse()

            response = ajax_dashboard_widget(request=mock.Mock())

            mock_render_esi.assert_called_once_with(
                request=mock.ANY,
                template_name="esistatus/partials/dashboard-widget/esi-status.html",
                with_compat_date=True,
            )
            self.assertEqual(response, mock_render_esi.return_value)

    def test_handles_empty_esi_status_for_dashboard_widget(self):
        """
        Test that the AJAX dashboard widget view handles empty ESI status gracefully

        :return:
        :rtype:
        """

        with mock.patch(MODULE + "._render_esi_status") as mock_render_esi:
            mock_render_esi.return_value = HttpResponse()

            response = ajax_dashboard_widget(request=mock.Mock())

            mock_render_esi.assert_called_once_with(
                request=mock.ANY,
                template_name="esistatus/partials/dashboard-widget/esi-status.html",
                with_compat_date=True,
            )
            self.assertEqual(response, mock_render_esi.return_value)


class TestIndex(BaseTestCase):
    """
    Test the index view
    """

    def test_renders_index_view_successfully(self):
        """
        Test that the index view renders successfully

        :return:
        :rtype:
        """

        request = mock.Mock()

        with mock.patch(MODULE + ".render") as mock_render:
            index(request)
            mock_render.assert_called_once_with(
                request=request, template_name="esistatus/index.html"
            )


class TestHelperRenderEsiStatus(BaseTestCase):
    """
    Test the _render_esi_status function
    """

    def test__render_esi_status_includes_latest_status_history_and_compat_date_when_requested(
        self,
    ):
        """
        Test that _render_esi_status includes the latest status, history, and compatibility date when requested.

        :return:
        """

        with patch.dict(
            esistatus_models.__dict__, {"ESISTATUS_SHOW_HISTORY_THRESHOLD": 24}
        ):
            with patch(MODULE + ".ESISTATUS_SHOW_HISTORY_THRESHOLD", 24):
                now = timezone.now()

                recent = esistatus_models.EsiStatus.objects.create(
                    compatibility_date="2024-01-01",
                    esi_name="recent_view",
                    status_data={"OK": {"count": 2}, "Down": {"count": 1}},
                    total_endpoints=3,
                )
                esistatus_models.EsiStatus.objects.filter(pk=recent.pk).update(
                    timestamp=now - timedelta(hours=1)
                )

                rf = RequestFactory()
                request = rf.get("/")

                mock_render = MagicMock(return_value=HttpResponse())

                with patch(MODULE + ".render", mock_render):
                    _render_esi_status(
                        request=request,
                        template_name="esistatus/whatever.html",
                        with_compat_date=True,
                    )

                mock_render.assert_called_once()
                _, kwargs = mock_render.call_args
                context = kwargs.get("context", {})

                self.assertEqual(context.get("esi_name"), "recent_view")
                self.assertEqual(context.get("total_endpoints"), 3)
                self.assertIn("esi_endpoint_history", context)
                self.assertTrue(
                    any(
                        h["esi_name"] == "recent_view"
                        for h in context["esi_endpoint_history"]
                    )
                )
                self.assertEqual(context.get("compatibility_date"), "2024-01-01")
                self.assertEqual(context.get("retention_threshold"), 24)

    def test__render_esi_status_omits_compatibility_date_when_flag_not_set(self):
        """
        Test that _render_esi_status omits the compatibility date when with_compat_date is False.

        :return:
        """

        with patch.dict(
            esistatus_models.__dict__, {"ESISTATUS_SHOW_HISTORY_THRESHOLD": 24}
        ):
            with patch(MODULE + ".ESISTATUS_SHOW_HISTORY_THRESHOLD", 24):
                now = timezone.now()

                recent = esistatus_models.EsiStatus.objects.create(
                    compatibility_date="2024-02-02",
                    esi_name="no_compat_flag",
                    status_data={"OK": {"count": 1}},
                    total_endpoints=1,
                )
                esistatus_models.EsiStatus.objects.filter(pk=recent.pk).update(
                    timestamp=now - timedelta(hours=1)
                )

                rf = RequestFactory()
                request = rf.get("/")

                mock_render = MagicMock(return_value=HttpResponse())

                with patch(MODULE + ".render", mock_render):
                    _ = _render_esi_status(
                        request=request,
                        template_name="esistatus/whatever.html",
                        with_compat_date=False,
                    )

                mock_render.assert_called_once()
                _, kwargs = mock_render.call_args
                context = kwargs.get("context", {})

                self.assertEqual(context.get("esi_name"), "no_compat_flag")
                self.assertNotIn("compatibility_date", context)

    def test__render_esi_status_handles_no_snapshots_and_returns_empty_history_and_none_latest(
        self,
    ):
        """
        Test that _render_esi_status handles the case where there are no ESI status snapshots and returns empty history and None for latest status.

        :return:
        """

        # Ensure DB is empty for this test
        esistatus_models.EsiStatus.objects.all().delete()

        with patch.dict(
            esistatus_models.__dict__, {"ESISTATUS_SHOW_HISTORY_THRESHOLD": 24}
        ):
            with patch(MODULE + ".ESISTATUS_SHOW_HISTORY_THRESHOLD", 24):
                rf = RequestFactory()
                request = rf.get("/")

                mock_render = MagicMock(return_value=HttpResponse())

                with patch(MODULE + ".render", mock_render):
                    _ = _render_esi_status(
                        request=request,
                        template_name="esistatus/whatever.html",
                        with_compat_date=True,
                    )

                mock_render.assert_called_once()
                _, kwargs = mock_render.call_args
                context = kwargs.get("context", {})

                self.assertIsNone(context.get("esi_endpoint_status"))
                self.assertEqual(context.get("esi_endpoint_history"), [])
                self.assertIsNone(context.get("esi_name"))
                self.assertEqual(context.get("retention_threshold"), 24)
