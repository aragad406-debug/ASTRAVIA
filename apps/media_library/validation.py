"""Server-side upload validation by file signature (magic bytes), never by extension alone."""
from django.conf import settings
from django.core.exceptions import ValidationError

# kind -> list of (detected_type, mime, predicate on the first 64 bytes)
SIGNATURES = {
    "image": [
        ("png", "image/png", lambda b: b.startswith(b"\x89PNG\r\n\x1a\n")),
        ("jpeg", "image/jpeg", lambda b: b.startswith(b"\xff\xd8\xff")),
        ("webp", "image/webp", lambda b: b[:4] == b"RIFF" and b[8:12] == b"WEBP"),
        ("gif", "image/gif", lambda b: b[:6] in (b"GIF87a", b"GIF89a")),
        ("avif", "image/avif", lambda b: b[4:12] in (b"ftypavif", b"ftypavis")),
    ],
    "audio": [
        ("mp3", "audio/mpeg", lambda b: b.startswith(b"ID3") or (len(b) > 1 and b[0] == 0xFF and (b[1] & 0xE0) == 0xE0)),
        ("ogg", "audio/ogg", lambda b: b.startswith(b"OggS")),
        ("wav", "audio/wav", lambda b: b[:4] == b"RIFF" and b[8:12] == b"WAVE"),
        ("flac", "audio/flac", lambda b: b.startswith(b"fLaC")),
        ("m4a", "audio/mp4", lambda b: b[4:8] == b"ftyp" and b[8:11] in (b"M4A", b"mp4", b"iso")),
    ],
    "video": [
        ("mp4", "video/mp4", lambda b: b[4:8] == b"ftyp" and b[8:12] not in (b"avif", b"avis")),
        ("webm", "video/webm", lambda b: b.startswith(b"\x1a\x45\xdf\xa3")),
    ],
    "document": [
        ("pdf", "application/pdf", lambda b: b.startswith(b"%PDF-")),
    ],
}

# SVG and HTML are deliberately not accepted: they can carry script.


def sniff(uploaded_file, kind):
    """Return (detected_type, mime) or raise ValidationError."""
    if kind not in SIGNATURES:
        raise ValidationError("Unsupported media kind.")
    limit = settings.MEDIA_LIMITS.get(kind)
    size = getattr(uploaded_file, "size", None)
    if size is None or size <= 0:
        raise ValidationError("The file is empty.")
    if limit and size > limit:
        raise ValidationError(f"File is too large: {size // 1024} KB. The limit for {kind} files is {limit // (1024 * 1024)} MB.")
    position = uploaded_file.tell() if hasattr(uploaded_file, "tell") else 0
    uploaded_file.seek(0)
    head = uploaded_file.read(64)
    uploaded_file.seek(position)
    for detected, mime, predicate in SIGNATURES[kind]:
        try:
            if predicate(head):
                return detected, mime
        except IndexError:
            continue
    allowed = ", ".join(sig[0].upper() for sig in SIGNATURES[kind])
    raise ValidationError(f"This file's contents are not a supported {kind} format. Allowed: {allowed}.")


def verify_image(uploaded_file):
    """Fully decode the header with Pillow; returns (width, height)."""
    from PIL import Image, UnidentifiedImageError

    position = uploaded_file.tell()
    uploaded_file.seek(0)
    try:
        with Image.open(uploaded_file) as img:
            img.verify()
        uploaded_file.seek(0)
        with Image.open(uploaded_file) as img:
            width, height = img.size
    except (UnidentifiedImageError, OSError, SyntaxError) as exc:
        raise ValidationError("The image file is damaged or not a real image.") from exc
    finally:
        uploaded_file.seek(position)
    if width * height > 80_000_000:
        raise ValidationError("Image dimensions are too large.")
    return width, height
