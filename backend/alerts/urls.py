from django.urls import path

from .views import AlertListView, BrowserLocationCheckView

urlpatterns = [
    path("", AlertListView.as_view(), name="alert-list"),
    path("check-location/", BrowserLocationCheckView.as_view(), name="browser-check-location"),
]
