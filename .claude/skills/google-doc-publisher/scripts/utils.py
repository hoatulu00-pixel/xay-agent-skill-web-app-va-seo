"""Common utilities: settings loader, logging, slugify, retry, SEO validator."""
from __future__ import annotations

import json
import logging
import re
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

try:
    import truststore as _truststore
    _truststore.inject_into_ssl()
except Exception:
    pass

import io as _io
if hasattr(sys.stdout, "buffer") and getattr(sys.stdout, "encoding", "").lower() != "utf-8":
    try:
        sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

SKILL_ROOT = Path(__file__).resolve().parent.parent
SETTINGS_PATH = SKILL_ROOT / "config" / "settings.json"
SETTINGS_EXAMPLE_PATH = SKILL_ROOT / "config" / "settings.example.json"
CACHE_DIR = SKILL_ROOT / ".cache"
OUTPUTS_DIR = SKILL_ROOT / "outputs" / "runs"


def get_logger(name: str = "seo-publisher") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s", "%H:%M:%S"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


log = get_logger()


def load_settings() -> dict:
    if not SETTINGS_PATH.exists():
        raise FileNotFoundError(
            f"Missing {SETTINGS_PATH}. Copy {SETTINGS_EXAMPLE_PATH.name} -> settings.json and fill in values. See SETUP.md."
        )
    return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))


def save_settings(data: dict) -> None:
    SETTINGS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def slugify(text: str, max_len: int = 80) -> str:
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.lower()
    text = re.sub(r"[đĐ]", "d", text)
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text).strip("-")
    return text[:max_len].rstrip("-")


def retry(fn: Callable[[], Any], attempts: int = 3, delay_sec: float = 2.0, label: str = "op") -> Any:
    last_exc: Exception | None = None
    for i in range(1, attempts + 1):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            last_exc = e
            log.warning("%s failed attempt %d/%d: %s", label, i, attempts, e)
            if i < attempts:
                time.sleep(delay_sec * i)
    raise last_exc  # type: ignore[misc]


def make_run_dir(slug: str) -> Path:
    today = datetime.now().strftime("%Y-%m-%d")
    run_dir = OUTPUTS_DIR / f"{today}_{slug}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def rebuild_md(meta: dict, body: str) -> str:
    fm_lines = ["---"]
    for k, v in meta.items():
        if isinstance(v, list):
            inner = ", ".join(f'"{x}"' for x in v)
            fm_lines.append(f"{k}: [{inner}]")
        else:
            v_str = str(v).replace('"', '\\"')
            fm_lines.append(f'{k}: "{v_str}"')
    fm_lines.append("---")
    return "\n".join(fm_lines) + "\n\n" + body


def parse_frontmatter(md: str) -> tuple[dict, str]:
    """Extract YAML-ish frontmatter between two `---` lines. Returns (meta, body)."""
    if not md.startswith("---"):
        return {}, md
    parts = md.split("---", 2)
    if len(parts) < 3:
        return {}, md
    raw = parts[1].strip()
    body = parts[2].lstrip("\n")
    meta: dict = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip().strip('"').strip("'")
        if v.startswith("[") and v.endswith("]"):
            inner = v[1:-1]
            meta[k.strip()] = [s.strip().strip('"').strip("'") for s in inner.split(",") if s.strip()]
        else:
            meta[k.strip()] = v
    return meta, body


def validate_seo(meta: dict, body: str) -> list[str]:
    errors: list[str] = []
    title = meta.get("title", "")
    excerpt = meta.get("excerpt", "")
    primary_kw = (meta.get("primary_keyword") or "").lower()

    if not title:
        errors.append("Missing title in frontmatter")
    elif len(title) > 65:
        errors.append(f"Title too long ({len(title)} > 60)")
    elif primary_kw and primary_kw not in title.lower():
        errors.append("Primary keyword missing in title")

    if not excerpt:
        errors.append("Missing excerpt")
    elif not (140 <= len(excerpt) <= 170):
        errors.append(f"Excerpt length {len(excerpt)} not in 150-160 range")

    h1_count = len(re.findall(r"(?m)^#\s+", body))
    h2_count = len(re.findall(r"(?m)^##\s+", body))
    if h1_count != 1:
        errors.append(f"Need exactly 1 H1, found {h1_count}")
    if h2_count < 3:
        errors.append(f"Need >=3 H2 sections, found {h2_count}")

    if "Câu hỏi thường gặp" not in body and "FAQ" not in body:
        errors.append("Missing FAQ section")
    if "Tóm tắt nhanh" not in body:
        errors.append("Missing TL;DR (Tóm tắt nhanh) block")

    word_count = len(re.findall(r"\S+", body))
    if word_count < 550:
        errors.append(f"Body too short ({word_count} words, min 550)")

    return errors
