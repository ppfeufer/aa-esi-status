"""
The views
"""

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
        "total_endpoints": esi_status.total_endpoints,
        "esi_status": esi_status.status_data,
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
    context = {
        "esi_endpoint_status": esi_status.get("esi_status"),
        "total_endpoints": esi_status.get("total_endpoints"),
    }

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
