from django.core.management.base import BaseCommand

from achievements.models import AchievementCategory

DEFAULTS = (
    ("video_published", "Vidéo publiée"),
    ("positive_review", "Avis client positif"),
)


class Command(BaseCommand):
    help = "Seed default achievement categories."

    def handle(self, *args, **options):
        for code, label in DEFAULTS:
            obj, created = AchievementCategory.objects.get_or_create(
                code=code,
                defaults={"label": label, "is_active": True},
            )
            if not created and obj.label != label:
                obj.label = label
                obj.save(update_fields=["label"])
            self.stdout.write(f"{'Created' if created else 'OK'}: {code}")
