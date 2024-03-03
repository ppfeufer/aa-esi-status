"""
Test the apps' views
"""

# Standard Library
import json
from http import HTTPStatus
from unittest.mock import patch

# Third Party
from requests import RequestException

# Django
from django.test import TestCase
from django.urls import reverse

# Alliance Auth (External Libs)
from app_utils.testing import create_fake_user

# AA ESI Status
from esistatus import views


class TestDashboardWidget(TestCase):
    """
    Test the dashboard widget
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
        self.superuser.is_staff = True

        self.normal_user = create_fake_user(
            character_id=1001, character_name="Peter Parker"
        )

    # def test_dashboard_widget_with_superuser(self):
    #     self.client.force_login(self.superuser)
    #     response = self.client.get(path=reverse(viewname="authentication:dashboard"))
    #     self.assertContains(
    #         response,
    #         '<div class="card-title text-center mb-0">ESI Status</div>',
    #         html=True,
    #     )

    def test_dashboard_widget_with_normal_user(self):
        """
        Test that a normal user does not see the ESI status widget

        :return:
        :rtype:
        """

        self.client.force_login(user=self.normal_user)
        response = self.client.get(path=reverse(viewname="authentication:dashboard"))
        self.assertNotContains(
            response=response,
            text='<div class="card-title text-center mb-0">ESI Status</div>',
            html=True,
        )


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
        response = self.client.get(path=reverse(viewname="esistatus:ajax_esi_status"))
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

    @patch("requests.get")
    def test_esi_status_with_request_exception(self, mock_get):
        """
        Test the _esi_status function with a request exception

        :param mock_get:
        :type mock_get:
        :return:
        :rtype:
        """

        mock_get.side_effect = RequestException("Request Exception")
        has_status_result, esi_endpoint_status = views._esi_status()

        self.assertFalse(expr=has_status_result)
        self.assertEqual(first=esi_endpoint_status, second={})

    @patch("requests.get")
    def test_esi_status_with_json_decode_error(self, mock_get):
        """
        Test the _esi_status function with a JSON decode error

        :param mock_get:
        :type mock_get:
        :return:
        :rtype:
        """

        mock_get.return_value.json.side_effect = json.JSONDecodeError(
            msg="Expecting property name enclosed in double quotes", doc="{}", pos=0
        )
        has_status_result, esi_endpoint_status = views._esi_status()

        self.assertFalse(expr=has_status_result)
        self.assertEqual(first=esi_endpoint_status, second={})
