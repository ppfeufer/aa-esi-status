"""
App url config
"""

# Django
from django.urls import path

# AA ESI Status
from esistatus import views

app_name: str = "esistatus"

urlpatterns = [
    path("", views.index, name="index"),
]
