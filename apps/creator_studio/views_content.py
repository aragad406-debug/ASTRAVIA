"""Generic, registry-driven content screens: list, create, edit, workflow transitions, revisions, delete."""
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import ProtectedError, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.core import audit, publishing, revisions
from apps.core.models import ContentRevision, ContentStatus, PublicationRecord

from .access import studio_required
from .forms import ScheduleForm, build_form, build_formsets
from .registry import GROUPS, SECTIONS, get_section

# Records whose removal would orphan narrative content: archive them instead of deleting.
SAFE_DELETE_CHECKS = {
    "worlds": ["characters", "quests", "lore_entries", "story_arcs", "chapters", "boss_encounters", "dialogue_lines"],
    "characters": ["ruled_worlds", "dialogue_lines", "boss_encounters", "quests_given", "lore_entries", "chapters"],
    "quests": ["required_by", "boss_encounters", "dialogue_lines", "unlocks_chapters"],
    "arcs": ["chapters"],
    "lore": ["required_by_chapters", "artifacts"],
}


def _section_or_404(key):
    section = get_section(key)
    if section is None:
        raise Http404
    return section


def _perm(action):
    return lambda request, key, *a, **kw: _section_or_404(key).perm(action)


def _queryset(section):
    qs = section.model.objects.all()
    related = [f.name for f in section.model._meta.fields if f.is_relation and f.many_to_one and f.name in section.list_display]
    if related:
        qs = qs.select_related(*related)
    if section.ordering:
        qs = qs.order_by(*section.ordering)
    return qs


@studio_required(_perm("view"))
def content_list(request, key):
    section = _section_or_404(key)
    qs = _queryset(section)
    q = request.GET.get("q", "").strip()[:100]
    if q:
        cond = Q()
        for f in section.search_fields:
            cond |= Q(**{f"{f}__icontains": q})
        qs = qs.filter(cond)
    status = request.GET.get("status", "")
    if section.publishable and status in ContentStatus.values:
        qs = qs.filter(status=status)
    active_filters = {}
    filter_options = []
    for name in section.filters:
        field = section.model._meta.get_field(name)
        value = request.GET.get(name, "")
        if field.is_relation:
            choices = [(str(o.pk), str(o)) for o in field.related_model.objects.all()[:200]]
        else:
            choices = [(str(v), str(label)) for v, label in field.flatchoices]
        if value and value in {c[0] for c in choices}:
            qs = qs.filter(**{f"{name}_id" if field.is_relation else name: value})
            active_filters[name] = value
        filter_options.append({"name": name, "label": field.verbose_name.capitalize(), "choices": choices, "value": value})
    page = Paginator(qs, 25).get_page(request.GET.get("page"))
    return render(request, "creator_studio/content_list.html", {
        "section": section, "page_obj": page, "q": q, "status": status, "filter_options": filter_options,
        "statuses": ContentStatus.choices, "can_add": request.user.has_perm(section.perm("add")),
    })


def _save(request, section, form, formsets, created):
    with transaction.atomic():
        obj = form.save(commit=False)
        if created and section.model.__name__ == "MediaAsset":
            obj.uploaded_by = request.user
        obj.save()
        form.save_m2m()
        for fs in formsets:
            fs.instance = obj
            fs.save()
        changed = ", ".join(form.changed_data[:8]) or "inline records"
        revisions.create_revision(obj, author=request.user, summary=("Created" if created else f"Edited: {changed}"))
        audit.record("content_created" if created else "content_updated", actor=request.user, target=obj, request=request,
                     summary=f"{section.label}: {'created' if created else 'changed ' + changed}")
    return obj


