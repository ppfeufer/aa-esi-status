"""
The models
"""

# Django
from django.db import models
from django.utils.translation import gettext_lazy as _


class EsiStatus(models.Model):
    """
    Model to store ESI endpoint status
    """

    compatibility_date = models.CharField(
        help_text=_("The ESI compatibility date."), max_length=10
    )

    status_data = models.JSONField(
        help_text=_("The ESI status data."), null=True, blank=True
    )

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("ESI Endpoint Status")
        verbose_name_plural = _("ESI Endpoint Statuses")
