import os
import subprocess
import sys
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import TestCase, override_settings

BASE = Path(settings.BASE_DIR)


def run_python(code, env):
    full_env = {**os.environ, **env}
    return subprocess.run([sys.executable, "-c", code], cwd=BASE, env=full_env, capture_output=True, text=True, timeout=120)


class ProductionSettingsTests(TestCase):
    def test_production_refuses_weak_secret(self):
        r = run_python("import django,os;os.environ['DJANGO_SETTINGS_MODULE']='config.settings.production';django.setup()",
                       {"SECRET_KEY": "short", "DATABASE_URL": "postgres://u:p@localhost/db"})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("SECRET_KEY", r.stderr)

    def test_production_requires_database(self):
        r = run_python("import django,os;os.environ['DJANGO_SETTINGS_MODULE']='config.settings.production';django.setup()",
                       {"SECRET_KEY": "x" * 60, "DATABASE_URL": ""})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("DATABASE_URL", r.stderr)

    def test_production_security_settings_and_deploy_check(self):
        code = (
            "import django,os;os.environ['DJANGO_SETTINGS_MODULE']='config.settings.production';django.setup();"
            "from django.conf import settings as s;"
            "assert not s.DEBUG and s.SESSION_COOKIE_SECURE and s.CSRF_COOKIE_SECURE and s.SECURE_SSL_REDIRECT;"
            "assert s.SECURE_HSTS_SECONDS>0 and 'example.onrender.com' in s.ALLOWED_HOSTS;"
            "assert s.DATABASES['default']['ENGINE']=='django.db.backends.postgresql';"
            "from django.core.management import call_command; call_command('check','--deploy','--fail-level','WARNING')"
        )
        r = run_python(code, {"SECRET_KEY": "k" * 64 + "Zz9!", "DATABASE_URL": "postgres://u:p@localhost:5432/db",
                              "RENDER_EXTERNAL_HOSTNAME": "example.onrender.com", "DEBUG": "False", "ALLOWED_HOSTS": ""})
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])

    def test_collectstatic(self):
        out = BASE / "staticfiles_test"
        code = (
            "import django,os;os.environ['DJANGO_SETTINGS_MODULE']='config.settings.production';django.setup();"
            "from django.core.management import call_command; call_command('collectstatic','--noinput','-v','0')"
        )
        try:
            r = run_python(code + "", {"SECRET_KEY": "k" * 64, "DATABASE_URL": "postgres://u:p@localhost:5432/db",
                                       "DJANGO_STATIC_ROOT_OVERRIDE": str(out)})
            self.assertEqual(r.returncode, 0, r.stderr[-2000:])
            self.assertTrue((BASE / "staticfiles" / "staticfiles.json").exists())
        finally:
            pass


class HealthAndSeoTests(TestCase):
    def test_health_ok(self):
        r = self.client.get("/healthz/")
        self.assertEqual(r.json(), {"status": "ok", "database": "ok"})

    def test_health_reports_database_failure(self):
        with mock.patch("apps.core.views.connection.cursor", side_effect=Exception("down")):
            r = self.client.get("/healthz/")
        self.assertEqual(r.status_code, 503)

    def test_robots_blocks_private_areas(self):
        body = self.client.get("/robots.txt").content.decode()
        for path in ("/creator-studio/", "/accounts/", "/api/"):
            self.assertIn(f"Disallow: {path}", body)

    def test_security_headers(self):
        r = self.client.get("/")
        self.assertIn("script-src 'self'", r["Content-Security-Policy"])
        self.assertEqual(r["X-Frame-Options"], "DENY")
        r = self.client.get("/creator-studio/login/")
        self.assertEqual(r["X-Robots-Tag"], "noindex, nofollow")

    def test_rtl_layout(self):
        r = self.client.get("/?lang=ar")
        self.assertContains(r, '<html lang="ar" dir="rtl"')
        r = self.client.get("/")  # remembered by cookie
        self.assertContains(r, 'dir="rtl"')
        r = self.client.get("/?lang=en")
        self.assertContains(r, '<html lang="en" dir="ltr"')

    @override_settings(DEBUG=False)
    def test_custom_404(self):
        r = self.client.get("/no-such-page/")
        self.assertEqual(r.status_code, 404)
        self.assertContains(r, "star chart", status_code=404)
