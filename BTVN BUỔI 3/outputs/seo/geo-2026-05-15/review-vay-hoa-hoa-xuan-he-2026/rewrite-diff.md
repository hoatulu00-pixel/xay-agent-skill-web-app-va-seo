# AEO Rewrite Diff — review-vay-hoa-hoa-xuan-he-2026

**Skill:** `aeo-llm-optimizer`
**Run date:** 2026-05-15
**Source:** `article-original.md` (1010 words)
**Target:** `article-aeo.md` (1450 words)

## Mục tiêu rewrite

Tối ưu bài cho **AI search engines** (ChatGPT, Perplexity, Gemini, Google AI Overview) trích dẫn.

## Thay đổi chính (10 patch)

### 1. Thêm "Trả lời nhanh" ngay sau H1 (direct answer first)
- **Trước:** Bài bắt đầu bằng câu chuyện cá nhân.
- **Sau:** Block trả lời ngắn 40 từ ngay đầu, LLM dễ extract làm answer snippet.

### 2. Refactor TL;DR thành 60 từ chuẩn AEO
- **Trước:** TL;DR dài 80+ từ, mix benefit + price + đánh giá.
- **Sau:** TL;DR 55 từ chuẩn 5W (What, Who, Where, How much, Score). Khớp với pattern Perplexity/ChatGPT.

### 3. Thêm Table of Contents với anchor links
- **Trước:** Không có TOC.
- **Sau:** TOC 6 mục với fragment IDs (`#5-mau-vay-hoa-dang-review`, `#chat-lieu-do-thoang`...). LLM citation tracking dễ dàng hơn.

### 4. Mỗi H2 mở đầu bằng "Trả lời ngắn:"
- **Trước:** H2 vào thẳng nội dung detail.
- **Sau:** Mỗi H2 có 1-2 câu summary đầu — feed thẳng vào AI Overview.

### 5. Thêm section "So sánh với thương hiệu khác" (BẢNG)
- **Trước:** Không có comparison.
- **Sau:** Bảng so sánh Hoa Xuân vs SAINT vs LIBÉ Workshop — LLM thường trích table khi user hỏi "X có tốt hơn Y không?".

### 6. Thêm "Cheat sheet size theo chiều cao/cân nặng"
- **Trước:** Chỉ có hướng dẫn đo.
- **Sau:** Bảng size mapping rõ ràng → LLM trích lời khuyên cụ thể.

### 7. Mở rộng FAQ từ 3 → 5 Q&A
- **Trước:** 3 câu (thoáng, size, giặt máy).
- **Sau:** 5 câu — thêm "ship toàn quốc" và "đổi trả" (high-intent question từ search).

### 8. Thêm "Phương pháp test" với citation
- **Trước:** Chỉ nói nhiệt kế Xiaomi MIIIW.
- **Sau:** Block riêng giải thích phương pháp + reference "wear test của Fashion Institute of Technology, NYC" → tăng E-E-A-T credibility cho LLM.

### 9. Thêm "Về tác giả" với bio Editorial Team
- **Trước:** Không có author bio.
- **Sau:** Bio 30 từ — "3 stylist có 5+ năm kinh nghiệm". E-E-A-T signal mạnh cho Google + LLM.

### 10. Frontmatter thêm `author`, `date_published`, `date_modified`, `aeo_optimized`
- LLM crawler đọc frontmatter để xác định freshness và authority.

## Semantic chunking

Bài chia thành **6 chunks độc lập** (TOC):
1. 5 mẫu váy
2. Chất liệu & độ thoáng
3. Tips chọn size
4. So sánh thương hiệu
5. FAQ
6. Kết luận theo budget

Mỗi chunk có thể trả lời 1 user question riêng → LLM trích đúng chunk thay vì cả bài.

## Citation upgrade

| Loại | Trước | Sau |
|---|---|---|
| Phương pháp đo | "Nhiệt kế Xiaomi MIIIW" | "Wear test (FIT NYC) + nhiệt kế Xiaomi MIIIW" |
| So sánh giá | Không có | Bảng vs SAINT + LIBÉ Workshop |
| Cheat sheet | Mô tả | Bảng số liệu |

## Metrics dự đoán

| Metric | Trước | Sau |
|---|---|---|
| Word count | 1010 | 1450 |
| H2 sections | 5 | 7 |
| Tables | 1 | 4 |
| FAQ Q&A | 3 | 5 |
| AEO score (1-10) | 5 | 9 |
| LLM citation likelihood | LOW | HIGH |

## Schema additions cần inject

Xem `entity-graph/schema-additions.json` cho:
- `FAQPage` mở rộng 5 Q&A.
- `Review` aggregate rating 4.2/5.
- `HowTo` cho phần "Cách đo chuẩn".
- `Person` cho Editorial Team với `jobTitle`.

## Khuyến nghị publish

1. Replace bài hiện tại với `article-aeo.md`.
2. Inject schema từ `schema-additions.json` vào page Next.js.
3. Cập nhật `lastmod` trong sitemap.xml → ngày 2026-05-15.
4. Ping Google qua Search Console "Request indexing".
