from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from accounts.models import Employee
from achievements.evidence import MAX_IMAGES, store_image_evidence, validate_proof_url
from achievements.models import Achievement, AchievementCategory, Evidence
from audit.services import (
    IdempotencyConflict,
    begin_idempotent,
    record_audit,
    store_receipt,
)


class StaleRevisionError(ValidationError):
    pass


@dataclass
class AchievementDraft:
    employee: Employee
    category: AchievementCategory
    occurred_on: date
    proof_urls: list[str] = field(default_factory=list)
    image_uploads: list[Any] = field(default_factory=list)
    idempotency_token: str = ""


def _achievement_snapshot(achievement: Achievement) -> dict:
    return {
        "employee_id": str(achievement.employee_id),
        "category_id": str(achievement.category_id),
        "occurred_on": str(achievement.occurred_on),
        "state": achievement.state,
        "revision": achievement.revision,
        "review_note": achievement.review_note,
    }


def _resolve_initial_state(*, actor, employee: Employee) -> str:
    actor_is_manager = bool(getattr(actor, "is_manager", False))
    beneficiary_user_id = employee.user_id
    if actor_is_manager and beneficiary_user_id and beneficiary_user_id != actor.pk:
        return Achievement.State.APPROVED
    return Achievement.State.PENDING


def _attach_evidence(*, achievement: Achievement, actor, urls: list[str], uploads) -> None:
    cleaned_urls = []
    for raw in urls:
        raw = (raw or "").strip()
        if raw:
            cleaned_urls.append(validate_proof_url(raw))
    uploads = [u for u in uploads if u]
    if not cleaned_urls and not uploads:
        raise ValidationError("Ajoutez au moins un lien ou une image de preuve.")
    if len(uploads) > MAX_IMAGES:
        raise ValidationError(f"Maximum {MAX_IMAGES} images.")

    for url in cleaned_urls:
        Evidence.objects.create(
            achievement=achievement,
            kind=Evidence.Kind.URL,
            safe_url=url,
            created_by=actor,
        )
    for upload in uploads:
        key, mime, size, label = store_image_evidence(upload)
        Evidence.objects.create(
            achievement=achievement,
            kind=Evidence.Kind.IMAGE,
            storage_key=key,
            mime_type=mime,
            size_bytes=size,
            original_label=label,
            created_by=actor,
        )


@transaction.atomic
def submit_achievement(*, actor, draft: AchievementDraft) -> Achievement:
    if draft.occurred_on > timezone.localdate():
        raise ValidationError("La date du succès ne peut pas être dans le futur.")
    if not draft.category.is_active:
        raise ValidationError("Cette catégorie n’est plus active.")

    payload = {
        "employee": str(draft.employee.pk),
        "category": str(draft.category.pk),
        "occurred_on": str(draft.occurred_on),
        "urls": draft.proof_urls,
        "image_names": [getattr(u, "name", "") for u in draft.image_uploads],
    }
    token = draft.idempotency_token or ""
    if token:
        existing, ref = begin_idempotent(
            actor=actor, action="achievement.submit", token=token, payload=payload
        )
        if existing and ref:
            return Achievement.objects.get(pk=ref)

    state = _resolve_initial_state(actor=actor, employee=draft.employee)
    achievement = Achievement.objects.create(
        employee=draft.employee,
        created_by=actor,
        category=draft.category,
        occurred_on=draft.occurred_on,
        state=state,
        revision=1,
    )
    if state == Achievement.State.APPROVED:
        achievement.reviewed_by = actor
        achievement.reviewed_at = timezone.now()
        achievement.save(update_fields=["reviewed_by", "reviewed_at"])

    _attach_evidence(
        achievement=achievement,
        actor=actor,
        urls=draft.proof_urls,
        uploads=draft.image_uploads,
    )

    record_audit(
        actor=actor,
        entity_type="achievement",
        entity_id=str(achievement.pk),
        operation="submit",
        after=_achievement_snapshot(achievement),
    )
    if token:
        store_receipt(
            actor=actor,
            action="achievement.submit",
            token=token,
            payload=payload,
            result_reference=str(achievement.pk),
        )
    return achievement


