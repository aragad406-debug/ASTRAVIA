"""Dedicated studio tools: sign-in, dashboard, story flow, dialogue preview, voice, storyboard,
localization, team & roles, audit log, publication history, site settings, deletion requests."""
import json
from itertools import chain

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.forms import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.accounts.forms import RateLimitedAuthenticationForm
from apps.accounts.models import AccountDeletionRequest
from apps.characters.models import Character
from apps.core import audit, publishing, revisions
from apps.core.conditions import ConditionContext, evaluate
from apps.core.models import AuditEvent, ContentStatus, PublicationRecord, SiteConfiguration, UIString, Visibility
from apps.core.ui import STRINGS, clear_cache
from apps.dialogues.models import DialogueEntry, VoiceGenerationRequest, VoiceProfile
from apps.dialogues.voice import request_generation
from apps.localization.models import TranslationReview, text_fingerprint
from apps.media_library.models import MediaAsset
from apps.narrative.graph import layout, validate_chapter
from apps.narrative.models import Artifact, Cinematic, LoreEntry, StoryBranch, StoryChapter, StoryNode
from apps.quests.models import Quest
from apps.worlds.models import World

from .access import studio_required
from .forms import DialoguePreviewForm, SiteConfigurationForm, TeamMemberForm, TranslationImportForm, formfield_callback
from .registry import SECTIONS, get_section, localized_models, publishable_models

User = get_user_model()


# ------------------------------------------------------------------ sign-in
class StudioLoginView(auth_views.LoginView):
    template_name = "creator_studio/login.html"
    authentication_form = RateLimitedAuthenticationForm
    redirect_authenticated_user = True

    def get_default_redirect_url(self):
        from django.urls import reverse

        return reverse("creator_studio:dashboard")


# ------------------------------------------------------------------ dashboard
def _incomplete_records():
    rows = []
    for w in World.objects.not_archived():
        if not (w.short_description_en and w.description_en) or not w.ruler_id:
            rows.append(("worlds", w, "Missing description or ruler"))
    for c in Character.objects.not_archived().exclude(visibility=Visibility.TEASER):
        if not (c.biography_en or c.biography_ar):
            rows.append(("characters", c, "No biography"))
    for q in Quest.objects.not_archived().annotate(n=Count("objectives")).filter(n=0):
        rows.append(("quests", q, "No objectives"))
    for ch in StoryChapter.objects.not_archived().annotate(n=Count("nodes")).filter(n=0, body_en="", body_ar=""):
        rows.append(("chapters", ch, "No text and no story nodes"))
    return rows


def _missing_translation_count():
    total = 0
    for section in localized_models():
        for obj in section.model.objects.all().iterator():
            total += len(obj.missing_translations())
    return total


@studio_required()
def dashboard(request):
    models = publishable_models()
    status_counts = {s: 0 for s in ContentStatus.values}
    recent = []
    for model in models:
        for row in model.objects.values("status").annotate(n=Count("pk")):
            status_counts[row["status"]] += row["n"]
        recent.extend(model.objects.order_by("-updated_at")[:6])
    recent.sort(key=lambda o: o.updated_at, reverse=True)
    from .registry import section_for

    recent_rows = [(section_for(o), o) for o in recent[:10] if section_for(o)]
    media = MediaAsset.objects.filter(is_archived=False).aggregate(n=Count("pk"), size=Sum("size_bytes"))
    file_assets = MediaAsset.objects.filter(is_archived=False).exclude(kind=MediaAsset.Kind.EXTERNAL)[:200]
    broken = [a for a in file_assets if a.is_missing]
    activity = AuditEvent.objects.select_related("actor")
    if not request.user.has_perm("core.view_audit_log"):
        activity = activity.filter(actor=request.user)
    context = {
        "totals": {
            "Worlds": World.objects.count(), "Characters": Character.objects.count(), "Quests": Quest.objects.count(),
            "Dialogue entries": DialogueEntry.objects.count(), "Story chapters": StoryChapter.objects.count(),
            "Lore entries": LoreEntry.objects.count(),
        },
        "status_counts": status_counts,
        "scheduled": list(chain.from_iterable(m.objects.filter(status=ContentStatus.SCHEDULED).order_by("publish_at")[:5] for m in models))[:8],
        "in_review": list(chain.from_iterable(m.objects.filter(status=ContentStatus.IN_REVIEW)[:5] for m in models))[:8],
        "recent_rows": recent_rows,
        "activity": activity[:10],
        "media": media,
        "broken_media": broken[:10],
        "missing_portraits": Character.objects.not_archived().filter(portrait__isnull=True).exclude(visibility=Visibility.HIDDEN)
        .exclude(category=Character.Category.HISTORICAL),
        "missing_translations": _missing_translation_count(),
        "incomplete": _incomplete_records()[:12],
        "section_for": section_for,
    }
    return render(request, "creator_studio/dashboard.html", context)


