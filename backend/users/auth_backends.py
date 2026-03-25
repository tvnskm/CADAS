from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class UsernameOrEmailBackend(ModelBackend):
    """
    Allow Django auth to accept either a username or an email address.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        login_value = username or kwargs.get("email")
        if not login_value or not password:
            return None

        UserModel = get_user_model()
        username_match = (
            UserModel.objects.filter(username__iexact=login_value).order_by("id").first()
        )
        if username_match and username_match.check_password(password):
            if self.user_can_authenticate(username_match):
                return username_match

        email_matches = UserModel.objects.filter(email__iexact=login_value).order_by("id")
        for user in email_matches:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None
