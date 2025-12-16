"""
Test the apps' views
"""

# Standard Library
from unittest import mock

# AA ESI Status
from esistatus.models import EsiStatus
from esistatus.tests import BaseTestCase
from esistatus.views import (
    _append_value,
    _esi_endpoint_status_from_json,
    _esi_status,
    _render_esi_status,
    ajax_dashboard_widget,
    ajax_esi_status,
    dashboard_widget,
    index,
)


class TestAppendValue(BaseTestCase):
    """
    Test the _append_value function
    """

    def test_append_value_to_existing_key_with_list(self):
        """
        Test the _append_value function with an existing key that has a list value

        :return:
        :rtype:
        """

        dict_obj = {"key1": [1, 2]}
        _append_value(dict_obj, "key1", 3)

        self.assertEqual(dict_obj, {"key1": [1, 2, 3]})

    def test_append_value_to_existing_key_without_list(self):
        """
        Test the _append_value function with an existing key that has a non-list value

        :return:
        :rtype:
        """

        dict_obj = {"key1": 1}
        _append_value(dict_obj, "key1", 2)

        self.assertEqual(dict_obj, {"key1": [1, 2]})

    def test_append_value_to_non_existing_key(self):
        """
        Test the _append_value function with a non-existing key

        :return:
        :rtype:
        """

        dict_obj = {}
        _append_value(dict_obj, "key1", 1)

        self.assertEqual(dict_obj, {"key1": [1]})

    def test_append_value_to_existing_key_with_empty_list(self):
        """
        Test the _append_value function with an existing key that has an empty list value

        :return:
        :rtype:
        """

        dict_obj = {"key1": []}
        _append_value(dict_obj, "key1", 1)

        self.assertEqual(dict_obj, {"key1": [1]})

    def test_append_value_to_existing_key_with_non_list_value(self):
        """
        Test the _append_value function with an existing key that has a non-list value

        :return:
        :rtype:
        """

        dict_obj = {"key1": "value1"}
        _append_value(dict_obj, "key1", "value2")

        self.assertEqual(dict_obj, {"key1": ["value1", "value2"]})


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

    def test_renders_esi_status_view_with_valid_data(self):
        """
        Test that the AJAX ESI status view renders with valid data

        :return:
        :rtype:
        """

        request = mock.Mock()

        with (
            mock.patch(
                "esistatus.views._esi_status",
                return_value={
                    "esi_status": {"status": "OK"},
                    "compatibility_date": "2023-01-01",
                },
            ),
            mock.patch("esistatus.views.render") as mock_render,
        ):
            ajax_esi_status(request)

            mock_render.assert_called_once_with(
                request=request,
                template_name="esistatus/partials/index/esi-status.html",
                context={
                    "esi_endpoint_status": {"status": "OK"},
                    "compatibility_date": "2023-01-01",
                },
            )

    def test_handles_esi_status_view_with_no_data(self):
        """
        Test that the AJAX ESI status view handles no data gracefully

        :return:
        :rtype:
        """

        request = mock.Mock()

        with (
            mock.patch(
                "esistatus.views._esi_status",
                return_value={"esi_status": None, "compatibility_date": None},
            ),
            mock.patch("esistatus.views.render") as mock_render,
        ):
            ajax_esi_status(request)

            mock_render.assert_called_once_with(
                request=request,
                template_name="esistatus/partials/index/esi-status.html",
                context={"esi_endpoint_status": None, "compatibility_date": None},
            )

    def test_renders_dashboard_widget_with_esi_status(self):
        """
        Test that the AJAX dashboard widget renders with ESI status

        :return:
        :rtype:
        """

        request = mock.Mock()

        with (
            mock.patch(
                "esistatus.views._esi_status",
                return_value={
                    "esi_status": {"status": "OK"},
                    "compatibility_date": "2023-01-01",
                },
            ),
            mock.patch("esistatus.views.render") as mock_render,
        ):
            ajax_dashboard_widget(request)

            mock_render.assert_called_once_with(
                request=request,
                template_name="esistatus/partials/dashboard-widget/esi-status.html",
                context={
                    "esi_endpoint_status": {"status": "OK"},
                    "compatibility_date": "2023-01-01",
                },
            )

    def test_handles_missing_esi_status_gracefully(self):
        """
        Test that the AJAX dashboard widget handles missing ESI status gracefully

        :return:
        :rtype:
        """

        request = mock.Mock()

        with (
            mock.patch(
                "esistatus.views._esi_status",
                return_value={"esi_status": None, "compatibility_date": None},
            ),
            mock.patch("esistatus.views.render") as mock_render,
        ):
            ajax_dashboard_widget(request)

            mock_render.assert_called_once_with(
                request=request,
                template_name="esistatus/partials/dashboard-widget/esi-status.html",
                context={"esi_endpoint_status": None, "compatibility_date": None},
            )

    def test_returns_esi_status_with_valid_data(self):
        """
        Test that the _esi_status function returns ESI status with valid data

        :return:
        :rtype:
        """

        with (
            mock.patch("esistatus.views.EsiStatus.objects.get") as mock_get,
            mock.patch(
                "esistatus.views._esi_endpoint_status_from_json"
            ) as mock_status_from_json,
        ):
            mock_get.return_value.status_data = [{"dummy": "data"}]
            mock_get.return_value.compatibility_date = "2023-01-01"
            mock_status_from_json.return_value = {"processed_status": "OK"}

            result = _esi_status()

            self.assertEqual(
                result,
                {
                    "esi_status": {"processed_status": "OK"},
                    "compatibility_date": "2023-01-01",
                },
            )

    def test_processes_empty_esi_status_data(self):
        """
        Test that the _esi_status function processes empty ESI status data

        :return:
        :rtype:
        """

        with (
            mock.patch("esistatus.views.EsiStatus.objects.get") as mock_get,
            mock.patch(
                "esistatus.views._esi_endpoint_status_from_json"
            ) as mock_status_from_json,
        ):
            mock_get.return_value.status_data = []
            mock_get.return_value.compatibility_date = None
            mock_status_from_json.return_value = {}

            result = _esi_status()

            self.assertEqual(result, {"esi_status": {}, "compatibility_date": None})


