"""
App config
"""

# Django
from django.apps import AppConfig
from django.utils.text import format_lazy

# AA ESI Status
from esistatus import __app_name__, __title_translated__, __version__


class AaEsiStatusConfig(AppConfig):
    """
    Application config
    """

    name = __app_name__
    label = __app_name__
    verbose_name = format_lazy(
        "{app_title} v{version}", app_title=__title_translated__, version=__version__
    )
