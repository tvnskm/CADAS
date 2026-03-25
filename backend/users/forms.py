from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    vehicle_id = forms.CharField(
        max_length=100,
        required=False,
        label="Vehicle Code",
        help_text="Use a simple code like CAR-101. Hazard verification depends on different vehicle codes.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "vehicle_id", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            user.profile.vehicle_id = self.cleaned_data.get("vehicle_id", "")
            user.profile.save()
        return user


class ProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label="Login Name")
    email = forms.EmailField(required=True)

    class Meta:
        model = Profile
        fields = ("vehicle_id",)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["username"].initial = self.user.username
        self.fields["email"].initial = self.user.email
        self.fields["vehicle_id"].label = "Vehicle Code"
        self.fields["vehicle_id"].help_text = (
            "Example: CAR-101. Two different vehicle codes are needed to verify the same hazard."
        )
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def save(self, commit=True):
        self.user.username = self.cleaned_data["username"]
        self.user.email = self.cleaned_data["email"]
        profile = super().save(commit=False)
        profile.user = self.user
        if commit:
            self.user.save()
            profile.save()
        return profile


class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
