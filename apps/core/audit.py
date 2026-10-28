"""Audit logging. Summaries must never contain passwords, tokens or secrets."""
import logging

from django.contrib.contenttypes.models import ContentType

from .models import AuditEvent

logger = logging.getLogger("astravia.audit")
SENSITIVE_WORDS = ("password", "token", "secret", "api_key", "apikey", "csrf", "session")


def client_ip(request):
    if request is None:
        return None
    # Render sets X-Forwarded-For; the left-most entry is the client.
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip = forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR")
    return ip or None


def _scrub(summary):
    summary = (summary or "")[:500]
    lowered = summary.lower()
    if any(word in lowered for word in SENSITIVE_WORDS):
        return "[summary withheld: referenced a sensitive field]"
    return summary


def record(action, *, actor=None, target=None, summary="", request=None, actor_label=None):
    if actor is not None and not getattr(actor, "is_authenticated", False):
        actor = None
    event = AuditEvent(
        actor=actor,
        actor_label=actor_label or (actor.email if actor else ""),
        action=action[:40],
        summary=_scrub(summary),
        ip_address=client_ip(request),
    )
    if target is not None and getattr(target, "pk", None) is not None:
        event.target_type = ContentType.objects.get_for_model(target, for_concrete_model=False)
        event.target_id = target.pk
        event.target_repr = str(target)[:200]
    event.save()
    logger.info("audit action=%s actor=%s target=%s", event.action, event.actor_label or "-", event.target_repr or "-")
    return event
