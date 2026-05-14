---
name: aeo-llm-optimizer
description: Rewrite bài blog Hoa Xuân để tối ưu cho AI search (ChatGPT, Perplexity, Gemini, Google AI Overview) — thêm TL;DR 40-60 từ, direct answer first, FAQ structured, citations, semantic chunking. Kích hoạt khi user nói "tối ưu AEO", "GEO", "AI Overview", "LLM citation", "rewrite cho ChatGPT search", "AEO checklist". Output là article-aeo.md + diff so với original.
---

# Skill: AEO/GEO LLM Optimizer

Rewrite content existing để tăng khả năng được LLM trích dẫn (ChatGPT, Perplexity, Gemini, AI Overview).

## Khi nào kích hoạt

- "Rewrite top 3 bài top traffic cho GEO"
- "Tối ưu bài này cho AI Overview"
- "AEO check bài [slug]"
- "Bài này LLM có cite không?"
- Agent `seo-geo` định kỳ rewrite quarterly

## Input

```json
{
  "article_path": "BTVN BUỔI 3/outputs/seo/.../article.md",
  "preserve_voice": true,    // giữ tone brand
  "preserve_facts": true,    // không đổi data/sự kiện
  "target_chunks": 8         // số chunk semantic (vd 8 đoạn lớn)
}
```

## Output

3 files lưu cạnh article gốc:
- `article-original.md` — copy bản gốc (backup)
- `article-aeo.md` — bản rewrite
- `rewrite-diff.md` — diff side-by-side để review

```markdown
# Rewrite Diff — cach-phoi-vay-hoa-mua-he-2026

## Section: Intro
- **Before**: 250 từ giới thiệu chung về váy hoa
+ **After**: 80 từ intro + **TL;DR 50 từ direct answer**

## Section: H2 "5 cách phối"
- **Before**: Paragraph dài 200 từ/cách
+ **After**: 50-80 từ/cách + bullet list + ảnh alt text rõ ràng

## Section: FAQ
- **Before**: Không có
+ **After**: 5 Q&A structured (mỗi câu trả lời 30-50 từ độc lập)

## AEO Score
- Before: 45/100
- After: 88/100
- Improvements: +TL;DR, +FAQ, +semantic chunking, +citation source
```

## Files trong skill

- `scripts/rewrite_for_aeo.py` — apply AEO patterns lên Markdown input
- `references/aeo-patterns.md` — 10 patterns AEO chi tiết với example
- `references/citation-formats.md` — cách format citation để LLM trust (date, author, source URL)

## 10 AEO Patterns

1. **TL;DR 40-60 từ** ngay sau intro — direct answer cho câu hỏi chính
2. **Direct answer first**: Câu đầu của mỗi H2 trả lời ngay, expand sau
3. **Q&A FAQ structured**: mỗi câu trả lời độc lập (LLM quote 1 Q&A)
4. **Lists & tables**: dễ extract data structured
5. **Semantic chunking**: đoạn 2-4 câu, 1 ý/đoạn (chunk size tối ưu RAG)
6. **Numbers + dates cụ thể**: "2026", "85% phụ nữ Việt Nam" (LLM trust số liệu)
7. **Brand mentions full name**: "Hoa Xuân Fashion" (không viết tắt "HX")
8. **Citation cho fact**: "Theo báo cáo Vogue Vietnam 2026, ..."
9. **Conversational tone**: "Bạn có thể...", "Nếu bạn..." thay vì marketing fluff
10. **Avoid keyword stuffing**: LLM phạt spam giống Google

## Workflow

1. **Đọc article gốc** (.md với frontmatter).
2. **Parse sections** (H1, H2, H3, paragraphs, lists, FAQ).
3. **Apply 10 patterns** theo thứ tự:
   - Nếu thiếu TL;DR → sinh 40-60 từ sau intro
   - Nếu intro >150 từ → cắt còn 80 từ
   - Mỗi H2 paragraph đầu → rewrite thành direct answer
   - Thiếu FAQ → sinh ≥3 Q&A từ `questions` keyword research
   - Đoạn >5 câu → split thành 2-3 đoạn
   - Fact không citation → add source (manual research hoặc placeholder cho user fill)
4. **Compute AEO score**:
   - +10 nếu có TL;DR đúng format
   - +10 nếu có FAQ ≥3 Q&A
   - +5/chunk size phù hợp
   - +5/citation đúng format
   - ... (xem `references/aeo-patterns.md` cho rubric đầy đủ)
5. **Save 3 files** + report score before/after.

## Quy tắc

1. **KHÔNG đổi facts** (số liệu, ngày tháng, tên brand) — chỉ restructure.
2. **Giữ giọng văn brand** (Hoa Xuân: trẻ trung, thân thiện).
3. **TL;DR không stuff keyword** — viết natural, direct answer.
4. **FAQ structured**: mỗi Q câu hỏi đầy đủ, A trả lời độc lập (LLM có thể quote A mà không cần context).
5. **Preserve internal links** — không remove link đến category/related post.

## Anti-patterns

- ❌ Rewrite đến mức mất giọng brand (LLM không phải audience duy nhất)
- ❌ TL;DR stuff keyword: "váy hoa mùa hè váy hoa mùa hè váy..."
- ❌ FAQ generic không liên quan keyword research
- ❌ Bịa citation (Source: Vogue 2026 mà thực tế không có) → LLM phạt + reputation issue
- ❌ Remove FAQ visible khỏi page mà giữ schema FAQPage → Google phạt cloaking

## Liên kết

- Input từ: `seo-content-writer` (article.md đã có) hoặc bài đã publish trên webapp
- Sister skill: `entity-knowledge-graph` (sau khi AEO, thêm entity sameAs để LLM build mental model)
- Agent dùng: `seo-geo`
