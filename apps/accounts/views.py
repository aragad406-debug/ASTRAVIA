from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_POST

from apps.core import audit, ratelimit
from apps.core.audit import client_ip
from apps.core.ui import ui

from .forms import DeletionRequestForm, ProfileForm, RateLimitedAuthenticationForm, RegistrationForm
from .models import AccountDeletionRequest
from .verification import read_token, send_verification

User = get_user_model()


def _apply_language(response, user):
    profile = getattr(user, "profile", None)
    if profile and profile.preferred_language:
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, profile.preferred_language,
                            max_age=settings.LANGUAGE_COOKIE_AGE, samesite="Lax",
                            secure=getattr(settings, "LANGUAGE_COOKIE_SECURE", False))
    return response


class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    authentication_form = RateLimitedAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        return _apply_language(response, form.get_user())


@sensitive_post_parameters("password1", "password2")
def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST":
        if ratelimit.hit(f"register:{client_ip(request)}", limit=10, window=3600):
            messages.error(request, ui("account.rate_limited"))
        elif form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
            except IntegrityError:
                form.add_error("email", "An account with this email already exists.")
            else:
                login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                audit.record("account_created", actor=user, target=user, request=request, summary="Registered")
                send_verification(request, user)
                messages.success(request, ui("account.verify.sent"))
                return redirect("accounts:profile")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    profile = request.user.profile
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        audit.record("profile_updated", actor=request.user, target=request.user, request=request, summary="Profile settings changed")
        messages.success(request, ui("account.profile.saved"))
        return _apply_language(redirect("accounts:profile"), request.user)
    pending = AccountDeletionRequest.objects.filter(user=request.user, status=AccountDeletionRequest.Status.PENDING).first()
    return render(request, "accounts/profile.html", {
        "form": form, "pending_deletion": pending, "deletion_form": DeletionRequestForm(request.user),
    })


@login_required
@require_POST
def resend_verification(request):
    if request.user.email_verified:
        return redirect("accounts:profile")
    if not ratelimit.hit(f"verify:{request.user.pk}", limit=3, window=3600):
        send_verification(request, request.user)
    messages.success(request, ui("account.verify.sent"))
    return redirect("accounts:profile")


def verify_email(request, token):
    data = read_token(token)
    user = User.objects.filter(pk=data["uid"]).first() if data else None
    if user is None or user.email != data.get("email"):
        messages.error(request, ui("account.verify.invalid"))
        return redirect("accounts:profile" if request.user.is_authenticated else "accounts:login")
    if not user.email_verified:
        user.email_verified = True
        user.save(update_fields=["email_verified"])
        audit.record("email_verified", actor=user, target=user, request=request, summary="Email verified")
    messages.success(request, ui("account.verify.done"))
    return redirect("accounts:profile" if request.user.is_authenticated else "accounts:login")


@login_required
@require_POST
@sensitive_post_parameters("password")
def request_deletion(request):
    form = DeletionRequestForm(request.user, request.POST)
    if AccountDeletionRequest.objects.filter(user=request.user, status=AccountDeletionRequest.Status.PENDING).exists():
        messages.info(request, ui("account.delete.pending"))
    elif form.is_valid():
        AccountDeletionRequest.objects.create(user=request.user, email_snapshot=request.user.email, reason=form.cleaned_data["reason"])
        audit.record("deletion_requested", actor=request.user, target=request.user, request=request, summary="Account deletion requested")
        messages.success(request, ui("account.delete.requested"))
    else:
        for error in form.errors.get("password", []):
            messages.error(request, error)
    return redirect("accounts:profile")


@method_decorator(sensitive_post_parameters(), name="dispatch")
class PasswordResetView(auth_views.PasswordResetView):
    """Same response whether or not the address has an account; throttled per IP."""

    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/email/password_reset.txt"
    subject_template_name = "accounts/email/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")

    def form_valid(self, form):
        if ratelimit.hit(f"reset:{client_ip(self.request)}", limit=5, window=3600):
            return redirect(self.success_url)  # silently drop, same response as success
        return super().form_valid(form)


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:profile")

    def form_valid(self, form):
        response = super().form_valid(form)
        audit.record("password_changed", actor=self.request.user, target=self.request.user, request=self.request, summary="Password changed")
        messages.success(self.request, ui("account.profile.saved"))
        return response
