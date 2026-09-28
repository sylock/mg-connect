import uuid

from django.conf import settings
from django.db import models


class AuditEvent(models.Model):
    """Append-only audit trail (writers added with domain mutations)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    entity_type = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=64)
    operation = models.CharField(max_length=64)
    before = models.JSONField(null=True, blank=True)
    after = models.JSONField(null=True, blank=True)
    reason = models.TextField(blank=True)
    correlation_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.operation} {self.entity_type}:{self.entity_id}"


class MutationReceipt(models.Model):
    """Idempotency receipts for user mutations."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mutation_receipts",
    )
    action = models.CharField(max_length=64)
    token = models.CharField(max_length=128)
    request_hash = models.CharField(max_length=64)
    result_reference = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["actor", "action", "token"],
                name="uniq_mutation_actor_action_token",
            )
        ]

    def __str__(self) -> str:
        return f"{self.action}:{self.token}"
