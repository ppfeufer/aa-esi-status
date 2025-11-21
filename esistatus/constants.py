"""
Constants we use throughout the app
"""

# All internal URLs need to start with this prefix
INTERNAL_URL_PREFIX = "-"


# Standard Library
from enum import Enum


class ESIMetaUrl(Enum):
    """
    ESI Meta Endpoint URLs
    """

    COMPATIBILITY_DATES = "https://esi.evetech.net/meta/compatibility-dates"
    """ESI Compatibility Dates URL"""

    STATUS = (
        "https://esi.evetech.net/meta/status?compatibility_date={compatibility_date}"
    )
    """ESI Status URL"""

    OPENAPI_SPECS = "https://esi.evetech.net/meta/openapi.json?compatibility_date={compatibility_date}"
    """ESI OpenAPI Specs URL"""
