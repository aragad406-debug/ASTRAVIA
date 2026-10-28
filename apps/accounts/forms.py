from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from apps.core import ratelimit
from apps.core.audit import client_ip
from apps.core.ui import t, ui
from apps.media_library.validation import sniff, verify_image

from .models import UserProfile

User = get_user_model()


class RateLimitedAuthenticationForm(AuthenticationForm):
    """Email + password sign-in, throttled per (IP, email) and per IP."""

    username = forms.EmailField(label=t("account.email"), widget=forms.EmailInput(attrs={"autocomplete": "email", "autofocus": True}))
    password = forms.CharField(label=t("account.password"), strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))

    error_messages = {
        "invalid_login": t("account.invalid"),
        "inactive": t("account.invalid"),
    }

    def _keys(self):
        ip = client_ip(self.request) or "unknown"
        email = (self.data.get("username") or "").strip().lower()
        return f"login:{ip}:{email}", f"login-ip:{ip}"

    def clean(self):
        conf = settings.LOGIN_RATE_LIMIT
        pair_key, ip_key = self._keys()
        if ratelimit.is_limited(pair_key, conf["attempts"]) or ratelimit.is_limited(ip_key, conf["attempts"] * 4):
            raise ValidationError(ui("account.rate_limited"), code="rate_limited")
        try:
            cleaned = super().clean()
        except ValidationError:
            ratelimit.hit(pair_key, conf["attempts"], conf["window_seconds"])
            ratelimit.hit(ip_key, conf["attempts"] * 4, conf["window_seconds"])
            raise
        ratelimit.reset(pair_key)
        return cleaned


class RegistrationForm(forms.Form):
    email = forms.EmailField(label=t("account.email"), widget=forms.EmailInput(attrs={"autocomplete": "email"}))
    display_name = forms.CharField(label=t("account.display_name"), max_length=60, required=False)
    password1 = forms.CharField(label=t("account.password"), strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))
    password2 = forms.CharField(label=t("account.password_confirm"), strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))
    website = forms.CharField(required=False, widget=forms.HiddenInput)  # honeypot: humans never fill it

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            # Explicit here (registration), as is standard; password reset stays generic.
            raise ValidationError("An account with this email already exists. Sign in or reset your password.")
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("website"):
            raise ValidationError("Registration failed.")
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "The two passwords don't match.")
        if p1 and cleaned.get("email"):
            try:
                password_validation.validate_password(p1, User(email=cleaned["email"]))
            except ValidationError as exc:
                self.add_error("password1", exc)
        return cleaned

    def save(self):
        user = User.objects.create_user(email=self.cleaned_data["email"], password=self.cleaned_data["password1"])
        profile = user.profile
        profile.display_name = self.cleaned_data.get("display_name", "")
        profile.save()
        return user


class ProfileForm(forms.ModelForm):
    AVATAR_LIMIT = 2 * 1024 * 1024

    class Meta:
        model = UserProfile
        fields = ["display_name", "bio", "preferred_language", "avatar", "show_public_profile", "receive_news_emails"]
        labels = {"display_name": t("account.display_name")}
        widgets = {"bio": forms.Textarea(attrs={"rows": 3, "maxlength": 300})}

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if isinstance(avatar, UploadedFile):
            if avatar.size > self.AVATAR_LIMIT:
                raise ValidationError("Avatar images must be 2 MB or smaller.")
            sniff(avatar, "image")
            verify_image(avatar)
        return avatar


class DeletionRequestForm(forms.Form):
    password = forms.CharField(label=t("account.password"), strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))
    reason = forms.CharField(required=False, max_length=1000, widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data["password"]
        if not self.user.check_password(password):
            raise ValidationError("That password is incorrect.")
        return password
