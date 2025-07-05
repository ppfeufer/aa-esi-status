"""
App url config
"""

# Django
from django.urls import path

# AA ESI Status
from esistatus import __app_name__, views

app_name: str = __app_name__

urlpatterns = [
    path(route="", view=views.index, name="index"),
    path(route="ajax/esi_status/", view=views.ajax_esi_status, name="ajax_esi_status"),
]
