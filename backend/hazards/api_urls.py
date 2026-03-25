from django.urls import path

from .api_views import HazardListAPIView, HazardReportAPIView, TestAPIView, UploadVideoAPIView

urlpatterns = [
    path("test/", TestAPIView.as_view(), name="api-test"),
    path("report/", HazardReportAPIView.as_view(), name="api-report-hazard"),
    path("hazards/", HazardListAPIView.as_view(), name="api-hazard-list"),
    path("upload-video/", UploadVideoAPIView.as_view(), name="api-upload-video"),
]
