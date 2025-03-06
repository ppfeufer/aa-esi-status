"""
Constants used in this app
"""

# Standard Library
import os

# Third Party
from requests.__version__ import __version__ as requests_version

# AA ESI Status
from esistatus import __version__

APP_NAME = "aa-esi-status"
APP_NAME_VERBOSE = "AA ESI Status"
APP_NAME_VERBOSE_USERAGENT = "AA-ESI-Status"
PACKAGE_NAME = "esistatus"
GITHUB_URL = f"https://github.com/ppfeufer/{APP_NAME}"
USER_AGENT = f"{APP_NAME_VERBOSE_USERAGENT}/{__version__} (+{GITHUB_URL}) requests/{requests_version}"

APP_BASE_DIR = os.path.join(os.path.dirname(__file__))
APP_STATIC_DIR = os.path.join(APP_BASE_DIR, "static", PACKAGE_NAME)