# ------------------------------------------------------------------ story flow editor
def _branch_formset_class():
    return modelformset_factory(
        StoryBranch, fields=["from_node", "to_node", "label_en", "label_ar", "condition", "consequences", "order"],
        extra=2, can_delete=True, formfield_callback=formfield_callback,
    )


@studio_required("narrative.view_storychapter")
def story_flow(request, pk):
    chapter = get_object_or_404(StoryChapter.objects.select_related("arc"), pk=pk)
    can_edit = request.user.has_perm("narrative.change_storybranch") and publishing.can_edit(request.user, chapter)
    qs = StoryBranch.objects.filter(from_node__chapter=chapter).select_related("from_node", "to_node")
    FormSet = _branch_formset_class()
    formset = FormSet(request.POST or None, queryset=qs, prefix="branch")
    chapter_nodes = StoryNode.objects.filter(chapter=chapter)
    arc_nodes = StoryNode.objects.filter(chapter__arc=chapter.arc).select_related("chapter")
    for form in formset.forms:
        form.fields["from_node"].queryset = chapter_nodes
        form.fields["to_node"].queryset = arc_nodes
        form.fields["to_node"].label_from_instance = lambda n: f"{n.chapter.slug} · {n.key}"
        form.fields["from_node"].label_from_instance = lambda n: n.key
    if request.method == "POST":
        if not can_edit:
            raise PermissionDenied
        if formset.is_valid():
            with transaction.atomic():
                formset.save()
                revisions.create_revision(chapter, author=request.user, summary="Story branches edited")
                audit.record("story_flow_updated", actor=request.user, target=chapter, request=request, summary="Branches edited")
            messages.success(request, "Branches saved.")
            return redirect("creator_studio:story_flow", pk=pk)
        messages.error(request, "Some branches are invalid. Fix the highlighted rows.")
    return render(request, "creator_studio/story_flow.html", {
        "chapter": chapter, "formset": formset, "can_edit": can_edit, "report": validate_chapter(chapter),
        "graph": layout(chapter), "section": get_section("chapters"),
    })


# ------------------------------------------------------------------ dialogue preview & voice
@studio_required("dialogues.view_dialogueentry")
def dialogue_preview(request, pk):
    entry = get_object_or_404(DialogueEntry.objects.select_related("speaker", "voice_en", "voice_ar"), pk=pk)
    quests = [(q.slug, q.title_en) for q in Quest.objects.all()]
    lore = [(l.slug, l.title_en) for l in LoreEntry.objects.all()]
    items = [(a.slug, a.name_en) for a in Artifact.objects.all()]
    form = DialoguePreviewForm(request.GET or None, quests=quests, lore=lore, items=items, initial={"language": "en", "flags": {}})
    result = None
    if form.is_bound and form.is_valid():
        d = form.cleaned_data
        states = {slug: "completed" for slug in d["completed_quests"]}
        states.update({slug: "active" for slug in d["active_quests"]})
        ctx = ConditionContext(quest_states=states, discovered_lore=set(d["discovered_lore"]), items=set(d["items"]),
                               flags=d["flags"] or {}, page=d["page"] or "")
        lang = d["language"]
        result = {
            "lang": lang,
            "entry_passes": evaluate(entry.conditions, ctx),
            "text": entry.text_ar if lang == "ar" else entry.text_en,
            "voice": entry.voice_for(lang),
            "choices": [
                {"choice": c, "passes": evaluate(c.condition, ctx), "text": c.text_ar if lang == "ar" else c.text_en}
                for c in entry.choices.select_related("next_entry")
            ],
        }
    return render(request, "creator_studio/dialogue_preview.html", {"entry": entry, "form": form, "result": result, "section": get_section("dialogue")})


