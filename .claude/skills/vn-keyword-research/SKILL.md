---
name: vn-keyword-research
description: Research keyword tiếng Việt từ Google autocomplete, People Also Ask (PAA), related searches. Kích hoạt khi user nói "research keyword", "tìm keyword tiếng Việt", "tìm topic SEO", "Google autocomplete", "PAA", hoặc khi agent seo-content cần input keyword trước viết bài. Output JSON với primary + secondary keywords + questions.
---

# Skill: Vietnamese Keyword Research

Research keyword cho thị trường Việt Nam, không cần API trả phí — dùng Google scraping miễn phí.

## Khi nào kích hoạt

- User: "research keyword 'váy hoa hè'", "tìm keyword cho topic ...", "Google autocomplete cho X"
- User: "tìm topic SEO mùa hè 2026"
- Agent `seo-content` cần keyword input trước khi viết bài hoặc tạo brief

## Input

- **Topic** (string, bắt buộc): chủ đề gốc bằng tiếng Việt. VD: "váy hoa mùa hè", "cách phối đầm dự tiệc"

## Output

JSON file `keywords.json` lưu vào `BTVN BUỔI 3/outputs/seo/<date>_<slug>/` hoặc trả về stdout:

```json
{
  "topic": "váy hoa mùa hè",
  "primary_keyword": "váy hoa mùa hè",
  "secondary_keywords": [
    "váy hoa nhí mùa hè",
    "váy hoa dáng dài mùa hè",
    "cách phối váy hoa mùa hè",
    "..."
  ],
  "questions": [
    "Váy hoa mùa hè mặc với gì?",
    "Cách phối váy hoa cho người béo?",
    "..."
  ],
  "related_searches": ["..."],
  "search_volume_estimate": "high|medium|low (heuristic)"
}
```

## Files trong skill

- `scripts/keyword_research.py` — main entrypoint, scrape Google autocomplete + PAA
- `scripts/topic_expander.py` — mở rộng topic thành 3-5 biến thể câu hỏi ("là gì", "cách", "tại sao", "ở đâu", "khi nào")

## Cách dùng

```bash
python -m scripts.keyword_research "váy hoa mùa hè"
# hoặc với topic expansion trước:
python -m scripts.topic_expander "váy hoa" | python -m scripts.keyword_research
```

Trong code Python:
```python
from scripts.keyword_research import research
result = research(topic="váy hoa mùa hè", num_secondary=8, num_questions=5)
```

## Quy tắc

1. **Topic input phải tiếng Việt có dấu** (không "vay hoa mua he").
2. **Output luôn JSON serializable**, lưu file theo path agent quy định.
3. **Fallback khi scraping fail**: trả về topic gốc + biến thể tự sinh, không crash.
4. **Rate limit**: 1 request/giây, không bulk scrape (tránh Google block IP).
5. **Validate output**: `primary_keyword` không rỗng, `secondary_keywords` ≥3, `questions` ≥3.

## Anti-patterns

- ❌ Hardcode keyword (không thực sự research)
- ❌ Bulk scrape >50 topics/lần (Google sẽ block)
- ❌ Trả về raw Google response (phải parse + clean)
- ❌ Bỏ qua "People Also Ask" — nguồn câu hỏi vàng cho AEO

## Liên kết

- Skill kế tiếp trong pipeline: `content-brief-builder` (dùng keyword để tạo brief)
- Reference: skill cũ `seo-content-workspace/.claude/skills/seo-content-publisher` (đã refactor lấy 2 scripts từ đó)
