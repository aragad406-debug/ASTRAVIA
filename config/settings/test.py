"""Settings for the automated test suite. Uses DATABASE_URL (PostgreSQL) when set, otherwise SQLite."""
from .base import *  # noqa: F401,F403
from .base import BASE_DIR, DATABASES

DEBUG = False
SECRET_KEY = "test-secret-key-not-for-production-use-0123456789abcdef"
if not DATABASES:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "test.sqlite3"}}  # noqa: F811
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]  # speed only; never in production
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
STORAGES = {  # noqa: F811
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
REST_FRAMEWORK = {**REST_FRAMEWORK, "DEFAULT_THROTTLE_RATES": {"anon": "10000/minute", "user": "10000/minute"}}  # noqa: F405
