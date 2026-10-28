"""Publication workflow. Every transition checks permissions server-side and is recorded."""
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from . import audit
from .models import ContentStatus, PublicationRecord

S = ContentStatus
A = PublicationRecord.Action

# action -> (allowed from-statuses, to-status, required permission (None = model change perm), record action)
TRANSITIONS = {
    "submit": ({S.DRAFT, S.APPROVED}, S.IN_REVIEW, None, A.SUBMITTED),
    "approve": ({S.IN_REVIEW}, S.APPROVED, "core.review_content", A.APPROVED),
    "return_draft": ({S.IN_REVIEW, S.APPROVED, S.ARCHIVED}, S.DRAFT, None, A.REJECTED),
    "publish": ({S.DRAFT, S.IN_REVIEW, S.APPROVED, S.SCHEDULED, S.ARCHIVED}, S.PUBLISHED, "core.publish_content", A.PUBLISHED),
    "schedule": ({S.DRAFT, S.IN_REVIEW, S.APPROVED}, S.SCHEDULED, "core.publish_content", A.SCHEDULED),
    "unpublish": ({S.PUBLISHED, S.SCHEDULED}, S.DRAFT, "core.publish_content", A.UNPUBLISHED),
    "archive": ({S.DRAFT, S.IN_REVIEW, S.APPROVED, S.SCHEDULED, S.PUBLISHED}, S.ARCHIVED, "core.publish_content", A.ARCHIVED),
}


def change_perm(instance):
    meta = instance._meta
    return f"{meta.app_label}.change_{meta.model_name}"


def available_actions(user, instance):
    actions = []
    for name, (sources, _target, perm, _rec) in TRANSITIONS.items():
        if instance.status not in sources:
            continue
        if not user.has_perm(change_perm(instance)):
            continue
        if perm and not user.has_perm(perm):
            continue
        actions.append(name)
    return actions


def can_edit(user, instance):
    """Editing live content changes the public site immediately, so it requires publish permission."""
    if not user.has_perm(change_perm(instance)):
        return False
    if getattr(instance, "is_live", False) and not user.has_perm("core.publish_content"):
        return False
    return True


def transition(instance, action, user, *, publish_at=None, note="", request=None):
    if action not in TRANSITIONS:
        raise ValidationError("Unknown action.")
    sources, target, perm, record_action = TRANSITIONS[action]
    if not user.has_perm(change_perm(instance)) or (perm and not user.has_perm(perm)):
        raise PermissionDenied("You don't have permission for this action.")
    if instance.status not in sources:
        raise ValidationError(f"Cannot {action.replace('_', ' ')} content that is {instance.get_status_display().lower()}.")
    if action == "schedule":
        if publish_at is None or publish_at <= timezone.now():
            raise ValidationError("Choose a publication time in the future.")
        instance.publish_at = publish_at
    previous = instance.status
    with transaction.atomic():
        instance.status = target
        fields = ["status", "publish_at", "updated_at"]
        if target == S.PUBLISHED:
            instance.published_at = instance.published_at or timezone.now()
            fields.append("published_at")
        if action == "unpublish":
            instance.publish_at = None
        instance.save(update_fields=fields)
        PublicationRecord.objects.create(
            content_type=ContentType.objects.get_for_model(instance, for_concrete_model=False),
            object_id=instance.pk, object_repr=str(instance)[:200], action=record_action,
            from_status=previous, to_status=target, note=note[:255], actor=user,
        )
        audit.record(f"content_{action}", actor=user, target=instance, request=request,
                     summary=f"{previous} → {target}")
    return instance


def promote_due_scheduled(models_list, now=None):
    """Flip scheduled items whose time has arrived to Published (the public queryset already treats
    them as live; this keeps the stored status and published_at accurate)."""
    now = now or timezone.now()
    count = 0
    for model in models_list:
        for obj in model.objects.filter(status=S.SCHEDULED, publish_at__lte=now):
            obj.status = S.PUBLISHED
            obj.published_at = obj.published_at or obj.publish_at
            obj.save(update_fields=["status", "published_at", "updated_at"])
            PublicationRecord.objects.create(
                content_type=ContentType.objects.get_for_model(obj, for_concrete_model=False), object_id=obj.pk,
                object_repr=str(obj)[:200], action=A.PUBLISHED, from_status=S.SCHEDULED, to_status=S.PUBLISHED,
                note="Scheduled publication",
            )
            count += 1
    return count
