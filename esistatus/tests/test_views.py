"""
Test for the UI
"""

# Standard Library
from unittest.mock import patch

# Third Party
from django_webtest import WebTest

# AA ESI Status
from esistatus.views import _get_template_path

VIEWS_PATH = "esistatus.views"


class TestBulletinUI(WebTest):
    """
    Test ESI Status UI
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up tests

        :return:
        :rtype:
        """

        super().setUpClass()

        cls.template_path = _get_template_path()

    def test_should_return_template_path(self):
        """
        Test should return the template path

        :return:
        :rtype:
        """

        with patch(target=VIEWS_PATH + ".allianceauth__version", new="4.0.0"):
            template_path = _get_template_path()
            expected_template_path = "esistatus"

            self.assertEqual(first=template_path, second=expected_template_path)

    def test_should_return_legacy_template_path(self):
        """
        Test should return the template path to the legacy templates

        :return:
        :rtype:
        """

        with patch(target=VIEWS_PATH + ".allianceauth__version", new="3.7.1"):
            template_path = _get_template_path()
            expected_template_path = "esistatus/legacy_templates"

            self.assertEqual(first=template_path, second=expected_template_path)
