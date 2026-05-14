# Google Setup — Service Account

Reference đầy đủ. Hướng dẫn step-by-step xem `SETUP.md` ở root.

## Scopes cần thiết

```python
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
```

## Khởi tạo client

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

creds = service_account.Credentials.from_service_account_file(
    settings["service_account_path"], scopes=SCOPES
)
docs = build("docs", "v1", credentials=creds)
sheets = build("sheets", "v4", credentials=creds)
drive = build("drive", "v3", credentials=creds)
```

## Tạo Doc trong folder cụ thể

Service Account API tạo Doc mặc định ở root Drive của SA (không thấy được). Phải:

1. Tạo Doc qua Drive API trong folder đã share:
   ```python
   file_metadata = {
       "name": title,
       "mimeType": "application/vnd.google-apps.document",
       "parents": [settings["drive_folder_id"]],
   }
   doc = drive.files().create(body=file_metadata, fields="id").execute()
   doc_id = doc["id"]
   ```

2. Insert content qua Docs API:
   ```python
   docs.documents().batchUpdate(
       documentId=doc_id,
       body={"requests": [...formatted requests...]}
   ).execute()
   ```

3. Trả share link: `https://docs.google.com/document/d/{doc_id}/edit`

## Tạo Sheet quản lý

Tương tự Doc, tạo qua Drive API với `mimeType="application/vnd.google-apps.spreadsheet"`.

Header row 9 cột (xem `sheet_schema.md`).

## Share Sheet về email user

Sau khi seed Sheet, tự share Editor cho `hoatulu00@gmail.com` để admin có thể edit:

```python
drive.permissions().create(
    fileId=sheet_id,
    body={"type": "user", "role": "writer", "emailAddress": "hoatulu00@gmail.com"},
    sendNotificationEmail=True,
).execute()
```

## Lưu ý quan trọng

- **Folder Drive PHẢI share Editor cho service account email** trước khi tạo file lần đầu, nếu không sẽ 403.
- Service account không có Drive personal — mọi file phải có `parents` trỏ về folder đã share.
- Quota: 60 read req/min/user, đủ cho skill chạy < 10 bài/ngày.
