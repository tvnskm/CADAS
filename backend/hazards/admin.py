from django.contrib import admin

from .models import HazardEvent, HazardReport, VideoUpload


@admin.register(HazardEvent)
class HazardEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "hazard_type",
        "status",
        "validation_count",
        "latitude",
        "longitude",
        "first_reported_at",
        "last_reported_at",
    )
    list_filter = ("hazard_type", "status")
    search_fields = ("reports__vehicle_id",)


@admin.register(HazardReport)
class HazardReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "vehicle_id",
        "hazard_type",
        "confidence",
        "latitude",
        "longitude",
        "detected_at",
        "event",
        "video_upload",
    )
    list_filter = ("hazard_type",)
    search_fields = ("vehicle_id",)


@admin.register(VideoUpload)
class VideoUploadAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uploaded_by",
        "vehicle_id",
        "status",
        "total_metadata_entries",
        "created_at",
        "processed_at",
    )
    list_filter = ("status",)
    search_fields = ("vehicle_id", "uploaded_by__username")
