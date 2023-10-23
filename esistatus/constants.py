"""
Constants used in this app
"""

# Django
from django.utils.text import slugify

# AA ESI Status
from esistatus import __version__
from esistatus.app_settings import template_path

VERBOSE_NAME = "AA ESI Status for Alliance Auth"

slugified_name: str = slugify(VERBOSE_NAME, allow_unicode=True)
github_url: str = "https://github.com/ppfeufer/aa-esi-status"

USER_AGENT = f"{slugified_name} v{__version__} {github_url}"

TEMPLATE_PATH = template_path()
