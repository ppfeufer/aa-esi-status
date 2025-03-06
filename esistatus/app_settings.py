"""
App Settings
"""

# Standard Library
from re import RegexFlag

# Django
from django.conf import settings


def debug_enabled() -> RegexFlag:
    """
    Check if DEBUG is enabled

    :return:
    :rtype:
    """

    return settings.DEBUG
