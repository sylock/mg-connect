"""Local development settings."""

from .base import *  # noqa: F401,F403
import os
from pathlib import Path

DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() in {"1", "true", "yes"}
ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Temporary local-only escape hatch when PostgreSQL is unavailable.
# Prefer Postgres (docker compose up db). Do not use in production.
if os.environ.get("USE_SQLITE", "").lower() in {"1", "true", "yes"}:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": Path(__file__).resolve().parent.parent.parent / "db.sqlite3",
        }
    }
