from django.urls import path

from .views import HazardDetailView, HazardListView

urlpatterns = [
    path("", HazardListView.as_view(), name="hazard-list"),
    path("<int:pk>/", HazardDetailView.as_view(), name="hazard-detail"),
]
