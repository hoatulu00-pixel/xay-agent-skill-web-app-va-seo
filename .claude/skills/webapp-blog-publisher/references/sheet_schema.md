# Tracker Sheet Schema

Sheet name: `Hoa Xuan Blog Tracker`
Tab name: `Posts`

## Header row (A1:I1)

| Col | Header | Loại data | Auto-fill bởi | Admin sửa được |
|-----|--------|-----------|---------------|----------------|
| A | STT | Number | sheet_tracker (auto-increment) | ❌ (key) |
| B | Ngày đăng | Date `YYYY-MM-DD` | sheet_tracker (today nếu publish) | ✅ |
| C | Keyword | Text | research → primary keyword | ✅ |
| D | Tiêu đề bài viết | Text | content_writer | ✅ |
| E | Link Google Doc | URL | google_doc_writer | ❌ (auto) |
| F | Content Status | Enum | publisher | ✅ |
| G | Web Status | Enum | publisher | ✅ |
| H | Link Web | URL | publisher | ❌ (auto) |
| I | Notes | Text | publisher (error) hoặc admin | ✅ |

## Enum values

**Content Status:**
- `Pending` — admin pre-fill, chờ skill xử lý (mode `--from-queue`)
- `Drafting` — đang viết (intermediate)
- `Done` — Doc đã viết xong
- `Failed` — lỗi tạo Doc, xem cột Notes

**Web Status:**
- `Not yet` — chưa đăng
- `Publishing` — đang POST
- `Published` — đăng OK
- `Failed` — lỗi POST, xem Notes
- `Skip` — admin đánh dấu bỏ qua

## Conditional formatting (apply qua Sheets API)

- Content Status = `Done` → background green nhạt
- Content Status = `Failed` → background red nhạt
- Web Status = `Published` → bold + green
- Web Status = `Failed` → red

## Mode `--from-queue` query

```
Lọc rows có Content Status = "Pending"
Sort theo STT ascending
Lấy row đầu tiên → dùng cell C (Keyword) làm topic
Update row đó (không append mới)
```

## Cập nhật row tồn tại

Khi pipeline xong:
1. Tìm row theo STT (pre-stored khi pick từ queue)
2. Update các cell B, D, E, F, G, H bằng `sheets.values().update()`
3. Cột I (Notes) chỉ ghi đè nếu có error mới — preserve admin edit

## API call mẫu

```python
# Append mới
sheets.spreadsheets().values().append(
    spreadsheetId=tracker_sheet_id,
    range="Posts!A:I",
    valueInputOption="USER_ENTERED",
    insertDataOption="INSERT_ROWS",
    body={"values": [[stt, date, keyword, title, doc_link, "Done", "Published", web_link, ""]]}
).execute()

# Update theo row index
sheets.spreadsheets().values().update(
    spreadsheetId=tracker_sheet_id,
    range=f"Posts!B{row_idx}:I{row_idx}",
    valueInputOption="USER_ENTERED",
    body={"values": [[date, keyword, title, doc_link, "Done", "Published", web_link, notes]]}
).execute()
```
