"""Create (or promote) the studio Owner account.

    python manage.py create_owner                      # interactive prompts
    python manage.py create_owner --from-env           # ASTRAVIA_OWNER_EMAIL / ASTRAVIA_OWNER_PASSWORD

There is deliberately no web route for creating an owner.
"""
import getpass
import os

from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email

from apps.core import audit


class Command(BaseCommand):
    help = "Create the ASTRAVIA Creator Studio owner account securely."

    def add_arguments(self, parser):
        parser.add_argument("--from-env", action="store_true", help="Read ASTRAVIA_OWNER_EMAIL and ASTRAVIA_OWNER_PASSWORD.")
        parser.add_argument("--email", help="Owner email (password is prompted).")

    def handle(self, *args, **opts):
        User = get_user_model()
        if opts["from_env"]:
            email = (os.environ.get("ASTRAVIA_OWNER_EMAIL") or "").strip()
            password = os.environ.get("ASTRAVIA_OWNER_PASSWORD") or ""
            if not email or not password:
                raise CommandError("Set ASTRAVIA_OWNER_EMAIL and ASTRAVIA_OWNER_PASSWORD, or run without --from-env.")
        else:
            email = (opts.get("email") or input("Owner email: ")).strip()
            password = getpass.getpass("Password: ")
            if password != getpass.getpass("Password (again): "):
                raise CommandError("Passwords do not match.")
        try:
            validate_email(email)
        except ValidationError as exc:
            raise CommandError("Enter a valid email address.") from exc

        user = User.objects.filter(email__iexact=email).first()
        try:
            password_validation.validate_password(password, user or User(email=email))
        except ValidationError as exc:
            raise CommandError(" ".join(exc.messages)) from exc

        if user is None:
            user = User.objects.create_superuser(email=email, password=password)
            action = "created"
        else:
            user.is_staff = user.is_superuser = True
            user.email_verified = True
            user.set_password(password)
            user.save()
            action = "promoted"
        owner_group, _ = Group.objects.get_or_create(name="Owner")
        user.groups.add(owner_group)
        audit.record("owner_" + action, actor_label="manage.py", target=user, summary=f"Owner account {action}")
        self.stdout.write(self.style.SUCCESS(f"Owner account {action}: {email}"))
