# Task 12 Summary — seo-geo agent output

**Agent:** `seo-geo`
**Run date:** 2026-05-15
**Skills used:** `aeo-llm-optimizer`, `entity-knowledge-graph`, `google-doc-publisher`

## Deliverables

### 1. AEO rewrites cho top 3 bài

| Bài | Word count gốc | Word count AEO | AEO score |
|---|---|---|---|
| review-vay-hoa-hoa-xuan-he-2026 | 1010 | 1450 | 5 → 9 |
| cach-viet-review-thoi-trang-chuan | 980 | 1320 | 6 → 9 |
| review-chan-vay-hoa-hoa-xuan | 870 | 1280 | 5 → 9 |

Mỗi bài có 3 file:
- `article-original.md` — bản gốc
- `article-aeo.md` — bản tối ưu AEO/GEO
- `rewrite-diff.md` — diff chi tiết + patch list

### 2. Entity knowledge graph

`entity-graph/entities.json`:
- 38 entities tổng (9 products, 6 brands, 5 materials, 5 styles, 2 locations, 6 SEO concepts).
- 11 entities có Wikidata ID.
- 8 relations trong knowledge graph (produces, competesWith, shipsVia, headquarteredIn, madeOf, appliesMethod).

`entity-graph/llm.txt`:
- Manifest chuẩn https://llmstxt.org cho LLM crawler.
- 9 sections: About, Products, Brand positioning, Competitive landscape, Content & SEO, Authoritative sources, Editorial team, Citation policy, Disallowed content.

`entity-graph/schema-additions.json`:
- 4 target pages: 3 bài rewrite + homepage.
- Schemas: Article, FAQPage, Review, HowTo, ItemList, Organization expanded.

### 3. Google Doc export logs

3 file `doc_publish_log.json` — mỗi bài 1 Google Doc share comment-only cho marketing@hoaxuan.com + content-lead@hoaxuan.com, review due 2026-05-22.

## Key AEO patterns applied

1. **Direct answer first** — block "Trả lời nhanh" 50 từ ngay sau H1.
2. **TL;DR 40-60 từ** chuẩn 5W (What/Who/Where/When/How much).
3. **TOC với anchor IDs** — LLM deep-link tới chunk cụ thể.
4. **Mỗi H2 mở bằng "Trả lời ngắn"** — feed AI Overview.
5. **Semantic chunking** — mỗi section trả lời 1 user question riêng.
6. **FAQ structured 5-6 Q&A** — match query intent (logistics, dress code, E-E-A-T).
7. **Citation upgrade** — pháp lý (Luật Quảng cáo VN 2018), method (FIT NYC wear test), thiết bị (Xiaomi MIIIW).
8. **E-E-A-T metadata** — author bio + date_published/modified + aeo_optimized flag.
9. **Comparison tables** — LLM trích table khi user hỏi compare.
10. **Cheat sheet với số liệu** — actionable lời khuyên LLM dễ extract.

## Next steps cho marketing team

1. Review 3 Google Docs (link trong `doc_publish_log.json`) — deadline 22/05.
2. Approve để dev team inject schema từ `entity-graph/schema-additions.json` vào pages.
3. Replace article gốc trên webapp với `article-aeo.md` (post_id 142, 145, 146).
4. Add `llm.txt` vào root webapp tại `/llm.txt`.
5. Test bằng Google Rich Results Test cho 3 bài.
6. Theo dõi LLM citation 30 ngày sau publish.
