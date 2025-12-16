"""
The views
"""

# Standard Library
from typing import Any

# Django
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# AA ESI Status
from esistatus import __title__
from esistatus.models import EsiStatus
from esistatus.providers import AppLogger

logger = AppLogger(my_logger=get_extension_logger(__name__), prefix=__title__)


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


def _esi_endpoint_status_from_json(esi_endpoint_json: list) -> dict:
    """
    Get the ESI endpoint status from the ESI json

    :param esi_endpoint_json: The ESI endpoint json
    :type esi_endpoint_json: dict
    :return: The ESI endpoint status
    :rtype: dict
    """

    esi_endpoint_status = {
        "Unknown": {"endpoints": {}, "count": 0, "percentage": "0.00%"},
        "OK": {"endpoints": {}, "count": 0, "percentage": "0.00%"},
        "Degraded": {"endpoints": {}, "count": 0, "percentage": "0.00%"},
        "Down": {"endpoints": {}, "count": 0, "percentage": "0.00%"},
        "Recovering": {"endpoints": {}, "count": 0, "percentage": "0.00%"},
    }

    for esi_endpoint in esi_endpoint_json:
        status = esi_endpoint["status"]

        _append_value(
            dict_obj=esi_endpoint_status[status]["endpoints"],
            key=esi_endpoint["tags"][0],
            value={
                "path": esi_endpoint["path"],
                "method": esi_endpoint["method"].upper(),
                "operation_id": esi_endpoint["operation_id"],
                "summary": esi_endpoint["summary"],
                "description": esi_endpoint["description"],
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

    # Return the whole jazz
    return esi_endpoint_status


def _esi_status() -> dict:
    """
    Get the ESI status

    :return: The ESI status
    :rtype: dict
    """

    try:
        esi_status = EsiStatus.objects.get(pk=1)
    except EsiStatus.DoesNotExist:
        logger.debug("ESI Status data does not exist.")

        return {}

    return {
        "esi_status": _esi_endpoint_status_from_json(
            esi_endpoint_json=esi_status.status_data
        ),
        "compatibility_date": esi_status.compatibility_date,
    }


def index(request: WSGIRequest) -> HttpResponse:
    """
    Index view

    :param request: The request
    :type request: WSGIRequest
    :return: The response
    :rtype: HttpResponse
    """

    return render(request=request, template_name="esistatus/index.html")


def _render_esi_status(
    request: WSGIRequest, template_name: str, with_compat_date: bool = False
) -> HttpResponse:
    """
    Render the ESI status template with the ESI status context data

    :param request:
    :type request:
    :param template_name:
    :type template_name:
    :return:
    :rtype:
    """

    esi_status = _esi_status() or {}
    context = {"esi_endpoint_status": esi_status.get("esi_status")}

    if with_compat_date:
        context["compatibility_date"] = esi_status.get("compatibility_date")

    return render(
        request=request,
        template_name=template_name,
        context=context,
    )


def ajax_esi_status(request: WSGIRequest) -> HttpResponse:
    """
    AJAX ESI Status view for the main index page

    :param request:
    :type request:
    :return:
    :rtype:
    """

    return _render_esi_status(
        request=request,
        template_name="esistatus/partials/index/esi-status.html",
        with_compat_date=True,
    )


def ajax_dashboard_widget(request: WSGIRequest) -> HttpResponse:
    """
    AJAX ESI Status view for the dashboard widget

    :param request:
    :type request:
    :return:
    :rtype:
    """

    return _render_esi_status(
        request=request,
        template_name="esistatus/partials/dashboard-widget/esi-status.html",
        with_compat_date=True,
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
