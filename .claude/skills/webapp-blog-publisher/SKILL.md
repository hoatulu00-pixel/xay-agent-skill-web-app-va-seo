---
name: webapp-blog-publisher
description: Publish bài blog Markdown lên Hoa Xuân Fashion webapp (POST /posts) kèm upload cover image qua Cloudinary và update Google Sheet tracker. Kích hoạt khi user nói "đăng bài lên webapp", "publish blog Hoa Xuân", "POST /posts", "upload bài lên Railway", hoặc khi agent seo-technical cần publish bài đã viết xong. Input là article.md có frontmatter, output là URL bài đã đăng + log JSON.
---

# Skill: Hoa Xuân Webapp Blog Publisher

Publish Markdown article lên Hoa Xuân Fashion (`https://resilient-expression-production-1149.up.railway.app`) qua REST API.

## Khi nào kích hoạt

- User: "đăng bài này lên web", "publish blog Hoa Xuân", "POST /posts"
- User: "upload bài đã viết xong"
- Agent `seo-technical` đã có `article.md` + schema markup, cần publish

## Input

File Markdown `article.md` với frontmatter:
```markdown
---
title: "..."
slug: "..."
meta_description: "..."
excerpt: "..."
cover_image: "vay-hoa-cover.jpg"   # path relative hoặc URL Cloudinary có sẵn
category_id: 3
tags: ["..."]
---

# Heading 1
...
```

## Output

`publish_log.json` lưu vào `BTVN BUỔI 3/outputs/seo/<date>_<slug>/`:
```json
{
  "post_id": 142,
  "slug": "cach-phoi-vay-hoa-mua-he-2026",
  "url": "https://resilient-expression-production-1149.up.railway.app/blog/cach-phoi-vay-hoa-mua-he-2026",
  "cover_image_url": "https://res.cloudinary.com/.../vay-hoa-cover.jpg",
  "sheet_row": 23,
  "published_at": "2026-05-14T10:30:00Z",
  "status": "success"
}
```

## Files trong skill

- `scripts/auth_webapp.py` — JWT login vào `/auth/login`, cache token tại `.cache/webapp_token.json`
- `scripts/markdown_to_html.py` — convert Markdown → HTML (giữ semantic: h1-h6, lists, blockquote, links, img, table)
- `scripts/cloudinary_uploader.py` — upload ảnh lên Cloudinary, trả về URL public
- `scripts/image_processor.py` — resize/optimize ảnh trước upload (WebP, max 1920px width)
- `scripts/thumbnail_designer.py` — sinh thumbnail từ cover image + title overlay (nếu cần)
- `scripts/seed_categories.py` — tạo 7 categories chuẩn trên Hoa Xuân webapp (chạy 1 lần đầu setup)
- `config/settings.example.json` — template config (user copy → `settings.json` và fill credentials)
- `config/categories_seed.json` — danh sách 7 categories chuẩn
- `references/api_endpoints.md` — spec endpoints `/posts`, `/upload`, `/categories`
- `references/sheet_schema.md` — schema 9 cột Google Sheet tracker

## Workflow nội bộ

1. **Auth**: `auth_webapp.login(email, password)` → trả JWT, cache vào `.cache/webapp_token.json` (15 phút)
2. **Process cover image**:
   - Nếu `cover_image` là path local → resize qua `image_processor` → upload Cloudinary qua `cloudinary_uploader`
   - Nếu là URL Cloudinary rồi → skip upload, dùng nguyên URL
3. **Convert Markdown → HTML** qua `markdown_to_html.py`
4. **POST `/posts`** với payload:
   ```json
   {
     "title": "...",
     "slug": "...",
     "content": "<h1>...</h1>...",
     "excerpt": "...",
     "meta_description": "...",
     "cover_image_url": "https://res.cloudinary.com/.../vay-hoa.jpg",
     "category_id": 3,
     "is_published": true
   }
   ```
   Header: `Authorization: Bearer <jwt>`
5. **Lưu publish_log** với response data
6. **Update Google Sheet tracker** (optional, nếu có `google_sheet_id` trong settings): append row 9 cột

## Cách dùng

```bash
# Setup lần đầu (chạy 1 lần)
python -m scripts.seed_categories   # tạo 7 categories trên webapp

# Publish bài
python -m scripts.publish article.md    # (cần wrapper script publish.py — agent sẽ implement)
```

Code Python:
```python
from scripts.auth_webapp import login
from scripts.markdown_to_html import convert
from scripts.cloudinary_uploader import upload
import requests, json, frontmatter

token = login()
post = frontmatter.load("article.md")
html = convert(post.content)
cover_url = upload(post["cover_image"])

response = requests.post(
    "https://resilient-expression-production-1149.up.railway.app/posts",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "title": post["title"], "slug": post["slug"],
        "content": html, "excerpt": post["excerpt"],
        "cover_image_url": cover_url,
        "category_id": post["category_id"], "is_published": True
    }
)
```

## Setup yêu cầu

1. Copy `config/settings.example.json` → `config/settings.json` và fill:
   ```json
   {
     "webapp_url": "https://resilient-expression-production-1149.up.railway.app",
     "webapp_email": "admin@hoaxuan.com",
     "webapp_password": "<password>",
     "cloudinary_url": "cloudinary://<key>:<secret>@<cloud_name>",
     "google_service_account": "/path/to/service-account.json",
     "google_sheet_id": "<sheet_id>",
     "drive_folder_id": "<folder_id>"
   }
   ```
2. `pip install requests python-frontmatter markdown cloudinary google-api-python-client`
3. Chạy `python -m scripts.seed_categories` lần đầu nếu webapp chưa có 7 categories chuẩn.

## Quy tắc

1. **KHÔNG hard-code credentials** trong script. Mọi config đọc từ `settings.json`.
2. **`is_published: false` cho draft** — chỉ set `true` khi đã review.
3. **Cache token JWT** (15 phút) để tránh login mỗi lần.
4. **Lưu publish_log** mỗi lần publish (kể cả fail) — để debug/audit.
5. **Cover image bắt buộc** — bài không cover trông thiếu chuyên nghiệp.

## Anti-patterns

- ❌ POST `/posts` không có Auth header → 401
- ❌ Upload cover image không resize → tốn Cloudinary bandwidth
- ❌ HTML có inline `<script>` (XSS risk) → check trong `markdown_to_html`
- ❌ Publish bài chưa có schema markup (mất AEO) — coordinate với `schema-markup-generator` trước
- ❌ Trùng slug → server trả 409 Conflict, phải đổi slug hoặc dùng update endpoint

## Liên kết

- Input từ: `seo-content-writer` (article.md), `schema-markup-generator` (JSON-LD inline)
- Output: log JSON cho tracker
- Reference: skill cũ — copy 6 scripts core (auth_webapp, markdown_to_html, cloudinary_uploader, image_processor, thumbnail_designer, seed_categories)
