"""Email verification links signed with SECRET_KEY (no tokens stored in the database)."""
from django.conf import settings
from django.core import signing
from django.core.mail import send_mail
from django.urls import reverse

SALT = "astravia.email-verification"
MAX_AGE = 60 * 60 * 24 * 3


def make_token(user):
    return signing.dumps({"uid": user.pk, "email": user.email}, salt=SALT)


def read_token(token):
    try:
        data = signing.loads(token, salt=SALT, max_age=MAX_AGE)
    except signing.BadSignature:
        return None
    return data


def send_verification(request, user):
    """Send the link. Returns False when no email provider is configured in production."""
    url = request.build_absolute_uri(reverse("accounts:verify", args=[make_token(user)]))
    body = (
        "Confirm your ASTRAVIA account email address by opening this link (valid for 3 days):\n\n"
        f"{url}\n\nIf you didn't create an account, ignore this message.\n\n"
        "أكّد بريدك الإلكتروني لحساب أسترافيا بفتح الرابط أعلاه (صالح لمدة 3 أيام)."
    )
    send_mail("Confirm your ASTRAVIA email", body, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)
    return settings.EMAIL_CONFIGURED or settings.DEBUG
