"""
utilities
"""

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA ESI Status
from esistatus import __title__

logger = LoggerAddTag(get_extension_logger(__name__), __title__)
