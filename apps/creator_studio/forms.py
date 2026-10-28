import json

from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.contrib.auth.models import Group
from django.db import models
from django.forms import inlineformset_factory, modelform_factory

from apps.core.models import SiteConfiguration
from apps.media_library.models import MediaAsset
from apps.media_library.validation import sniff, verify_image

from .registry import STUDIO_EXCLUDE

JSON_HELP = "JSON. Conditions use the structured grammar described in the Creator Studio guide; leave {} for none."


class PrettyJSONField(forms.JSONField):
    def prepare_value(self, value):
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False, indent=2)


def _widget_for(db_field):
    name = db_field.name
    attrs = {}
    if name.endswith("_ar"):
        attrs.update({"dir": "rtl", "lang": "ar"})
    elif name.endswith("_en"):
        attrs.update({"dir": "ltr", "lang": "en"})
    if isinstance(db_field, models.TextField):
        rows = 8 if any(k in name for k in ("body", "content", "biography", "description")) else 3
        return forms.Textarea(attrs={**attrs, "rows": rows})
    if isinstance(db_field, models.DateTimeField):
        return forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M")
    if isinstance(db_field, models.ManyToManyField):
        return forms.SelectMultiple(attrs={"size": 6})
    if attrs and isinstance(db_field, models.CharField) and not db_field.choices:
        return forms.TextInput(attrs=attrs)
    return None


def formfield_callback(db_field, **kwargs):
    if isinstance(db_field, models.JSONField):
        return PrettyJSONField(
            required=not db_field.blank, initial=db_field.default() if callable(db_field.default) else db_field.default,
            help_text=db_field.help_text or JSON_HELP, label=db_field.verbose_name.capitalize(),
            widget=forms.Textarea(attrs={"rows": 3, "class": "json", "dir": "ltr", "spellcheck": "false"}),
        )
    widget = _widget_for(db_field)
    if widget is not None:
        kwargs["widget"] = widget
    return db_field.formfield(**kwargs)


def editable_fields(model):
    return [
        f.name for f in list(model._meta.fields) + list(model._meta.many_to_many)
        if f.editable and not f.primary_key and f.name not in STUDIO_EXCLUDE
    ]


def build_form(section):
    if section.model is MediaAsset:
        return MediaAssetForm
    fields = section.fields or editable_fields(section.model)
    return modelform_factory(section.model, fields=fields, formfield_callback=formfield_callback)


def build_formsets(section, instance, data=None, files=None):
    formsets = []
    for inline in section.inlines:
        factory = inlineformset_factory(
            section.model, inline.model, fields=inline.fields, fk_name=inline.fk_name, extra=inline.extra,
            can_delete=True, formfield_callback=formfield_callback,
        )
        prefix = inline.model._meta.model_name
        fs = factory(data=data, files=files, instance=instance, prefix=prefix)
        fs.studio_label = inline.label
        formsets.append(fs)
    return formsets


class MediaAssetForm(forms.ModelForm):
    class Meta:
        model = MediaAsset
        fields = ["title", "kind", "role", "file", "external_url", "unreal_asset_path", "alt_text_en", "alt_text_ar",
                  "description_en", "description_ar", "tags", "is_archived"]
        widgets = {
            "alt_text_ar": forms.TextInput(attrs={"dir": "rtl", "lang": "ar"}),
            "description_en": forms.Textarea(attrs={"rows": 3}),
            "description_ar": forms.Textarea(attrs={"rows": 3, "dir": "rtl", "lang": "ar"}),
        }

    def clean(self):
        cleaned = super().clean()
        kind = cleaned.get("kind")
        upload = cleaned.get("file")
        is_new_upload = isinstance(upload, UploadedFile)
        if kind == MediaAsset.Kind.EXTERNAL:
            if not (cleaned.get("external_url") or cleaned.get("unreal_asset_path")):
                raise forms.ValidationError("External assets need an external URL or an Unreal asset path.")
            if is_new_upload:
                self.add_error("file", "External references don't take an uploaded file.")
            return cleaned
        if not upload and not (self.instance.pk and self.instance.file):
            self.add_error("file", "Choose a file to upload.")
            return cleaned
        if is_new_upload:
            try:
                detected, mime = sniff(upload, kind)
                width = height = None
                if kind == MediaAsset.Kind.IMAGE:
                    width, height = verify_image(upload)
            except forms.ValidationError as exc:
                self.add_error("file", exc)
                return cleaned
            self._file_meta = {"detected_format": detected, "mime_type": mime, "size_bytes": upload.size,
                               "width": width, "height": height}
        elif self.instance.pk and "kind" in self.changed_data:
            self.add_error("kind", "Upload a new file to change the media kind.")
        if kind == MediaAsset.Kind.IMAGE and not (cleaned.get("alt_text_en") or cleaned.get("alt_text_ar")):
            self.add_error("alt_text_en", "Describe the image for screen-reader users (alt text).")
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        for key, value in getattr(self, "_file_meta", {}).items():
            setattr(obj, key, value)
        if commit:
            obj.save()
        return obj


