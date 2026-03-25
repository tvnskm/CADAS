from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormView

from .forms import VideoUploadForm
from .models import HazardEvent, VideoUpload
from .upload_services import get_vehicle_id_for_user, start_video_processing


class HazardListView(LoginRequiredMixin, ListView):
    model = HazardEvent
    template_name = "hazards/hazard_list.html"
    context_object_name = "hazards"
    ordering = ["-last_reported_at"]
    paginate_by = 25


class HazardDetailView(LoginRequiredMixin, DetailView):
    model = HazardEvent
    template_name = "hazards/hazard_detail.html"
    context_object_name = "hazard"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reports"] = self.object.reports.order_by("-detected_at")
        return context


class UploadVideoView(LoginRequiredMixin, FormView):
    template_name = "hazards/upload_video.html"
    form_class = VideoUploadForm
    success_url = reverse_lazy("video-upload")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["uploads"] = VideoUpload.objects.filter(
            uploaded_by=self.request.user
        ).order_by("-created_at")
        return context

    def form_valid(self, form):
        try:
            vehicle_id = get_vehicle_id_for_user(self.request.user)
        except ValueError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)

        video_upload = VideoUpload.objects.create(
            uploaded_by=self.request.user,
            vehicle_id=vehicle_id,
            video_file=form.cleaned_data["video"],
        )
        start_video_processing(video_upload, self.request.user)
        messages.info(self.request, "Processing started. The video is being analyzed in the background.")
        return super().form_valid(form)
