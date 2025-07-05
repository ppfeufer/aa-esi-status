"""
App config
"""

# Django
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

# AA ESI Status
from esistatus import __app_name__, __version__


class AaEsiStatusConfig(AppConfig):
    """
    Application config
    """

    name = __app_name__
    label = __app_name__
    verbose_name = _(f"ESI Status v{__version__}")
