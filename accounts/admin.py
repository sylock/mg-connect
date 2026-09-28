from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from accounts.models import Employee, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Salon", {"fields": ("display_name", "is_salon_active")}),
    )
    list_display = ("username", "display_name", "is_salon_active", "is_staff", "is_active")
    search_fields = ("username", "display_name", "email")


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("display_name", "is_active", "user", "employment_start", "employment_end")
    search_fields = ("display_name",)
    list_filter = ("is_active",)
