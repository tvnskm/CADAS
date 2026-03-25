from django import forms


class BrowserLocationCheckForm(forms.Form):
    vehicle_id = forms.CharField(max_length=100)
    latitude = forms.FloatField()
    longitude = forms.FloatField()

    def __init__(self, *args, **kwargs):
        initial_vehicle_id = kwargs.pop("initial_vehicle_id", "")
        super().__init__(*args, **kwargs)
        if initial_vehicle_id:
            self.fields["vehicle_id"].initial = initial_vehicle_id
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
