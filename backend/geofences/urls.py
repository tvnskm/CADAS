from django.urls import path

from .views import GeofenceListCreateView

urlpatterns = [
    path("", GeofenceListCreateView.as_view(), name="geofence-list"),
]
