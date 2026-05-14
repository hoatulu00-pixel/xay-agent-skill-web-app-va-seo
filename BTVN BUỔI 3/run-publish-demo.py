"""Demo: chay that skill webapp-blog-publisher tu skill cu de publish 1 bai len Hoa Xuan webapp.

Chay lenh:
    python "BTVN BUOI 3/run-publish-demo.py"
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Add skill cu vao sys.path de import scripts (vi co relative import .utils)
ROOT = Path(__file__).resolve().parent.parent
OLD_SKILL = ROOT / "seo-content-workspace" / ".claude" / "skills" / "seo-content-publisher"
sys.path.insert(0, str(OLD_SKILL))

import frontmatter
from scripts.webapp_publisher import publish_post, get_post_by_slug, update_post
from scripts.utils import load_settings


def main():
    article_path = ROOT / "BTVN BUOI 3" / "outputs" / "seo" / "2026-05-15_review-vay-hoa-hoa-xuan-he-2026" / "article.md"
    # Path co dau, dung tieng Viet
    article_path = Path(str(article_path).replace("BTVN BUOI 3", "BTVN BUỔI 3"))
    if not article_path.exists():
        print(f"ERROR: not found {article_path}")
        sys.exit(1)

    print(f"[1/4] Reading article: {article_path.name}")
    post = frontmatter.load(article_path)
    meta = dict(post.metadata)
    body_md = post.content
    print(f"      Title: {meta['title'][:60]}")
    print(f"      Slug: {meta.get('slug')}")
    print(f"      Word count: ~{len(body_md.split())}")

    print("[2/4] Loading settings + login...")
    settings = load_settings()
    print(f"      Base URL: {settings['webapp_base_url']}")
    print(f"      Blog prefix: {settings['blog_url_prefix']}")

    category_map = settings.get("category_map", {})
    # Map ngo nguoc: category_id trong frontmatter da co san
    category_id = meta.get("category_id", 4)  # 4 = product_review
    print(f"      category_id: {category_id}")

    slug = meta.get("slug")
    print(f"[3/4] Checking if slug '{slug}' existed...")
    existing = None
    try:
        existing = get_post_by_slug(slug)
    except Exception as e:
        print(f"      (cannot check existence, will create new: {e})")

    if existing:
        post_id = existing["id"]
        print(f"      Slug exists with post_id={post_id} -> UPDATE in place")
        print("[4/4] Updating post...")
        result = update_post(post_id, meta, body_md, category_id)
    else:
        print("      Slug new -> CREATE")
        print("[4/4] Publishing new post...")
        result = publish_post(meta, body_md, category_id)

    print()
    print("=" * 70)
    print("KET QUA THAT:")
    print("=" * 70)
    print(f"  post_id: {result['post_id']}")
    print(f"  slug:    {result['slug']}")
    print(f"  URL:     {result['web_url']}")
    print(f"  API:     {settings['webapp_base_url']}/posts/{result['slug']}")
    print("=" * 70)

    # Ghi log that ra file de minh chung
    out_log = article_path.parent / "publish_log_REAL.json"
    out_log.write_text(json.dumps({
        "skill": "webapp-blog-publisher (chay that)",
        "executed_at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        "input_article": str(article_path.relative_to(ROOT)),
        "result": {
            "post_id": result["post_id"],
            "slug": result["slug"],
            "web_url": result["web_url"],
            "blog_url_prefix": settings["blog_url_prefix"],
            "api_url": f"{settings['webapp_base_url']}/posts/{result['slug']}",
        },
        "operation": "update" if existing else "create",
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nLog saved: {out_log.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
