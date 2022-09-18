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

        # User cannot access fleetpings
        cls.user_1001 = create_fake_user(1001, "Peter Parker")

        # User can access fleetpings
        cls.user_1002 = create_fake_user(
            1002, "Bruce Wayne", permissions=["esistatus.basic_access"]
        )

    def test_has_no_access(self):
        """
        Test that a user without access get a 302
        :return:
        """

        # given
        self.client.force_login(self.user_1001)

        # when
        res = self.client.get(reverse("esistatus:index"))

        # then
        self.assertEqual(res.status_code, HTTPStatus.FOUND)

    def test_has_access(self):
        """
        Test that a user with access get to see it
        :return:
        """

        # given
        self.client.force_login(self.user_1002)

        # when
        res = self.client.get(reverse("esistatus:index"))

        # then
        self.assertEqual(res.status_code, HTTPStatus.OK)
