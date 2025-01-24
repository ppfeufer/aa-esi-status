"""
Test the apps' template tags
"""

# Django
from django.template import Context, Template
from django.test import TestCase, override_settings

# AA ESI Status
from esistatus import __version__
from esistatus.helper.static_files import calculate_integrity_hash


class TestVersionedStatic(TestCase):
    """
    Test aa_bulletin_board_static template tag
    """

    @override_settings(DEBUG=False)
    def test_versioned_static_without_debug_enabled(self) -> None:
        """
        Test versioned static template tag without DEBUG enabled

        :return:
        :rtype:
        """

        context = Context({"version": __version__})
        template_to_render = Template(
            template_string=(
                "{% load esistatus %}"
                "{% esistatus_static 'css/esistatus.min.css' %}"
                "{% esistatus_static 'javascript/esistatus-dashboard-widget.min.js' %}"
            )
        )

        rendered_template = template_to_render.render(context=context)

        expected_static_css_src = (
            f'/static/esistatus/css/esistatus.min.css?v={context["version"]}'
        )
        expected_static_css_src_integrity = calculate_integrity_hash(
            "css/esistatus.min.css"
        )
        expected_static_js_src = f'/static/esistatus/javascript/esistatus-dashboard-widget.min.js?v={context["version"]}'
        expected_static_js_src_integrity = calculate_integrity_hash(
            "javascript/esistatus-dashboard-widget.min.js"
        )

        self.assertIn(member=expected_static_css_src, container=rendered_template)
        self.assertIn(
            member=expected_static_css_src_integrity, container=rendered_template
        )
        self.assertIn(member=expected_static_js_src, container=rendered_template)
        self.assertIn(
            member=expected_static_js_src_integrity, container=rendered_template
        )

    @override_settings(DEBUG=True)
    def test_versioned_static_with_debug_enabled(self) -> None:
        """
        Test versioned static template tag with DEBUG enabled

        :return:
        :rtype:
        """

        context = Context({"version": __version__})
        template_to_render = Template(
            template_string=(
                "{% load esistatus %}" "{% esistatus_static 'css/esistatus.min.css' %}"
            )
        )

        rendered_template = template_to_render.render(context=context)

        expected_static_css_src = (
            f'/static/esistatus/css/esistatus.min.css?v={context["version"]}'
        )

        self.assertIn(member=expected_static_css_src, container=rendered_template)
        self.assertNotIn(member="integrity=", container=rendered_template)