class SiteConfigurationForm(forms.ModelForm):
    class Meta:
        model = SiteConfiguration
        exclude = ["created_at", "updated_at"]
        field_classes = {"social_links": PrettyJSONField}
        widgets = {
            name: forms.Textarea(attrs={"rows": 3, **({"dir": "rtl", "lang": "ar"} if name.endswith("_ar") else {})})
            for name in ("hero_intro_en", "hero_intro_ar", "universe_intro_en", "universe_intro_ar", "narrative_intro_en",
                         "narrative_intro_ar", "gameplay_intro_en", "gameplay_intro_ar")
        } | {
            "hero_title_ar": forms.TextInput(attrs={"dir": "rtl", "lang": "ar"}),
            "project_status_ar": forms.TextInput(attrs={"dir": "rtl", "lang": "ar"}),
            "social_links": forms.Textarea(attrs={"rows": 4, "dir": "ltr", "class": "json"}),
        }


class ScheduleForm(forms.Form):
    publish_at = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
                                     input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"])


class TeamMemberForm(forms.Form):
    email = forms.EmailField()
    roles = forms.ModelMultipleChoiceField(queryset=Group.objects.none(), widget=forms.CheckboxSelectMultiple, required=False)

    def __init__(self, *args, allow_owner=False, **kwargs):
        super().__init__(*args, **kwargs)
        qs = Group.objects.order_by("name")
        if not allow_owner:
            qs = qs.exclude(name="Owner")
        self.fields["roles"].queryset = qs


class DialoguePreviewForm(forms.Form):
    language = forms.ChoiceField(choices=[("en", "English"), ("ar", "العربية")])
    completed_quests = forms.MultipleChoiceField(required=False, widget=forms.SelectMultiple(attrs={"size": 5}))
    active_quests = forms.MultipleChoiceField(required=False, widget=forms.SelectMultiple(attrs={"size": 5}))
    discovered_lore = forms.MultipleChoiceField(required=False, widget=forms.SelectMultiple(attrs={"size": 5}))
    items = forms.MultipleChoiceField(required=False, widget=forms.SelectMultiple(attrs={"size": 5}))
    flags = PrettyJSONField(required=False, initial=dict, help_text='e.g. {"crown_broken": true}',
                            widget=forms.Textarea(attrs={"rows": 2, "dir": "ltr", "class": "json"}))
    page = forms.CharField(required=False, help_text="Website page context for guide lines, e.g. home")

    def __init__(self, *args, quests=(), lore=(), items=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["completed_quests"].choices = quests
        self.fields["active_quests"].choices = quests
        self.fields["discovered_lore"].choices = lore
        self.fields["items"].choices = items

    def clean_flags(self):
        value = self.cleaned_data.get("flags") or {}
        if not isinstance(value, dict):
            raise forms.ValidationError("Flags must be a JSON object.")
        return value


class TranslationImportForm(forms.Form):
    file = forms.FileField(help_text="A JSON file previously produced by Export (max 2 MB).")

    def clean_file(self):
        f = self.cleaned_data["file"]
        if f.size > 2 * 1024 * 1024:
            raise forms.ValidationError("The file is larger than 2 MB.")
        try:
            data = json.loads(f.read().decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise forms.ValidationError("The file is not valid UTF-8 JSON.") from exc
        if not isinstance(data, dict) or not isinstance(data.get("records"), list):
            raise forms.ValidationError('Expected an object with a "records" list.')
        return data
