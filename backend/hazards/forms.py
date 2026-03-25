from django import forms


class VideoUploadForm(forms.Form):
    video = forms.FileField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["video"].widget.attrs["class"] = "form-control"