@studio_required("dialogues.add_voicegenerationrequest")
@require_POST
def voice_generate(request, pk):
    entry = get_object_or_404(DialogueEntry, pk=pk)
    profile = get_object_or_404(VoiceProfile, pk=request.POST.get("voice_profile"))
    language = "ar" if request.POST.get("language") == "ar" else "en"
    req = request_generation(entry, profile, language, request.user)
    audit.record("voice_generation", actor=request.user, target=entry, request=request, summary=f"{language}: {req.status}")
    if req.status == VoiceGenerationRequest.Status.SUCCEEDED:
        messages.success(request, "Voice generated and saved to the media library. Attach it to the line to use it.")
    else:
        messages.warning(request, f"Voice not generated: {req.error_message}")
    return redirect("creator_studio:content_edit", key="dialogue", pk=pk)


# ------------------------------------------------------------------ storyboard
@studio_required("narrative.view_cinematic")
def storyboard(request, pk):
    cinematic = get_object_or_404(Cinematic.objects.select_related("story_chapter", "rendered_video"), pk=pk)
    scenes = cinematic.scenes.select_related("dialogue", "voice_track")
    total = sum(s.duration_seconds or 0 for s in scenes)
    return render(request, "creator_studio/storyboard.html", {"cinematic": cinematic, "scenes": scenes, "total": total, "section": get_section("cinematics")})


# ------------------------------------------------------------------ localization studio
def _review_state(obj, field):
    ct = ContentType.objects.get_for_model(obj, for_concrete_model=False)
    review = TranslationReview.objects.filter(content_type=ct, object_id=obj.pk, field=field).first()
    current = text_fingerprint(getattr(obj, f"{field}_en", ""), getattr(obj, f"{field}_ar", ""))
    if review is None:
        return "unreviewed"
    return "reviewed" if review.fingerprint == current else "stale"


@studio_required("localization.view_glossaryterm")
def localization_overview(request):
    rows = []
    for section in localized_models():
        if not request.user.has_perm(section.perm("view")):
            continue
        objs = list(section.model.objects.all())
        missing = [(o, o.missing_translations()) for o in objs]
        missing = [(o, m) for o, m in missing if m]
        rows.append({"section": section, "total": len(objs), "missing_records": len(missing), "missing_fields": sum(len(m) for _, m in missing)})
    return render(request, "creator_studio/localization_overview.html", {"rows": rows})


@studio_required("localization.view_glossaryterm")
def localization_missing(request):
    key = request.GET.get("section", "")
    lang = request.GET.get("lang", "")
    sections = [s for s in localized_models() if request.user.has_perm(s.perm("view"))]
    rows = []
    for section in sections:
        if key and section.key != key:
            continue
        for obj in section.model.objects.all():
            for field, missing_lang in obj.missing_translations():
                if lang and missing_lang != lang:
                    continue
                rows.append({"section": section, "obj": obj, "field": field, "lang": missing_lang})
    page = Paginator(rows, 40).get_page(request.GET.get("page"))
    return render(request, "creator_studio/localization_missing.html", {"page_obj": page, "sections": sections, "key": key, "lang": lang})


@studio_required(lambda request, key, pk: get_section(key).perm("view") if get_section(key) else "core.__none__")
def localization_compare(request, key, pk):
    section = get_section(key)
    obj = get_object_or_404(section.model, pk=pk)
    if request.method == "POST":
        if not (request.user.has_perm("localization.add_translationreview") or request.user.has_perm("localization.change_translationreview")):
            raise PermissionDenied
        ct = ContentType.objects.get_for_model(obj, for_concrete_model=False)
        reviewed = [f for f in request.POST.getlist("reviewed") if f in obj.localized_fields]
        for field in reviewed:
            TranslationReview.objects.update_or_create(
                content_type=ct, object_id=obj.pk, field=field,
                defaults={"fingerprint": text_fingerprint(getattr(obj, f"{field}_en", ""), getattr(obj, f"{field}_ar", "")),
                          "reviewed_by": request.user},
            )
        audit.record("translation_reviewed", actor=request.user, target=obj, request=request, summary=f"{len(reviewed)} field(s) reviewed")
        messages.success(request, f"{len(reviewed)} field(s) marked as reviewed.")
        return redirect("creator_studio:localization_compare", key=key, pk=pk)
    fields = [{"name": f, "en": getattr(obj, f"{f}_en", ""), "ar": getattr(obj, f"{f}_ar", ""), "state": _review_state(obj, f)}
              for f in obj.localized_fields]
    return render(request, "creator_studio/localization_compare.html", {"section": section, "obj": obj, "fields": fields})


