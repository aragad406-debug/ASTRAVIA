"""Production settings (Render). Every secret comes from the environment."""
from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403
from .base import DATABASES, EMAIL_HOST, SECRET_KEY, env, env_bool

DEBUG = env_bool("DEBUG", False)

if not SECRET_KEY or SECRET_KEY.startswith("replace-") or len(SECRET_KEY) < 40:
    raise ImproperlyConfigured("SECRET_KEY must be set to a long random value in production.")
if not DATABASES:
    raise ImproperlyConfigured("DATABASE_URL must be set in production (PostgreSQL).")

# Render terminates TLS at its proxy.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
SECURE_REDIRECT_EXEMPT = [r"^healthz/$"]
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
LANGUAGE_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = int(env("SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", False)
SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", False)
# includeSubDomains and preload are opt-in once a custom domain is confirmed HTTPS-only (see docs/SECURITY.md).
SILENCED_SYSTEM_CHECKS = [c for c, on in (("security.W005", SECURE_HSTS_INCLUDE_SUBDOMAINS), ("security.W021", SECURE_HSTS_PRELOAD)) if not on]

# Render provides RENDER_EXTERNAL_HOSTNAME automatically.
_render_host = env("RENDER_EXTERNAL_HOSTNAME")
if _render_host:
    ALLOWED_HOSTS.append(_render_host)  # noqa: F405
    CSRF_TRUSTED_ORIGINS.append(f"https://{_render_host}")  # noqa: F405

# Shared cache across gunicorn workers (table created by `createcachetable` in build.sh).
CACHES = {"default": {"BACKEND": "django.core.cache.backends.db.DatabaseCache", "LOCATION": "astravia_cache"}}  # noqa: F811

if not EMAIL_HOST:
    # No provider configured: never print emails (and their tokens) to production logs.
    EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

LOGGING["root"]["level"] = env("LOG_LEVEL", "INFO")  # noqa: F405
