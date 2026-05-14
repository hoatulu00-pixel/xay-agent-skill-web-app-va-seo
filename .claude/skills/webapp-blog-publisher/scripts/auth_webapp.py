"""Hoa Xuan Fashion API auth — login + cached JWT."""
from __future__ import annotations

import json
import time
from pathlib import Path

import requests

from .utils import CACHE_DIR, load_settings, log, retry

TOKEN_CACHE_FILE = CACHE_DIR / "webapp_token.json"
TOKEN_TTL_SEC = 6 * 24 * 3600  # refresh after 6 days


def _login(base_url: str, email: str, password: str, timeout: int) -> str:
    r = requests.post(
        f"{base_url}/auth/login",
        json={"email": email, "password": password},
        timeout=timeout,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def login(force_refresh: bool = False) -> tuple[str, str]:
    """Returns (token, base_url). Cached unless expired or force_refresh=True."""
    settings = load_settings()
    base_url = settings["webapp_base_url"].rstrip("/")
    email = settings["webapp_email"]
    password = settings["webapp_password"]
    timeout = settings.get("defaults", {}).get("request_timeout_sec", 30)

    if not force_refresh and TOKEN_CACHE_FILE.exists():
        cache = json.loads(TOKEN_CACHE_FILE.read_text(encoding="utf-8"))
        if time.time() - cache.get("issued_at", 0) < TOKEN_TTL_SEC and cache.get("base_url") == base_url:
            return cache["token"], base_url

    log.info("Logging in to web app %s as %s", base_url, email)
    token = retry(lambda: _login(base_url, email, password, timeout), label="webapp.login")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_CACHE_FILE.write_text(
        json.dumps({"token": token, "issued_at": time.time(), "base_url": base_url}),
        encoding="utf-8",
    )
    return token, base_url


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


if __name__ == "__main__":
    token, base = login(force_refresh=True)
    print(f"OK. base={base} token_prefix={token[:20]}...")
