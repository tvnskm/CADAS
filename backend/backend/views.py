from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.timezone import now
from django.views.generic import TemplateView

from alerts.models import Alert
from geofences.models import Geofence
from hazards.models import HazardEvent
from hazards.models import VideoUpload


class LandingPageView(TemplateView):
    template_name = "landing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "public_verified_hazards": HazardEvent.objects.filter(
                    status=HazardEvent.STATUS_VALIDATED
                ).count(),
                "public_uploads": VideoUpload.objects.count(),
                "public_alerts": Alert.objects.count(),
                "public_geofences": Geofence.objects.count(),
            }
        )
        return context


class AboutView(TemplateView):
    template_name = "about.html"


class ContactView(TemplateView):
    template_name = "contact.html"


class DocumentationView(TemplateView):
    template_name = "documentation.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        last_24_hours = now() - timedelta(hours=24)
        verified_hazards_qs = HazardEvent.objects.filter(
            status=HazardEvent.STATUS_VALIDATED
        ).order_by("-last_reported_at")
        pending_hazards_qs = HazardEvent.objects.filter(
            status=HazardEvent.STATUS_PENDING
        )
        auto_geofences_qs = Geofence.objects.filter(auto_generated=True)
        recent_uploads_qs = VideoUpload.objects.order_by("-created_at")

        context.update(
            {
                "total_hazards": HazardEvent.objects.count(),
                "verified_hazards": verified_hazards_qs.count(),
                "pending_hazards": pending_hazards_qs.count(),
                "active_geofence_alerts": Alert.objects.filter(
                    alert_type=Alert.ALERT_TYPE_GEOFENCE,
                    timestamp__gte=last_24_hours,
                ).count(),
                "recent_alerts": Alert.objects.order_by("-timestamp")[:5],
                "recent_uploads": recent_uploads_qs[:5],
                "total_uploads": recent_uploads_qs.count(),
                "auto_geofences": auto_geofences_qs.count(),
                "map_hazards": list(
                    verified_hazards_qs
                    .values(
                        "id",
                        "hazard_type",
                        "latitude",
                        "longitude",
                        "validation_count",
                    )
                ),
                "map_geofences": list(
                    Geofence.objects.order_by("-auto_generated", "-created_at").values(
                        "id",
                        "name",
                        "center_lat",
                        "center_lon",
                        "radius",
                        "auto_generated",
                    )
                ),
                "verified_hazard_cards": verified_hazards_qs[:3],
            }
        )
        return context