@transaction.atomic
def decide_achievement(
    *,
    actor,
    achievement: Achievement,
    approve: bool,
    expected_revision: int,
    note: str = "",
) -> Achievement:
    if not getattr(actor, "is_manager", False):
        raise ValidationError("Réservé aux gérants.")
    achievement = Achievement.objects.select_for_update().get(pk=achievement.pk)
    if achievement.revision != expected_revision:
        raise StaleRevisionError("Cette demande a déjà été mise à jour. Rechargez la page.")
    if achievement.state != Achievement.State.PENDING:
        raise ValidationError("Seules les demandes en attente peuvent être tranchées.")
    if not approve and not (note or "").strip():
        raise ValidationError("Une explication est obligatoire en cas de refus.")

    before = _achievement_snapshot(achievement)
    achievement.state = Achievement.State.APPROVED if approve else Achievement.State.REJECTED
    achievement.reviewed_by = actor
    achievement.reviewed_at = timezone.now()
    achievement.review_note = (note or "").strip()
    achievement.revision += 1
    achievement.save()
    record_audit(
        actor=actor,
        entity_type="achievement",
        entity_id=str(achievement.pk),
        operation="approve" if approve else "reject",
        before=before,
        after=_achievement_snapshot(achievement),
        reason=achievement.review_note,
    )
    return achievement


@transaction.atomic
def void_achievement(
    *,
    actor,
    achievement: Achievement,
    expected_revision: int,
    reason: str,
) -> Achievement:
    if not getattr(actor, "is_manager", False):
        raise ValidationError("Réservé aux gérants.")
    if not (reason or "").strip():
        raise ValidationError("Un motif est obligatoire pour annuler un succès.")
    achievement = Achievement.objects.select_for_update().get(pk=achievement.pk)
    if achievement.revision != expected_revision:
        raise StaleRevisionError("Cette fiche a déjà été mise à jour. Rechargez la page.")
    if achievement.state == Achievement.State.VOIDED:
        raise ValidationError("Ce succès est déjà annulé.")
    before = _achievement_snapshot(achievement)
    achievement.state = Achievement.State.VOIDED
    achievement.review_note = reason.strip()
    achievement.reviewed_by = actor
    achievement.reviewed_at = timezone.now()
    achievement.revision += 1
    achievement.save()
    record_audit(
        actor=actor,
        entity_type="achievement",
        entity_id=str(achievement.pk),
        operation="void",
        before=before,
        after=_achievement_snapshot(achievement),
        reason=reason.strip(),
    )
    return achievement


@transaction.atomic
def correct_achievement(
    *,
    actor,
    achievement: Achievement,
    expected_revision: int,
    reason: str,
    category: AchievementCategory | None = None,
    occurred_on: date | None = None,
) -> Achievement:
    if not getattr(actor, "is_manager", False):
        raise ValidationError("Réservé aux gérants.")
    if not (reason or "").strip():
        raise ValidationError("Un motif de correction est obligatoire.")
    achievement = Achievement.objects.select_for_update().get(pk=achievement.pk)
    if achievement.revision != expected_revision:
        raise StaleRevisionError("Cette fiche a déjà été mise à jour. Rechargez la page.")
    if achievement.state not in {Achievement.State.APPROVED, Achievement.State.PENDING}:
        raise ValidationError("Correction impossible pour cet état.")
    if occurred_on and occurred_on > timezone.localdate():
        raise ValidationError("La date du succès ne peut pas être dans le futur.")

    before = _achievement_snapshot(achievement)
    if category is not None:
        achievement.category = category
    if occurred_on is not None:
        achievement.occurred_on = occurred_on
    achievement.revision += 1
    achievement.save()
    record_audit(
        actor=actor,
        entity_type="achievement",
        entity_id=str(achievement.pk),
        operation="correct",
        before=before,
        after=_achievement_snapshot(achievement),
        reason=reason.strip(),
    )
    return achievement


def count_approved(*, employee: Employee | None, date_from: date | None, date_to: date | None) -> dict[str, int]:
    qs = Achievement.objects.filter(state=Achievement.State.APPROVED)
    if employee is not None:
        qs = qs.filter(employee=employee)
    if date_from is not None:
        qs = qs.filter(occurred_on__gte=date_from)
    if date_to is not None:
        qs = qs.filter(occurred_on__lte=date_to)
    totals: dict[str, int] = {}
    for row in qs.values_list("category__code", flat=True):
        totals[row] = totals.get(row, 0) + 1
    return totals


def user_can_view_evidence(*, user, evidence: Evidence) -> bool:
    if not user.is_authenticated:
        return False
    if getattr(user, "is_manager", False):
        return True
    beneficiary = evidence.achievement.employee
    return beneficiary.user_id == user.pk
