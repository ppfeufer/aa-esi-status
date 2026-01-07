"""
Test the apps' views
"""

# Standard Library
from unittest import mock

# AA ESI Status
from esistatus.models import EsiStatus
from esistatus.tests import BaseTestCase
from esistatus.views import (
    _esi_status,
    _render_esi_status,
    ajax_dashboard_widget,
    ajax_esi_status,
    dashboard_widget,
    index,
)


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

        with mock.patch("esistatus.views.render_to_string") as mock_render:
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

        with (
            mock.patch("esistatus.views._esi_status") as mock_esi_status,
            mock.patch("esistatus.views.render") as mock_render,
        ):
            mock_esi_status.return_value = {
                "esi_status": {"key": "value"},
                "total_endpoints": 5,
                "compatibility_date": "2023-10-01",
            }

            response = ajax_esi_status(request=mock.Mock())

            mock_render.assert_called_once_with(
                request=mock.ANY,
                template_name="esistatus/partials/index/esi-status.html",
                context={
                    "esi_endpoint_status": {"key": "value"},
                    "total_endpoints": 5,
                    "compatibility_date": "2023-10-01",
                },
            )
            self.assertEqual(response, mock_render.return_value)

    def test_handles_empty_esi_status_gracefully(self):
        """
        Test that the AJAX ESI status view handles empty ESI status gracefully

        :return:
        :rtype:
        """

        with (
            mock.patch("esistatus.views._esi_status") as mock_esi_status,
            mock.patch("esistatus.views.render") as mock_render,
        ):
            mock_esi_status.return_value = {}

            response = ajax_esi_status(request=mock.Mock())

            mock_render.assert_called_once_with(
                request=mock.ANY,
                template_name="esistatus/partials/index/esi-status.html",
                context={
                    "esi_endpoint_status": None,
                    "total_endpoints": None,
                    "compatibility_date": None,
                },
            )
            self.assertEqual(response, mock_render.return_value)


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

        with (
            mock.patch("esistatus.views._esi_status") as mock_esi_status,
            mock.patch("esistatus.views.render") as mock_render,
        ):
            mock_esi_status.return_value = {
                "esi_status": {"status": "OK"},
                "total_endpoints": 5,
                "compatibility_date": "2023-10-01",
            }

            ajax_dashboard_widget(request=mock.Mock())

            mock_render.assert_called_once_with(
                request=mock.ANY,
                template_name="esistatus/partials/dashboard-widget/esi-status.html",
                context={
                    "esi_endpoint_status": {"status": "OK"},
                    "total_endpoints": 5,
                    "compatibility_date": "2023-10-01",
                },
            )

    def test_handles_empty_esi_status_for_dashboard_widget(self):
        """
        Test that the AJAX dashboard widget view handles empty ESI status gracefully

        :return:
        :rtype:
        """

        with (
            mock.patch("esistatus.views._esi_status") as mock_esi_status,
            mock.patch("esistatus.views.render") as mock_render,
        ):
            mock_esi_status.return_value = {}

            ajax_dashboard_widget(request=mock.Mock())

            mock_render.assert_called_once_with(
                request=mock.ANY,
                template_name="esistatus/partials/dashboard-widget/esi-status.html",
                context={
                    "esi_endpoint_status": None,
                    "total_endpoints": None,
                    "compatibility_date": None,
                },
            )


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

        with mock.patch("esistatus.views.render") as mock_render:
            index(request)
            mock_render.assert_called_once_with(
                request=request, template_name="esistatus/index.html"
            )


