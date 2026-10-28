from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from apps.core.models import TimeStampedModel


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError("An email address is required.")
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("email_verified", True)
        if not extra["is_staff"] or not extra["is_superuser"]:
            raise ValueError("Superusers need is_staff and is_superuser.")
        return self._create_user(email, password, **extra)


class User(AbstractUser):
    """Email-based account. Usernames are not used."""

    username = None
    email = models.EmailField("email address", unique=True)
    email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ["email"]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

    @property
    def display_name(self):
        profile = getattr(self, "profile", None)
        return (profile.display_name if profile and profile.display_name else "") or self.email.split("@")[0]


def avatar_path(instance, filename):
    import uuid

    return f"avatars/{uuid.uuid4().hex}.img"


class UserProfile(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(max_length=60, blank=True)
    bio = models.CharField(max_length=300, blank=True)
    preferred_language = models.CharField(max_length=5, choices=settings.LANGUAGES, default="en")
    avatar = models.FileField(upload_to=avatar_path, blank=True)
    show_public_profile = models.BooleanField(default=False)
    receive_news_emails = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile of {self.user}"


class AccountDeletionRequest(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="deletion_requests")
    email_snapshot = models.EmailField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user"], condition=models.Q(status="pending"), name="one_pending_deletion_per_user")
        ]

    def __str__(self):
        return f"Deletion request: {self.email_snapshot} ({self.status})"
