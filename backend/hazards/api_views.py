from rest_framework import parsers
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import HazardEvent, VideoUpload
from .serializers import (
    HazardEventSerializer,
    HazardReportSerializer,
    VideoUploadRequestSerializer,
)
from .upload_services import get_vehicle_id_for_user, start_video_processing
from .services import create_or_update_hazard


class TestAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"message": "Hazards API is working.", "status": "ok"})


class HazardReportAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = HazardReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        report, event, created = create_or_update_hazard(
            vehicle_id=serializer.validated_data["vehicle_id"],
            hazard_type=serializer.validated_data["hazard_type"],
            latitude=serializer.validated_data["latitude"],
            longitude=serializer.validated_data["longitude"],
            confidence=serializer.validated_data["confidence"],
            detected_at=serializer.validated_data["timestamp"],
        )

        return Response(
            {
                "message": "Hazard report stored successfully.",
                "report_id": report.id,
                "event_id": event.id,
                "event_created": created,
                "hazard_status": event.display_status,
                "validation_count": event.validation_count,
                "required_validations": event.required_validations,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class HazardListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        hazards = HazardEvent.objects.order_by("-last_reported_at")
        serializer = HazardEventSerializer(hazards, many=True)
        return Response(serializer.data)


class UploadVideoAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request):
        serializer = VideoUploadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        video_file = serializer.validated_data["video"]

        try:
            vehicle_id = get_vehicle_id_for_user(request.user)
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        video_upload = VideoUpload.objects.create(
            uploaded_by=request.user,
            vehicle_id=vehicle_id,
            video_file=video_file,
        )
        start_video_processing(video_upload, request.user)

        return Response(
            {
                "status": "processing started",
                "upload_id": video_upload.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )
