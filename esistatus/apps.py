"""
app config
"""

# Django
from django.apps import AppConfig

# AA ESI Status
from esistatus import __version__


class AaEsiStatusConfig(AppConfig):
    """
    application config
    """

    name = "esistatus"
    label = "esistatus"
    verbose_name = f"ESI Status v{__version__}"
