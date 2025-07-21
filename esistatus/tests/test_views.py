"""
Test the apps' views
"""

# Standard Library
import json
from http import HTTPStatus
from unittest.mock import MagicMock, Mock, patch

# Third Party
import requests

# Django
from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse

# Alliance Auth (External Libs)
from app_utils.testing import create_fake_user

# AA ESI Status
from esistatus import views
from esistatus.views import (
    _append_value,
    _esi_endpoint_status_from_json,
    _esi_status,
    dashboard_widget,
)


class TestAppendValue(TestCase):
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


class TestDashboardWidget(TestCase):
    """
    Test the dashboard widget
    """

    def setUp(self):
        """
        Set up the test case

        :return:
        :rtype:
        """

        self.superuser = create_fake_user(
            character_id=1002, character_name="Clark Kent"
        )
        self.superuser.is_superuser = True
        self.superuser.is_staff = True

        self.normal_user = create_fake_user(
            character_id=1001, character_name="Peter Parker"
        )

        self.widget_wrapper = '<div id="esi-status-dashboard-panel" class="aa-esistatus col-12 mb-3 collapse"></div>'

    def test_dashboard_widget_with_superuser(self):
        """
        Test that a superuser sees the ESI status widget

        :param mock_render_to_string:
        :type mock_render_to_string:
        :return:
        :rtype:
        """

        request = MagicMock(spec=HttpRequest)
        request.user = MagicMock()
        request.user.is_superuser = True
        request.META = {}

        result = dashboard_widget(request)

        self.assertInHTML(self.widget_wrapper, result)

    def test_dashboard_widget_with_normal_user(self):
        """
        Test that a normal user does not see the ESI status widget

        :return:
        :rtype:
        """

        request = MagicMock(spec=HttpRequest)
        request.user = MagicMock()
        request.user.is_superuser = False
        request.META = {}

        result = dashboard_widget(request)

        self.assertEqual(result, "")


class TestAjaxEsiStatus(TestCase):
    """
    Test the AJAX ESI Status view
    """

    def setUp(self):
        """
        Set up users

        :return:
        :rtype:
        """

        self.superuser = create_fake_user(
            character_id=1002, character_name="Clark Kent"
        )
        self.superuser.is_superuser = True

        self.client.force_login(user=self.superuser)

    @patch("esistatus.views._esi_status")
    def test_ajax_esi_status_with_status_result(self, mock_esi_status):
        """
        Test the AJAX ESI Status view with HTTPStatus.OK

        :param mock_esi_status:
        :type mock_esi_status:
        :return:
        :rtype:
        """

        mock_esi_status.return_value = (True, {})

        response = self.client.get(path=reverse(viewname="esistatus:ajax_esi_status"))

        self.assertEqual(first=response.status_code, second=HTTPStatus.OK)


class TestAjaxEsiStatusDasboardWidget(TestCase):
    """
    Test the AJAX ESI Status view for the dashboard widget
    """

    def setUp(self):
        """
        Set up users

        :return:
        :rtype:
        """

        self.superuser = create_fake_user(
            character_id=1002, character_name="Clark Kent"
        )
        self.superuser.is_superuser = True

        self.client.force_login(user=self.superuser)

    @patch("esistatus.views._esi_status")
    def test_ajax_esi_status_with_status_result(self, mock_esi_status):
        """
        Test the AJAX ESI Status view with HTTPStatus.OK

        :param mock_esi_status:
        :type mock_esi_status:
        :return:
        :rtype:
        """

        mock_esi_status.return_value = (True, {})

        response = self.client.get(
            path=reverse(viewname="esistatus:ajax_dashboard_widget")
        )

        self.assertEqual(first=response.status_code, second=HTTPStatus.OK)

    @patch("esistatus.views._esi_status")
    def test_ajax_esi_status_without_status_result(self, mock_esi_status):
        """
        Test the AJAX ESI Status view with HTTPStatus.NO_CONTENT

        :param mock_esi_status:
        :type mock_esi_status:
        :return:
        :rtype:
        """

        mock_esi_status.return_value = (False, {})

        response = self.client.get(
            path=reverse(viewname="esistatus:ajax_dashboard_widget")
        )

        self.assertEqual(first=response.status_code, second=HTTPStatus.NO_CONTENT)


class TestIndex(TestCase):
    """
    Test the index view
    """

    def setUp(self):
        """
        Set up users

        :return:
        :rtype:
        """

        self.superuser = create_fake_user(
            character_id=1002, character_name="Clark Kent"
        )
        self.superuser.is_superuser = True

        self.client.force_login(user=self.superuser)

    @patch("esistatus.views._esi_status")
    def test_index_with_status_result(self, mock_esi_status):
        """
        Test the index view with a status result

        :param mock_esi_status:
        :type mock_esi_status:
        :return:
        :rtype:
        """

        mock_esi_status.return_value = (True, {})
        response = self.client.get(path=reverse(viewname="esistatus:index"))

        self.assertEqual(first=response.status_code, second=HTTPStatus.OK)

    @patch("esistatus.views._esi_status")
    def test_index_without_status_result(self, mock_esi_status):
        """
        Test the index view without a status result

        :param mock_esi_status:
        :type mock_esi_status:
        :return:
        :rtype:
        """

        mock_esi_status.return_value = (False, {})
        response = self.client.get(path=reverse(viewname="esistatus:index"))

        self.assertEqual(first=response.status_code, second=HTTPStatus.OK)


