"""
hook into AA
"""

# Django
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

# AA ESI Status
from esistatus import __title__, urls


class AaEsiStatusMenuItem(MenuItemHook):  # pylint: disable=too-few-public-methods
    """This class ensures only authorized users will see the menu entry"""

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            _(__title__),
            "fas fa-signal fa-fw",
            "esistatus:index",
            navactive=["esistatus:index"],
        )

    def render(self, request):
        """
        check if the user has the permission to view this app
        :param request:
        :return:
        """
        if request.user.has_perm("esistatus.basic_access"):
            return MenuItemHook.render(self, request)

        return ""


@hooks.register("menu_item_hook")
def register_menu():
    """
    register our menu item
    :return:
    """
    return AaEsiStatusMenuItem()


@hooks.register("url_hook")
def register_urls():
    """
    register our basu url
    :return:
    """
    return UrlHook(urls, "esistatus", r"^esi-status/")
