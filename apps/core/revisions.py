"""Revision snapshots: every studio save stores a JSON snapshot that can be compared and restored."""
import json

from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models, transaction

from .models import ContentRevision

EXCLUDED = {"search_document", "created_at", "updated_at", "revision", "published_at"}


def snapshot(instance):
    data = {}
    for field in instance._meta.concrete_fields:
        if field.name in EXCLUDED or field.primary_key:
            continue
        value = field.value_from_object(instance)
        if isinstance(field, models.FileField):
            value = value.name if value else ""
        data[field.attname] = value
    for field in instance._meta.many_to_many:
        if instance.pk:
            data[field.name] = sorted(getattr(instance, field.name).values_list("pk", flat=True))
    return json.loads(json.dumps(data, cls=DjangoJSONEncoder))


def create_revision(instance, author=None, summary=""):
    ct = ContentType.objects.get_for_model(instance, for_concrete_model=False)
    with transaction.atomic():
        last = (
            ContentRevision.objects.select_for_update()
            .filter(content_type=ct, object_id=instance.pk)
            .order_by("-revision_number")
            .values_list("revision_number", flat=True)
            .first()
        )
        number = (last or 0) + 1
        rev = ContentRevision.objects.create(
            content_type=ct, object_id=instance.pk, revision_number=number,
            snapshot=snapshot(instance), author=author if getattr(author, "is_authenticated", False) else None,
            summary=summary[:255],
        )
        if hasattr(instance, "revision"):
            type(instance).objects.filter(pk=instance.pk).update(revision=number)
            instance.revision = number
    return rev


def revisions_for(instance):
    ct = ContentType.objects.get_for_model(instance, for_concrete_model=False)
    return ContentRevision.objects.filter(content_type=ct, object_id=instance.pk).select_related("author")


def diff(old: dict, new: dict):
    """Return [(field, old_value, new_value)] for fields that differ."""
    keys = sorted(set(old) | set(new))
    return [(key, old.get(key), new.get(key)) for key in keys if old.get(key) != new.get(key)]


RESTORE_SKIP = {"status", "publish_at", "is_seeded"}  # restoring content never changes publication state


def restore(instance, revision, author=None):
    """Apply a revision's content to the instance (publication state is preserved), then snapshot again."""
    data = revision.snapshot
    field_map = {f.attname: f for f in instance._meta.concrete_fields}
    with transaction.atomic():
        for attname, value in data.items():
            if attname in RESTORE_SKIP:
                continue
            field = field_map.get(attname)
            if field is None or field.primary_key or field.name in EXCLUDED:
                continue
            if field.is_relation and value is not None:
                if not field.related_model.objects.filter(pk=value).exists():
                    value = None if field.null else getattr(instance, attname)
            if isinstance(field, models.FileField):
                continue  # files are not rolled back; reattach manually if needed
            setattr(instance, attname, field.to_python(value) if value is not None else None)
        instance.save()
        for m2m in instance._meta.many_to_many:
            if m2m.name in data:
                existing = m2m.related_model.objects.filter(pk__in=data[m2m.name]).values_list("pk", flat=True)
                getattr(instance, m2m.name).set(list(existing))
        return create_revision(instance, author=author, summary=f"Restored revision {revision.revision_number}")
