"""
The views
"""

# Standard Library
import json
from typing import Any

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
from esistatus import __title__, __user_agent__

logger = LoggerAddTag(my_logger=get_extension_logger(__name__), prefix=__title__)


def _append_value(dict_obj: dict, key: str, value: Any) -> None:
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

    dict_obj.setdefault(key, [])

    if not isinstance(dict_obj[key], list):
        dict_obj[key] = [dict_obj[key]]

    dict_obj[key].append(value)


def _esi_endpoint_status_from_json(esi_endpoint_json: json) -> tuple:
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
        status = esi_endpoint["status"]
        _append_value(
            dict_obj=esi_endpoint_status[status]["endpoints"],
            key=esi_endpoint["tags"][0],
            value={
                "route": esi_endpoint["route"],
                "method": esi_endpoint["method"].upper(),
            },
        )
        esi_endpoint_status[status]["count"] += 1

    # Sort endpoints alphabetically by tag (key)
    for status_data in esi_endpoint_status.values():
        status_data["endpoints"] = dict(sorted(status_data["endpoints"].items()))

    endpoints_total = sum(
        esi_endpoint_status[status]["count"]
        for status in esi_endpoint_status  # pylint: disable=consider-using-dict-items
    )

    # Calculate percentages for all statuses
    for status_data in esi_endpoint_status.values():
        percentage = (
            (status_data["count"] / endpoints_total * 100)
            if status_data["count"] > 0
            else 0
        )
        status_data["percentage"] = f"{percentage:.2f}%"

    # Return the whole jazz (Tuple[(bool) Has Status Results, (dict) Endpoint Status])
    return True, esi_endpoint_status


def _esi_status() -> tuple:
    """
    Get the ESI status

    :return: The ESI status
    :rtype: Tuple (Tuple[(bool) Has Status Results, (dict) Endpoint Status])
    """

    request_headers = {"User-Agent": __user_agent__}
    esi_status_json_url = "https://esi.evetech.net/status.json?version=latest"

    try:
        response = requests.get(
            url=esi_status_json_url, headers=request_headers, timeout=10
        )
        response.raise_for_status()
        esi_endpoint_json = response.json()

        return _esi_endpoint_status_from_json(esi_endpoint_json=esi_endpoint_json)
    except requests.exceptions.RequestException as exc:
        error_str = (
            f"{exc.response.status_code} - {exc.response.reason}"
            if exc.response is not None
            else str(exc)
        )

        logger.info(msg=f"Unable to get ESI status. Error: {error_str}")

        return False, error_str
    except json.JSONDecodeError:
        logger.info(
            msg="Unable to get ESI status. ESI returning gibberish, I can't understand …"
        )

        return False, {}


def index(request: WSGIRequest) -> HttpResponse:
    """
    Index view

    :param request: The request
    :type request: WSGIRequest
    :return: The response
    :rtype: HttpResponse
    """

    return render(request=request, template_name="esistatus/index.html")


def ajax_esi_status(request: WSGIRequest) -> HttpResponse:
    """
    AJAX ESI Status view

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
        request=request,
        template_name="esistatus/partials/index/esi-status.html",
        context=context,
    )


def ajax_dashboard_widget(request: WSGIRequest) -> HttpResponse:
    """
    AJAX ESI Status view

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

    return (
        render(
            request=request,
            template_name="esistatus/partials/dashboard-widget/esi-status.html",
            context=context,
        )
        if has_status_result
        else HttpResponse(status=204)
    )


def dashboard_widget(request: WSGIRequest) -> str:
    """
    Dashboard widget

    :param request: The request
    :type request: WSGIRequest
    :return: The widget
    :rtype: str
    """

    return (
        render_to_string(
            template_name="esistatus/dashboard-widget.html", request=request
        )
        if request.user.is_superuser
        else ""
    )
