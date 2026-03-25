from django.contrib import admin

from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = (
        "vehicle_id",
        "alert_type",
        "message",
        "latitude",
        "longitude",
        "timestamp",
    )
    list_filter = ("alert_type",)
    search_fields = ("vehicle_id", "message")
