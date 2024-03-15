"""
Test the apps' template tags
"""

# Django
from django.template import Context, Template
from django.test import TestCase

# AA ESI Status
from esistatus import __version__


class TestVersionedStatic(TestCase):
    """
    Test the esistatus_static template tag
    """

    def test_versioned_static(self):
        """
        Test should return a versioned static file

        :return:
        :rtype:
        """

        context = Context(dict_={"version": __version__})
        template_to_render = Template(
            template_string=(
                "{% load esistatus %}"
                "{% esistatus_static 'esistatus/css/esistatus.min.css' %}"
            )
        )

        rendered_template = template_to_render.render(context=context)

        self.assertInHTML(
            needle=f'/static/esistatus/css/esistatus.min.css?v={context["version"]}',
            haystack=rendered_template,
        )
