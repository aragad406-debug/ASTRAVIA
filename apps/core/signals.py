from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import audit


@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    audit.record("login", actor=user, request=request, summary="Signed in")


@receiver(user_logged_out)
def on_logout(sender, request, user, **kwargs):
    if user is not None:
        audit.record("logout", actor=user, request=request, summary="Signed out")


@receiver(user_login_failed)
def on_login_failed(sender, credentials, request=None, **kwargs):
    # Only the attempted identifier is kept; the password is never logged.
    identifier = str((credentials or {}).get("username") or (credentials or {}).get("email") or "")[:254]
    audit.record("login_failed", request=request, actor_label=identifier, summary="Failed sign-in attempt")


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_profile(sender, instance, created, **kwargs):
    if created:
        from apps.accounts.models import UserProfile

        UserProfile.objects.get_or_create(user=instance)
