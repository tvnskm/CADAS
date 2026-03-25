from django.urls import path

from .views import CheckLocationAPIView

urlpatterns = [
    path("check-location/", CheckLocationAPIView.as_view(), name="api-check-location"),
]
