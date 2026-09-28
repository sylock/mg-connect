from __future__ import annotations

import io
import secrets
from pathlib import Path
from urllib.parse import urlparse

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from PIL import Image, UnidentifiedImageError

ALLOWED_IMAGE_FORMATS = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_IMAGES = 3
MAX_DIMENSION = 4096


def validate_proof_url(raw: str) -> str:
    raw = (raw or "").strip()
    if not raw:
        raise ValidationError("URL vide.")
    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"}:
        raise ValidationError("Seuls les liens http(s) sont acceptés.")
    if not parsed.netloc:
        raise ValidationError("URL invalide.")
    return raw


def store_image_evidence(upload: UploadedFile) -> tuple[str, str, int, str]:
    """Validate and re-encode image. Returns storage_key, mime, size, original_label."""
    if upload.size is not None and upload.size > MAX_IMAGE_BYTES:
        raise ValidationError("Image trop volumineuse (max. 5 Mo).")

    raw = upload.read()
    if len(raw) > MAX_IMAGE_BYTES:
        raise ValidationError("Image trop volumineuse (max. 5 Mo).")

    try:
        image = Image.open(io.BytesIO(raw))
        image.load()
    except UnidentifiedImageError as exc:
        raise ValidationError("Fichier image non reconnu.") from exc

    fmt = (image.format or "").upper()
    if fmt not in ALLOWED_IMAGE_FORMATS:
        raise ValidationError("Formats autorisés : JPEG, PNG, WebP.")
    if max(image.size) > MAX_DIMENSION:
        raise ValidationError("Dimensions d’image trop grandes.")

    # Re-encode to strip metadata; keep format family.
    out = io.BytesIO()
    save_fmt = "JPEG" if fmt == "JPEG" else fmt
    if save_fmt == "JPEG" and image.mode not in {"RGB", "L"}:
        image = image.convert("RGB")
    image.save(out, format=save_fmt, optimize=True)
    data = out.getvalue()
    if len(data) > MAX_IMAGE_BYTES:
        raise ValidationError("Image trop volumineuse après traitement.")

    ext = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}[save_fmt]
    key = f"{secrets.token_urlsafe(24)}{ext}"
    root = Path(settings.PRIVATE_MEDIA_ROOT)
    root.mkdir(parents=True, exist_ok=True)
    path = root / key
    path.write_bytes(data)

    mime = ALLOWED_IMAGE_FORMATS[save_fmt]
    label = getattr(upload, "name", "") or key
    return key, mime, len(data), label[:255]


def private_media_path(storage_key: str) -> Path:
    root = Path(settings.PRIVATE_MEDIA_ROOT).resolve()
    path = (root / storage_key).resolve()
    if not str(path).startswith(str(root)) or not path.is_file():
        raise FileNotFoundError
    return path
