"""
App url config
"""

# Django
from django.urls import path

# AA ESI Status
from esistatus import views

app_name: str = "esistatus"

urlpatterns = [
    path(route="", view=views.index, name="index"),
    path(route="ajax/esi_status/", view=views.ajax_esi_status, name="ajax_esi_status"),
]