class TestEsiStatus(TestCase):
    """
    Test the _esi_status function
    """

    @patch("requests.get")
    def test_esi_status_with_valid_response(self, mock_get):
        """
        Test the _esi_status function with a valid response

        :param mock_get:
        :type mock_get:
        :return:
        :rtype:
        """

        mock_get.return_value.json.return_value = []
        mock_get.return_value.raise_for_status.return_value = None
        has_status_result, esi_endpoint_status = views._esi_status()

        self.assertTrue(has_status_result)
        self.assertEqual(
            first=esi_endpoint_status,
            second={
                "green": {"endpoints": {}, "count": 0, "percentage": "0.00%"},
                "yellow": {"endpoints": {}, "count": 0, "percentage": "0.00%"},
                "red": {"endpoints": {}, "count": 0, "percentage": "0.00%"},
            },
        )

    @patch("esistatus.views.requests.get")
    def test_esi_status_request_exception(self, mock_get):
        """
        Test the _esi_status function with a request exception

        :param mock_get:
        :type mock_get:
        :return:
        :rtype:
        """

        mock_get.side_effect = requests.exceptions.RequestException("Error")

        has_status_result, error_str = _esi_status()

        self.assertFalse(has_status_result)
        self.assertIn("Error", error_str)

    @patch("esistatus.views.requests.get")
    def test_esi_status_request_exception_with_response(self, mock_get):
        """
        Test the _esi_status function with a request exception that has a response

        :param mock_get:
        :type mock_get:
        :return:
        :rtype:
        """

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.reason = "Internal Server Error"
        mock_get.side_effect = requests.exceptions.RequestException(
            response=mock_response
        )

        has_status_result, error_str = _esi_status()

        self.assertFalse(has_status_result)
        self.assertEqual(error_str, "500 - Internal Server Error")

    @patch("esistatus.views.requests.get")
    def test_esi_status_request_exception_without_response(self, mock_get):
        """
        Test the _esi_status function with a request exception that does not have a response

        :param mock_get:
        :type mock_get:
        :return:
        :rtype:
        """

        mock_get.side_effect = requests.exceptions.RequestException("Network Error")

        has_status_result, error_str = _esi_status()

        self.assertFalse(has_status_result)
        self.assertEqual(error_str, "Network Error")

    @patch("esistatus.views.requests.get")
    def test_esi_status_json_decode_error(self, mock_get):
        """
        Test the _esi_status function with a JSON decode error

        :param mock_get:
        :type mock_get:
        :return:
        :rtype:
        """

        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Error", "", 0)
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        has_status_result, esi_endpoint_status = _esi_status()

        self.assertFalse(has_status_result)
        self.assertEqual(esi_endpoint_status, {})

    def test_returns_correct_status_counts_and_percentages(self):
        """
        Test the _esi_endpoint_status_from_json function with a sample ESI endpoint JSON

        :return:
        """

        esi_endpoint_json = [
            {"status": "green", "tags": ["tag1"], "route": "/route1", "method": "get"},
            {
                "status": "yellow",
                "tags": ["tag2"],
                "route": "/route2",
                "method": "post",
            },
            {"status": "red", "tags": ["tag3"], "route": "/route3", "method": "put"},
            {"status": "green", "tags": ["tag1"], "route": "/route4", "method": "get"},
        ]
        has_status_result, esi_endpoint_status = _esi_endpoint_status_from_json(
            esi_endpoint_json
        )
        self.assertTrue(has_status_result)
        self.assertEqual(esi_endpoint_status["green"]["count"], 2)
        self.assertEqual(esi_endpoint_status["yellow"]["count"], 1)
        self.assertEqual(esi_endpoint_status["red"]["count"], 1)
        self.assertEqual(esi_endpoint_status["green"]["percentage"], "50.00%")
        self.assertEqual(esi_endpoint_status["yellow"]["percentage"], "25.00%")
        self.assertEqual(esi_endpoint_status["red"]["percentage"], "25.00%")

    def test_handles_empty_esi_endpoint_json(self):
        """
        Test the _esi_endpoint_status_from_json function with an empty ESI endpoint JSON

        :return:
        """

        esi_endpoint_json = []
        has_status_result, esi_endpoint_status = _esi_endpoint_status_from_json(
            esi_endpoint_json
        )
        self.assertTrue(has_status_result)
        self.assertEqual(esi_endpoint_status["green"]["count"], 0)
        self.assertEqual(esi_endpoint_status["yellow"]["count"], 0)
        self.assertEqual(esi_endpoint_status["red"]["count"], 0)
        self.assertEqual(esi_endpoint_status["green"]["percentage"], "0.00%")
        self.assertEqual(esi_endpoint_status["yellow"]["percentage"], "0.00%")
        self.assertEqual(esi_endpoint_status["red"]["percentage"], "0.00%")
