"""Demo: chay full pipeline tu ATOMIC SKILLS MOI (.claude/skills/).

Pipeline (thu tu DUNG):
  0. webapp-blog-publisher.image_fetcher -> tai cover image tu Pexels
     webapp-blog-publisher.cloudinary_uploader -> upload Cloudinary -> public URL
  1. webapp-blog-publisher.webapp_publisher -> POST /posts (with cover URL)
  2. google-doc-publisher.google_doc_writer -> tao Doc (with cover + tables)
  3. webapp-blog-publisher.sheet_tracker -> append row (doc_link + content_status="Done")

Lenh:
  python "BTVN BUỔI 3/run-pipeline-from-new-skills.py"
"""
from __future__ import annotations

import importlib
import io
import json
import sys
from datetime import datetime
from pathlib import Path

# Force UTF-8 stdout/stderr on Windows for tieng Viet
if hasattr(sys.stdout, "buffer"):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / ".claude" / "skills"


def load_skill_module(skill_name: str, module_path: str):
    """Load 1 module tu 1 atomic skill cu the (tranh conflict scripts/ folder)."""
    skill_root = SKILLS_DIR / skill_name
    to_remove = [k for k in sys.modules if k.startswith("scripts")]
    for k in to_remove:
        del sys.modules[k]
    sys.path[:] = [p for p in sys.path if str(SKILLS_DIR) not in p]
    sys.path.insert(0, str(skill_root))
    return importlib.import_module(module_path)


def fetch_cover_image(meta: dict, run_dir: Path) -> str | None:
    """Tai cover image tu Pexels va upload Cloudinary, tra ve public URL."""
    print("\n" + "=" * 70)
    print("[SKILL: webapp-blog-publisher.image_fetcher + cloudinary]  Fetch cover")
    print("=" * 70)

    fetcher = load_skill_module("webapp-blog-publisher", "scripts.image_fetcher")
    cloud = load_skill_module("webapp-blog-publisher", "scripts.cloudinary_uploader")

    primary_kw = meta.get("primary_keyword")
    if not primary_kw:
        tags = meta.get("tags") or []
        primary_kw = tags[0] if tags else "chân váy hoa"
    query = "floral skirt outfit fashion vietnam women"

    print(f"  Pexels query: {query!r}")
    try:
        result = fetcher.fetch_for_topic(
            query=query,
            primary_keyword=str(primary_kw),
            run_dir=run_dir,
            section_idx=0,
            descriptor="cover",
        )
        if not result:
            print("  WARNING: Pexels khong tra ve anh phu hop")
            return None
        local_path, alt = result
        print(f"  Downloaded: {local_path.name}")

        public_url = cloud.upload_local_file(local_path, folder="hoaxuan-blog/btvn3")
        if not public_url:
            print("  WARNING: Cloudinary upload failed")
            return None
        print(f"  Cloudinary URL: {public_url}")
        return public_url
    except Exception:
        import traceback
        traceback.print_exc()
        return None


def run_publish(meta: dict, body_md: str, cover_url: str | None):
    print("\n" + "=" * 70)
    print("[SKILL: webapp-blog-publisher]  POST /posts len Hoa Xuan webapp")
    print("=" * 70)

    pub = load_skill_module("webapp-blog-publisher", "scripts.webapp_publisher")
    utils = load_skill_module("webapp-blog-publisher", "scripts.utils")

    meta = dict(meta)
    if cover_url:
        meta["cover_image"] = cover_url
        print(f"  Cover URL injected: {cover_url}")

    category_id = meta.get("category_id", 4)
    slug = meta.get("slug")
    try:
        existing = pub.get_post_by_slug(slug)
    except Exception:
        existing = None

    if existing:
        print(f"  Slug ton tai (post_id={existing['id']}) -> UPDATE")
        result = pub.update_post(existing["id"], meta, body_md, category_id)
    else:
        print(f"  Slug moi -> CREATE")
        result = pub.publish_post(meta, body_md, category_id)

    settings = utils.load_settings()
    return {
        "post_id": result["post_id"],
        "slug": result["slug"],
        "web_url": result["web_url"],
        "api_url": f"{settings['webapp_base_url']}/posts/{result['slug']}",
        "title": meta["title"],
        "category_id": category_id,
        "word_count": len(body_md.split()),
        "cover_url": cover_url,
    }


