"""
Tasks for ESI status monitoring.
"""

# Standard Library
import json
from typing import Any

# Third Party
import requests
from celery import shared_task

# Django
from django.utils.datetime_safe import datetime

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# AA ESI Status
from esistatus import __title__, __user_agent__
from esistatus.constants import ESIMetaUrl
from esistatus.handler.cache import Cache
from esistatus.models import EsiStatus
from esistatus.providers import AppLogger

logger = AppLogger(my_logger=get_extension_logger(__name__), prefix=__title__)

request_headers = {"User-Agent": __user_agent__}


def _get_latest_compatibility_date() -> str | None:
    """
    Retrieve the latest ESI compatibility date.

    :return:
    :rtype:
    """

    logger.debug("Retrieving latest ESI compatibility date.")

    url = ESIMetaUrl.COMPATIBILITY_DATES.value
    cache_subkey = "compatibility-dates:latest"
    cached = Cache(subkey=cache_subkey).get()

    if cached:
        logger.debug(f"Using cached ESI compatibility date: {cached}")

        return cached

    try:
        response = requests.get(url, headers=request_headers, timeout=10)
        response.raise_for_status()

        dates = response.json().get("compatibility_dates", [])

        logger.debug(f"ESI compatibility dates response: {dates}")

        valid_dates = []

        for d in dates:
            if not isinstance(d, str):
                continue

            try:
                valid_dates.append(datetime.strptime(d, "%Y-%m-%d").date())
            except ValueError:
                logger.debug(f"Skipping invalid compatibility date: {d}")

                continue

        if not valid_dates:
            logger.debug("No valid ESI compatibility dates found.")

            return None

        latest = max(valid_dates).isoformat()

        logger.debug(f"Latest ESI compatibility date: {latest}")

        Cache(subkey=cache_subkey).set(value=latest)

        return latest
    except (requests.exceptions.RequestException, json.JSONDecodeError) as exc:
        logger.debug(f"Error retrieving ESI compatibility dates: {exc}")

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
    cacke_subkey = f"openapi:{compatibility_date}"
    cached = Cache(subkey=cacke_subkey).get()

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

        Cache(subkey=cacke_subkey).set(value=openapi_specs)

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


def _enrich_status_json(status: dict[str, Any], openapi: dict[str, Any]) -> list[Any]:
    """
    Enrich ESI status routes with description, operation_id, summary and tags from OpenAPI specs.

    Inspired by this script by CCP Pinky:
    https://gist.github.com/ccp-pinky/28e60a5a79df5f7db4f7f46704c9f818

    :param status:
    :type status:
    :param openapi:
    :type openapi:
    :return:
    :rtype:
    """

    for route in status["routes"]:
        spec = openapi["paths"].get(route["path"], {}).get(route["method"].lower(), {})

        route["description"] = spec.get("description", None)
        route["operation_id"] = spec.get("operationId", None)
        route["summary"] = spec.get("summary", None)
        route["tags"] = spec.get("tags", ["Deprecated"])

    return status["routes"]


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

    enriched_status = _enrich_status_json(status=esi_status, openapi=openapi_specs)

    if not any(route.get("tags") for route in enriched_status):
        logger.debug("Enriched ESI status has no tags. Skipping database update.")

        return

    EsiStatus.objects.update_or_create(
        pk=1,
        defaults={
            "compatibility_date": latest_compatibility_date,
            "status_data": enriched_status,
        },
    )

    logger.info(
        f"ESI status updated in database for compatibility date: {latest_compatibility_date}."
    )
