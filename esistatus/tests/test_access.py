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
        cls.user_1002 = create_fake_user(character_id=1002, character_name="Clark Kent")
        cls.user_1002.is_superuser = True
        cls.user_1003 = create_fake_user(
            character_id=1003, character_name="Bruce Wayne"
        )
        cls.user_1003.is_staff = True

    def test_has_access(self):
        """
        Test that a user without access gets a 302
        """

        # when
        res = self.client.get(path=reverse(viewname="esistatus:index"))

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_logged_in_has_access(self):
        """
        Test that a user with access gets to see it
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        res = self.client.get(path=reverse(viewname="esistatus:index"))

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_superuser_has_access(self):
        """
        Test that a superuser has access
        """

        # given
        self.client.force_login(user=self.user_1002)

        # when
        res = self.client.get(path=reverse(viewname="esistatus:index"))

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_staff_user_has_access(self):
        """
        Test that a staff user has access
        """

        # given
        self.client.force_login(user=self.user_1003)

        # when
        res = self.client.get(path=reverse(viewname="esistatus:index"))

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_response_content(self):
        """
        Test that the response contains the expected content
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        res = self.client.get(path=reverse(viewname="esistatus:index"))

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)
        self.assertContains(response=res, text="ESI Status")
