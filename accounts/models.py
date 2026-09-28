import uuid

from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Salon login account. Manager privileges come from the Manager group."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    display_name = models.CharField(_("display name"), max_length=150, blank=True)
    # Soft activity flag distinct from Django's is_active when needed later.
    is_salon_active = models.BooleanField(_("salon active"), default=True)

    class Meta:
        ordering = ["username"]

    def __str__(self) -> str:
        return self.display_name or self.get_username()

    @property
    def is_manager(self) -> bool:
        if not self.is_authenticated or not self.is_salon_active:
            return False
        return self.groups.filter(name="Manager").exists()


class Employee(models.Model):
    """Employment identity; may exist before a login account is provisioned."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    display_name = models.CharField(_("display name"), max_length=150)
    is_active = models.BooleanField(default=True)
    employment_start = models.DateField(null=True, blank=True)
    employment_end = models.DateField(null=True, blank=True)
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_profile",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_name"]

    def __str__(self) -> str:
        return self.display_name


def get_manager_group() -> Group:
    group, _ = Group.objects.get_or_create(name="Manager")
    return group
