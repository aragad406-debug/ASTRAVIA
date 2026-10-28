"""Local development settings."""
from .base import *  # noqa: F401,F403
from .base import BASE_DIR, DATABASES, EMAIL_HOST, SECRET_KEY, env_bool

DEBUG = env_bool("DEBUG", True)
SECRET_KEY = SECRET_KEY or "dev-only-insecure-key-do-not-use-in-production"  # noqa: F811
SERVE_MEDIA = True

if not DATABASES:
    # Lightweight fallback. PostgreSQL is still recommended locally to match production.
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}  # noqa: F811

if not EMAIL_HOST:
    # Development only: emails (including verification links) are printed to the terminal.
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

STORAGES = {  # noqa: F811 - plain static storage so runserver works without collectstatic
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
