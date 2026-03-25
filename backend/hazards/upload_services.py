import threading

from django.contrib.auth import get_user_model
from django.db import close_old_connections
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_naive, make_aware, now

from ml_model.yolo_inference import process_video

from .models import VideoUpload
from .services import create_or_update_hazard

User = get_user_model()


def get_vehicle_id_for_user(user):
    vehicle_id = getattr(getattr(user, "profile", None), "vehicle_id", "").strip()
    if not vehicle_id:
        raise ValueError("Set a vehicle ID on your profile before uploading videos.")
    return vehicle_id


def _normalize_detected_at(timestamp_value):
    detected_at = parse_datetime(str(timestamp_value))
    if detected_at is None:
        raise ValueError(
            f"Invalid timestamp returned by YOLO pipeline: {timestamp_value}"
        )
    if is_naive(detected_at):
        detected_at = make_aware(detected_at)
    return detected_at


def process_uploaded_video(video_upload_id, user_id):
    video_upload = VideoUpload.objects.select_related("uploaded_by").get(pk=video_upload_id)
    user = User.objects.get(pk=user_id)
    vehicle_id = get_vehicle_id_for_user(user)

    metadata_entries = process_video(video_upload.video_file.path)

    for entry in metadata_entries:
        create_or_update_hazard(
            vehicle_id=vehicle_id,
            hazard_type=entry.get("hazard_type", "pothole"),
            latitude=float(entry["latitude"]),
            longitude=float(entry["longitude"]),
            confidence=float(entry["confidence"]),
            detected_at=_normalize_detected_at(entry["timestamp"]),
            video_upload=video_upload,
        )

    video_upload.status = VideoUpload.STATUS_COMPLETED
    video_upload.total_metadata_entries = len(metadata_entries)
    video_upload.error_message = ""
    video_upload.processed_at = now()
    video_upload.save(
        update_fields=[
            "status",
            "total_metadata_entries",
            "error_message",
            "processed_at",
        ]
    )


def run_yolo_async(video_path, user, upload_id=None):
    # This wrapper keeps database connections isolated from the request thread.
    close_old_connections()
    try:
        user_id = user.pk if hasattr(user, "pk") else int(user)
        if upload_id is None:
            raise ValueError("upload_id is required for asynchronous processing.")
        process_uploaded_video(upload_id, user_id)
    except Exception as exc:
        if upload_id is not None:
            VideoUpload.objects.filter(pk=upload_id).update(
                status=VideoUpload.STATUS_FAILED,
                error_message=str(exc),
                processed_at=now(),
            )
    finally:
        close_old_connections()


def start_video_processing(video_upload, user):
    worker = threading.Thread(
        target=run_yolo_async,
        args=(video_upload.video_file.path, user, video_upload.pk),
        daemon=True,
    )
    worker.start()
    return worker
