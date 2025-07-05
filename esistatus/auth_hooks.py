"""
Hook into AA
"""

# Alliance Auth
from allianceauth import hooks
from allianceauth.hooks import DashboardItemHook
from allianceauth.services.hooks import MenuItemHook, UrlHook

# AA ESI Status
from esistatus import __app_name__, __title__, urls
from esistatus.views import dashboard_widget


class AaEsiStatusMenuItem(MenuItemHook):  # pylint: disable=too-few-public-methods
    """
    This class ensures only authorized users will see the menu entry
    """

    def __init__(self):
        # Setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            text=__title__,
            classes="fa-solid fa-signal",
            url_name="esistatus:index",
            navactive=["esistatus:"],
        )

    def render(self, request):
        """
        Check if the user has the permission to view this app

        :param request:
        :type request:
        :return:
        :rtype:
        """

        return MenuItemHook.render(self, request)


class AaEsiStatusDashboardHook(DashboardItemHook):
    """
    This class adds the widget to the dashboard
    """

    def __init__(self):
        # Setup dashboard widget
        DashboardItemHook.__init__(self=self, view_function=dashboard_widget, order=1)


@hooks.register("menu_item_hook")
def register_menu():
    """
    Register our menu item

    :return: The hook
    :rtype: AaEsiStatusMenuItem
    """

    return AaEsiStatusMenuItem()


@hooks.register("url_hook")
def register_urls():
    """
    Register our base url

    :return: The hook
    :rtype: UrlHook
    """

    return UrlHook(
        urls=urls,
        namespace=__app_name__,
        base_url=r"^esi-status/",
        excluded_views=["esistatus.views.index"],
    )


@hooks.register("dashboard_hook")
def register_esi_status_dashboard_hook():
    """
    Register our dashboard hook

    :return: The hook
    :rtype: AaEsiStatusDashboardHook
    """

    return AaEsiStatusDashboardHook()
