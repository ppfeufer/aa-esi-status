"""
Constants used in this app
"""

# Third Party
from requests.__version__ import __version__ as requests_version

# AA ESI Status
from esistatus import __version__

APP_NAME = "aa-esi-status"
GITHUB_URL = f"https://github.com/ppfeufer/{APP_NAME}"
USER_AGENT = f"{APP_NAME}/{__version__} ({GITHUB_URL}) via requests/{requests_version}"
