def studio(request):
    """Studio navigation, only computed for studio pages."""
    if not request.path.startswith("/creator-studio/") or not request.user.is_authenticated:
        return {}
    from .views_content import nav_context

    return {"studio_nav": nav_context(request.user)}
