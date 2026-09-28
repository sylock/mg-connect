from __future__ import annotations

from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

from accounts.models import Employee, get_manager_group

User = get_user_model()


class LastManagerError(ValidationError):
    """Raised when an action would remove the last active manager."""


@dataclass
class AccountDraft:
    username: str
    password: str | None
    display_name: str
    email: str = ""
    is_salon_active: bool = True
    is_manager: bool = False
    employee: Employee | None = None
    create_employee: bool = True


def count_active_managers() -> int:
    return (
        User.objects.filter(
            groups__name="Manager",
            is_salon_active=True,
            is_active=True,
        )
        .distinct()
        .count()
    )


@transaction.atomic
def create_account(actor: User | None, draft: AccountDraft) -> User:
    if User.objects.filter(username=draft.username).exists():
        raise ValidationError({"username": "Ce nom d’utilisateur existe déjà."})
    if not draft.password:
        raise ValidationError({"password": "Un mot de passe est requis."})

    user = User(
        username=draft.username,
        display_name=draft.display_name or draft.username,
        email=draft.email,
        is_salon_active=draft.is_salon_active,
        is_active=True,
    )
    user.set_password(draft.password)
    user.save()

    employee = draft.employee
    if employee is None and draft.create_employee:
        employee = Employee.objects.create(
            display_name=user.display_name,
            user=user,
            is_active=draft.is_salon_active,
        )
    elif employee is not None:
        if employee.user_id and employee.user_id != user.pk:
            raise ValidationError({"employee": "Cet employé a déjà un compte."})
        employee.user = user
        employee.save(update_fields=["user", "updated_at"])

    if draft.is_manager:
        user.groups.add(get_manager_group())

    return user


@transaction.atomic
def update_account(
    *,
    actor: User,
    user: User,
    display_name: str,
    email: str,
    is_salon_active: bool,
    is_manager: bool,
    new_password: str | None = None,
) -> User:
    was_manager = user.is_manager
    becoming_inactive = not is_salon_active
    losing_manager = was_manager and (not is_manager or becoming_inactive)

    if losing_manager and count_active_managers() <= 1:
        raise LastManagerError(
            "Impossible de retirer ou désactiver le dernier gérant actif."
        )

    user.display_name = display_name or user.username
    user.email = email
    user.is_salon_active = is_salon_active
    if new_password:
        user.set_password(new_password)
    user.save()

    group = get_manager_group()
    if is_manager and is_salon_active:
        user.groups.add(group)
    else:
        user.groups.remove(group)

    return user


@transaction.atomic
def bootstrap_first_manager(
    *,
    username: str,
    password: str,
    display_name: str = "",
) -> User:
    if count_active_managers() > 0:
        raise ValidationError("Un gérant existe déjà ; utilisez l’interface de gestion.")
    return create_account(
        actor=None,
        draft=AccountDraft(
            username=username,
            password=password,
            display_name=display_name or username,
            is_manager=True,
            is_salon_active=True,
        ),
    )
