from rest_framework import serializers

from .models import HazardEvent


class HazardReportSerializer(serializers.Serializer):
    vehicle_id = serializers.CharField(max_length=100)
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)
    lat = serializers.FloatField(required=False)
    lon = serializers.FloatField(required=False)
    confidence = serializers.FloatField()
    timestamp = serializers.DateTimeField()
    hazard_type = serializers.CharField(max_length=50, required=False, default="pothole")

    def validate(self, attrs):
        latitude = attrs.get("latitude", attrs.get("lat"))
        longitude = attrs.get("longitude", attrs.get("lon"))

        if latitude is None or longitude is None:
            raise serializers.ValidationError(
                "Provide latitude/longitude or lat/lon."
            )

        attrs["latitude"] = latitude
        attrs["longitude"] = longitude
        return attrs


class HazardEventSerializer(serializers.ModelSerializer):
    vehicle_id = serializers.SerializerMethodField()
    confidence = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = HazardEvent
        fields = [
            "id",
            "hazard_type",
            "latitude",
            "longitude",
            "vehicle_id",
            "confidence",
            "timestamp",
            "status",
            "validation_count",
        ]

    def get_vehicle_id(self, obj):
        latest_report = obj.latest_report
        return latest_report.vehicle_id if latest_report else None

    def get_confidence(self, obj):
        latest_report = obj.latest_report
        return latest_report.confidence if latest_report else None

    def get_timestamp(self, obj):
        latest_report = obj.latest_report
        return latest_report.detected_at if latest_report else obj.last_reported_at

    def get_status(self, obj):
        return obj.display_status


class VideoUploadRequestSerializer(serializers.Serializer):
    video = serializers.FileField()
