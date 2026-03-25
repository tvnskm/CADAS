from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import GeofenceForm
from .models import Geofence


class GeofenceListCreateView(LoginRequiredMixin, FormView):
    template_name = "geofences/geofence_list.html"
    form_class = GeofenceForm
    success_url = reverse_lazy("geofence-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["geofences"] = Geofence.objects.order_by("-auto_generated", "-created_at")
        return context

    def form_valid(self, form):
        geofence = form.save(commit=False)
        geofence.created_by = self.request.user
        geofence.save()
        messages.success(self.request, "Geofence created successfully.")
        return super().form_valid(form)
