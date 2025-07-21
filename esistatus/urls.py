"""
App url config
"""

# Django
from django.urls import include, path

# AA ESI Status
from esistatus import __app_name__, views
from esistatus.constants import INTERNAL_URL_PREFIX

app_name: str = __app_name__

ajax_urls = [
    path(
        route="ajax/",
        view=include(
            [
                path(
                    route="dashboard-widget/",
                    view=views.ajax_dashboard_widget,
                    name="ajax_dashboard_widget",
                ),
            ]
        ),
    ),
]

urlpatterns = [
    path(route="", view=views.index, name="index"),
    path(
        route=f"{INTERNAL_URL_PREFIX}/",
        view=include(ajax_urls),
    ),
]
