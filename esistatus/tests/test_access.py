"""
Test checks for access to fleetpings
"""

# Standard Library
from http import HTTPStatus

# Django
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

# AA ESI Status
from esistatus.tests.utils import create_fake_user


class TestAccess(TestCase):
    """
    Test access to the app
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up groups and users
        """

        super().setUpClass()

        cls.group = Group.objects.create(name="Superhero")

        cls.user_1001 = create_fake_user(
            character_id=1001, character_name="Peter Parker"
        )

    def test_has_access(self):
        """
        Test that a user without access gets a 302

        :return:
        :rtype:
        """

        # when
        res = self.client.get(path=reverse(viewname="esistatus:index"))

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_logged_in_has_access(self):
        """
        Test that a user with access gets to see it

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        res = self.client.get(path=reverse(viewname="esistatus:index"))

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)