def run_google_doc(meta: dict, body_md: str, cover_url: str | None):
    print("\n" + "=" * 70)
    print("[SKILL: google-doc-publisher]  Tao Google Doc (cover + bang)")
    print("=" * 70)

    writer = load_skill_module("google-doc-publisher", "scripts.google_doc_writer")
    auth = load_skill_module("google-doc-publisher", "scripts.auth_google")

    title = f"[BTVN3 - Atomic Skill] {meta['title']}"
    print(f"  Title: {title}")
    print(f"  Cover URL: {cover_url or '(none)'}")

    try:
        g = auth.get_clients()
        result = writer.create_doc(g, title, body_md, cover_image_url=cover_url)
        if isinstance(result, tuple) and len(result) == 2:
            doc_id, url = result
            print(f"  OK: doc_id={doc_id}")
            print(f"      url={url}")
            return {"doc_id": doc_id, "url": url}
        return {"raw": str(result)}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


def run_sheet_tracker(publish_result: dict, doc_result: dict):
    print("\n" + "=" * 70)
    print("[SKILL: webapp-blog-publisher.sheet_tracker]  Append row (doc + status)")
    print("=" * 70)

    tracker = load_skill_module("webapp-blog-publisher", "scripts.sheet_tracker")
    utils = load_skill_module("webapp-blog-publisher", "scripts.utils")

    settings = utils.load_settings()
    sheet_url = settings.get("tracker_sheet_url",
        f"https://docs.google.com/spreadsheets/d/{settings['tracker_sheet_id']}/edit")

    doc_link = doc_result.get("url", "") if isinstance(doc_result, dict) else ""
    print(f"  doc_link to append: {doc_link or '(none)'}")

    try:
        stt = tracker.append_row(
            keyword=publish_result["slug"],
            title=publish_result["title"],
            doc_link=doc_link,
            content_status="Done",
            web_status="Published",
            web_link=publish_result["web_url"],
            notes=f"BTVN3 atomic skill - post_id={publish_result['post_id']} - cover={'YES' if publish_result.get('cover_url') else 'NO'}",
        )
        print(f"  OK: row stt={stt} appended (content_status=Done, doc_link set)")
        return {"sheet_url": sheet_url, "stt": stt, "doc_link_in_row": doc_link}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"sheet_url": sheet_url, "error": str(e)}


def main():
    import frontmatter

    print("\n" + "=" * 70)
    print("FULL PIPELINE v2 - ATOMIC SKILLS (.claude/skills/)")
    print("Fix: cover image + table render + doc_link + content_status")
    print("=" * 70)

    article_path = ROOT / "BTVN BUỔI 3" / "outputs" / "seo" / "2026-05-15_review-chan-vay-hoa-hoa-xuan" / "article.md"
    print(f"  Article: {article_path.relative_to(ROOT)}")
    post = frontmatter.load(article_path)
    meta = dict(post.metadata)
    body_md = post.content

    run_dir = article_path.parent / "_pipeline_assets"
    run_dir.mkdir(parents=True, exist_ok=True)

    cover_url = fetch_cover_image(meta, run_dir)
    publish_result = run_publish(meta, body_md, cover_url)
    doc_result = run_google_doc(meta, body_md, cover_url)
    sheet_result = run_sheet_tracker(publish_result, doc_result)

    print("\n\n" + "=" * 70)
    print("                       KET QUA THAT v2")
    print("=" * 70)
    print(f"\nBLOG URL (LIVE):")
    print(f"   {publish_result['web_url']}")
    print(f"\nCOVER IMAGE URL (Cloudinary):")
    print(f"   {cover_url or '(failed)'}")
    print(f"\nGOOGLE DOC (with cover + real tables):")
    if isinstance(doc_result, dict) and doc_result.get("url"):
        print(f"   {doc_result['url']}")
    else:
        print(f"   Error: {doc_result}")
    print(f"\nGOOGLE SHEET TRACKER:")
    print(f"   {sheet_result['sheet_url']}")
    if sheet_result.get("stt"):
        print(f"   row stt={sheet_result['stt']} - doc_link in row: {sheet_result.get('doc_link_in_row', '')[:70]}")
    elif sheet_result.get("error"):
        print(f"   Error: {sheet_result['error']}")
    print("\n" + "=" * 70)

    out = ROOT / "BTVN BUỔI 3" / "outputs" / "seo" / "2026-05-15_review-chan-vay-hoa-hoa-xuan" / "pipeline_REAL.json"
    out.write_text(json.dumps({
        "executed_at": datetime.now().isoformat(timespec="seconds"),
        "source": "atomic skills moi - fix v2 (cover image + table + doc_link + status)",
        "cover_image_url": cover_url,
        "publish": publish_result,
        "google_doc": doc_result,
        "sheet": sheet_result,
    }, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"\nLog: {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
