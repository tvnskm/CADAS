from datetime import timedelta
from math import asin, cos, radians, sin, sqrt

from django.db.models import Count
from geofences.services import sync_hazard_geofence

from .models import HazardEvent, HazardReport

# Reports inside this radius are treated as the same physical hazard.
MATCH_RADIUS_METERS = 30

# Reports inside this time window are treated as the same recent event.
MATCH_TIME_WINDOW = timedelta(minutes=10)

# Two different vehicles are required to validate the hazard.
REQUIRED_VALIDATIONS = 2

# Vehicles inside this radius should be warned about a validated hazard.
HAZARD_ALERT_RADIUS_METERS = 100


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius_m = 6371000
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    start_lat = radians(lat1)
    end_lat = radians(lat2)

    a = sin(d_lat / 2) ** 2 + cos(start_lat) * cos(end_lat) * sin(d_lon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return earth_radius_m * c


def find_matching_event(hazard_type: str, latitude: float, longitude: float, detected_at):
    candidate_events = HazardEvent.objects.filter(
        hazard_type=hazard_type,
        last_reported_at__gte=detected_at - MATCH_TIME_WINDOW,
        first_reported_at__lte=detected_at + MATCH_TIME_WINDOW,
    ).order_by("-last_reported_at")

    for event in candidate_events:
        distance = haversine_distance_meters(
            latitude,
            longitude,
            event.latitude,
            event.longitude,
        )
        if distance <= MATCH_RADIUS_METERS:
            return event
    return None


def attach_report_to_event(*, event: HazardEvent, vehicle_id: str, hazard_type: str, latitude: float, longitude: float, confidence: float, detected_at, video_upload=None):
    report = HazardReport.objects.create(
        event=event,
        vehicle_id=vehicle_id,
        hazard_type=hazard_type,
        latitude=latitude,
        longitude=longitude,
        confidence=confidence,
        detected_at=detected_at,
        video_upload=video_upload,
    )

    unique_vehicle_count = (
        event.reports.values("vehicle_id")
        .annotate(total=Count("vehicle_id"))
        .count()
    )

    report_count = event.reports.count()
    event.latitude = ((event.latitude * (report_count - 1)) + latitude) / report_count
    event.longitude = ((event.longitude * (report_count - 1)) + longitude) / report_count
    event.first_reported_at = min(event.first_reported_at, detected_at)
    event.last_reported_at = max(event.last_reported_at, detected_at)
    event.validation_count = unique_vehicle_count
    became_validated = False
    if unique_vehicle_count >= event.required_validations:
        became_validated = event.status != HazardEvent.STATUS_VALIDATED
        event.status = HazardEvent.STATUS_VALIDATED
    event.save(
        update_fields=[
            "latitude",
            "longitude",
            "first_reported_at",
            "last_reported_at",
            "validation_count",
            "status",
            "updated_at",
        ]
    )

    if event.status == HazardEvent.STATUS_VALIDATED:
        # Auto-create or update the geofence so verified hazards immediately
        # participate in geofence-based alerting.
        sync_hazard_geofence(event)

    return report, event


def create_or_update_hazard(*, vehicle_id: str, hazard_type: str, latitude: float, longitude: float, confidence: float, detected_at, video_upload=None):
    event = find_matching_event(
        hazard_type=hazard_type,
        latitude=latitude,
        longitude=longitude,
        detected_at=detected_at,
    )

    created = False
    if event is None:
        event = HazardEvent.objects.create(
            hazard_type=hazard_type,
            latitude=latitude,
            longitude=longitude,
            status=HazardEvent.STATUS_PENDING,
            validation_count=1,
            required_validations=REQUIRED_VALIDATIONS,
            first_reported_at=detected_at,
            last_reported_at=detected_at,
        )
        created = True

    report, event = attach_report_to_event(
        event=event,
        vehicle_id=vehicle_id,
        hazard_type=hazard_type,
        latitude=latitude,
        longitude=longitude,
        confidence=confidence,
        detected_at=detected_at,
        video_upload=video_upload,
    )

    return report, event, created


def get_nearby_validated_events(*, latitude: float, longitude: float):
    nearby_events = []

    for event in HazardEvent.objects.filter(status=HazardEvent.STATUS_VALIDATED).order_by("-last_reported_at"):
        distance = haversine_distance_meters(
            latitude,
            longitude,
            event.latitude,
            event.longitude,
        )
        if distance <= HAZARD_ALERT_RADIUS_METERS:
            nearby_events.append((event, round(distance, 2)))

    nearby_events.sort(key=lambda item: item[1])
    return nearby_events
