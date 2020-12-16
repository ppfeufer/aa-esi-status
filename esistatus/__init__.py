# -*- coding: utf-8 -*-

"""
a couple of variable to use throughout the app
"""

default_app_config: str = "esistatus.apps.AaEsiStatusConfig"

__version__ = "1.0.1"
__title__ = "ESI Status"
__verbose_name__ = "AA ESI Status for Alliance Auth"
__user_agent__ = "{verbose_name} - v{version} - {github_url}".format(
    verbose_name=__verbose_name__,
    version=__version__,
    github_url="https://github.com/ppfeufer/aa-esi-status",
)
