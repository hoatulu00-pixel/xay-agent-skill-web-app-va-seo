---
name: content-brief-builder
description: Sinh content brief 1 trang cho writer SEO từ keyword research output — bao gồm intent, content type, outline H2-H3, internal link gợi ý, FAQ candidates, target word count. Kích hoạt khi user nói "tạo brief", "content brief cho bài X", "outline cho writer", "brief 1 trang". Output là brief.md đầy đủ cho agent seo-content-writer dùng.
---

# Skill: Content Brief Builder

Tạo brief 1 trang giúp writer (human hoặc AI) viết bài SEO hiệu quả.

## Khi nào kích hoạt

- "Tạo brief cho topic 'váy hoa hè 2026'"
- "Lên brief cho 5 bài blog tháng sau"
- Agent `seo-content` đã có keyword research, cần brief trước khi viết

## Input

Output từ `vn-keyword-research`:
```json
{
  "topic": "váy hoa mùa hè",
  "primary_keyword": "váy hoa mùa hè",
  "secondary_keywords": [...],
  "questions": [...],
  "related_searches": [...]
}
```

## Output

File `brief.md` lưu vào `BTVN BUỔI 3/outputs/seo/<date>_<slug>/`:
```markdown
# Content Brief — Cách phối váy hoa mùa hè 2026

## Metadata
- **Primary keyword**: váy hoa mùa hè
- **Secondary keywords**: váy hoa nhí mùa hè, váy hoa dáng dài, cách phối váy hoa
- **Intent**: informational (how-to + listicle hybrid)
- **Content type**: how_to (template: how_to.md)
- **Target word count**: 1200-1500 từ
- **Target audience**: phụ nữ 18-30, sống đô thị, thu nhập trung bình-cao
- **Category**: Phối đồ (category_id: 3)

## Title gợi ý
1. Cách phối váy hoa mùa hè 2026: 5 outfit dễ áp dụng
2. 5 cách phối váy hoa mùa hè sang chảnh, dễ mặc

## Meta description (150-160 ký tự)
Khám phá 5 cách phối váy hoa mùa hè 2026 sành điệu, từ váy hoa nhí cho buổi hẹn cuối tuần đến váy hoa dáng dài cho dạo phố. Click xem ngay!

## Outline (H2-H3)
1. ## Tại sao váy hoa là must-have mùa hè?
2. ## 5 cách phối váy hoa mùa hè 2026
   - ### 1. Váy hoa nhí + sandal đế bệt (casual)
   - ### 2. Váy hoa dáng dài + giày cao gót (dạo phố)
   - ### 3. Váy hoa crop + quần ống suông (Y2K style)
   - ### 4. Váy hoa midi + áo khoác denim (office casual)
   - ### 5. Váy hoa maxi + dép xăng đan (đi biển)
3. ## Cách chọn váy hoa hợp dáng người
   - ### Dáng người mảnh
   - ### Dáng người cong
4. ## Câu hỏi thường gặp (FAQ)
   - Q: Váy hoa mùa hè mặc với giày gì?
   - Q: Cách phối váy hoa cho người béo?
   - Q: Váy hoa có lỗi mốt không?

## Internal links bắt buộc (1-2)
- `/category/phoi-do` (Category Phối đồ)
- `/blog/cach-phoi-vay-mua-xuan` (bài liên quan đã có)

## TL;DR (40-60 từ) — viết ngay sau intro
Váy hoa mùa hè 2026 phối tốt nhất với giày sandal đế bệt + túi rơm cho phong cách casual, hoặc giày cao gót + clutch cho buổi tối. 5 outfit dưới đây dễ áp dụng, phù hợp dáng người Việt Nam, từ casual đến dạy phố.

## CTA cuối bài
"Khám phá thêm bộ sưu tập Hoa Xuân Fashion mùa hè 2026 tại [link products]"

## Tài liệu tham khảo
- Vogue Vietnam — trend báo cáo
- Pinterest summer 2026 board
```

## Files trong skill

- `templates/brief.md` — template skeleton với placeholders
- `scripts/build_brief.py` — auto-fill placeholders từ keyword research input
- `references/intent-types.md` — định nghĩa 4 intent types + mapping → content type

## Workflow

1. **Đọc keyword research output** (`keywords.json`).
2. **Classify intent** (informational/commercial/transactional/navigational) dựa trên question patterns:
   - "cách", "làm sao", "tại sao" → informational
   - "mua", "giá", "ở đâu" → commercial/transactional
3. **Pick content type** dựa intent + topic (xem `references/content-types.md` trong `seo-content-writer` skill).
4. **Estimate word count** dựa content type:
   - how_to: 1200-1800
   - listicle: 1500-2200
   - trend_report: 1800-2500
   - styling_guide: 1000-1500
5. **Suggest internal links**: scan sitemap (qua `webapp-blog-publisher`) hoặc category list, pick 1-2 link liên quan nhất.
6. **Generate 3 FAQ candidates** từ `questions[]` trong keyword research.
7. **Write brief.md** theo template.

## Quy tắc

1. **Brief phải actionable** — writer cầm brief là viết được luôn, không hỏi lại.
2. **Outline cụ thể** (H2 + H3 nếu cần), không vague (`## Some heading`).
3. **TL;DR draft sẵn** 40-60 từ — writer chỉ refine, không tự nghĩ.
4. **Internal links có URL thật** (check tồn tại trước, không bịa).
5. **Title 2-3 options** để writer A/B pick.

## Anti-patterns

- ❌ Brief generic kiểu "viết bài về váy hoa mùa hè" (writer phải tự nghĩ outline)
- ❌ Outline H2-only, thiếu H3 → bài thiếu depth
- ❌ Suggest internal link đến URL không tồn tại
- ❌ Word count không realistic (vd: 500 từ cho listicle 10 items)
- ❌ FAQ candidates copy từ keyword research mà không refine

## Liên kết

- Input từ: `vn-keyword-research`
- Output cho: `seo-content-writer`
- Agent dùng: `seo-content`
