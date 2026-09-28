from __future__ import annotations

import hashlib
import json
from typing import Any

from django.db import transaction

from audit.models import AuditEvent, MutationReceipt


def record_audit(
    *,
    actor,
    entity_type: str,
    entity_id: str,
    operation: str,
    before: dict | None = None,
    after: dict | None = None,
    reason: str = "",
    correlation_id=None,
) -> AuditEvent:
    return AuditEvent.objects.create(
        actor=actor,
        entity_type=entity_type,
        entity_id=str(entity_id),
        operation=operation,
        before=before,
        after=after,
        reason=reason,
        correlation_id=correlation_id,
    )


def hash_payload(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class IdempotencyConflict(Exception):
    """Same token reused with a different payload."""


@transaction.atomic
def begin_idempotent(*, actor, action: str, token: str, payload: dict) -> tuple[MutationReceipt | None, str | None]:
    """
    Returns (None, existing_result_ref) if token already succeeded,
    or (new_receipt_placeholder_unused, None) to proceed — caller must finalize.

    Simpler API: check_or_reserve returns existing Achievement id or None to proceed.
    """
    request_hash = hash_payload(payload)
    existing = (
        MutationReceipt.objects.select_for_update()
        .filter(actor=actor, action=action, token=token)
        .first()
    )
    if existing:
        if existing.request_hash != request_hash:
            raise IdempotencyConflict("Jeton d’idempotence réutilisé avec un autre contenu.")
        return existing, existing.result_reference
    return None, None


@transaction.atomic
def store_receipt(*, actor, action: str, token: str, payload: dict, result_reference: str) -> MutationReceipt:
    request_hash = hash_payload(payload)
    return MutationReceipt.objects.create(
        actor=actor,
        action=action,
        token=token,
        request_hash=request_hash,
        result_reference=result_reference,
    )
