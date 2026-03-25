from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    vehicle_id = models.CharField(max_length=100, blank=True)

    def __str__(self) -> str:
        return f"Profile for {self.user.username}"
