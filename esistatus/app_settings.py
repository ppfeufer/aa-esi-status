"""
Application settings
"""

# Third Party
from packaging import version

# Alliance Auth
from allianceauth import __version__ as allianceauth__version
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA ESI Status
from esistatus import __title__
from esistatus.apps import AaEsiStatusConfig

logger = LoggerAddTag(my_logger=get_extension_logger(name=__name__), prefix=__title__)


def allianceauth_major_version():
    """
    Get the major version of the current installed Alliance Auth instance

    :return:
    :rtype:
    """

    return version.parse(allianceauth__version).major


def template_path() -> str:
    """
    Get template path

    This is used to determine if we have Alliance Auth v4 or still v3, in which case we
    have to fall back to the legacy templates to ensure backwards compatibility

    :return:
    :rtype:
    """

    current_aa_major = allianceauth_major_version()
    app_name = AaEsiStatusConfig.name

    if current_aa_major < 4:
        logger.debug(
            msg="Alliance Auth v3 detected, falling back to legacy templates …"
        )

        return f"{app_name}/legacy_templates"

    return app_name
