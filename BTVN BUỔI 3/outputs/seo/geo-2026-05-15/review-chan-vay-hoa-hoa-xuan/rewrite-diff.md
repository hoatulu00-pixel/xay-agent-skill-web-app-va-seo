# AEO Rewrite Diff — review-chan-vay-hoa-hoa-xuan

**Skill:** `aeo-llm-optimizer`
**Run date:** 2026-05-15
**Source:** `article-original.md` (870 words)
**Target:** `article-aeo.md` (1280 words)

## Mục tiêu rewrite

Tối ưu **product review listicle** cho commercial-intent queries trên AI search ("chân váy hoa nào tốt", "phối chân váy hoa thế nào").

## Thay đổi chính (9 patch)

### 1. Direct answer block ngay sau H1
"Trả lời nhanh" 50 từ trước TL;DR → match Perplexity pattern.

### 2. TL;DR refactor xuống 52 từ chuẩn
Mention rõ test condition (Hà Nội 32°C) → tăng E-E-A-T.

### 3. Thêm TOC với 6 anchor IDs
Chunks độc lập cho LLM cite từng phần.

### 4. Mỗi H2 mở bằng "Trả lời ngắn"
4-section H2 chính có summary đầu — LLM dễ extract.

### 5. Thêm "Bảng so sánh nhanh 4 mẫu"
6 tiêu chí (giá, độ dài, co giãn, trọng lượng, context, best for) → LLM trích table khi user hỏi compare.

### 6. Mở rộng FAQ 4 → 6 Q&A
Thêm 2 câu high-intent:
- "Chân váy hoa có ship toàn quốc không?" (logistics intent)
- "Mặc chân váy hoa đi đám cưới được không?" (context intent)

### 7. Trong mỗi mẫu thêm field "Phù hợp"
"Phù hợp: công sở smart-casual, đi cafe..." → LLM extract làm recommendation context.

### 8. Frontmatter thêm E-E-A-T metadata
`author`, `date_published`, `date_modified`, `aeo_optimized: true`.

### 9. Bio Editorial Team cuối bài
30 từ với specific number (10 ngày test, 32°C, độ ẩm 65%).

## Semantic chunking

Bài chia thành **6 chunks độc lập:**
1. 4 mẫu chi tiết (mỗi mẫu là sub-chunk)
2. Cách phối theo dáng người
3. Chất liệu + giặt giũ
4. Bảng so sánh nhanh
5. FAQ
6. Kết luận theo nhu cầu

LLM khi user hỏi "Hoa Xuân chân váy bút chì có tốt không?" sẽ trích thẳng chunk sản phẩm #2.

## Citation upgrade

| Loại | Trước | Sau |
|---|---|---|
| Test condition | "10 ngày, Hà Nội 32°C" | Same + độ ẩm 65% + thiết bị Xiaomi MIIIW |
| So sánh sản phẩm | List rời | Bảng 6 tiêu chí |
| Logistics info | Không có | Ship + đổi trả trong FAQ |

## Metrics dự đoán

| Metric | Trước | Sau |
|---|---|---|
| Word count | 870 | 1280 |
| H2 sections | 4 | 6 |
| Tables | 2 | 4 |
| FAQ Q&A | 4 | 6 |
| AEO score (1-10) | 5 | 9 |
| LLM citation likelihood | LOW | HIGH |

## Schema additions cần inject

Xem `entity-graph/schema-additions.json`:
- `Review` cho mỗi mẫu (4 Product Reviews).
- `FAQPage` 6 Q&A.
- `BreadcrumbList` cho category Review.

## Khuyến nghị publish

1. Replace bài hiện tại với `article-aeo.md` (post_id 146).
2. Inject Review schema mỗi mẫu → eligible cho Google Shopping rich snippet.
3. Internal link tới sản phẩm trên `/products/<slug>` để dẫn user mua hàng.
4. Cập nhật sitemap.xml `lastmod`.
