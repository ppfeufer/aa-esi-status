"""
The models
"""

# Django
from django.db import models


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
        permissions = (("basic_access", "Can access this app"),)
