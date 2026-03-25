from django.contrib import admin

from .models import Geofence


@admin.register(Geofence)
class GeofenceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "auto_generated",
        "center_lat",
        "center_lon",
        "radius",
        "source_hazard",
        "created_by",
        "created_at",
    )
    list_filter = ("auto_generated",)
    search_fields = ("name",)
