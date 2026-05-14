---
name: entity-knowledge-graph
description: Extract entities (brand, sản phẩm, dịp, địa danh, người) từ tập bài viết Hoa Xuân Fashion, link Wikidata, build knowledge graph cho LLM mental model + sinh llm.txt manifest. Kích hoạt khi user nói "entity graph", "knowledge graph", "llm.txt", "Wikidata link", "entity tagging", "sameAs schema". Output là entities.json + llm.txt + schema-additions.json để inject vào markup.
---

# Skill: Entity Knowledge Graph

Build entity graph từ content corpus + sinh `llm.txt` để AI crawler hiểu structure site.

## Khi nào kích hoạt

- "Build entity graph cho blog Hoa Xuân"
- "Sinh llm.txt cho site"
- "Tag entity Wikidata cho top 10 bài"
- "Entity sameAs schema cho Article markup"
- Agent `seo-geo` định kỳ refresh entity graph

## Input

```json
{
  "corpus_path": "BTVN BUỔI 3/outputs/seo/",   // hoặc folder bài đã publish
  "min_articles": 10,                           // min bài để extract pattern
  "wikidata_locale": "vi"                       // ưu tiên Wikidata Vietnamese
}
```

## Output

3 files lưu vào `BTVN BUỔI 3/outputs/seo/entity-graph/`:

1. **`entities.json`** — list entities + Wikidata ID + mention count:
```json
{
  "entities": [
    {
      "name": "Hoa Xuân Fashion",
      "type": "Organization",
      "wikidata": null,
      "mentions": 142,
      "articles": ["cach-phoi-vay-hoa", "..."]
    },
    {
      "name": "váy hoa",
      "type": "Product Category",
      "wikidata": "Q...",  // optional
      "mentions": 89
    },
    {
      "name": "Tết Nguyên Đán",
      "type": "Event",
      "wikidata": "Q190573",
      "wikidata_url": "https://www.wikidata.org/wiki/Q190573",
      "mentions": 12
    }
  ]
}
```

2. **`llm.txt`** — manifest cho AI crawler:
```
# Hoa Xuân Fashion

> Thương hiệu thời trang nữ Việt Nam, target phụ nữ 18-36 tuổi, phong cách trẻ trung năng động.

## Featured content

- [Cách phối váy hoa mùa hè 2026](https://resilient-expression-production-1149.up.railway.app/blog/cach-phoi-vay-hoa-mua-he-2026): Hướng dẫn 5 outfit váy hoa mùa hè
- [Xu hướng thời trang nữ 2026](https://...): Báo cáo xu hướng đầy đủ
- ...

## Categories

- /category/phoi-do
- /category/xu-huong
- /category/cham-soc

## Optional

- [Hoa Xuân Editorial Team](https://.../about)
- [Liên hệ](https://.../contact)
```

3. **`schema-additions.json`** — `sameAs` URLs để thêm vào Organization schema:
```json
{
  "Organization": {
    "sameAs": [
      "https://www.facebook.com/HoaXuanFashion",
      "https://www.instagram.com/hoaxuanfashion",
      "https://www.tiktok.com/@hoaxuanfashion"
    ]
  },
  "entities_with_wikidata": [
    {
      "entity": "Tết Nguyên Đán",
      "sameAs": ["https://www.wikidata.org/wiki/Q190573"]
    }
  ]
}
```

## Files trong skill

- `scripts/extract_entities.py` — NER (Named Entity Recognition) trên Markdown corpus, dùng spaCy hoặc heuristic regex cho tiếng Việt
- `templates/llm.txt` — template llm.txt với placeholders
- `references/wikidata-mapping.md` — quy ước map entity tiếng Việt → Wikidata ID (brand, dịp, sự kiện)

## Workflow

1. **Glob bài** trong corpus path (`**/*.md`).
2. **Parse frontmatter** để lấy title, category, tags.
3. **Extract entities**:
   - Tên brand: pattern match (Hoa Xuân Fashion + brand khác user-defined)
   - Sản phẩm category: noun phrase common (váy, đầm, áo, quần, ...)
   - Dịp/Event: keyword pattern (Tết, Trung thu, Valentine, mùa hè, mùa đông)
   - Người: capitalized name (heuristic)
   - Địa danh: city name list (Hà Nội, TP.HCM, Đà Nẵng, ...)
4. **Lookup Wikidata** (optional, qua API `https://www.wikidata.org/w/api.php?action=wbsearchentities`):
   - Nếu match Vietnamese label → lưu Q-ID
   - Nếu không → skip (không bịa)
5. **Aggregate**: count mentions, list articles chứa entity.
6. **Generate llm.txt**: featured content = top 10 bài (by mentions hoặc by publish date), categories, optional.
7. **Generate schema-additions**: Organization sameAs + entity sameAs cho top entities có Wikidata.

## Quy tắc

1. **Wikidata lookup KHÔNG bịa** — chỉ link nếu match chính xác Vietnamese label.
2. **llm.txt featured content max 20 bài** — quá nhiều thì AI crawler ignore.
3. **Format llm.txt** theo spec llmtxt.org (Markdown đơn giản, có `# H1`, `> blockquote` intro, `## sections`).
4. **Entity name dùng full form** (`Hoa Xuân Fashion` không `HX`) — LLM build mental model chính xác.
5. **schema-additions** chỉ suggest, không tự inject — để `schema-markup-generator` skill apply sau.

## Anti-patterns

- ❌ Bịa Wikidata ID (LLM phạt + Google phạt structured data sai)
- ❌ Llm.txt list 100+ URLs (AI crawler ignore noise)
- ❌ Entity name viết tắt (LLM không recognize)
- ❌ Skip frontmatter parse → entity context không có
- ❌ Run NER trên corpus rỗng (<10 bài) → entity graph noise

## Liên kết

- Input từ: corpus bài đã publish (`BTVN BUỔI 3/outputs/seo/`)
- Output cho: `schema-markup-generator` (inject sameAs), `webapp-frontend` (deploy llm.txt vào public/)
- Agent dùng: `seo-geo`
- Reference: llmtxt.org spec, Wikidata API
