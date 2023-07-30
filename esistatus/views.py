"""
The views
"""

# Standard Library
import json
from typing import Any, Dict, Tuple

# Third Party
import requests

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.shortcuts import render

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA ESI Status
from esistatus import __title__
from esistatus.constants import USER_AGENT

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


def _append_value(dict_obj: Dict, key: str, value: Any) -> None:
    """
    Appending values to dicts
    :param dict_obj:
    :param key:
    :param value:
    :return:
    """

    # Check if key exists in dict or not
    if key in dict_obj:
        # Key exist in dict.
        # Check if the type of the value of a key is a list or not
        if not isinstance(dict_obj[key], list):
            # If the type is not list then make it list
            dict_obj[key] = [dict_obj[key]]

        # Append the value in a list
        dict_obj[key].append(value)
    else:
        # As key is not in dict, so, add a key-value pair
        dict_obj[key] = [value]


def _esi_endpoint_status(esi_endpoint_json: json) -> Tuple:
    """
    Get the ESI endpoint status from the ESI json
    :param esi_endpoint_json:
    :return:
    """

    esi_endpoint_status = {
        "green": {"endpoints": {}, "count": 0, "percentage": ""},
        "yellow": {"endpoints": {}, "count": 0, "percentage": ""},
        "red": {"endpoints": {}, "count": 0, "percentage": ""},
    }

    for esi_endpoint in esi_endpoint_json:
        # Green endpoints
        if esi_endpoint["status"] == "green":
            _append_value(
                esi_endpoint_status["green"]["endpoints"],
                esi_endpoint["tags"][0],
                {
                    "route": esi_endpoint["route"],
                    "method": esi_endpoint["method"].upper(),
                },
            )

            esi_endpoint_status["green"]["count"] += 1

        # Yellow endpoints
        if esi_endpoint["status"] == "yellow":
            _append_value(
                esi_endpoint_status["yellow"]["endpoints"],
                esi_endpoint["tags"][0],
                {
                    "route": esi_endpoint["route"],
                    "method": esi_endpoint["method"].upper(),
                },
            )

            esi_endpoint_status["yellow"]["count"] += 1

        # Red endpoints
        if esi_endpoint["status"] == "red":
            _append_value(
                esi_endpoint_status["red"]["endpoints"],
                esi_endpoint["tags"][0],
                {
                    "route": esi_endpoint["route"],
                    "method": esi_endpoint["method"].upper(),
                },
            )

            esi_endpoint_status["red"]["count"] += 1

    endpoints_total = (
        esi_endpoint_status["green"]["count"]
        + esi_endpoint_status["yellow"]["count"]
        + esi_endpoint_status["red"]["count"]
    )

    # Calculate percentages
    # Green endpoints
    green_percentage_calc = (
        esi_endpoint_status["green"]["count"] / endpoints_total * 100
    )
    esi_endpoint_status["green"]["percentage"] = f"{green_percentage_calc:.2f}%"

    # Yellow endpoints
    yellow_percentage_calc = (
        esi_endpoint_status["yellow"]["count"] / endpoints_total * 100
    )
    esi_endpoint_status["yellow"]["percentage"] = f"{yellow_percentage_calc:.2f}%"

    # Red endpoints
    red_percentage_calc = esi_endpoint_status["red"]["count"] / endpoints_total * 100
    esi_endpoint_status["red"]["percentage"] = f"{red_percentage_calc:.2f}%"

    # Return the whole jazz (Tuple[(dict) Endpoint Status, (bool) Has Status Results])
    return esi_endpoint_status, True


@login_required
@permission_required("esistatus.basic_access")
def index(request) -> HttpResponse:
    """
    Index view
    """

    esi_endpoint_status = {}
    has_status_result = False
    request_headers = {"User-Agent": USER_AGENT}
    esi_status_json_url = "https://esi.evetech.net/status.json?version=latest"
    esi_endpoint_status_result = requests.get(
        esi_status_json_url, headers=request_headers, timeout=10
    )

    try:
        esi_endpoint_status_result.raise_for_status()
    except requests.exceptions.RequestException as exc:
        error_str = str(exc)

        logger.warning(
            f"Unable to get ESI status. Error: {error_str}",
            exc_info=True,
        )

        context = {"has_status_result": has_status_result}

        return render(request, "esistatus/index.html", context)

    try:
        esi_endpoint_json = esi_endpoint_status_result.json()
    except requests.exceptions.JSONDecodeError:
        has_status_result = False
    else:
        esi_endpoint_status, has_status_result = _esi_endpoint_status(esi_endpoint_json)

    context = {
        "has_status_result": has_status_result,
        "esi_endpoint_status": esi_endpoint_status,
    }

    return render(request, "esistatus/index.html", context)