class TestHelperEsiStatus(BaseTestCase):
    """
    Test the _esi_status function
    """

    def test_returns_esi_status_with_valid_data(self):
        """
        Test that the _esi_status function returns ESI status with valid data

        :return:
        :rtype:
        """

        with mock.patch("esistatus.views.EsiStatus.objects.get") as mock_get:
            mock_get.return_value.total_endpoints = 5
            mock_get.return_value.status_data = {"key": "value"}
            mock_get.return_value.compatibility_date = "2023-10-01"

            result = _esi_status()

            self.assertEqual(
                result,
                {
                    "total_endpoints": 5,
                    "esi_status": {"key": "value"},
                    "compatibility_date": "2023-10-01",
                },
            )

    def test_returns_empty_dict_when_esi_status_does_not_exist(self):
        """
        Test that the _esi_status function returns an empty dict when ESI status does not exist

        :return:
        :rtype:
        """

        with (
            mock.patch(
                "esistatus.views.EsiStatus.objects.get",
                side_effect=EsiStatus.DoesNotExist,
            ),
            mock.patch("esistatus.views.logger.debug") as mock_debug,
        ):
            result = _esi_status()

            self.assertEqual(result, {})
            mock_debug.assert_called_with("ESI Status data does not exist.")

    def test_processes_empty_esi_status_data(self):
        """
        Test that the _esi_status function processes empty ESI status data

        :return:
        :rtype:
        """

        with mock.patch("esistatus.views.EsiStatus.objects.get") as mock_get:
            mock_get.return_value.total_endpoints = 0
            mock_get.return_value.status_data = []
            mock_get.return_value.compatibility_date = None

            result = _esi_status()

            self.assertEqual(
                result,
                {"total_endpoints": 0, "esi_status": [], "compatibility_date": None},
            )


class TestHelperRenderEsiStatus(BaseTestCase):
    """
    Test the _render_esi_status function
    """

    def test_renders_context_with_compat_date_when_flag_is_true(self):
        """
        Test that the context includes compatibility date when the flag is true

        :return:
        :rtype:
        """

        with (
            mock.patch("esistatus.views._esi_status") as mock_esi_status,
            mock.patch("esistatus.views.render") as mock_render,
        ):
            mock_esi_status.return_value = {
                "esi_status": {"status": "OK"},
                "total_endpoints": 5,
                "compatibility_date": "2023-10-01",
            }

            _render_esi_status(
                request=mock.Mock(),
                template_name="esistatus/partials/index/esi-status.html",
                with_compat_date=True,
            )

            mock_render.assert_called_once_with(
                request=mock.ANY,
                template_name="esistatus/partials/index/esi-status.html",
                context={
                    "esi_endpoint_status": {"status": "OK"},
                    "total_endpoints": 5,
                    "compatibility_date": "2023-10-01",
                },
            )

    def test_renders_context_without_compat_date_when_flag_is_false(self):
        """
        Test that the context excludes compatibility date when the flag is false

        :return:
        :rtype:
        """

        with (
            mock.patch("esistatus.views._esi_status") as mock_esi_status,
            mock.patch("esistatus.views.render") as mock_render,
        ):
            mock_esi_status.return_value = {
                "esi_status": {"status": "OK"},
                "total_endpoints": 5,
                "compatibility_date": "2023-10-01",
            }

            _render_esi_status(
                request=mock.Mock(),
                template_name="esistatus/partials/index/esi-status.html",
                with_compat_date=False,
            )

            mock_render.assert_called_once_with(
                request=mock.ANY,
                template_name="esistatus/partials/index/esi-status.html",
                context={
                    "esi_endpoint_status": {"status": "OK"},
                    "total_endpoints": 5,
                },
            )

    def test_handles_empty_esi_status_gracefully(self):
        """
        Test that the rendering handles empty ESI status gracefully

        :return:
        :rtype:
        """

        with (
            mock.patch("esistatus.views._esi_status") as mock_esi_status,
            mock.patch("esistatus.views.render") as mock_render,
        ):
            mock_esi_status.return_value = {}

            _render_esi_status(
                request=mock.Mock(),
                template_name="esistatus/partials/index/esi-status.html",
                with_compat_date=True,
            )

            mock_render.assert_called_once_with(
                request=mock.ANY,
                template_name="esistatus/partials/index/esi-status.html",
                context={
                    "esi_endpoint_status": None,
                    "total_endpoints": None,
                    "compatibility_date": None,
                },
            )
