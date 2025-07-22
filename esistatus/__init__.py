"""
A couple of variables to use throughout the app
"""

# Third Party
import requests

# Django
from django.utils.translation import gettext_lazy as _

__version__ = "2.8.1"
__title__ = _("ESI Status")

__package_name__ = "aa-esi-status"
__package_name_verbose__ = "AA ESI Status"
__package_name_useragent__ = "AA-ESI-Status"
__app_name__ = "esistatus"
__github_url__ = f"https://github.com/ppfeufer/{__package_name__}"
__user_agent__ = (
    f"{__package_name_useragent__}/{__version__} "
    f"(+{__github_url__}) requests/{requests.__version__}"
)
