"""Pipeline step: fetch Pexels images, design thumbnail, upload, inject into body."""
from __future__ import annotations

import re
from pathlib import Path

from . import image_fetcher, thumbnail_designer, webapp_publisher
from .utils import log, slugify


def _section_queries(body: str, primary_keyword: str) -> list[str]:
    h2s = re.findall(r"(?m)^##\s+(?!#)(.*)$", body)
    queries: list[str] = []
    for h in h2s:
        cleaned = re.sub(r"[^\w\sÀ-ỹ]", " ", h).strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        queries.append(f"{primary_keyword} {cleaned}".strip() if cleaned else primary_keyword)
    return queries


def _insert_after_h2(body: str, image_pairs: list[tuple[str, str]]) -> str:
    """Inject markdown image blocks after the 2nd, 3rd, 4th H2 headings."""
    if not image_pairs:
        return body
    pairs = list(image_pairs)
    out: list[str] = []
    h2_count = 0
    for line in body.splitlines():
        out.append(line)
        if line.startswith("## ") and not line.startswith("### "):
            h2_count += 1
            if h2_count >= 2 and pairs:
                url, alt = pairs.pop(0)
                out.append("")
                out.append(f"![{alt}]({url})")
                out.append("")
    return "\n".join(out)


def process(meta: dict, body: str, run_dir: Path, brief: dict) -> tuple[dict, str]:
    """Fetch images, design cover, upload everything, inject into body. Returns (meta, body)."""
    pk = brief["primary_keyword"]
    title = meta.get("title") or pk

    log.info("Fetching cover image base from Pexels for %r...", pk)
    cover_pair = image_fetcher.fetch_for_topic(
        query=pk, primary_keyword=pk, run_dir=run_dir, section_idx=0,
        descriptor="cover", prefer_size="large2x",
    )
    cover_url = ""
    if cover_pair:
        base_path, _ = cover_pair
        thumb_path = run_dir / "images" / f"{slugify(pk)}-thumbnail.jpg"
        try:
            thumbnail_designer.design(
                base_image=base_path, title=title, primary_keyword=pk, out_path=thumb_path,
            )
            log.info("Thumbnail designed: %s", thumb_path.name)
            cover_url = webapp_publisher.upload_image(thumb_path) or ""
        except Exception as e:  # noqa: BLE001
            log.warning("Thumbnail design failed (%s); uploading base image as cover", e)
            cover_url = webapp_publisher.upload_image(base_path) or ""
    else:
        log.warning("No cover image available; post will have no cover")

    if cover_url:
        meta["cover_image"] = cover_url

    queries = _section_queries(body, pk)
    target_queries = queries[1:4]  # skip 1st H2 (covered visually by intro+cover)
    log.info("Fetching %d body images...", len(target_queries))

    body_pairs: list[tuple[str, str]] = []
    for idx, q in enumerate(target_queries, start=1):
        pair = image_fetcher.fetch_for_topic(
            query=q, primary_keyword=pk, run_dir=run_dir, section_idx=idx,
            descriptor=f"section-{idx}", prefer_size="large",
        )
        if not pair:
            continue
        local, alt = pair
        url = webapp_publisher.upload_image(local)
        if url:
            body_pairs.append((url, alt))

    body = _insert_after_h2(body, body_pairs)
    log.info("Inserted %d body images", len(body_pairs))
    return meta, body
