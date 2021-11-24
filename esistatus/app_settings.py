"""
our app setting
"""

from esistatus.utils import clean_setting

# AA-GDPR
AVOID_CDN = clean_setting("AVOID_CDN", False)


def avoid_cdn() -> bool:
    """
    check if we should aviod CDN usage
    :return: bool
    """

    return AVOID_CDN
