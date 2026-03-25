from django.db import models


class Alert(models.Model):
    ALERT_TYPE_HAZARD = "hazard"
    ALERT_TYPE_GEOFENCE = "geofence"

    ALERT_TYPE_CHOICES = [
        (ALERT_TYPE_HAZARD, "Hazard"),
        (ALERT_TYPE_GEOFENCE, "Geofence"),
    ]

    vehicle_id = models.CharField(max_length=100)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    message = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    hazard = models.ForeignKey(
        "hazards.HazardEvent",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="generated_alerts",
    )
    geofence = models.ForeignKey(
        "geofences.Geofence",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="alerts",
    )

    def __str__(self) -> str:
        return f"{self.alert_type} alert for {self.vehicle_id}"
