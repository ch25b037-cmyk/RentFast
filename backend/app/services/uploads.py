"""Validated image upload handling with metadata stripping."""

from io import BytesIO
from pathlib import Path
from uuid import uuid4

from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import DomainError
from app.models.user import User

Image.MAX_IMAGE_PIXELS = 20_000_000

ALLOWED_TYPES = {
    "image/jpeg": ("JPEG", ".jpg"),
    "image/png": ("PNG", ".png"),
    "image/webp": ("WEBP", ".webp"),
}


async def save_image(db: Session, user: User, upload) -> str:
    del db, user
    settings = get_settings()
    if upload.content_type not in ALLOWED_TYPES:
        raise DomainError("VALIDATION_ERROR", "Only JPEG, PNG, and WebP images are supported.")
    data = await upload.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise DomainError("VALIDATION_ERROR", f"Images must be {settings.max_upload_mb} MB or smaller.")
    try:
        with Image.open(BytesIO(data)) as source:
            source.verify()
        with Image.open(BytesIO(data)) as source:
            image_format, extension = ALLOWED_TYPES[upload.content_type]
            mode = "RGBA" if source.mode in {"RGBA", "LA"} or "transparency" in source.info else "RGB"
            clean = Image.new(mode, source.size)
            clean.paste(source.convert(mode))
            output = BytesIO()
            save_options = {"optimize": True}
            if image_format == "JPEG":
                save_options.update(quality=90, progressive=True)
            clean.save(output, format=image_format, **save_options)
    except (Image.DecompressionBombError, SyntaxError, UnidentifiedImageError, OSError) as exc:
        raise DomainError("VALIDATION_ERROR", "The uploaded file is not a valid image.") from exc

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{extension}"
    (upload_dir / filename).write_bytes(output.getvalue())
    return f"/uploads/{filename}"
