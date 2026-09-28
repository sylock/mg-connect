from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import FileResponse, Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods

from accounts.models import Employee
from accounts.permissions import manager_required
from achievements.evidence import private_media_path
from achievements.forms import (
    AchievementSubmitForm,
    CorrectForm,
    ReasonForm,
    RejectForm,
    ReviewForm,
)
from achievements.models import Achievement, Evidence
from achievements.services import (
    AchievementDraft,
    StaleRevisionError,
    correct_achievement,
    count_approved,
    decide_achievement,
    submit_achievement,
    user_can_view_evidence,
    void_achievement,
)
from audit.services import IdempotencyConflict


def _employee_for_user(user) -> Employee | None:
    return getattr(user, "employee_profile", None)


@login_required
@require_http_methods(["GET"])
def achievement_list(request: HttpRequest) -> HttpResponse:
    qs = Achievement.objects.select_related(
        "employee", "category", "created_by", "reviewed_by"
    )
    if not request.user.is_manager:
        emp = _employee_for_user(request.user)
        if emp is None:
            qs = qs.none()
        else:
            qs = qs.filter(employee=emp)

    year = request.GET.get("year")
    month = request.GET.get("month")
    date_from = date_to = None
    try:
        if year and month:
            y, m = int(year), int(month)
            date_from = date(y, m, 1)
            if m == 12:
                date_to = date(y + 1, 1, 1)
            else:
                date_to = date(y, m + 1, 1)
            # inclusive end = day before next month
            from datetime import timedelta

            date_to = date_to - timedelta(days=1)
        elif year:
            y = int(year)
            date_from, date_to = date(y, 1, 1), date(y, 12, 31)
    except ValueError:
        date_from = date_to = None

    if date_from and date_to:
        qs = qs.filter(occurred_on__gte=date_from, occurred_on__lte=date_to)

    counts = count_approved(
        employee=None if request.user.is_manager else _employee_for_user(request.user),
        date_from=date_from,
        date_to=date_to,
    )
    return render(
        request,
        "achievements/list.html",
        {
            "page_title": "Succès",
            "achievements": qs[:200],
            "counts": counts,
            "filter_year": year or "",
            "filter_month": month or "",
            "generated_at": timezone.now(),
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def achievement_create(request: HttpRequest) -> HttpResponse:
    form = AchievementSubmitForm(request.POST or None, request.FILES or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        emp = form.cleaned_data.get("beneficiary")
        if request.user.is_manager and emp is not None:
            beneficiary = emp
        else:
            beneficiary = _employee_for_user(request.user)
            if beneficiary is None:
                form.add_error(None, "Aucun profil employé lié à votre compte.")
                beneficiary = None
        if beneficiary is not None:
            images = request.FILES.getlist("images") or form.cleaned_data.get("images") or []
            urls = [
                form.cleaned_data.get("proof_url") or "",
                form.cleaned_data.get("proof_url_2") or "",
            ]
            try:
                submit_achievement(
                    actor=request.user,
                    draft=AchievementDraft(
                        employee=beneficiary,
                        category=form.cleaned_data["category"],
                        occurred_on=form.cleaned_data["occurred_on"],
                        proof_urls=urls,
                        image_uploads=images,
                        idempotency_token=form.cleaned_data.get("idempotency_token") or "",
                    ),
                )
            except IdempotencyConflict as exc:
                form.add_error(None, str(exc))
            except ValidationError as exc:
                form.add_error(None, exc.messages[0] if getattr(exc, "messages", None) else str(exc))
            else:
                messages.success(request, "Succès enregistré.")
                return redirect("achievements:list")
    return render(
        request,
        "achievements/form.html",
        {"page_title": "Déclarer un succès", "form": form},
    )


@login_required
@require_http_methods(["GET"])
def achievement_detail(request: HttpRequest, pk) -> HttpResponse:
    achievement = get_object_or_404(
        Achievement.objects.select_related("employee", "category", "created_by"),
        pk=pk,
    )
    if not request.user.is_manager:
        emp = _employee_for_user(request.user)
        if emp is None or achievement.employee_id != emp.pk:
            raise Http404()
    evidence = achievement.evidence_items.filter(superseded_at__isnull=True)
    return render(
        request,
        "achievements/detail.html",
        {
            "page_title": "Détail du succès",
            "achievement": achievement,
            "evidence_items": evidence,
            "approve_form": ReviewForm(initial={"expected_revision": achievement.revision}),
            "reject_form": RejectForm(initial={"expected_revision": achievement.revision}),
            "void_form": ReasonForm(initial={"expected_revision": achievement.revision}),
            "correct_form": CorrectForm(
                initial={
                    "expected_revision": achievement.revision,
                    "category": achievement.category_id,
                    "occurred_on": achievement.occurred_on,
                }
            ),
        },
    )


def _manager_decision(request, pk, approve: bool):
    achievement = get_object_or_404(Achievement, pk=pk)
    form_cls = ReviewForm if approve else RejectForm
    form = form_cls(request.POST)
    if not form.is_valid():
        messages.error(request, "Formulaire invalide.")
        return redirect("achievements:detail", pk=pk)
    try:
        decide_achievement(
            actor=request.user,
            achievement=achievement,
            approve=approve,
            expected_revision=form.cleaned_data["expected_revision"],
            note=form.cleaned_data.get("note") or "",
        )
    except StaleRevisionError:
        messages.error(request, "Conflit : rechargez la page.")
        return HttpResponse(status=409)
    except ValidationError as exc:
        messages.error(request, exc.messages[0] if exc.messages else str(exc))
    else:
        messages.success(request, "Décision enregistrée.")
    return redirect("achievements:detail", pk=pk)


@manager_required
@require_http_methods(["POST"])
def achievement_approve(request: HttpRequest, pk) -> HttpResponse:
    return _manager_decision(request, pk, approve=True)


@manager_required
@require_http_methods(["POST"])
def achievement_reject(request: HttpRequest, pk) -> HttpResponse:
    return _manager_decision(request, pk, approve=False)


@manager_required
@require_http_methods(["POST"])
def achievement_void(request: HttpRequest, pk) -> HttpResponse:
    achievement = get_object_or_404(Achievement, pk=pk)
    form = ReasonForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Motif requis.")
        return redirect("achievements:detail", pk=pk)
    try:
        void_achievement(
            actor=request.user,
            achievement=achievement,
            expected_revision=form.cleaned_data["expected_revision"],
            reason=form.cleaned_data["reason"],
        )
    except StaleRevisionError:
        messages.error(request, "Conflit : rechargez la page.")
        return HttpResponse(status=409)
    except ValidationError as exc:
        messages.error(request, exc.messages[0] if exc.messages else str(exc))
    else:
        messages.success(request, "Succès annulé.")
    return redirect("achievements:detail", pk=pk)


@manager_required
@require_http_methods(["POST"])
def achievement_correct(request: HttpRequest, pk) -> HttpResponse:
    achievement = get_object_or_404(Achievement, pk=pk)
    form = CorrectForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Correction invalide.")
        return redirect("achievements:detail", pk=pk)
    try:
        correct_achievement(
            actor=request.user,
            achievement=achievement,
            expected_revision=form.cleaned_data["expected_revision"],
            reason=form.cleaned_data["reason"],
            category=form.cleaned_data.get("category"),
            occurred_on=form.cleaned_data.get("occurred_on"),
        )
    except StaleRevisionError:
        messages.error(request, "Conflit : rechargez la page.")
        return HttpResponse(status=409)
    except ValidationError as exc:
        messages.error(request, exc.messages[0] if exc.messages else str(exc))
    else:
        messages.success(request, "Correction enregistrée.")
    return redirect("achievements:detail", pk=pk)


@login_required
@require_GET
def evidence_download(request: HttpRequest, pk) -> HttpResponse:
    evidence = get_object_or_404(Evidence, pk=pk)
    if not user_can_view_evidence(user=request.user, evidence=evidence):
        raise Http404()
    if evidence.kind != Evidence.Kind.IMAGE or not evidence.storage_key:
        raise Http404()
    try:
        path = private_media_path(evidence.storage_key)
    except FileNotFoundError as exc:
        raise Http404() from exc
    response = FileResponse(path.open("rb"), content_type=evidence.mime_type or "application/octet-stream")
    response["Content-Disposition"] = f'inline; filename="{evidence.original_label or path.name}"'
    response["Cache-Control"] = "private, no-store"
    return response
