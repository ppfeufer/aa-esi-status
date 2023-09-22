"""
The models
"""

# Django
from django.db import models
from django.utils.translation import gettext_lazy as _


class EsiStatus(models.Model):
    """
    Meta model for app permissions
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        managed = False
        default_permissions = ()
        permissions = (("basic_access", _("Can access this app")),)
