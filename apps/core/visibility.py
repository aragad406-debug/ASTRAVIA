"""Public/preview access rules shared by all public views."""
from django.http import Http404

from .models import Visibility


def can_preview(user, model):
    meta = model._meta
    return (
        user.is_authenticated
        and user.has_perm("core.access_studio")
        and user.has_perm(f"{meta.app_label}.view_{meta.model_name}")
    )


def public_queryset(request, model):
    return model.objects.visible_to(request.user)


def get_for_request(request, queryset, **lookup):
    """Return a published, visible object — or, for studio members with `?preview=1`, any object.

    Sets request.is_preview so templates can show a preview banner. Raises Http404 otherwise,
    so unpublished or hidden content is indistinguishable from content that does not exist.
    """
    model = queryset.model
    request.is_preview = False
    if request.GET.get("preview") == "1" and can_preview(request.user, model):
        obj = model.objects.filter(**lookup).first()
        if obj is None:
            raise Http404
        request.is_preview = not getattr(obj, "is_live", True)
        return obj
    obj = queryset.visible_to(request.user).filter(**lookup).first() if hasattr(queryset, "visible_to") else queryset.filter(**lookup).first()
    if obj is None:
        raise Http404
    return obj


def is_teaser(obj):
    return getattr(obj, "visibility", "") == Visibility.TEASER
