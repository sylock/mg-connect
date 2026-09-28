import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class AchievementCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.SlugField(unique=True, max_length=64)
    label = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["label"]
        verbose_name_plural = "achievement categories"

    def __str__(self) -> str:
        return self.label


class Achievement(models.Model):
    class State(models.TextChoices):
        PENDING = "pending", _("En attente")
        APPROVED = "approved", _("Accepté")
        REJECTED = "rejected", _("Refusé")
        VOIDED = "voided", _("Annulé")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.PROTECT,
        related_name="achievements",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="achievements_created",
    )
    category = models.ForeignKey(
        AchievementCategory,
        on_delete=models.PROTECT,
        related_name="achievements",
    )
    occurred_on = models.DateField()
    state = models.CharField(
        max_length=20,
        choices=State.choices,
        default=State.PENDING,
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="achievements_reviewed",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True)
    revision = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-occurred_on", "-created_at"]

    def __str__(self) -> str:
        return f"{self.category.code} {self.occurred_on} ({self.state})"


class Evidence(models.Model):
    class Kind(models.TextChoices):
        URL = "url", _("Lien")
        IMAGE = "image", _("Image")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name="evidence_items",
    )
    kind = models.CharField(max_length=16, choices=Kind.choices)
    safe_url = models.URLField(blank=True, max_length=2000)
    storage_key = models.CharField(blank=True, max_length=255)
    mime_type = models.CharField(blank=True, max_length=100)
    size_bytes = models.PositiveIntegerField(default=0)
    original_label = models.CharField(blank=True, max_length=255)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="evidence_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    superseded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name_plural = "evidence"

    def __str__(self) -> str:
        return f"{self.kind}:{self.pk}"
