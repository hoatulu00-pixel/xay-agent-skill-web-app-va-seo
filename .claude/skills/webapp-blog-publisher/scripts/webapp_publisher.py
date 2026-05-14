"""Publish article to Hoa Xuan Fashion web app."""
from __future__ import annotations

from pathlib import Path

import requests

from .auth_webapp import auth_headers, login
from .markdown_to_html import to_html
from .utils import load_settings, log, retry


def upload_image(local_path: str | Path) -> str | None:
    """Upload image and return public URL.

    Strategy:
      1) Direct Cloudinary upload (preferred — works regardless of backend config)
      2) Fallback to webapp's /upload endpoint
    """
    if not local_path:
        return None
    fp = Path(local_path)
    if not fp.exists():
        log.warning("Image %s not found, skipping", fp)
        return None

    from . import cloudinary_uploader
    direct_url = cloudinary_uploader.upload_local_file(fp)
    if direct_url:
        return direct_url

    log.info("Falling back to webapp /upload endpoint...")
    try:
        token, base = login()
        with fp.open("rb") as f:
            files = {"file": (fp.name, f, "image/jpeg")}
            r = requests.post(f"{base}/upload", files=files, headers=auth_headers(token), timeout=60)
        r.raise_for_status()
        url = r.json()["url"]
        log.info("Uploaded via webapp: %s", url)
        return url
    except Exception as e:  # noqa: BLE001
        log.error("Both Cloudinary direct + webapp /upload failed: %s", e)
        return None


def get_post_by_slug(slug: str) -> dict | None:
    """Fetch a published post by slug. Returns full post dict including id."""
    token, base = login()
    r = requests.get(f"{base}/posts/{slug}", timeout=30)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


def update_post(post_id: int, meta: dict, body_md: str, category_id: int) -> dict:
    """PUT /posts/{id} — update existing post in place. Returns the updated post."""
    settings = load_settings()
    blog_url_prefix = settings["blog_url_prefix"].rstrip("/")
    token, base = login()

    cover_url = meta.get("cover_image") or ""
    if cover_url and not cover_url.startswith("http"):
        cover_url = upload_image(cover_url) or ""

    html = to_html(body_md)
    payload = {
        "title": meta["title"],
        "content": html,
        "excerpt": meta.get("excerpt", "")[:500],
        "cover_image_url": cover_url or None,
        "category_id": category_id,
        "is_published": True,
    }
    log.info("PUT /posts/%d (title=%s)", post_id, meta["title"][:50])

    def _put():
        r = requests.put(f"{base}/posts/{post_id}", json=payload, headers=auth_headers(token), timeout=60)
        if r.status_code == 401:
            new_token, _ = login(force_refresh=True)
            r = requests.put(f"{base}/posts/{post_id}", json=payload, headers=auth_headers(new_token), timeout=60)
        r.raise_for_status()
        return r.json()

    post = retry(_put, label="posts.update")
    web_url = f"{blog_url_prefix}/{post['slug']}"
    log.info("Updated: %s", web_url)
    return {"post_id": post["id"], "slug": post["slug"], "web_url": web_url, "raw": post}


def publish_post(meta: dict, body_md: str, category_id: int) -> dict:
    settings = load_settings()
    blog_url_prefix = settings["blog_url_prefix"].rstrip("/")
    token, base = login()

    cover_url = meta.get("cover_image") or ""
    if cover_url and not cover_url.startswith("http"):
        cover_url = upload_image(cover_url) or ""

    html = to_html(body_md)
    payload = {
        "title": meta["title"],
        "content": html,
        "excerpt": meta.get("excerpt", "")[:500],
        "cover_image_url": cover_url or None,
        "category_id": category_id,
        "is_published": settings.get("defaults", {}).get("is_published_on_create", True),
    }

    log.info("POST /posts (category_id=%s, title=%s)", category_id, meta["title"][:50])

    def _post():
        r = requests.post(f"{base}/posts", json=payload, headers=auth_headers(token), timeout=60)
        if r.status_code == 401:
            new_token, _ = login(force_refresh=True)
            r = requests.post(f"{base}/posts", json=payload, headers=auth_headers(new_token), timeout=60)
        r.raise_for_status()
        return r.json()

    post = retry(_post, label="posts.create")
    web_url = f"{blog_url_prefix}/{post['slug']}"
    log.info("Published: %s", web_url)
    return {"post_id": post["id"], "slug": post["slug"], "web_url": web_url, "raw": post}
