# -*- coding: utf-8 -*-

"""
the views
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required

from esistatus.app_settings import avoid_cdn


@login_required
@permission_required("esistatus.basic_access")
def index(request):
    """
    Index view
    """

    context = {
        "avoidCdn": avoid_cdn(),
    }

    return render(request, "esistatus/index.html", context)
