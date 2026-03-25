from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import FormView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import BrowserLocationCheckForm
from .models import Alert
from .serializers import LocationCheckSerializer
from .services import check_location_and_create_alerts


class AlertListView(LoginRequiredMixin, ListView):
    model = Alert
    template_name = "alerts/alert_list.html"
    context_object_name = "alerts"
    paginate_by = 25
    ordering = ["-timestamp"]


class BrowserLocationCheckView(LoginRequiredMixin, FormView):
    template_name = "alerts/check_location.html"
    form_class = BrowserLocationCheckForm
    success_url = reverse_lazy("browser-check-location")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["initial_vehicle_id"] = getattr(
            getattr(self.request.user, "profile", None),
            "vehicle_id",
            "",
        )
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("generated_alerts", [])
        return context

    def form_valid(self, form):
        alerts = check_location_and_create_alerts(
            vehicle_id=form.cleaned_data["vehicle_id"],
            latitude=form.cleaned_data["latitude"],
            longitude=form.cleaned_data["longitude"],
        )
        if alerts:
            messages.success(self.request, "Location checked successfully.")
        else:
            messages.info(self.request, "No alerts were triggered for this location.")
        return self.render_to_response(
            self.get_context_data(
                form=form,
                generated_alerts=alerts,
            )
        )


class CheckLocationAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LocationCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        alerts = check_location_and_create_alerts(
            vehicle_id=serializer.validated_data["vehicle_id"],
            latitude=serializer.validated_data["latitude"],
            longitude=serializer.validated_data["longitude"],
        )

        return Response(
            {
                "vehicle_id": serializer.validated_data["vehicle_id"],
                "alert_count": len(alerts),
                "alerts": alerts,
            }
        )
