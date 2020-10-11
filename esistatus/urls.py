# -*- coding: utf-8 -*-

"""
pages url config
"""

from django.urls import path

from esistatus import views


app_name: str = "esistatus"

urlpatterns = [
    path("", views.index, name="index"),
]
