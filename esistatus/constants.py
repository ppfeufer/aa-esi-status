# coding=utf-8

"""
constants used in this app
"""

from django.utils.text import slugify

from esistatus import __version__

VERBOSE_NAME = "AA ESI Status for Alliance Auth"
USER_AGENT = "{verbose_name} v{version} {github_url}".format(
    verbose_name=slugify(VERBOSE_NAME, allow_unicode=True),
    version=__version__,
    github_url="https://github.com/ppfeufer/aa-esi-status",
)
