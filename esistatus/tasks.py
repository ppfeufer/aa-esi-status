"""
Tasks for ESI status monitoring.
"""

# Standard Library
import copy
import json
import re
from typing import Any

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
from esistatus.models import EsiStatus

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


def _enrich_routes_with_tags(
    routes: dict[str, Any], openapi: dict[str, Any]
) -> list[Any]:
    """
    Enrich ESI routes with OpenAPI tags.

    :param routes:
    :type routes:
    :param openapi:
    :type openapi:
    :return:
    :rtype:
    """

    routes_copy = copy.deepcopy(routes)
    paths = openapi.get("paths") or {}

    def normalize_template(p: str) -> str:
        """
        Normalize a path template by replacing path parameters with "{}".

        :param p:
        :type p:
        :return:
        :rtype:
        """

        return re.sub(r"\{[^/}]+\}", "{}", p)

    def path_to_regex(p: str) -> re.Pattern:
        """
        Convert a path template to a regex pattern.

        :param p:
        :type p:
        :return:
        :rtype:
        """

        parts = re.split(r"(\{[^}]+\})", p)
        pattern = "".join(
            "[^/]+" if part.startswith("{") else re.escape(part) for part in parts
        )

        return re.compile("^" + pattern + "$")

    # Build normalized map for faster candidate lookup
    normalized_map = {}
    for p in paths.keys():
        normalized_map.setdefault(normalize_template(p), []).append(p)

    def find_matching_path(route_path: str):
        """
        Find the matching OpenAPI path for a given route path.

        :param route_path:
        :type route_path:
        :return:
        :rtype:
        """

        if route_path in paths:
            return route_path

        normalized = normalize_template(route_path)
        candidates = normalized_map.get(normalized, [])

        if len(candidates) == 1:
            return candidates[0]

        for cand in candidates:
            if path_to_regex(cand).match(route_path):
                return cand

        for cand in paths.keys():
            if path_to_regex(cand).match(route_path):
                return cand

        return None

    def extract_tags_for(route: dict[str, Any]):
        """
        Extract tags for a given route from OpenAPI specs.

        :param route:
        :type route:
        :return:
        :rtype:
        """

        match = find_matching_path(route.get("path", ""))

        if not match:
            return []

        path_item = paths.get(match) or {}
        method = route.get("method", "").lower()
        op = path_item.get(method)

        if isinstance(op, dict) and "tags" in op:
            return op.get("tags", [])

        for op_def in path_item.values():
            if isinstance(op_def, dict) and "tags" in op_def:
                return op_def.get("tags", [])

        return []

    for r in routes_copy.get("routes", []):
        r["tags"] = extract_tags_for(r)

    routes_with_tags = routes_copy.get("routes", [])

    logger.debug(f"Enriched {len(routes_with_tags)} routes with OpenAPI tags.")

    return routes_with_tags


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

    enriched_status = _enrich_routes_with_tags(routes=esi_status, openapi=openapi_specs)

    # Consider enriched status empty if there are no entries or none of the entries have tags
    if not enriched_status or not any(route.get("tags") for route in enriched_status):
        logger.debug("Enriched OpenAPI status is empty; skipping database update.")

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
