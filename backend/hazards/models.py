from django.conf import settings
from django.db import models


class HazardEvent(models.Model):
    STATUS_PENDING = "pending"
    STATUS_VALIDATED = "validated"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_VALIDATED, "Validated"),
        (STATUS_REJECTED, "Rejected"),
    ]

    hazard_type = models.CharField(max_length=50, default="pothole")
    latitude = models.FloatField()
    longitude = models.FloatField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    validation_count = models.PositiveIntegerField(default=1)
    required_validations = models.PositiveIntegerField(default=2)
    first_reported_at = models.DateTimeField()
    last_reported_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.hazard_type} ({self.status})"

    @property
    def latest_report(self):
        return self.reports.order_by("-detected_at", "-id").first()

    @property
    def display_status(self) -> str:
        if self.status == self.STATUS_VALIDATED:
            return "verified"
        return self.status


class VideoUpload(models.Model):
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PROCESSING, "Processing"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    ]

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="video_uploads",
    )
    vehicle_id = models.CharField(max_length=100)
    video_file = models.FileField(upload_to="uploads/")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PROCESSING,
    )
    total_metadata_entries = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Upload {self.id} ({self.status})"


class HazardReport(models.Model):
    event = models.ForeignKey(
        HazardEvent,
        on_delete=models.CASCADE,
        related_name="reports",
    )
    vehicle_id = models.CharField(max_length=100)
    hazard_type = models.CharField(max_length=50, default="pothole")
    latitude = models.FloatField()
    longitude = models.FloatField()
    confidence = models.FloatField()
    detected_at = models.DateTimeField()
    video_upload = models.ForeignKey(
        VideoUpload,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hazard_reports",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.vehicle_id} -> event {self.event_id}"
