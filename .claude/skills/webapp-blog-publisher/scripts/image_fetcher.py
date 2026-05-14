"""Fetch realistic stock images from Pexels (free API, real photos)."""
from __future__ import annotations

import random
from pathlib import Path

import requests

from .utils import load_settings, log, retry, slugify

PEXELS_SEARCH_URL = "https://api.pexels.com/v1/search"
TIMEOUT = 30

_USED_PHOTO_IDS: set[int] = set()


def reset_used() -> None:
    _USED_PHOTO_IDS.clear()


def mark_used(photo_id: int) -> None:
    _USED_PHOTO_IDS.add(photo_id)


def _api_key() -> str:
    settings = load_settings()
    key = (settings.get("pexels_api_key") or "").strip()
    if not key or key.startswith("PASTE_"):
        raise RuntimeError(
            "Missing pexels_api_key in settings.json. "
            "Get a free key at https://www.pexels.com/api/"
        )
    return key


def search_pexels(query: str, n: int = 30, orientation: str = "landscape") -> list[dict]:
    headers = {"Authorization": _api_key()}
    params = {
        "query": query,
        "per_page": max(1, min(n, 80)),
        "orientation": orientation,
        "size": "large",
        "locale": "vi-VN",
    }

    def _do() -> list[dict]:
        r = requests.get(PEXELS_SEARCH_URL, headers=headers, params=params, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json().get("photos", [])

    try:
        photos = retry(_do, label=f"pexels.search({query!r})")
    except Exception as e:  # noqa: BLE001
        log.warning("Pexels search failed for %r: %s", query, e)
        return []
    return photos


def download_image(photo: dict, out_path: Path, prefer_size: str = "large2x") -> Path | None:
    src = photo.get("src", {})
    url = src.get(prefer_size) or src.get("large") or src.get("original")
    if not url:
        return None
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        out_path.write_bytes(r.content)
        log.info("Downloaded image: %s (%d KB)", out_path.name, len(r.content) // 1024)
        return out_path
    except Exception as e:  # noqa: BLE001
        log.warning("Image download failed for %s: %s", url, e)
        return None


def _seo_filename(primary_keyword: str, descriptor: str | None, idx: int) -> str:
    base = slugify(primary_keyword, max_len=50)
    desc = slugify(descriptor or "", max_len=30) if descriptor else ""
    parts = [p for p in (base, desc, str(idx) if idx else "") if p]
    return "-".join(parts).strip("-") + ".jpg"


def _pick_unseen(photos: list[dict]) -> dict | None:
    fresh = [p for p in photos if p.get("id") not in _USED_PHOTO_IDS]
    if not fresh:
        return None
    return random.choice(fresh[: min(10, len(fresh))])


def fetch_for_topic(
    query: str,
    primary_keyword: str,
    run_dir: Path,
    section_idx: int = 0,
    descriptor: str | None = None,
    prefer_size: str = "large2x",
) -> tuple[Path, str] | None:
    """Search & download 1 image, deduped against previously used photos.

    Returns (local_path, seo_alt_text) or None.
    """
    queries_to_try = [query]
    if query.strip().lower() != primary_keyword.lower():
        queries_to_try.append(primary_keyword)

    photo = None
    for q in queries_to_try:
        photos = search_pexels(q, n=30)
        photo = _pick_unseen(photos)
        if photo:
            break

    if not photo:
        log.warning("No unseen photo for %r (seen %d so far)", query, len(_USED_PHOTO_IDS))
        return None

    fname = _seo_filename(primary_keyword, descriptor, section_idx)
    local = run_dir / "images" / fname
    saved = download_image(photo, local, prefer_size=prefer_size)
    if not saved:
        return None

    mark_used(int(photo.get("id", 0)))

    raw_alt = (photo.get("alt") or "").strip()
    if raw_alt and raw_alt.lower() != primary_keyword.lower():
        seo_alt = f"{primary_keyword.capitalize()} - {raw_alt}"
    else:
        seo_alt = primary_keyword.capitalize()
    return saved, seo_alt[:120]
