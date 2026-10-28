from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command

User = get_user_model()
PASSWORD = "Orbit-Lantern-4410"


def seed():
    call_command("seed_astravia", verbosity=0)


def make_user(email, *roles, superuser=False):
    if superuser:
        user = User.objects.create_superuser(email=email, password=PASSWORD)
    else:
        user = User.objects.create_user(email=email, password=PASSWORD)
    for role in roles:
        user.groups.add(Group.objects.get(name=role))
    return user