class TestAjaxEsiStatusDasboardWidget(BaseTestCase):
    """
    Test the AJAX ESI Status view for the dashboard widget
    """

    def test_renders_dashboard_widget_with_esi_status(self):
        """
        Test that the AJAX dashboard widget renders with ESI status

        :return:
        :rtype:
        """

        request = mock.Mock()

        with (
            mock.patch(
                "esistatus.views._esi_status",
                return_value={
                    "esi_status": {"status": "OK"},
                    "compatibility_date": "2023-01-01",
                },
            ),
            mock.patch("esistatus.views.render") as mock_render,
        ):
            ajax_dashboard_widget(request)

            mock_render.assert_called_once_with(
                request=request,
                template_name="esistatus/partials/dashboard-widget/esi-status.html",
                context={
                    "esi_endpoint_status": {"status": "OK"},
                    "compatibility_date": "2023-01-01",
                },
            )

    def test_handles_missing_esi_status_gracefully(self):
        """
        Test that the AJAX dashboard widget handles missing ESI status gracefully

        :return:
        :rtype:
        """

        request = mock.Mock()

        with (
            mock.patch(
                "esistatus.views._esi_status",
                return_value={"esi_status": None, "compatibility_date": None},
            ),
            mock.patch("esistatus.views.render") as mock_render,
        ):
            ajax_dashboard_widget(request)
            mock_render.assert_called_once_with(
                request=request,
                template_name="esistatus/partials/dashboard-widget/esi-status.html",
                context={"esi_endpoint_status": None, "compatibility_date": None},
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


class TestEsiStatus(BaseTestCase):
    """
    Test the _esi_status function
    """

    def test_returns_esi_status_with_valid_data(self):
        """
        Test that the _esi_status function returns ESI status with valid data

        :return:
        :rtype:
        """

        with (
            mock.patch("esistatus.views.EsiStatus.objects.get") as mock_get,
            mock.patch(
                "esistatus.views._esi_endpoint_status_from_json"
            ) as mock_status_from_json,
        ):
            mock_get.return_value.status_data = [{"dummy": "data"}]
            mock_get.return_value.compatibility_date = "2023-01-01"
            mock_status_from_json.return_value = {"processed_status": "OK"}

            result = _esi_status()

            self.assertEqual(
                result,
                {
                    "esi_status": {"processed_status": "OK"},
                    "compatibility_date": "2023-01-01",
                },
            )

    def test_returns_empty_dict_when_esi_status_does_not_exist(self):
        """
        Test that the _esi_status function returns an empty dict when ESI status does not exist

        :return:
        :rtype:
        """

        with (
            mock.patch("esistatus.views.EsiStatus.objects.get") as mock_get,
            mock.patch("esistatus.views.logger") as mock_logger,
        ):
            mock_get.side_effect = EsiStatus.DoesNotExist

            result = _esi_status()

            self.assertEqual(result, {})
            mock_logger.debug.assert_called_once_with("ESI Status data does not exist.")

    def test_processes_empty_esi_status_data(self):
        """
        Test that the _esi_status function processes empty ESI status data

        :return:
        :rtype:
        """

        with (
            mock.patch("esistatus.views.EsiStatus.objects.get") as mock_get,
            mock.patch(
                "esistatus.views._esi_endpoint_status_from_json"
            ) as mock_status_from_json,
        ):
            mock_get.return_value.status_data = []
            mock_get.return_value.compatibility_date = None
            mock_status_from_json.return_value = {}

            result = _esi_status()

            self.assertEqual(result, {"esi_status": {}, "compatibility_date": None})


class TestEsiEndpointStatusFromJson(BaseTestCase):
    """
    Test the _esi_endpoint_status_from_json function
    """

    def test_processes_valid_esi_endpoint_json(self):
        """
        Test that the _esi_endpoint_status_from_json function processes valid ESI endpoint JSON

        :return:
        :rtype:
        """

        esi_endpoint_json = [
            {
                "status": "OK",
                "tags": ["tag1"],
                "path": "/path1",
                "method": "get",
                "operation_id": None,
                "summary": None,
                "description": None,
            },
            {
                "status": "Down",
                "tags": ["tag2"],
                "path": "/path2",
                "method": "post",
                "operation_id": None,
                "summary": None,
                "description": None,
            },
        ]

        result = _esi_endpoint_status_from_json(esi_endpoint_json)

        self.assertEqual(result["OK"]["count"], 1)
        self.assertEqual(result["Down"]["count"], 1)
        self.assertEqual(result["OK"]["endpoints"]["tag1"][0]["path"], "/path1")
        self.assertEqual(result["Down"]["endpoints"]["tag2"][0]["method"], "POST")

    def test_handles_empty_esi_endpoint_json(self):
        """
        Test that the _esi_endpoint_status_from_json function handles empty ESI endpoint JSON

        :return:
        :rtype:
        """

        esi_endpoint_json = []

        result = _esi_endpoint_status_from_json(esi_endpoint_json)

        self.assertEqual(result["OK"]["count"], 0)
        self.assertEqual(result["Down"]["count"], 0)
        self.assertEqual(result["OK"]["percentage"], "0.00%")
        self.assertEqual(result["Down"]["percentage"], "0.00%")

    def test_calculates_percentages_correctly(self):
        """
        Test that the _esi_endpoint_status_from_json function calculates percentages correctly

        :return:
        :rtype:
        """

        esi_endpoint_json = [
            {
                "status": "OK",
                "tags": ["tag1"],
                "path": "/path1",
                "method": "get",
                "operation_id": None,
                "summary": None,
                "description": None,
            },
            {
                "status": "OK",
                "tags": ["tag2"],
                "path": "/path2",
                "method": "post",
                "operation_id": None,
                "summary": None,
                "description": None,
            },
            {
                "status": "Down",
                "tags": ["tag3"],
                "path": "/path3",
                "method": "get",
                "operation_id": None,
                "summary": None,
                "description": None,
            },
        ]

        result = _esi_endpoint_status_from_json(esi_endpoint_json)

        self.assertEqual(result["OK"]["percentage"], "66.67%")
        self.assertEqual(result["Down"]["percentage"], "33.33%")

    def test_sorts_endpoints_alphabetically_by_tag(self):
        """
        Test that the _esi_endpoint_status_from_json function sorts endpoints alphabetically by tag

        :return:
        :rtype:
        """

        esi_endpoint_json = [
            {
                "status": "OK",
                "tags": ["tagB"],
                "path": "/pathB",
                "method": "get",
                "operation_id": None,
                "summary": None,
                "description": None,
            },
            {
                "status": "OK",
                "tags": ["tagA"],
                "path": "/pathA",
                "method": "post",
                "operation_id": None,
                "summary": None,
                "description": None,
            },
        ]

        result = _esi_endpoint_status_from_json(esi_endpoint_json)

        self.assertEqual(list(result["OK"]["endpoints"].keys()), ["tagA", "tagB"])


class TestRenderEsiStatus(BaseTestCase):
    """
    Test the rendering of ESI status in views
    """

    def test_renders_context_with_compat_date_when_flag_is_true(self):
        """
        Test that the context includes compatibility date when the flag is true

        :return:
        :rtype:
        """

        request = mock.Mock()

        with (
            mock.patch(
                "esistatus.views._esi_status",
                return_value={
                    "esi_status": {"status": "OK"},
                    "compatibility_date": "2023-01-01",
                },
            ),
            mock.patch("esistatus.views.render") as mock_render,
        ):
            _render_esi_status(
                request=request,
                template_name="esistatus/partials/index/esi-status.html",
                with_compat_date=True,
            )
            mock_render.assert_called_once_with(
                request=request,
                template_name="esistatus/partials/index/esi-status.html",
                context={
                    "esi_endpoint_status": {"status": "OK"},
                    "compatibility_date": "2023-01-01",
                },
            )

    def test_excludes_compat_date_from_context_when_flag_is_false(self):
        """
        Test that the context excludes compatibility date when the flag is false

        :return:
        :rtype:
        """

        request = mock.Mock()

        with (
            mock.patch(
                "esistatus.views._esi_status",
                return_value={
                    "esi_status": {"status": "OK"},
                    "compatibility_date": "2023-01-01",
                },
            ),
            mock.patch("esistatus.views.render") as mock_render,
        ):
            _render_esi_status(
                request=request,
                template_name="esistatus/partials/index/esi-status.html",
                with_compat_date=False,
            )
            mock_render.assert_called_once_with(
                request=request,
                template_name="esistatus/partials/index/esi-status.html",
                context={"esi_endpoint_status": {"status": "OK"}},
            )

    def test_handles_missing_esi_status_gracefully(self):
        """
        Test that the rendering handles missing ESI status gracefully

        :return:
        :rtype:
        """

        request = mock.Mock()

        with (
            mock.patch(
                "esistatus.views._esi_status",
                return_value={},
            ),
            mock.patch("esistatus.views.render") as mock_render,
        ):
            _render_esi_status(
                request=request,
                template_name="esistatus/partials/index/esi-status.html",
                with_compat_date=True,
            )
            mock_render.assert_called_once_with(
                request=request,
                template_name="esistatus/partials/index/esi-status.html",
                context={
                    "esi_endpoint_status": None,
                    "compatibility_date": None,
                },
            )
