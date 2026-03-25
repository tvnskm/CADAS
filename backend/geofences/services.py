from .models import Geofence


def sync_hazard_geofence(hazard_event):
    """
    Keep one auto-generated geofence in sync with a verified hazard.
    """
    geofence, _ = Geofence.objects.update_or_create(
        source_hazard=hazard_event,
        defaults={
            "name": f"Auto Hazard Zone #{hazard_event.id}",
            "center_lat": hazard_event.latitude,
            "center_lon": hazard_event.longitude,
            "radius": Geofence.DEFAULT_HAZARD_RADIUS_METERS,
            "auto_generated": True,
            "created_by": None,
        },
    )
    return geofence
