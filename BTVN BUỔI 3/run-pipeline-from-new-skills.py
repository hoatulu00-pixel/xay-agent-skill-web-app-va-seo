"""Demo: chay full pipeline tu ATOMIC SKILLS MOI (.claude/skills/).

Pipeline:
  1. webapp-blog-publisher skill -> Blog URL THAT
  2. webapp-blog-publisher.sheet_tracker -> Sheet row THAT
  3. google-doc-publisher skill -> Google Doc URL THAT

Lenh:
  python "BTVN BUỔI 3/run-pipeline-from-new-skills.py"
"""
from __future__ import annotations

import importlib
import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / ".claude" / "skills"


def load_skill_module(skill_name: str, module_path: str):
    """Load 1 module tu 1 atomic skill cu the (tranh conflict scripts/ folder)."""
    skill_root = SKILLS_DIR / skill_name
    # Clear cache cua scripts module tu skill khac
    to_remove = [k for k in sys.modules if k.startswith("scripts")]
    for k in to_remove:
        del sys.modules[k]
    # Remove old skill paths
    sys.path[:] = [p for p in sys.path if str(SKILLS_DIR) not in p]
    sys.path.insert(0, str(skill_root))
    return importlib.import_module(module_path)


def run_publish():
    print("\n" + "=" * 70)
    print("[SKILL: webapp-blog-publisher]  POST /posts len Hoa Xuan webapp")
    print("=" * 70)

    pub = load_skill_module("webapp-blog-publisher", "scripts.webapp_publisher")
    utils = load_skill_module("webapp-blog-publisher", "scripts.utils")
    import frontmatter

    article_path = ROOT / "BTVN BUỔI 3" / "outputs" / "seo" / "2026-05-15_review-chan-vay-hoa-hoa-xuan" / "article.md"
    print(f"  Article: {article_path.relative_to(ROOT)}")

    post = frontmatter.load(article_path)
    meta = dict(post.metadata)
    body_md = post.content
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
    }


def run_sheet_tracker(publish_result):
    print("\n" + "=" * 70)
    print("[SKILL: webapp-blog-publisher.sheet_tracker]  Update Google Sheet")
    print("=" * 70)

    tracker = load_skill_module("webapp-blog-publisher", "scripts.sheet_tracker")
    utils = load_skill_module("webapp-blog-publisher", "scripts.utils")

    settings = utils.load_settings()
    sheet_url = settings["tracker_sheet_url"]

    # Tim function append/update phu hop trong sheet_tracker
    candidates = [n for n in dir(tracker) if not n.startswith("_") and callable(getattr(tracker, n))]
    print(f"  Functions trong sheet_tracker: {candidates}")

    print(f"  Goi tracker.append_row(...)")
    try:
        stt = tracker.append_row(
            keyword=publish_result["slug"],
            title=publish_result["title"],
            doc_link="",  # sẽ điền sau khi tạo Doc
            content_status="Written",
            web_status="Published",
            web_link=publish_result["web_url"],
            notes=f"BTVN3 demo - atomic skill MOI - post_id={publish_result['post_id']}",
        )
        print(f"  OK: row stt={stt} appended")
        return {"sheet_url": sheet_url, "stt": stt}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"sheet_url": sheet_url, "error": str(e)}


def run_google_doc(publish_result):
    print("\n" + "=" * 70)
    print("[SKILL: google-doc-publisher]  Tao Google Doc that")
    print("=" * 70)

    writer = load_skill_module("google-doc-publisher", "scripts.google_doc_writer")
    auth = load_skill_module("google-doc-publisher", "scripts.auth_google")
    import frontmatter

    article_path = ROOT / "BTVN BUỔI 3" / "outputs" / "seo" / "2026-05-15_review-chan-vay-hoa-hoa-xuan" / "article.md"
    post = frontmatter.load(article_path)
    title = f"[BTVN3 - Atomic Skill] {post.metadata['title']}"

    print(f"  Goi writer.create_doc(...)")
    try:
        g = auth.get_clients()
        result = writer.create_doc(g, title, post.content)
        # create_doc returns (doc_id, url) tuple
        if isinstance(result, tuple) and len(result) == 2:
            doc_id, url = result
            print(f"  OK: doc_id={doc_id}\n     url={url}")
            return {"doc_id": doc_id, "url": url}
        return {"raw": str(result)}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


def main():
    print("\n" + "=" * 70)
    print("FULL PIPELINE - CHAY TU ATOMIC SKILLS MOI (.claude/skills/)")
    print("=" * 70)

    publish_result = run_publish()
    sheet_result = run_sheet_tracker(publish_result)
    doc_result = run_google_doc(publish_result)

    print("\n\n" + "█" * 70)
    print("█" + " " * 25 + "KET QUA THAT" + " " * 32 + "█")
    print("█" * 70)
    print(f"\n📝 BLOG URL (LIVE):")
    print(f"   {publish_result['web_url']}")
    print(f"\n📊 GOOGLE SHEET TRACKER:")
    print(f"   {sheet_result['sheet_url']}")
    if "result" in sheet_result:
        print(f"   Updated: {sheet_result['result']}")
    elif "error" in sheet_result:
        print(f"   Error: {sheet_result['error']}")
    print(f"\n📄 GOOGLE DOC:")
    if isinstance(doc_result, dict):
        if doc_result.get("url") or doc_result.get("doc_url"):
            print(f"   {doc_result.get('url') or doc_result.get('doc_url')}")
        else:
            print(f"   Error: {doc_result.get('error', 'unknown')}")
    print("\n" + "█" * 70)

    out = ROOT / "BTVN BUỔI 3" / "outputs" / "seo" / "2026-05-15_review-chan-vay-hoa-hoa-xuan" / "pipeline_REAL.json"
    out.write_text(json.dumps({
        "executed_at": datetime.now().isoformat(timespec="seconds"),
        "source": "atomic skills moi tu .claude/skills/",
        "publish": publish_result,
        "sheet": sheet_result,
        "google_doc": doc_result,
    }, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"\nLog: {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
