"""One-time bootstrap: seed 7 categories on web app + create tracker Sheet."""
from __future__ import annotations

import json

import requests

from .auth_google import get_clients
from .auth_webapp import auth_headers, login
from .sheet_tracker import create_tracker_sheet
from .utils import SKILL_ROOT, load_settings, log, retry, save_settings

SEED_FILE = SKILL_ROOT / "config" / "categories_seed.json"


def list_existing_categories(base: str) -> list[dict]:
    r = requests.get(f"{base}/categories", timeout=20)
    r.raise_for_status()
    return r.json()


def create_category(base: str, token: str, name: str, description: str) -> dict:
    payload = {"name": name, "description": description}
    r = requests.post(f"{base}/categories", json=payload, headers=auth_headers(token), timeout=20)
    if r.status_code == 401:
        token, _ = login(force_refresh=True)
        r = requests.post(f"{base}/categories", json=payload, headers=auth_headers(token), timeout=20)
    r.raise_for_status()
    return r.json()


def seed_webapp_categories() -> dict:
    settings = load_settings()
    seed = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    token, base = login()

    existing = list_existing_categories(base)
    by_name = {c["name"]: c for c in existing}

    cat_map: dict[str, int] = {}
    for entry in seed:
        ctype = entry["content_type"]
        name = entry["name"]
        if name in by_name:
            cat_map[ctype] = by_name[name]["id"]
            log.info("Category exists: %s (id=%d)", name, by_name[name]["id"])
        else:
            created = retry(
                lambda: create_category(base, token, name, entry["description"]),
                label=f"create_category({name})",
            )
            cat_map[ctype] = created["id"]
            log.info("Category created: %s (id=%d)", name, created["id"])

    settings["category_map"] = cat_map
    save_settings(settings)
    return cat_map


def main() -> None:
    log.info("=== Bootstrap: seeding categories + tracker sheet ===")
    cat_map = seed_webapp_categories()

    settings = load_settings()
    if not settings.get("tracker_sheet_id"):
        g = get_clients()
        sheet_id = create_tracker_sheet(g)
        log.info("Tracker sheet ID saved to settings.json: %s", sheet_id)
    else:
        log.info("Tracker sheet already exists: %s", settings.get("tracker_sheet_url"))

    settings = load_settings()
    print("\n=== SEED COMPLETE ===")
    print(f"Categories: {json.dumps(cat_map, indent=2)}")
    print(f"Tracker:    {settings.get('tracker_sheet_url')}")
    print("Next step: /seo-publish \"<your topic>\"")


if __name__ == "__main__":
    main()
