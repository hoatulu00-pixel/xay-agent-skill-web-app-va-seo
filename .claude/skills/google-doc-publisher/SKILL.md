---
name: google-doc-publisher
description: Tạo Google Doc formatted (headings, lists, tables) trong Google Drive folder và share permission cho team review. Kích hoạt khi user nói "tạo Google Doc", "export to Drive", "share bài cho team marketing review", "xuất Doc cho client". Input là Markdown hoặc rich content, output là Doc URL có share link.
---

# Skill: Google Doc Publisher

Tạo Google Doc formatted từ Markdown/text + share link cho team marketing review trước khi publish lên webapp.

## Khi nào kích hoạt

- User: "tạo Google Doc cho bài này", "export Doc"
- User: "share bài cho marketing review trước khi publish"
- Agent `seo-geo` cần xuất bài đã rewrite AEO ra Doc cho team approve
- Pipeline `/seo-publish` cần Doc làm intermediate artifact

## Input

```json
{
  "title": "Cách phối váy hoa mùa hè 2026: 5 outfit gợi ý",
  "content_markdown": "# ...",
  "drive_folder_id": "<folder_id>",      // optional, default từ settings
  "share_emails": ["marketing@hoaxuan.com"],   // optional
  "share_permission": "writer"            // reader/commenter/writer
}
```

## Output

```json
{
  "doc_id": "1AbC...XYZ",
  "doc_url": "https://docs.google.com/document/d/1AbC...XYZ/edit",
  "drive_folder": "Hoa Xuân SEO Review",
  "share_status": ["marketing@hoaxuan.com: writer"]
}
```

## Files trong skill

- `scripts/auth_google.py` — Service Account auth, trả `(docs, sheets, drive)` clients
- `references/google_setup.md` — hướng dẫn tạo Service Account + share Drive folder cho email service account

## Workflow nội bộ

1. **Parse Markdown** thành structured blocks (headings, paragraphs, lists, tables, links, images).
2. **Auth Google** qua Service Account (`auth_google.get_clients()`).
3. **Tạo Doc trong Drive folder** (parent = `drive_folder_id`):
   ```python
   doc = docs.documents().create(body={"title": title}).execute()
   ```
4. **Insert content theo block**:
   - Headings → apply Heading 1/2/3 style
   - Bold, italic → text styling
   - Lists → bulleted/numbered
   - Links → hyperlink
   - Images → insertInlineImage (cần URL public)
5. **Share** qua Drive API permissions (nếu có `share_emails`):
   ```python
   drive.permissions().create(
       fileId=doc_id,
       body={"role": "writer", "type": "user", "emailAddress": email}
   ).execute()
   ```
6. **Lưu log** vào `BTVN BUỔI 3/outputs/seo/<date>_<slug>/doc_publish_log.json`.

## Setup yêu cầu

Xem `references/google_setup.md` chi tiết. Tóm tắt:

1. Tạo Google Cloud Project → enable Docs API + Drive API
2. Tạo Service Account, download JSON key
3. Đường dẫn JSON key cấu hình trong `config/settings.json` (cùng config với `webapp-blog-publisher`):
   ```json
   { "google_service_account": "/abs/path/to/service-account.json" }
   ```
4. Tạo Drive folder "Hoa Xuân SEO Review" trên Drive, share với email service account (quyền Editor) → lấy folder ID
5. `pip install google-api-python-client google-auth google-auth-httplib2`

## Cách dùng

```python
from scripts.auth_google import get_clients
# google_doc_writer.py sẽ được agent implement nếu chưa có, dựa trên workflow ở trên

clients = get_clients()
docs, sheets, drive = clients
# ... (logic tạo Doc, xem workflow)
```

## Quy tắc

1. **Doc title = bài title** (không thêm prefix/suffix).
2. **Folder mặc định**: "Hoa Xuân SEO Review" — share trước cho service account.
3. **Permission mặc định**: `commenter` (đủ để review, không sửa accidentally). Set `writer` chỉ khi yêu cầu rõ.
4. **Image trong Doc**: phải là URL public (đã upload Cloudinary trước qua `webapp-blog-publisher`).
5. **Lưu log** kể cả fail (log error vào log JSON).

## Anti-patterns

- ❌ Tạo Doc trong My Drive (root) thay vì Drive folder đã share → loose tracking
- ❌ Share `anyone with link` mà không cần thiết → security concern
- ❌ Insert plain text thay vì formatted (mất heading hierarchy)
- ❌ Embed ảnh local path (Doc API chỉ accept URL public)
- ❌ Tạo Doc trùng title nhiều lần (Drive cho phép, nhưng confusing)

## Liên kết

- Input từ: `seo-content-writer` (Markdown), `aeo-llm-optimizer` (Markdown rewrite)
- Output: link Doc cho team review
- Reference: skill cũ `seo-content-workspace/.claude/skills/seo-content-publisher` (đã copy `auth_google.py` + `google_setup.md`)
