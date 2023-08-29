"""
The views
"""

# Standard Library
import json
from typing import Any, Dict, Tuple

# Third Party
import requests

# Django
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

    # Check if key exists in the dict or not
    if key in dict_obj:
        # Key exist in the dict.
        # Check if the type of the value of a key is a list or not
        if not isinstance(dict_obj[key], list):
            # If the type is not list then make it list
            dict_obj[key] = [dict_obj[key]]

        # Append the value in a list
        dict_obj[key].append(value)
    else:
        # Is the key is not in the dict, add a key-value pair
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
        _append_value(
            dict_obj=esi_endpoint_status[esi_endpoint["status"]]["endpoints"],
            key=esi_endpoint["tags"][0],
            value={
                "route": esi_endpoint["route"],
                "method": esi_endpoint["method"].upper(),
            },
        )

        esi_endpoint_status[esi_endpoint["status"]]["count"] += 1

    endpoints_total = (
        esi_endpoint_status["green"]["count"]
        + esi_endpoint_status["yellow"]["count"]
        + esi_endpoint_status["red"]["count"]
    )

    # Calculate percentages - Green endpoints
    green_percentage_calc = (
        esi_endpoint_status["green"]["count"] / endpoints_total * 100
    )
    esi_endpoint_status["green"]["percentage"] = f"{green_percentage_calc:.2f}%"

    # Calculate percentages - Yellow endpoints
    yellow_percentage_calc = (
        esi_endpoint_status["yellow"]["count"] / endpoints_total * 100
    )
    esi_endpoint_status["yellow"]["percentage"] = f"{yellow_percentage_calc:.2f}%"

    # Calculate percentages - Red endpoints
    red_percentage_calc = esi_endpoint_status["red"]["count"] / endpoints_total * 100
    esi_endpoint_status["red"]["percentage"] = f"{red_percentage_calc:.2f}%"

    # Return the whole jazz (Tuple[(dict) Endpoint Status, (bool) Has Status Results])
    return esi_endpoint_status, True


def index(request) -> HttpResponse:
    """
    Index view
    """

    esi_endpoint_status = {}
    has_status_result = False
    request_headers = {"User-Agent": USER_AGENT}
    esi_status_json_url = "https://esi.evetech.net/status.json?version=latest"
    esi_endpoint_status_result = requests.get(
        url=esi_status_json_url, headers=request_headers, timeout=10
    )

    try:
        esi_endpoint_status_result.raise_for_status()
    except requests.exceptions.RequestException as exc:
        error_str = str(exc)

        logger.info(msg=f"Unable to get ESI status. Error: {error_str}")

        context = {"has_status_result": has_status_result}
    else:
        try:
            esi_endpoint_json = esi_endpoint_status_result.json()
        except requests.exceptions.JSONDecodeError:
            has_status_result = False

            logger.info(
                msg=(
                    "Unable to get ESI status. ESI returning gibberish, I can't understand …"
                )
            )
        else:
            esi_endpoint_status, has_status_result = _esi_endpoint_status(
                esi_endpoint_json=esi_endpoint_json
            )

        context = {
            "has_status_result": has_status_result,
            "esi_endpoint_status": esi_endpoint_status,
        }

    return render(
        request=request, template_name="esistatus/index.html", context=context
    )
