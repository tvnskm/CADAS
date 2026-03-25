from django import forms

from .models import Geofence


class GeofenceForm(forms.ModelForm):
    class Meta:
        model = Geofence
        fields = ("name", "center_lat", "center_lon", "radius")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
