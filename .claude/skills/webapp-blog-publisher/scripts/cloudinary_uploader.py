"""Direct Cloudinary upload — bypasses webapp /upload (which requires backend Cloudinary config).

Reads `cloudinary_url` from settings.json. Format:
    cloudinary://<api_key>:<api_secret>@<cloud_name>
"""
from __future__ import annotations

import re
from pathlib import Path

import cloudinary
import cloudinary.uploader

from .utils import load_settings, log

_CLOUDINARY_URL_RE = re.compile(r"^cloudinary://([^:]+):([^@]+)@(.+)$")
_CONFIGURED = False


def _ensure_configured() -> bool:
    global _CONFIGURED
    if _CONFIGURED:
        return True
    settings = load_settings()
    url = (settings.get("cloudinary_url") or "").strip()
    if not url or url.startswith("PASTE_") or "<" in url:
        return False
    m = _CLOUDINARY_URL_RE.match(url)
    if not m:
        log.warning("Malformed cloudinary_url; expected cloudinary://key:secret@cloud_name")
        return False
    api_key, api_secret, cloud_name = m.groups()
    cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret, secure=True)
    _CONFIGURED = True
    log.info("Cloudinary configured for cloud_name=%s", cloud_name)
    return True


def upload_local_file(
    file_path: str | Path,
    *,
    folder: str = "hoaxuan-blog",
    public_id: str | None = None,
) -> str | None:
    if not _ensure_configured():
        log.warning("cloudinary_url not set in settings.json; skipping direct upload")
        return None

    fp = Path(file_path)
    if not fp.exists():
        log.warning("Local image %s not found", fp)
        return None

    try:
        kwargs: dict = {
            "folder": folder,
            "resource_type": "image",
            "transformation": [{"quality": "auto", "fetch_format": "auto"}],
            "use_filename": True,
            "unique_filename": True,
            "overwrite": False,
        }
        if public_id:
            kwargs["public_id"] = public_id
        result = cloudinary.uploader.upload(str(fp), **kwargs)
        url = result.get("secure_url")
        if url:
            log.info("Cloudinary uploaded: %s -> %s", fp.name, url)
        return url
    except Exception as e:  # noqa: BLE001
        log.error("Cloudinary upload failed for %s: %s", fp.name, e)
        return None
