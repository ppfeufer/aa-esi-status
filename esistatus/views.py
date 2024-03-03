"""
The views
"""

# Standard Library
import json
from typing import Any, Dict, Tuple

# Third Party
import requests

# Django
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

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
    Append a value to a key in a dictionary

    :param dict_obj: The dictionary
    :type dict_obj: Dict
    :param key: The key
    :type key: str
    :param value: The value
    :type value: Any
    :return: None
    :rtype: None
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
        # If the key is not in the dict, add a key-value pair
        dict_obj[key] = [value]


def _esi_endpoint_status_from_json(esi_endpoint_json: json) -> Tuple:
    """
    Get the ESI endpoint status from the ESI json

    :param esi_endpoint_json: The ESI endpoint json
    :type esi_endpoint_json: json
    :return: The ESI endpoint status
    :rtype: Tuple[(bool) Has Status Results, (dict) Endpoint Status]
    """

    esi_endpoint_status = {
        "green": {"endpoints": {}, "count": 0, "percentage": "0.00%"},
        "yellow": {"endpoints": {}, "count": 0, "percentage": "0.00%"},
        "red": {"endpoints": {}, "count": 0, "percentage": "0.00%"},
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
        (esi_endpoint_status["green"]["count"] / endpoints_total * 100)
        if esi_endpoint_status["green"]["count"] > 0
        else 0
    )
    esi_endpoint_status["green"]["percentage"] = f"{green_percentage_calc:.2f}%"

    # Calculate percentages - Yellow endpoints
    yellow_percentage_calc = (
        (esi_endpoint_status["yellow"]["count"] / endpoints_total * 100)
        if esi_endpoint_status["yellow"]["count"] > 0
        else 0
    )
    esi_endpoint_status["yellow"]["percentage"] = f"{yellow_percentage_calc:.2f}%"

    # Calculate percentages - Red endpoints
    red_percentage_calc = (
        (esi_endpoint_status["red"]["count"] / endpoints_total * 100)
        if esi_endpoint_status["red"]["count"] > 0
        else 0
    )
    esi_endpoint_status["red"]["percentage"] = f"{red_percentage_calc:.2f}%"

    # Return the whole jazz (Tuple[(bool) Has Status Results, (dict) Endpoint Status])
    return True, esi_endpoint_status


def _esi_status() -> Tuple:
    """
    Get the ESI status

    :return: The ESI status
    :rtype: Tuple (Tuple[(bool) Has Status Results, (dict) Endpoint Status])
    """

    has_status_result = False
    request_headers = {"User-Agent": USER_AGENT}
    esi_status_json_url = "https://esi.evetech.net/status.json?version=latest"
    esi_endpoint_status = {}

    try:
        esi_endpoint_status_result = requests.get(
            url=esi_status_json_url, headers=request_headers, timeout=10
        )
        esi_endpoint_status_result.raise_for_status()
        esi_endpoint_json = esi_endpoint_status_result.json()
    except requests.exceptions.RequestException as exc:
        error_str = str(exc)

        logger.info(msg=f"Unable to get ESI status. Error: {error_str}")

        return has_status_result, esi_endpoint_status
    except json.JSONDecodeError:
        logger.info(
            msg=(
                "Unable to get ESI status. ESI returning gibberish, I can't understand …"
            )
        )

        return has_status_result, esi_endpoint_status

    has_status_result, esi_endpoint_status = _esi_endpoint_status_from_json(
        esi_endpoint_json=esi_endpoint_json
    )

    return has_status_result, esi_endpoint_status


def index(request: WSGIRequest) -> HttpResponse:
    """
    Index view

    :param request: The request
    :type request: WSGIRequest
    :return: The response
    :rtype: HttpResponse
    """

    has_status_result, esi_endpoint_status = _esi_status()

    context = {
        "has_status_result": has_status_result,
        "esi_endpoint_status": esi_endpoint_status,
    }

    return render(
        request=request, template_name="esistatus/index.html", context=context
    )


def ajax_esi_status(request: WSGIRequest) -> HttpResponse:
    """
    AJAX ESI Status view

    :param request: The request
    :type request: WSGIRequest
    :return: The response
    :rtype: HttpResponse
    """

    has_status_result, esi_endpoint_status = _esi_status()

    if has_status_result:
        context = {
            "has_status_result": has_status_result,
            "esi_endpoint_status": esi_endpoint_status,
        }

        return render(
            request=request,
            template_name="esistatus/partials/dashboard-widget/esi-status.html",
            context=context,
        )

    return HttpResponse(status=204)


def dashboard_widget(request: WSGIRequest) -> str:
    """
    Dashboard widget

    :param request: The request
    :type request: WSGIRequest
    :return: The widget
    :rtype: str
    """

    if request.user.is_superuser:
        return render_to_string(
            template_name="esistatus/dashboard-widget.html", request=request
        )

    return ""
