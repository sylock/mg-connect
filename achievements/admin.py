from django.contrib import admin

from achievements.models import Achievement, AchievementCategory, Evidence


@admin.register(AchievementCategory)
class AchievementCategoryAdmin(admin.ModelAdmin):
    list_display = ("code", "label", "is_active")


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("occurred_on", "category", "employee", "state", "created_by", "revision")
    list_filter = ("state", "category")


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ("kind", "achievement", "created_at", "superseded_at")
    readonly_fields = ("storage_key", "mime_type", "size_bytes")
