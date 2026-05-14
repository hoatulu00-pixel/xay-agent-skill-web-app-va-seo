# Outline Skeleton (chung cho mọi content type)

```
# {{title — chứa primary_keyword, ≤60 ký tự}}

> **Tóm tắt nhanh:** {{40-60 từ trả lời thẳng câu hỏi chính}}

## {{H2 #1 — câu hỏi chính, chứa primary_keyword}}

{{paragraph 40-80 từ trả lời trực tiếp}}

{{nội dung mở rộng, có bullet list nếu là so sánh}}

## {{H2 #2 — secondary keyword}}

{{...}}

### {{H3 con nếu cần chia nhỏ}}

## {{H2 #3 — secondary keyword khác}}

{{...}}

## {{H2 #4 — tips/lưu ý}}

{{...}}

## Câu hỏi thường gặp

### {{Question 1 từ "People also ask"}}

{{30-60 từ}}

### {{Question 2}}

{{30-60 từ}}

### {{Question 3}}

{{30-60 từ}}

## Lời kết

{{2-3 câu CTA về Hoa Xuân Fashion + internal link sang category page}}
```

---

## Frontmatter (parse bởi `webapp_publisher.py`)

```yaml
---
title: "{{title}}"
excerpt: "{{meta description 150-160 ký tự}}"
cover_image: "{{optional URL hoặc path local}}"
content_type: "{{how_to|listicle|trend_report|...}}"
primary_keyword: "{{kw}}"
secondary_keywords: ["kw1", "kw2", "kw3"]
---
```

Nếu `cover_image` không có → `webapp_publisher.py` sẽ skip upload, post không cover.
