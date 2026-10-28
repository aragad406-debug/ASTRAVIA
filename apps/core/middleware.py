from django.conf import settings
from django.utils import translation


class QueryLanguageMiddleware:
    """`?lang=ar` / `?lang=en` switches language for the request and remembers it in a cookie.

    Runs before LocaleMiddleware, which then reads the cookie on later requests.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.valid = {code for code, _ in settings.LANGUAGES}

    def __call__(self, request):
        lang = request.GET.get("lang")
        if lang in self.valid:
            request.COOKIES[settings.LANGUAGE_COOKIE_NAME] = lang
            translation.activate(lang)
        response = self.get_response(request)
        if lang in self.valid:
            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME, lang, max_age=settings.LANGUAGE_COOKIE_AGE,
                samesite=settings.LANGUAGE_COOKIE_SAMESITE, secure=getattr(settings, "LANGUAGE_COOKIE_SECURE", False),
            )
        return response


class SecurityHeadersMiddleware:
    """Content-Security-Policy, Permissions-Policy, and no-index for private areas."""

    PRIVATE_PREFIXES = ("/creator-studio/", "/accounts/", "/admin/", "/api/")

    def __init__(self, get_response):
        self.get_response = get_response
        media_src = "'self' https: blob:" if settings.MEDIA_STORAGE == "s3" else "'self' blob:"
        self.csp = "; ".join([
            "default-src 'self'",
            "script-src 'self'",
            # Inline style attributes carry validated hex theme colours (--world-*). No inline scripts are allowed.
            "style-src 'self' 'unsafe-inline'",
            f"img-src 'self' data: {media_src}",
            f"media-src {media_src}",
            "font-src 'self'",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "object-src 'none'",
        ])

    def __call__(self, request):
        response = self.get_response(request)
        if "text/html" not in response.get("Content-Type", "") or request.path.startswith(("/api/", "/admin/")):
            # Non-HTML responses need no script policy; the Django admin and DRF's browsable API ship inline scripts.
            response.headers.setdefault("Content-Security-Policy", "frame-ancestors 'none'; object-src 'none'; base-uri 'self'")
        else:
            response.headers.setdefault("Content-Security-Policy", self.csp)
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()")
        if request.path.startswith(self.PRIVATE_PREFIXES):
            response.headers["X-Robots-Tag"] = "noindex, nofollow"
            response.headers.setdefault("Cache-Control", "private, no-store")
        return response
