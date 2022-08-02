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

    esi_endpoint_status = {
        "green": {"endpoints": {}, "count": 0, "percentage": ""},
        "yellow": {"endpoints": {}, "count": 0, "percentage": ""},
        "red": {"endpoints": {}, "count": 0, "percentage": ""},
    }

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
        esi_endpoint_json = esi_endpoint_status_result.json()
    except requests.exceptions.RequestsJSONDecodeError:
        has_status_result = False
    else:
        for esi_endpoint in esi_endpoint_json:
            if esi_endpoint["status"] == "green":
                append_value(
                    esi_endpoint_status["green"]["endpoints"],
                    esi_endpoint["tags"][0],
                    {
                        "route": esi_endpoint["route"],
                        "method": esi_endpoint["method"].upper(),
                    },
                )

                esi_endpoint_status["green"]["count"] += 1

            if esi_endpoint["status"] == "yellow":
                append_value(
                    esi_endpoint_status["yellow"]["endpoints"],
                    esi_endpoint["tags"][0],
                    {
                        "route": esi_endpoint["route"],
                        "method": esi_endpoint["method"].upper(),
                    },
                )

                esi_endpoint_status["yellow"]["count"] += 1

            if esi_endpoint["status"] == "red":
                append_value(
                    esi_endpoint_status["red"]["endpoints"],
                    esi_endpoint["tags"][0],
                    {
                        "route": esi_endpoint["route"],
                        "method": esi_endpoint["method"].upper(),
                    },
                )

                esi_endpoint_status["red"]["count"] += 1

        has_status_result = True

        endpoints_total = (
            esi_endpoint_status["green"]["count"]
            + esi_endpoint_status["yellow"]["count"]
            + esi_endpoint_status["red"]["count"]
        )

        # calculate percentages
        green_percentage_calculation = (
            esi_endpoint_status["green"]["count"] / endpoints_total * 100
        )
        esi_endpoint_status["green"][
            "percentage"
        ] = f"{green_percentage_calculation:.2f}%"

        yellow_percentage_calculation = (
            esi_endpoint_status["yellow"]["count"] / endpoints_total * 100
        )
        esi_endpoint_status["yellow"][
            "percentage"
        ] = f"{yellow_percentage_calculation:.2f}%"

        red_percentage_calculation = (
            esi_endpoint_status["red"]["count"] / endpoints_total * 100
        )
        esi_endpoint_status["red"]["percentage"] = f"{red_percentage_calculation:.2f}%"

    context = {
        "has_status_result": has_status_result,
        "esi_endpoint_status": esi_endpoint_status,
    }

    return render(request, "esistatus/index.html", context)
