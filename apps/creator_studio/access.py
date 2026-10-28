"""Studio access control. Every studio view is wrapped; hiding a button is never the only check."""
from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.urls import reverse


def studio_required(*perms):
    """Require sign-in, `core.access_studio`, and every permission listed (callables get the request)."""

    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path(), reverse("creator_studio:login"))
            if not request.user.is_active or not request.user.has_perm("core.access_studio"):
                return render(request, "creator_studio/denied.html", status=403)
            for perm in perms:
                required = perm(request, *args, **kwargs) if callable(perm) else perm
                if required and not request.user.has_perm(required):
                    raise PermissionDenied
            return view(request, *args, **kwargs)

        return wrapper

    return decorator
