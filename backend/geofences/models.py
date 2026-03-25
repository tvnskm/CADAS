from django.conf import settings
from django.db import models


class Geofence(models.Model):
    DEFAULT_HAZARD_RADIUS_METERS = 100

    name = models.CharField(max_length=100)
    center_lat = models.FloatField()
    center_lon = models.FloatField()
    radius = models.FloatField(help_text="Radius in meters")
    auto_generated = models.BooleanField(default=False)
    source_hazard = models.OneToOneField(
        "hazards.HazardEvent",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="auto_geofence",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="geofences",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name
