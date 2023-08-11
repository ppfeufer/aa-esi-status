"""
Test auth_hooks
"""

# Standard Library
from http import HTTPStatus

# Django
from django.test import TestCase
from django.urls import reverse

# AA ESI Status
from esistatus.tests.utils import create_fake_user


class TestHooks(TestCase):
    """
    Test the app hook into allianceauth
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up groups and users
        """

        super().setUpClass()

        cls.user_1001 = create_fake_user(1001, "Peter Parker")

        cls.html_menu = f"""
            <li>
                <a class="active" href="{reverse('esistatus:index')}">
                    <i class="fas fa-signal fa-fw"></i>
                    ESI Status
                </a>
            </li>
        """

        cls.html_header = """
            <div class="aa-esistatus-header">
                <header>
                    <h1 class="page-header text-center">
                        ESI Status
                    </h1>
                </header>
            </div>
        """

    def test_render_hook_success(self):
        """
        Test should show the link to the app in the navigation to user with access
        :return:
        :rtype:
        """

        self.client.force_login(self.user_1001)

        response = self.client.get(path=reverse(viewname="esistatus:index"))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, self.html_menu, html=True)
        self.assertContains(response=response, text=self.html_header, html=True)

    def test_render_hook_with_public_page(self):
        """
        Test should show the public page

        :return:
        :rtype:
        """

        response = self.client.get(path=reverse(viewname="esistatus:index"))

        self.assertEqual(first=response.status_code, second=HTTPStatus.OK)
        self.assertContains(response=response, text=self.html_header, html=True)
