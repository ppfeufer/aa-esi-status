"""
Test the apps' template tags
"""

# Django
from django.template import Context, Template
from django.test import TestCase

# AA ESI Status
from esistatus import __version__


class TestVersionedStatic(TestCase):
    def test_versioned_static(self):
        context = Context({"version": __version__})
        template_to_render = Template(
            "{% load esistatus_versioned_static %}"
            "{% esistatus_static 'esistatus/css/esistatus.min.css' %}"
        )

        rendered_template = template_to_render.render(context)

        self.assertInHTML(
            f'/static/esistatus/css/esistatus.min.css?v={context["version"]}',
            rendered_template,
        )
