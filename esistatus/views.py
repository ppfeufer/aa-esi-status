"""
the views
"""

# Third Party
import requests

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA ESI Status
from esistatus import __title__
from esistatus.constants import USER_AGENT

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


def append_value(dict_obj, key, value):
    # Check if key exist in dict or not
    if key in dict_obj:
        # Key exist in dict.
        # Check if type of value of key is list or not
        if not isinstance(dict_obj[key], list):
            # If type is not list then make it list
            dict_obj[key] = [dict_obj[key]]

        # Append the value in list
        dict_obj[key].append(value)
    else:
        # As key is not in dict,
        # so, add key-value pair
        dict_obj[key] = [value]


@login_required
@permission_required("esistatus.basic_access")
def index(request):
    """
    Index view
    """

    has_status_result = False

    esi_endpoint_status_green = {}
    esi_endpoint_status_green_count = 0
    esi_endpoint_status_green_percentage = None
    esi_endpoint_status_yellow = {}
    esi_endpoint_status_yellow_count = 0
    esi_endpoint_status_yellow_percentage = None
    esi_endpoint_status_red = {}
    esi_endpoint_status_red_count = 0
    esi_endpoint_status_red_percentage = None

    try:
        request_headers = {"User-Agent": USER_AGENT}

        esi_status_json_url = "https://esi.evetech.net/status.json?version=latest"
        esi_endpoint_status_result = requests.get(
            esi_status_json_url, headers=request_headers
        )

        esi_endpoint_status_result.raise_for_status()

    except requests.exceptions.RequestException as e:
        error_str = str(e)

        logger.warning(
            f"Unable to get ESI status. Error: {error_str}",
            exc_info=True,
        )

        context = {"has_status_result": has_status_result}

        return render(request, "esistatus/index.html", context)

    try:
        for esi_endpoint in esi_endpoint_status_result.json():
            if esi_endpoint["status"] == "green":
                append_value(
                    esi_endpoint_status_green,
                    esi_endpoint["tags"][0],
                    {
                        "route": esi_endpoint["route"],
                        "method": esi_endpoint["method"].upper(),
                    },
                )

                esi_endpoint_status_green_count += 1

            if esi_endpoint["status"] == "yellow":
                append_value(
                    esi_endpoint_status_yellow,
                    esi_endpoint["tags"][0],
                    {
                        "route": esi_endpoint["route"],
                        "method": esi_endpoint["method"].upper(),
                    },
                )

                esi_endpoint_status_yellow_count += 1

            if esi_endpoint["status"] == "red":
                append_value(
                    esi_endpoint_status_red,
                    esi_endpoint["tags"][0],
                    {
                        "route": esi_endpoint["route"],
                        "method": esi_endpoint["method"].upper(),
                    },
                )

                esi_endpoint_status_red_count += 1

        has_status_result = True

        endpoints_total = (
            esi_endpoint_status_green_count
            + esi_endpoint_status_yellow_count
            + esi_endpoint_status_red_count
        )

        # calculate percentages
        esi_endpoint_status_green_percentage = "{:.2f}%".format(
            esi_endpoint_status_green_count / endpoints_total * 100
        )

        esi_endpoint_status_yellow_percentage = "{:.2f}%".format(
            esi_endpoint_status_yellow_count / endpoints_total * 100
        )

        esi_endpoint_status_red_percentage = "{:.2f}%".format(
            esi_endpoint_status_red_count / endpoints_total * 100
        )

    except Exception:
        has_status_result = False

    context = {
        "has_status_result": has_status_result,
        "esi_endpoint_status_green": dict(sorted(esi_endpoint_status_green.items())),
        "esi_endpoint_status_green_count": esi_endpoint_status_green_count,
        "esi_endpoint_status_green_percentage": esi_endpoint_status_green_percentage,
        "esi_endpoint_status_yellow": dict(sorted(esi_endpoint_status_yellow.items())),
        "esi_endpoint_status_yellow_count": esi_endpoint_status_yellow_count,
        "esi_endpoint_status_yellow_percentage": esi_endpoint_status_yellow_percentage,
        "esi_endpoint_status_red": dict(sorted(esi_endpoint_status_red.items())),
        "esi_endpoint_status_red_count": esi_endpoint_status_red_count,
        "esi_endpoint_status_red_percentage": esi_endpoint_status_red_percentage,
    }

    return render(request, "esistatus/index.html", context)
