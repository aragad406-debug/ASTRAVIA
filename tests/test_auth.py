from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import AccountDeletionRequest
from apps.accounts.verification import make_token
from apps.core.models import AuditEvent

from .helpers import PASSWORD, User, make_user


class RegistrationTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_registration_creates_user_profile_and_sends_verification(self):
        r = self.client.post(reverse("accounts:register"), {
            "email": "New@Example.com", "display_name": "Traveller", "password1": PASSWORD, "password2": PASSWORD,
        })
        self.assertRedirects(r, reverse("accounts:profile"))
        user = User.objects.get(email="new@example.com")
        self.assertEqual(user.profile.display_name, "Traveller")
        self.assertFalse(user.email_verified)
        self.assertTrue(user.check_password(PASSWORD))
        self.assertNotEqual(user.password, PASSWORD)  # hashed
        self.assertEqual(len(mail.outbox), 1)

    def test_registration_validation(self):
        make_user("taken@example.com")
        cases = [
            {"email": "taken@example.com", "password1": PASSWORD, "password2": PASSWORD},
            {"email": "a@example.com", "password1": PASSWORD, "password2": PASSWORD + "x"},
            {"email": "b@example.com", "password1": "short", "password2": "short"},
            {"email": "not-an-email", "password1": PASSWORD, "password2": PASSWORD},
        ]
        for data in cases:
            r = self.client.post(reverse("accounts:register"), data)
            self.assertEqual(r.status_code, 200, data)
        self.assertEqual(User.objects.count(), 1)

    def test_email_verification_link(self):
        user = make_user("v@example.com")
        r = self.client.get(reverse("accounts:verify", args=[make_token(user)]))
        self.assertEqual(r.status_code, 302)
        user.refresh_from_db()
        self.assertTrue(user.email_verified)
        r = self.client.get(reverse("accounts:verify", args=["tampered"]))
        self.assertEqual(r.status_code, 302)


class LoginTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = make_user("player@example.com")

    def test_login_success_and_logout(self):
        r = self.client.post(reverse("accounts:login"), {"username": "player@example.com", "password": PASSWORD})
        self.assertRedirects(r, reverse("accounts:profile"))
        self.assertTrue(AuditEvent.objects.filter(action="login", actor=self.user).exists())
        r = self.client.post(reverse("accounts:logout"))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self.client.get(reverse("accounts:profile")).status_code, 302)

    def test_login_failure_is_generic_and_audited_without_password(self):
        r = self.client.post(reverse("accounts:login"), {"username": "player@example.com", "password": "wrong-password"})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "don&#x27;t match an account")
        event = AuditEvent.objects.get(action="login_failed")
        self.assertNotIn("wrong-password", event.summary + event.actor_label)

    def test_login_rate_limit(self):
        for _ in range(5):
            self.client.post(reverse("accounts:login"), {"username": "player@example.com", "password": "nope"})
        r = self.client.post(reverse("accounts:login"), {"username": "player@example.com", "password": PASSWORD})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Too many sign-in attempts")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_requires_post(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("accounts:logout")).status_code, 405)


class PasswordResetTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_reset_response_does_not_reveal_accounts(self):
        make_user("exists@example.com")
        r1 = self.client.post(reverse("accounts:password_reset"), {"email": "exists@example.com"})
        r2 = self.client.post(reverse("accounts:password_reset"), {"email": "nobody@example.com"})
        self.assertEqual(r1.status_code, 302)
        self.assertEqual(r1["Location"], r2["Location"])
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/accounts/password/reset/", mail.outbox[0].body)


class ProfileAndDeletionTests(TestCase):
    def setUp(self):
        self.user = make_user("p@example.com")
        self.client.force_login(self.user)

    def test_profile_update_sets_language(self):
        r = self.client.post(reverse("accounts:profile"), {"display_name": "Star", "bio": "", "preferred_language": "ar"})
        self.assertEqual(r.status_code, 302)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.preferred_language, "ar")
        self.assertEqual(r.cookies["astravia_lang"].value, "ar")

    def test_deletion_request_requires_password(self):
        self.client.post(reverse("accounts:request_deletion"), {"password": "wrong"})
        self.assertFalse(AccountDeletionRequest.objects.exists())
        self.client.post(reverse("accounts:request_deletion"), {"password": PASSWORD, "reason": "Bye"})
        self.assertEqual(AccountDeletionRequest.objects.filter(user=self.user, status="pending").count(), 1)
