"""Keyword research via Google autocomplete + related searches (free, no API key)."""
from __future__ import annotations

import json
import re
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

from .utils import log, retry

AUTOCOMPLETE_URL = "https://suggestqueries.google.com/complete/search"
SERP_URL = "https://www.google.com/search"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/121.0 Safari/537.36"
    ),
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
}


def autocomplete(query: str, hl: str = "vi", gl: str = "vn") -> list[str]:
    params = {"client": "firefox", "q": query, "hl": hl, "gl": gl}
    r = requests.get(AUTOCOMPLETE_URL, params=params, headers=HEADERS, timeout=15)
    r.raise_for_status()
    data = r.json()
    return data[1] if isinstance(data, list) and len(data) > 1 else []


def related_and_paa(query: str) -> tuple[list[str], list[str]]:
    """Scrape Google SERP for related searches + 'People also ask'."""
    params = {"q": query, "hl": "vi", "gl": "vn"}
    r = requests.get(SERP_URL, params=params, headers=HEADERS, timeout=20)
    if r.status_code != 200:
        log.warning("SERP scrape returned %s", r.status_code)
        return [], []
    soup = BeautifulSoup(r.text, "html.parser")

    related: list[str] = []
    for el in soup.select("div.brs_col a, div[data-rs] a, a.k8XOCe"):
        txt = el.get_text(strip=True)
        if txt and len(txt) > 5:
            related.append(txt)

    paa: list[str] = []
    for el in soup.select("div[jsname='Cpkphb'], div.related-question-pair, div[data-q]"):
        q = el.get("data-q") or el.get_text(strip=True)
        if q and "?" in q:
            paa.append(q.split("?")[0] + "?")

    return list(dict.fromkeys(related))[:10], list(dict.fromkeys(paa))[:10]


def research(topic: str) -> dict:
    log.info("Researching keywords for: %s", topic)

    try:
        suggestions = autocomplete(topic)
    except Exception as e:  # noqa: BLE001
        log.warning("autocomplete primary failed: %s", e)
        suggestions = []

    # Build variant queries — full topic + progressively shorter heads + question forms
    words = topic.split()
    variant_queries: list[str] = [
        topic,
        f"cách {topic}",
        f"cách phối {topic}",
        f"{topic} mặc với áo gì",
    ]
    for n in range(len(words) - 1, 1, -1):
        variant_queries.append(" ".join(words[:n]))

    variants: list[str] = []
    for q in variant_queries:
        try:
            res = autocomplete(q)
            if res:
                variants.extend(res)
        except Exception as e:  # noqa: BLE001
            log.warning("autocomplete variant %r failed: %s", q, e)

    try:
        related, paa = related_and_paa(topic)
    except Exception as e:  # noqa: BLE001
        log.warning("SERP scrape failed: %s", e)
        related, paa = [], []

    all_keywords = list(dict.fromkeys([topic, *suggestions, *variants, *related]))
    if not all_keywords:
        all_keywords = [topic]

    primary = all_keywords[0]
    secondary = [k for k in all_keywords[1:8] if k.lower() != primary.lower()]

    if not paa:
        paa = [
            f"{topic} là gì?",
            f"Cách chọn {topic} phù hợp?",
            f"{topic} nên kết hợp với gì?",
        ]

    result = {
        "topic": topic,
        "primary_keyword": primary,
        "secondary_keywords": secondary[:5],
        "questions": paa[:5],
        "all_suggestions": all_keywords[:20],
    }
    log.info("Research done: %d keywords, %d questions", len(all_keywords), len(paa))
    return result


if __name__ == "__main__":
    import sys
    out = research(sys.argv[1] if len(sys.argv) > 1 else "chân váy hoa mùa xuân")
    print(json.dumps(out, ensure_ascii=False, indent=2))
