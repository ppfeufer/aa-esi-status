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

        cls.user_1001 = create_fake_user(
            character_id=1001, character_name="Peter Parker"
        )

        cls.html_menu = f"""
            <li class="d-flex flex-wrap m-2 p-2 pt-0 pb-0 mt-0 mb-0 me-0 pe-0">
                <i class="nav-link fas fa-signal fa-fw align-self-center me-3 active"></i>
                <a class="nav-link flex-fill align-self-center" href="{reverse('esistatus:index')}">
                    ESI Status
                </a>
            </li>
        """

        cls.html_header = """
            <div class="aa-esistatus-header">
                <header>
                    <h1 class="text-center">
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

        self.client.force_login(user=self.user_1001)

        response = self.client.get(path=reverse(viewname="esistatus:index"))

        self.assertEqual(first=response.status_code, second=HTTPStatus.OK)
        self.assertContains(response=response, text=self.html_menu, html=True)
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
