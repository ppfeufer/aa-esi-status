"""
App config
"""

# Django
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

# AA ESI Status
from esistatus import __version__


class AaEsiStatusConfig(AppConfig):
    """
    Application config
    """

    name = "esistatus"
    label = "esistatus"
    verbose_name = _(f"ESI Status v{__version__}")
