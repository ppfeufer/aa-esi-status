"""
A couple of variables to use throughout the app
"""

# Third Party
import requests

# Django
from django.utils.translation import gettext_lazy as _

__version__ = "2.5.4"
__title__ = _("ESI Status")

__app_name__ = "aa-esi-status"
__app_verbose_name__ = "AA ESI Status"
__app_verbose_useragent__ = "AA-ESI-Status"

__github_url__ = f"https://github.com/ppfeufer/{__app_name__}"

__user_agent__ = f"{__app_verbose_useragent__}/{__version__} (+{__github_url__}) requests/{requests.__version__}"