@studio_required("localization.view_glossaryterm")
def localization_export(request):
    only_missing = request.GET.get("missing") == "1"
    records = []
    for section in localized_models():
        if not request.user.has_perm(section.perm("view")):
            continue
        label = section.model._meta.label_lower
        for obj in section.model.objects.all():
            if only_missing and not obj.missing_translations():
                continue
            records.append({
                "model": label, "pk": obj.pk, "ref": getattr(obj, "slug", None) or getattr(obj, "key", None) or str(obj),
                "fields": {f: obj.loc_pair(f) for f in obj.localized_fields},
            })
    payload = {"format": "astravia-translations", "version": 1, "exported_at": timezone.now().isoformat(), "records": records}
    audit.record("translations_exported", actor=request.user, request=request, summary=f"{len(records)} records")
    response = HttpResponse(json.dumps(payload, ensure_ascii=False, indent=2), content_type="application/json; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="astravia-translations-{timezone.now():%Y%m%d}.json"'
    return response


@studio_required("localization.view_glossaryterm")
def localization_import(request):
    form = TranslationImportForm(request.POST or None, request.FILES or None)
    report = None
    if request.method == "POST" and form.is_valid():
        allowed = {s.model._meta.label_lower: s for s in localized_models()}
        updated, skipped, errors = 0, 0, []
        with transaction.atomic():
            for i, rec in enumerate(form.cleaned_data["file"]["records"][:5000]):
                section = allowed.get(str(rec.get("model", "")))
                if section is None or not isinstance(rec.get("fields"), dict):
                    skipped += 1
                    continue
                if not request.user.has_perm(section.perm("change")):
                    errors.append(f"Record {i + 1}: no permission to change {section.label}.")
                    continue
                obj = section.model.objects.filter(pk=rec.get("pk")).first()
                if obj is None:
                    errors.append(f"Record {i + 1}: {rec.get('model')} #{rec.get('pk')} not found.")
                    continue
                if getattr(obj, "is_live", False) and not request.user.has_perm("core.publish_content"):
                    errors.append(f"Record {i + 1}: “{obj}” is published; publishing permission is required.")
                    continue
                changed = []
                for field, langs in rec["fields"].items():
                    if field not in obj.localized_fields or not isinstance(langs, dict):
                        continue
                    for lang in ("en", "ar"):
                        value = langs.get(lang)
                        attr = f"{field}_{lang}"
                        if isinstance(value, str) and value != getattr(obj, attr):
                            max_len = obj._meta.get_field(attr).max_length
                            if max_len and len(value) > max_len:
                                errors.append(f"Record {i + 1}: {attr} longer than {max_len} characters.")
                                continue
                            setattr(obj, attr, value)
                            changed.append(attr)
                if changed:
                    obj.save()
                    revisions.create_revision(obj, author=request.user, summary=f"Translation import: {', '.join(changed[:6])}")
                    updated += 1
        audit.record("translations_imported", actor=request.user, request=request, summary=f"{updated} updated, {skipped} skipped")
        report = {"updated": updated, "skipped": skipped, "errors": errors[:50]}
        messages.success(request, f"Import finished: {updated} record(s) updated.")
    return render(request, "creator_studio/localization_import.html", {"form": form, "report": report})


@studio_required("core.view_uistring")
def interface_text(request):
    can_edit = request.user.has_perm("core.change_uistring") and request.user.has_perm("core.add_uistring")
    if request.method == "POST":
        if not can_edit:
            raise PermissionDenied
        key = request.POST.get("key", "")
        if key not in STRINGS:
            messages.error(request, "Unknown interface key.")
            return redirect("creator_studio:interface_text")
        en = request.POST.get("text_en", "").strip()[:500]
        ar = request.POST.get("text_ar", "").strip()[:500]
        if not en and not ar:
            UIString.objects.filter(key=key).delete()
            messages.success(request, f"“{key}” reset to the default text.")
        else:
            UIString.objects.update_or_create(key=key, defaults={"text_en": en, "text_ar": ar})
            messages.success(request, f"“{key}” saved.")
        clear_cache()
        audit.record("interface_text_changed", actor=request.user, request=request, summary=key)
        return redirect(f"{request.path}?q={request.POST.get('q', '')}#k-{key}")
    q = request.GET.get("q", "").strip().lower()
    overrides = {u.key: u for u in UIString.objects.all()}
    rows = [{"key": k, "en": v[0], "ar": v[1], "override": overrides.get(k)} for k, v in STRINGS.items()
            if not q or q in k.lower() or q in v[0].lower() or q in v[1]]
    return render(request, "creator_studio/interface_text.html", {"rows": rows, "q": q, "can_edit": can_edit})


# ------------------------------------------------------------------ team & roles
@studio_required("core.manage_team")
def team(request):
    allow_owner = request.user.is_superuser
    form = TeamMemberForm(request.POST or None, allow_owner=allow_owner)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"].lower()
        roles = list(form.cleaned_data["roles"])
        user = User.objects.filter(email__iexact=email).first()
        if user and user.is_superuser and not request.user.is_superuser:
            raise PermissionDenied
        created = False
        with transaction.atomic():
            if user is None:
                user = User.objects.create_user(email=email, password=None)  # unusable password until reset
                created = True
            keep = list(user.groups.filter(name="Owner")) if not allow_owner else []
            user.groups.set(roles + keep)
            audit.record("roles_changed", actor=request.user, target=user, request=request,
                         summary="Roles: " + (", ".join(g.name for g in roles) or "none"))
        if created:
            messages.success(request, f"{email} added. They set a password with “Forgot your password?” on the studio sign-in page.")
        else:
            messages.success(request, f"Roles updated for {email}.")
        return redirect("creator_studio:team")
    members = User.objects.filter(Q(groups__isnull=False) | Q(is_superuser=True)).distinct().prefetch_related("groups").order_by("email")
    return render(request, "creator_studio/team.html", {"form": form, "members": members, "groups": Group.objects.order_by("name")})


# ------------------------------------------------------------------ audit & publication history
@studio_required("core.view_audit_log")
def audit_log(request):
    qs = AuditEvent.objects.select_related("actor", "target_type")
    action = request.GET.get("action", "")
    actor = request.GET.get("actor", "").strip()
    if action:
        qs = qs.filter(action=action)
    if actor:
        qs = qs.filter(actor_label__icontains=actor)
    actions = AuditEvent.objects.order_by().values_list("action", flat=True).distinct()
    page = Paginator(qs, 50).get_page(request.GET.get("page"))
    return render(request, "creator_studio/audit_log.html", {"page_obj": page, "actions": sorted(actions), "action": action, "actor": actor})


@studio_required()
def publication_history(request):
    qs = PublicationRecord.objects.select_related("actor", "content_type")
    page = Paginator(qs, 50).get_page(request.GET.get("page"))
    return render(request, "creator_studio/publications.html", {"page_obj": page})


# ------------------------------------------------------------------ site settings
@studio_required("core.manage_site_settings")
def site_settings(request):
    config = SiteConfiguration.load()
    form = SiteConfigurationForm(request.POST or None, instance=config)
    if request.method == "POST" and form.is_valid():
        form.save()
        audit.record("site_settings_changed", actor=request.user, target=config, request=request,
                     summary="Changed: " + ", ".join(form.changed_data[:10]))
        messages.success(request, "Site settings saved.")
        return redirect("creator_studio:site_settings")
    return render(request, "creator_studio/site_settings.html", {"form": form})


# ------------------------------------------------------------------ account deletion requests
@studio_required("core.manage_team")
def deletion_requests(request):
    if request.method == "POST":
        req = get_object_or_404(AccountDeletionRequest, pk=request.POST.get("request_id"), status=AccountDeletionRequest.Status.PENDING)
        decision = request.POST.get("decision")
        with transaction.atomic():
            if decision == "complete":
                target = req.user
                if target and (target.is_superuser or target == request.user):
                    messages.error(request, "Owner and your own account must be deleted from the command line.")
                    return redirect("creator_studio:deletion_requests")
                audit.record("account_deleted", actor=request.user, request=request, summary=f"Deletion request #{req.pk} completed")
                if target:
                    target.delete()
                req.status = AccountDeletionRequest.Status.COMPLETED
            elif decision == "cancel":
                req.status = AccountDeletionRequest.Status.CANCELLED
                audit.record("deletion_cancelled", actor=request.user, request=request, summary=f"Deletion request #{req.pk} cancelled")
            else:
                messages.error(request, "Unknown decision.")
                return redirect("creator_studio:deletion_requests")
            req.processed_by = request.user
            req.processed_at = timezone.now()
            req.save()
        messages.success(request, "Request updated.")
        return redirect("creator_studio:deletion_requests")
    return render(request, "creator_studio/deletion_requests.html", {
        "pending": AccountDeletionRequest.objects.filter(status=AccountDeletionRequest.Status.PENDING),
        "processed": AccountDeletionRequest.objects.exclude(status=AccountDeletionRequest.Status.PENDING)[:20],
    })