@studio_required(_perm("add"))
def content_create(request, key):
    section = _section_or_404(key)
    Form = build_form(section)
    form = Form(request.POST or None, request.FILES or None)
    formsets = build_formsets(section, section.model(), request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid() and all(fs.is_valid() for fs in formsets):
        obj = _save(request, section, form, formsets, created=True)
        messages.success(request, f"{section.label}: “{obj}” created as a draft." if section.publishable else f"“{obj}” created.")
        return redirect("creator_studio:content_edit", key=key, pk=obj.pk)
    return render(request, "creator_studio/content_form.html", {"section": section, "form": form, "formsets": formsets, "obj": None})


@studio_required(_perm("view"))
def content_edit(request, key, pk):
    section = _section_or_404(key)
    obj = get_object_or_404(section.model, pk=pk)
    can_edit = publishing.can_edit(request.user, obj) if section.publishable else request.user.has_perm(section.perm("change"))
    Form = build_form(section)
    data = request.POST if request.method == "POST" else None
    files = request.FILES if request.method == "POST" else None
    form = Form(data, files, instance=obj)
    formsets = build_formsets(section, obj, data, files)
    if request.method == "POST":
        if not can_edit:
            raise PermissionDenied
        if form.is_valid() and all(fs.is_valid() for fs in formsets):
            _save(request, section, form, formsets, created=False)
            messages.success(request, "Saved.")
            return redirect("creator_studio:content_edit", key=key, pk=obj.pk)
        messages.error(request, "Fix the highlighted fields and save again.")
    if not can_edit:
        for f in form.fields.values():
            f.disabled = True
        for fs in formsets:
            for sub in fs.forms:
                for f in sub.fields.values():
                    f.disabled = True
    context = {
        "section": section, "obj": obj, "form": form, "formsets": formsets, "can_edit": can_edit,
        "actions": publishing.available_actions(request.user, obj) if section.publishable else [],
        "preview_url": section.preview_url(obj),
        "schedule_form": ScheduleForm(),
        "can_delete": request.user.has_perm(section.perm("delete")),
        "history": PublicationRecord.objects.filter(
            content_type=ContentType.objects.get_for_model(obj, for_concrete_model=False), object_id=obj.pk
        ).select_related("actor")[:8],
        "missing": obj.missing_translations() if hasattr(obj, "missing_translations") else [],
    }
    context.update(_extras(section, obj))
    return render(request, "creator_studio/content_form.html", context)


def _extras(section, obj):
    """Section-specific panels shown beside the edit form."""
    extras = {}
    if section.key == "chapters":
        from apps.narrative.graph import validate_chapter

        extras["graph_report"] = validate_chapter(obj)
    if section.key == "quests":
        cycle = obj.dependency_cycle()
        extras["quest_report"] = {"cycle": cycle}
    if section.key == "dialogue":
        from apps.dialogues.models import VoiceGenerationRequest, VoiceProfile

        extras["voice_profiles"] = VoiceProfile.objects.filter(character=obj.speaker, is_active=True) if obj.speaker_id else []
        extras["voice_requests"] = VoiceGenerationRequest.objects.filter(dialogue=obj)[:5]
    if section.key == "media" and obj.pk:
        extras["media_missing"] = obj.is_missing
    return extras


@studio_required(_perm("change"))
@require_POST
def content_transition(request, key, pk, action):
    section = _section_or_404(key)
    if not section.publishable:
        raise Http404
    obj = get_object_or_404(section.model, pk=pk)
    publish_at = None
    if action == "schedule":
        sched = ScheduleForm(request.POST)
        if not sched.is_valid():
            messages.error(request, "Choose a valid date and time to schedule publication.")
            return redirect("creator_studio:content_edit", key=key, pk=pk)
        publish_at = sched.cleaned_data["publish_at"]
    if action in {"publish", "schedule", "approve"} and section.key == "chapters":
        from apps.narrative.graph import validate_chapter

        report = validate_chapter(obj)
        if report["errors"]:
            messages.error(request, "This chapter's story graph has errors. Fix them in the flow editor before publishing.")
            return redirect("creator_studio:content_edit", key=key, pk=pk)
    try:
        publishing.transition(obj, action, request.user, publish_at=publish_at, note=request.POST.get("note", ""), request=request)
    except PermissionDenied:
        raise
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
    else:
        messages.success(request, f"“{obj}” is now {obj.get_status_display().lower()}.")
    return redirect("creator_studio:content_edit", key=key, pk=pk)


@studio_required(_perm("delete"))
@require_POST
def content_delete(request, key, pk):
    section = _section_or_404(key)
    obj = get_object_or_404(section.model, pk=pk)
    if section.publishable and obj.status not in {ContentStatus.DRAFT, ContentStatus.ARCHIVED}:
        messages.error(request, "Only drafts and archived records can be deleted. Unpublish or archive it first.")
        return redirect("creator_studio:content_edit", key=key, pk=pk)
    for rel in SAFE_DELETE_CHECKS.get(key, []):
        manager = getattr(obj, rel, None)
        if manager is not None and manager.exists():
            messages.error(request, f"“{obj}” is still linked to other content ({rel.replace('_', ' ')}). Archive it instead.")
            return redirect("creator_studio:content_edit", key=key, pk=pk)
    label = str(obj)
    try:
        with transaction.atomic():
            audit.record("content_deleted", actor=request.user, target=obj, request=request, summary=f"{section.label}: deleted")
            obj.delete()
    except ProtectedError:
        messages.error(request, f"“{label}” is protected by other records that depend on it. Archive it instead.")
        return redirect("creator_studio:content_edit", key=key, pk=pk)
    messages.success(request, f"“{label}” deleted.")
    return redirect("creator_studio:content_list", key=key)


@studio_required(_perm("view"))
def revision_list(request, key, pk):
    section = _section_or_404(key)
    obj = get_object_or_404(section.model, pk=pk)
    return render(request, "creator_studio/revisions.html", {"section": section, "obj": obj, "revisions": revisions.revisions_for(obj)})


@studio_required(_perm("view"))
def revision_detail(request, key, pk, number):
    section = _section_or_404(key)
    obj = get_object_or_404(section.model, pk=pk)
    rev = get_object_or_404(revisions.revisions_for(obj), revision_number=number)
    compare_to = request.GET.get("compare")
    if compare_to and compare_to.isdigit():
        other = get_object_or_404(revisions.revisions_for(obj), revision_number=int(compare_to))
        base, label = other.snapshot, f"revision {other.revision_number}"
    else:
        base, label = revisions.snapshot(obj), "current version"
    changes = revisions.diff(rev.snapshot, base)
    can_restore = request.user.has_perm(section.perm("change")) and (
        not section.publishable or publishing.can_edit(request.user, obj)
    )
    return render(request, "creator_studio/revision_detail.html", {
        "section": section, "obj": obj, "rev": rev, "changes": changes, "compare_label": label, "can_restore": can_restore,
    })


@studio_required(_perm("change"))
@require_POST
def revision_restore(request, key, pk, number):
    section = _section_or_404(key)
    obj = get_object_or_404(section.model, pk=pk)
    if section.publishable and not publishing.can_edit(request.user, obj):
        raise PermissionDenied
    rev = get_object_or_404(ContentRevision, content_type=ContentType.objects.get_for_model(obj, for_concrete_model=False),
                            object_id=obj.pk, revision_number=number)
    new_rev = revisions.restore(obj, rev, author=request.user)
    try:
        obj.refresh_from_db()
        obj.full_clean()
    except ValidationError as exc:
        messages.warning(request, "Restored, but some restored values no longer validate: " + "; ".join(exc.messages))
    if section.publishable:
        PublicationRecord.objects.create(
            content_type=ContentType.objects.get_for_model(obj, for_concrete_model=False), object_id=obj.pk,
            object_repr=str(obj)[:200], action=PublicationRecord.Action.RESTORED, from_status=obj.status,
            to_status=obj.status, note=f"Restored revision {number}", actor=request.user,
        )
    audit.record("revision_restored", actor=request.user, target=obj, request=request, summary=f"Restored revision {number} as {new_rev.revision_number}")
    messages.success(request, f"Revision {number} restored (saved as revision {new_rev.revision_number}).")
    return redirect("creator_studio:content_edit", key=key, pk=pk)


def nav_context(user):
    groups = []
    for gkey, label_en, label_ar in GROUPS:
        items = [s for s in SECTIONS if s.group == gkey and user.has_perm(s.perm("view"))]
        groups.append({"key": gkey, "label_en": label_en, "label_ar": label_ar, "items": items})
    return groups
