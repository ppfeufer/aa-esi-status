"""
App Settings
"""

# Django
from django.conf import settings

# Retention period for ESI status history in hours (default: 24 hours)
ESISTATUS_HISTORY_RETENTION_PERIOD = getattr(
    settings, "ESISTATUS_HISTORY_RETENTION_PERIOD", 24
)

# Display period for ESI status history in hours (default: 24 hours)
ESISTATUS_SHOW_HISTORY_THRESHOLD = getattr(
    settings, "ESISTATUS_SHOW_HISTORY_THRESHOLD", 24
)


def debug_enabled() -> bool:
    """
    Check if DEBUG is enabled

    :return: True if DEBUG is enabled, False otherwise
    :rtype: bool
    """

    return settings.DEBUG
