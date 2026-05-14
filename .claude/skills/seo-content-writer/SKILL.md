---
name: seo-content-writer
description: Viết bài blog Markdown chuẩn SEO + AEO cho Hoa Xuân Fashion theo 1 trong 7 content types (how_to, listicle, trend_report, styling_guide, product_review, care_guide, behind_scenes). Kích hoạt khi user nói "viết bài SEO", "compose article", "write content theo template", hoặc khi agent seo-content cần output Markdown từ brief. Input là brief (hoặc keyword + intent + outline), output là article.md hoàn chỉnh.
---

# Skill: SEO Content Writer

Compose bài blog Markdown chuẩn SEO on-page + AEO từ brief hoặc keyword research output.

## Khi nào kích hoạt

- User: "viết bài về váy hoa mùa hè", "compose article từ brief này", "write content theo template how_to"
- Agent `seo-content` đã có keyword research + brief, cần viết bài cuối cùng
- User: "lên outline + viết bài"

## Input

1 trong 2 format:

**A) Brief đầy đủ** (preferred):
```json
{
  "title_hint": "Cách phối váy hoa mùa hè 2026",
  "primary_keyword": "váy hoa mùa hè",
  "secondary_keywords": ["..."],
  "questions": ["..."],
  "intent": "informational",
  "content_type": "how_to",
  "outline": [...],
  "internal_links": ["/blog/...", "/category/..."],
  "category_id": 3
}
```

**B) Quick mode** (keyword + topic, skill tự sinh brief inline):
```json
{ "topic": "váy hoa mùa hè", "content_type": "how_to" }
```

## Output

File `article.md` với frontmatter + body:
```markdown
---
title: "Cách phối váy hoa mùa hè 2026: 5 outfit gợi ý"
slug: "cach-phoi-vay-hoa-mua-he-2026"
meta_description: "Khám phá 5 cách phối váy hoa mùa hè 2026 sành điệu..."
excerpt: "..."
cover_image: "vay-hoa-cover.jpg"
category_id: 3
tags: ["váy hoa", "phối đồ", "mùa hè"]
---

# Cách phối váy hoa mùa hè 2026: 5 outfit gợi ý

> **TL;DR:** Váy hoa mùa hè 2026 phối tốt nhất với giày sandal đế bệt + túi rơm... (40-60 từ direct answer)

## Tại sao váy hoa là must-have mùa hè?
(content...)

## 5 cách phối váy hoa mùa hè
### 1. Váy hoa nhí + sandal đế bệt
(content + ảnh alt text)

...

## Câu hỏi thường gặp (FAQ)
**Q1: Váy hoa mùa hè mặc với giày gì?**
A: ...

**Q2: ...**
```

## Files trong skill

- `scripts/intent_analyzer.py` — phân loại intent (informational/commercial/transactional)
- `scripts/category_classifier.py` — map intent → 1 trong 7 content types + category webapp
- `scripts/outline_generator.py` — sinh outline H1-H3 từ template
- `assets/article_templates/*.md` — 7 template (how_to, listicle, trend_report, styling_guide, product_review, care_guide, behind_scenes)
- `assets/prompts/*.txt` — 3 prompt: intent_prompt, outline_prompt, writing_prompt
- `assets/outline_template.md` — outline skeleton chung
- `references/seo_checklist.md` — 30 tiêu chí SEO on-page
- `references/aeo_guidelines.md` — AEO patterns chi tiết
- `references/content_types.md` — đặc điểm mỗi content type

## Workflow nội bộ

1. **Classify intent** (`intent_analyzer.py`) → informational/commercial/transactional/navigational
2. **Pick content type** (`category_classifier.py`) → 1 trong 7
3. **Generate outline** (`outline_generator.py`) → load `assets/article_templates/<type>.md`, fill primary/secondary keywords vào H2
4. **Compose bài** theo `writing_prompt.txt` + checklist trong `seo_checklist.md`:
   - Title ≤60 ký tự, có primary keyword
   - Meta description 150-160 ký tự
   - TL;DR 40-60 từ ngay sau intro (AEO requirement)
   - H1 unique, H2 chứa secondary keywords
   - Mỗi 300 từ có 1 heading
   - FAQ ≥3 câu cuối bài (AEO)
   - Alt text mô tả cho ảnh
   - 1-2 internal links sang category hoặc bài liên quan

## Cách dùng

```bash
# Mode 1: từ brief
python -m scripts.outline_generator --brief brief.json --output outline.md
# Tự agent viết article.md theo outline (LLM step, không phải script)

# Mode 2: phân tích intent + content type
python -m scripts.intent_analyzer "váy hoa mùa hè"
python -m scripts.category_classifier --intent informational --topic "váy hoa"
```

## Quy tắc

1. **Bắt buộc check** `references/seo_checklist.md` trước khi finalize bài.
2. **Bắt buộc có** TL;DR + FAQ section (AEO).
3. **Mỗi bài lưu artifact** `article.md` + `meta.json` (frontmatter parsed) vào `BTVN BUỔI 3/outputs/seo/<date>_<slug>/`.
4. **Tiếng Việt có dấu**, không dịch máy từ tiếng Anh, dùng từ chuyên ngành thời trang phổ biến.
5. **Internal link** trỏ vào URL tồn tại (check qua `webapp-blog-publisher` skill hoặc sitemap).

## Anti-patterns

- ❌ Bài <500 từ (too thin) hoặc >3000 từ (over-bloat cho fashion niche)
- ❌ Title >60 ký tự (truncate SERP)
- ❌ Thiếu TL;DR → mất AEO opportunity
- ❌ FAQ <3 câu hoặc không có
- ❌ Trùng heading H2 (mỗi H2 unique)
- ❌ Keyword stuffing (density >3%)

## Liên kết

- Input từ: `vn-keyword-research`, `content-brief-builder`
- Output cho: `webapp-blog-publisher` (publish lên Hoa Xuân), `aeo-llm-optimizer` (refine cho LLM)
- Reference: skill cũ `seo-content-workspace/.claude/skills/seo-content-publisher`
