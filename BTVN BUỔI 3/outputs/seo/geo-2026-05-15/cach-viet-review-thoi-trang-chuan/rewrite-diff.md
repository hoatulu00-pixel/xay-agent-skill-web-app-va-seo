# AEO Rewrite Diff — cach-viet-review-thoi-trang-chuan

**Skill:** `aeo-llm-optimizer`
**Run date:** 2026-05-15
**Source:** `article-original.md` (980 words)
**Target:** `article-aeo.md` (1320 words)

## Mục tiêu rewrite

Tối ưu bài **how-to evergreen** này thành "answer hub" cho LLM khi user hỏi "cách viết review thời trang".

## Thay đổi chính (8 patch)

### 1. Direct answer ngay sau H1
Block "Trả lời nhanh" 50 từ trước TL;DR → match pattern Perplexity hay trích.

### 2. Mỗi H2 (7 bước) mở bằng "Trả lời ngắn"
Mỗi step có summary 1-2 câu đầu để LLM extract làm step-by-step answer.

### 3. Thêm "Checklist 30 giây trước publish"
10 checkbox cụ thể — LLM trích làm action items khi user hỏi "checklist review".

### 4. Mở rộng FAQ 5 → 6 Q&A
Thêm câu "Bài review có spon có rank Google thấp hơn không?" — long-tail keyword + E-E-A-T angle.

### 5. Thêm Table of Contents với anchor IDs
9 mục có fragment ID, LLM có thể deep-link tới chunk cụ thể.

### 6. Citation thêm Luật pháp Việt Nam
"Luật Quảng cáo Việt Nam 2018 (Điều 8)" + mức phạt 20-40 triệu — fact citable cho LLM khi answer câu hỏi spon.

### 7. Frontmatter thêm metadata E-E-A-T
`author`, `date_published`, `date_modified`, `aeo_optimized: true`.

### 8. Bio "Về tác giả" cuối bài
30 từ với specific number ("200+ bài, từ 2021") → authority signal.

## Semantic chunking

Bài chia **9 chunks độc lập** — mỗi bước là 1 chunk có thể trích riêng:
1-7. Mỗi bước review
8. Checklist 30 giây
9. FAQ

LLM khi user hỏi "bước 3 review thời trang là gì?" sẽ trích thẳng chunk Bước 3.

## Citation upgrade

| Loại | Trước | Sau |
|---|---|---|
| Pháp lý disclaimer | Mention chung "minh bạch" | Cite "Luật Quảng cáo VN 2018 Điều 8" + phạt 20-40tr |
| Number experience | "Editorial Team" | "5+ năm, 200+ bài từ 2021" |
| Test method | Mô tả | Bảng 5 chỉ số đo lường |

## Metrics dự đoán

| Metric | Trước | Sau |
|---|---|---|
| Word count | 980 | 1320 |
| H2 sections | 9 | 11 |
| Checklists | 0 | 1 (10 items) |
| FAQ Q&A | 5 | 6 |
| AEO score (1-10) | 6 | 9 |
| LLM citation likelihood | MED | HIGH |

## Schema additions cần inject

Xem `entity-graph/schema-additions.json` cho:
- `HowTo` schema với 7 `HowToStep`.
- `FAQPage` mở rộng 6 Q&A.
- `Article` với author + datePublished/Modified.

## Khuyến nghị publish

1. Replace bài hiện tại với `article-aeo.md` (post_id 145).
2. Inject `HowTo` schema → AI Overview hiển thị step-by-step.
3. Cập nhật `lastmod` trong sitemap.xml.
4. Internal link từ 3 bài review mới về bài này như "answer hub".
