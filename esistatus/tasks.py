"""
Tasks for ESI status monitoring.
"""

# Standard Library
import json

# Third Party
import requests
from celery import shared_task

# Django
from django.utils.datetime_safe import date, datetime

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA ESI Status
from esistatus import __title__, __user_agent__
from esistatus.constants import ESIMetaUrl
from esistatus.handler import cache as cache_handler

logger = LoggerAddTag(my_logger=get_extension_logger(__name__), prefix=__title__)

request_headers = {"User-Agent": __user_agent__}


def _get_latest_compatibility_date() -> str | None:
    """
    Retrieve the latest ESI compatibility date.

    :return:
    :rtype:
    """

    logger.debug(msg="Retrieving latest ESI compatibility date.")

    url = ESIMetaUrl.COMPATIBILITY_DATES.value

    cached = cache_handler._get_cache(url)
    if cached:
        logger.debug(msg=f"Using cached ESI compatibility date: {cached}")

        return cached

    try:
        response = requests.get(url=url, headers=request_headers, timeout=10)
        response.raise_for_status()

        compatibility_dates = response.json()
        dates = compatibility_dates.get("compatibility_dates", [])

        logger.debug(msg=f"ESI compatibility dates response: {compatibility_dates}")

        def _parse_date(s: str) -> date | None:
            """
            Parse a date string in YYYY-MM-DD format.

            :param s:
            :type s:
            :return:
            :rtype:
            """

            try:
                return datetime.strptime(s, "%Y-%m-%d").date()
            except (TypeError, ValueError):
                return None

        date_objs = [d for d in (_parse_date(s) for s in dates) if d]

        if not date_objs:
            logger.debug(msg="No valid ESI compatibility dates found.")

            return None

        latest = max(date_objs).isoformat()

        logger.debug(msg=f"Latest ESI compatibility date: {latest}")

        cache_handler._set_cache(url, latest)

        return latest
    except requests.exceptions.RequestException as exc:
        resp = getattr(exc, "response", None)
        error_str = (
            f"{resp.status_code} - {resp.reason}" if resp is not None else str(exc)
        )

        logger.debug(msg=f"Unable to get ESI compatibility dates. Error: {error_str}")

        return None
    except json.JSONDecodeError:
        logger.debug(
            msg="Unable to get ESI status. ESI returning gibberish, I can't understand …"
        )

        return None


def _get_esi_status_json(compatibility_date: str) -> dict | None:
    """
    Retrieve the ESI status JSON for a given compatibility date.

    :param compatibility_date:
    :type compatibility_date:
    :return:
    :rtype:
    """

    status_url = ESIMetaUrl.STATUS.value.format(compatibility_date=compatibility_date)

    try:
        response = requests.get(url=status_url, headers=request_headers, timeout=10)
        response.raise_for_status()
        esi_status = response.json()

        logger.info(
            f"ESI status fetched successfully for for compatibility date: {compatibility_date}."
        )

        return esi_status
    except requests.exceptions.RequestException as exc:
        resp = getattr(exc, "response", None)
        error_str = (
            f"{resp.status_code} - {resp.reason}" if resp is not None else str(exc)
        )

        logger.error(f"Unable to update ESI status. Error: {error_str}")

        return None
    except json.JSONDecodeError:
        logger.error("Unable to update ESI status. ESI returned invalid JSON.")

        return None


def _get_openapi_specs_json(compatibility_date: str) -> dict | None:
    """
    Retrieve the ESI OpenAPI specs JSON for a given compatibility date.

    :param compatibility_date:
    :type compatibility_date:
    :return:
    :rtype:
    """

    openapi_url = ESIMetaUrl.OPENAPI_SPECS.value.format(
        compatibility_date=compatibility_date
    )

    cached = cache_handler._get_cache(openapi_url)
    if cached:
        logger.debug(
            msg=f"Using cached ESI OpenAPI specs for compatibility date: {compatibility_date}."
        )

        return cached

    try:
        response = requests.get(url=openapi_url, headers=request_headers, timeout=10)
        response.raise_for_status()
        openapi_specs = response.json()

        logger.info(
            f"ESI OpenAPI specs fetched successfully for compatibility date: {compatibility_date}."
        )

        cache_handler._set_cache(openapi_url, openapi_specs)

        return openapi_specs
    except requests.exceptions.RequestException as exc:
        resp = getattr(exc, "response", None)
        error_str = (
            f"{resp.status_code} - {resp.reason}" if resp is not None else str(exc)
        )

        logger.error(f"Unable to fetch ESI OpenAPI specs. Error: {error_str}")

        return None
    except json.JSONDecodeError:
        logger.error("Unable to fetch ESI OpenAPI specs. ESI returned invalid JSON.")

        return None


@shared_task()
def update_esi_status():
    """
    Task to update ESI status.
    """

    logger.debug("Starting ESI status update task.")

    latest_compatibility_date = _get_latest_compatibility_date()

    if latest_compatibility_date is None:
        logger.error("Failed to retrieve latest compatibility date.")

        return

    esi_status = _get_esi_status_json(compatibility_date=latest_compatibility_date)
    openapi_specs = _get_openapi_specs_json(
        compatibility_date=latest_compatibility_date
    )

    if esi_status is None or openapi_specs is None:
        logger.error("Failed to retrieve ESI status or OpenAPI specs.")

        return
