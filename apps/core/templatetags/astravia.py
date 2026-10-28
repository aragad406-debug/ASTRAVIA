from urllib.parse import urlencode

from django import template
from django.conf import settings
from django.utils.html import format_html

from apps.core.ui import ui as ui_lookup

register = template.Library()


@register.simple_tag
def ui(key, **fmt):
    """{% ui "nav.worlds" %} — interface text in the active language (studio-overridable)."""
    return ui_lookup(key, **fmt)


@register.filter
def loc(obj, field):
    """{{ world|loc:"name" }} — localized model field with English fallback."""
    if obj is None:
        return ""
    if hasattr(obj, "loc"):
        return obj.loc(field)
    return getattr(obj, field, "")


@register.filter
def loc_lang(obj, field):
    """Returns the language code the text was actually served in (for lang="" attributes on fallbacks)."""
    from apps.core.text import current_language

    lang = current_language()
    if getattr(obj, f"{field}_{lang}", ""):
        return lang
    return "en" if getattr(obj, f"{field}_en", "") else "ar"


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    """Keep current query parameters while changing some (pagination, filters)."""
    request = context["request"]
    params = request.GET.copy()
    for key, value in kwargs.items():
        if value in (None, ""):
            params.pop(key, None)
        else:
            params[key] = value
    return urlencode(params, doseq=True)


@register.simple_tag(takes_context=True)
def absolute_url(context, path=""):
    request = context.get("request")
    base = settings.SITE_URL
    if not base and request is not None:
        base = f"{request.scheme}://{request.get_host()}"
    return f"{base}{path}"


@register.simple_tag
def status_badge(obj):
    status = getattr(obj, "status", "")
    label = obj.get_status_display() if hasattr(obj, "get_status_display") else status
    return format_html('<span class="badge badge--{}">{}</span>', status, label)


@register.filter
def get_item(mapping, key):
    try:
        return mapping.get(key)
    except AttributeError:
        return None


@register.filter
def field_value(obj, name):
    """Display value for a model field in studio lists."""
    getter = getattr(obj, f"get_{name}_display", None)
    if callable(getter):
        return getter()
    value = getattr(obj, name, "")
    if callable(value):
        value = value()
    if value is True:
        return "✓"
    if value is False or value is None:
        return "—"
    return value


@register.filter
def initials(text):
    parts = [p for p in str(text or "").split() if p]
    return "".join(p[0] for p in parts[:2]).upper() or "?"
