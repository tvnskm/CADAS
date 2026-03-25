from rest_framework import serializers

from .models import Alert


class LocationCheckFormMixin:
    def normalize_location_fields(self, attrs):
        latitude = attrs.get("latitude", attrs.get("lat"))
        longitude = attrs.get("longitude", attrs.get("lon"))
        if latitude is None or longitude is None:
            raise serializers.ValidationError(
                "Provide latitude/longitude or lat/lon."
            )
        attrs["latitude"] = latitude
        attrs["longitude"] = longitude
        return attrs


class LocationCheckSerializer(serializers.Serializer):
    # API serializer for /api/check-location/
    vehicle_id = serializers.CharField(max_length=100)
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)
    lat = serializers.FloatField(required=False)
    lon = serializers.FloatField(required=False)

    def validate(self, attrs):
        return LocationCheckFormMixin().normalize_location_fields(attrs)


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = (
            "id",
            "vehicle_id",
            "alert_type",
            "message",
            "latitude",
            "longitude",
            "timestamp",
        )
