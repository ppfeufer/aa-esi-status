# -*- coding: utf-8 -*-

"""
app config
"""

from django.apps import AppConfig

from esistatus import __version__


class AaEsiStatusConfig(AppConfig):
    """
    application config
    """

    name = "esistatus"
    label = "esistatus"
    verbose_name = "ESI Statusv{}".format(__version__)
