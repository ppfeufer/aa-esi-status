"""
Test for the UI
"""

# Standard Library
from unittest.mock import patch

# Third Party
from django_webtest import WebTest

# AA ESI Status
from esistatus.app_settings import allianceauth_major_version, template_path
from esistatus.constants import TEMPLATE_PATH


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

        cls.template_path = TEMPLATE_PATH

    def test_should_return_aa_major_version(self):
        """
        Test should return the major version of the installed AA instance

        :return:
        :rtype:
        """

        with patch(target="esistatus.app_settings.allianceauth__version", new="4.0.0"):
            curren_aa_major_version = allianceauth_major_version()
            expected_aa_major_version = 4

            self.assertEqual(
                first=curren_aa_major_version, second=expected_aa_major_version
            )

    def test_should_return_template_path(self):
        """
        Test should return the template path

        :return:
        :rtype:
        """

        with patch(target="esistatus.app_settings.allianceauth__version", new="4.0.0"):
            current_template_path = template_path()
            expected_template_path = "esistatus"

            self.assertEqual(first=current_template_path, second=expected_template_path)

    def test_should_return_legacy_template_path(self):
        """
        Test should return the template path to the legacy templates

        :return:
        :rtype:
        """

        with patch(target="esistatus.app_settings.allianceauth__version", new="3.7.1"):
            current_template_path = template_path()
            expected_template_path = "esistatus/legacy_templates"

            self.assertEqual(first=current_template_path, second=expected_template_path)
