from datetime import timedelta

from django.utils.timezone import now

from geofences.models import Geofence
from hazards.services import (
    HAZARD_ALERT_RADIUS_METERS,
    get_nearby_validated_events,
    haversine_distance_meters,
)

from .models import Alert

ALERT_COOLDOWN = timedelta(minutes=5)


def _recent_alert_exists(*, vehicle_id: str, alert_type: str, hazard=None, geofence=None):
    queryset = Alert.objects.filter(
        vehicle_id=vehicle_id,
        alert_type=alert_type,
        timestamp__gte=now() - ALERT_COOLDOWN,
    )
    if hazard is not None:
        queryset = queryset.filter(hazard=hazard)
    if geofence is not None:
        queryset = queryset.filter(geofence=geofence)
    return queryset.exists()


def check_location_and_create_alerts(*, vehicle_id: str, latitude: float, longitude: float):
    alerts = []

    for hazard, distance_meters in get_nearby_validated_events(
        latitude=latitude,
        longitude=longitude,
    ):
        is_repeat = _recent_alert_exists(
            vehicle_id=vehicle_id,
            alert_type=Alert.ALERT_TYPE_HAZARD,
            hazard=hazard,
        )
        if not is_repeat:
            Alert.objects.create(
                vehicle_id=vehicle_id,
                alert_type=Alert.ALERT_TYPE_HAZARD,
                message=f"Verified {hazard.hazard_type} ahead within {int(distance_meters)} meters.",
                latitude=hazard.latitude,
                longitude=hazard.longitude,
                hazard=hazard,
            )
        alerts.append(
            {
                "alert_type": Alert.ALERT_TYPE_HAZARD,
                "message": f"Verified {hazard.hazard_type} ahead within {int(distance_meters)} meters.",
                "latitude": hazard.latitude,
                "longitude": hazard.longitude,
                "distance_meters": distance_meters,
                "is_repeat": is_repeat,
                "radius_meters": HAZARD_ALERT_RADIUS_METERS,
            }
        )

    for geofence in Geofence.objects.order_by("name"):
        distance_meters = round(
            haversine_distance_meters(
                latitude,
                longitude,
                geofence.center_lat,
                geofence.center_lon,
            ),
            2,
        )
        if distance_meters > geofence.radius:
            continue

        is_repeat = _recent_alert_exists(
            vehicle_id=vehicle_id,
            alert_type=Alert.ALERT_TYPE_GEOFENCE,
            geofence=geofence,
        )
        if not is_repeat:
            Alert.objects.create(
                vehicle_id=vehicle_id,
                alert_type=Alert.ALERT_TYPE_GEOFENCE,
                message=f"Vehicle entered geofence '{geofence.name}'.",
                latitude=geofence.center_lat,
                longitude=geofence.center_lon,
                geofence=geofence,
            )

        alerts.append(
            {
                "alert_type": Alert.ALERT_TYPE_GEOFENCE,
                "message": f"Vehicle entered geofence '{geofence.name}'.",
                "latitude": geofence.center_lat,
                "longitude": geofence.center_lon,
                "distance_meters": distance_meters,
                "is_repeat": is_repeat,
                "radius_meters": geofence.radius,
                "geofence_name": geofence.name,
            }
        )

    return alerts
