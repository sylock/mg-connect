from django.contrib import admin

from audit.models import AuditEvent, MutationReceipt


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("created_at", "operation", "entity_type", "entity_id", "actor")
    list_filter = ("operation", "entity_type")
    search_fields = ("entity_id", "reason")
    readonly_fields = (
        "id",
        "actor",
        "entity_type",
        "entity_id",
        "operation",
        "before",
        "after",
        "reason",
        "correlation_id",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MutationReceipt)
class MutationReceiptAdmin(admin.ModelAdmin):
    list_display = ("created_at", "action", "actor", "token", "result_reference")
    readonly_fields = (
        "id",
        "actor",
        "action",
        "token",
        "request_hash",
        "result_reference",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
