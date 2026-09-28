from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from accounts.forms import (
    FrenchAuthenticationForm,
    UserCreateForm,
    UserUpdateForm,
)
from accounts.models import User
from accounts.permissions import manager_required
from accounts.services import (
    AccountDraft,
    LastManagerError,
    create_account,
    update_account,
)


class SalonLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = FrenchAuthenticationForm
    redirect_authenticated_user = True


class SalonLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")


@login_required
def home(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "home/index.html",
        {
            "page_title": "Accueil",
            "clock_state_label": "Non pointé (aperçu)",
        },
    )


@login_required
def agenda_placeholder(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "agenda/index.html",
        {"page_title": "Agenda"},
    )


@login_required
def reports_placeholder(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "home/placeholder.html",
        {
            "page_title": "Rapports",
            "message": (
                "Les rapports d’équipe seront disponibles ici. "
                "Tous les comptes actifs du salon pourront les consulter."
            ),
        },
    )


@login_required
def feature_coming_soon(request: HttpRequest, feature: str) -> HttpResponse:
    labels = {
        "achievements": "Succès",
        "leave": "Congés",
        "clock": "Pointer",
    }
    return render(
        request,
        "home/placeholder.html",
        {
            "page_title": labels.get(feature, "Fonctionnalité"),
            "message": "Cette fonctionnalité arrive dans une prochaine étape.",
        },
    )


@manager_required
@require_http_methods(["GET", "POST"])
def user_list(request: HttpRequest) -> HttpResponse:
    users = User.objects.all().prefetch_related("groups").order_by("username")
    return render(
        request,
        "management/users.html",
        {"page_title": "Comptes", "users": users},
    )


@manager_required
@require_http_methods(["GET", "POST"])
def user_create(request: HttpRequest) -> HttpResponse:
    form = UserCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            create_account(
                actor=request.user,
                draft=AccountDraft(
                    username=form.cleaned_data["username"],
                    password=form.cleaned_data["password1"],
                    display_name=form.cleaned_data.get("display_name") or "",
                    email=form.cleaned_data.get("email") or "",
                    is_manager=form.cleaned_data.get("is_manager", False),
                    is_salon_active=form.cleaned_data.get("is_salon_active", True),
                ),
            )
        except Exception as exc:
            form.add_error(None, str(exc))
        else:
            return redirect("accounts:user_list")
    return render(
        request,
        "management/user_form.html",
        {"page_title": "Nouveau compte", "form": form, "mode": "create"},
    )


@manager_required
@require_http_methods(["GET", "POST"])
def user_edit(request: HttpRequest, user_id) -> HttpResponse:
    target = get_object_or_404(User, pk=user_id)
    initial = {
        "display_name": target.display_name,
        "email": target.email,
        "is_manager": target.is_manager,
        "is_salon_active": target.is_salon_active,
    }
    form = UserUpdateForm(request.POST or None, initial=initial, user=target)
    if request.method == "POST" and form.is_valid():
        try:
            update_account(
                actor=request.user,
                user=target,
                display_name=form.cleaned_data["display_name"],
                email=form.cleaned_data.get("email") or "",
                is_salon_active=form.cleaned_data.get("is_salon_active", False),
                is_manager=form.cleaned_data.get("is_manager", False),
                new_password=form.cleaned_data.get("new_password") or None,
            )
        except LastManagerError as exc:
            form.add_error(None, exc.messages[0] if exc.messages else str(exc))
        except Exception as exc:
            form.add_error(None, str(exc))
        else:
            return redirect("accounts:user_list")
    return render(
        request,
        "management/user_form.html",
        {
            "page_title": f"Compte · {target.username}",
            "form": form,
            "mode": "edit",
            "target_user": target,
        },
    )
