from django.core.management.base import BaseCommand, CommandError

from accounts.services import bootstrap_first_manager
from django.core.exceptions import ValidationError


class Command(BaseCommand):
    help = "Create the first manager account when none exists yet."

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)
        parser.add_argument("--password", required=True)
        parser.add_argument("--display-name", default="")

    def handle(self, *args, **options):
        try:
            user = bootstrap_first_manager(
                username=options["username"],
                password=options["password"],
                display_name=options["display_name"],
            )
        except ValidationError as exc:
            raise CommandError("; ".join(exc.messages)) from exc
        self.stdout.write(
            self.style.SUCCESS(
                f"Manager créé : {user.username} ({user.display_name or user.username})"
            )
        )
