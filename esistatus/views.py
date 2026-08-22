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
from esistatus.models import EsiStatus
from esistatus.providers.applogger import AppLogger

logger = AppLogger(my_logger=get_extension_logger(__name__))


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

    :param request: The request
    :type request: WSGIRequest
    :param template_name: The name of the template to render
    :type template_name: str
    :param with_compat_date: Whether to include the compatibility date in the context
    :type with_compat_date: bool
    :return: The response
    :rtype: HttpResponse
    """

    latest_esi_status = EsiStatus.get_latest_status_data()
    esi_status_history = EsiStatus.get_history()
    context = {
        "esi_endpoint_status": latest_esi_status.get("esi_status"),
        "esi_endpoint_history": esi_status_history,
        "total_endpoints": latest_esi_status.get("total_endpoints"),
        "esi_name": latest_esi_status.get("esi_name"),
    }

    if with_compat_date:
        context["compatibility_date"] = latest_esi_status.get("compatibility_date")

    return render(
        request=request,
        template_name=template_name,
        context=context,
    )


def ajax_esi_status(request: WSGIRequest) -> HttpResponse:
    """
    AJAX ESI Status view for the main index page

    :param request: The request
    :type request: WSGIRequest
    :return: The response
    :rtype: HttpResponse
    """

    return _render_esi_status(
        request=request,
        template_name="esistatus/partials/index/esi-status.html",
        with_compat_date=True,
    )


def ajax_dashboard_widget(request: WSGIRequest) -> HttpResponse:
    """
    AJAX ESI Status view for the dashboard widget

    :param request: The request
    :type request: WSGIRequest
    :return: The response
    :rtype: HttpResponse
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
