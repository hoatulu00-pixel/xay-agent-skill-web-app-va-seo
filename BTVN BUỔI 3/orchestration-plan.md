# Orchestration Plan — Nhiệm vụ lớn BTVN buổi 3

> Cách Claude Code tự phân bổ 1 task lớn cho 6 agents (Team WEB-APP + Team SEO) và 15 atomic skills.

## Task lớn (paste vào Claude Code)

```
Phát triển feature Comment cho blog Hoa Xuân Fashion:
- Backend: thêm /comments API có rate-limit
- Frontend: UI CommentBox + moderation admin page
- Security: audit JWT, rate-limit, XSS sanitization, dep scan trước khi merge

Song song, chiến dịch SEO tháng 5:
- 5 bài blog mới chủ đề "review/UGC fashion" tận dụng feature Comment
- Audit technical SEO blog hiện tại (crawl, broken link, Core Web Vitals)
- Rewrite top 3 bài top traffic theo GEO (AEO patterns + entity tagging)

Deliverables lưu vào BTVN BUỔI 3/outputs/{webapp,seo}/.
```

## Tại sao task này tốt

1. **Chạm đủ 6 agents** — minh hoạ rõ Claude Code tự phân bổ.
2. **Có cross-team dependency**: backend tạo Comment endpoint → frontend cần API contract → security audit → seo-content viết bài về "user reviews fashion" tận dụng feature mới.
3. **Deliverable cụ thể**: 5 bài blog Markdown, code patch, audit reports, entity graph — chấm điểm rõ.
4. **Realistic**: Đây là feature thật sự nên có cho blog Hoa Xuân (cải thiện UGC, tốt SEO).

## Phân bổ chi tiết

### Phần 1: Feature Comment (Team WEB-APP)

#### `webapp-backend` agent

**Skills dùng**: `fastapi-router-generator`, `alembic-migration-helper`

**Việc cụ thể:**
1. Tạo `models/comment.py`:
   - Fields: id, content (str max 1000), post_id (FK posts.id), user_id (FK users.id, nullable for guest), guest_name, guest_email, is_approved (bool default False), is_flagged (bool default False), created_at, updated_at
   - Relationships: post (back_populates=comments), user (back_populates=comments)

2. Tạo `schemas/comment.py`:
   - CommentBase, CommentCreate, CommentUpdate (admin only), CommentOut
   - `model_config = {"from_attributes": True}`

3. Tạo `routers/comments.py`:
   - `GET /posts/{post_id}/comments` (public, only is_approved=True)
   - `POST /posts/{post_id}/comments` (public hoặc auth, rate-limit 10/min/IP qua SlowAPI)
   - `PATCH /comments/{id}/approve` (admin only)
   - `PATCH /comments/{id}/flag` (admin only)
   - `DELETE /comments/{id}` (admin only)

4. Migration: `alembic revision --autogenerate -m "add Comment table"`, verify autogen (FK ondelete, index post_id), `alembic upgrade head`.

5. Register router trong `main.py`: `app.include_router(comments.router, ...)`.

**Output**: code diff patch lưu vào `BTVN BUỔI 3/outputs/webapp/comment-backend.patch`.

#### `webapp-frontend` agent

**Skills dùng**: `nextjs-component-scaffolder`, `ui-a11y-audit`

**Việc cụ thể:**
1. Tạo `frontend/components/blog/CommentBox.tsx`:
   - Client component (`"use client"`)
   - Form: textarea + name (nếu guest) + email + submit
   - React Query mutation `POST /comments`
   - Optimistic update + toast feedback
   - A11y: label htmlFor, aria-live cho status, focus management

2. Tạo `frontend/components/blog/CommentList.tsx`:
   - Server component fetch `GET /comments` với revalidate 60s
   - Pagination (load more) bằng React Query infinite query

3. Tạo trang admin `frontend/app/admin/comments/page.tsx`:
   - Table list comments với status (pending/approved/flagged)
   - Action buttons: Approve, Flag, Delete (confirm modal)
   - React Query mutations + toast

4. Inject CommentList + CommentBox vào `app/blog/[slug]/page.tsx`.

5. A11y audit: chạy `ui-a11y-audit` trên 3 component vừa tạo, fix HIGH findings.

**Output**: code diff lưu vào `BTVN BUỔI 3/outputs/webapp/comment-frontend.patch` + a11y report.

#### `webapp-security` agent

**Skills dùng**: `jwt-hardening-audit`, `dep-vulnerability-scan`

**Việc cụ thể:**
1. Audit `routers/comments.py` cho:
   - Rate-limit có thực sự enable không (SlowAPI key=client IP)
   - Content max length validated (Pydantic max_length=1000)
   - XSS: HTML tags trong `content` được sanitize bằng `bleach` hoặc whitelist
   - SQL injection: dùng SQLAlchemy ORM (an toàn)
   - CSRF: API có CSRF protection không (FastAPI mặc định không có nếu dùng cookie auth)

2. JWT audit: kiểm tra endpoint admin (`PATCH/DELETE /comments`) có `Depends(get_admin_user)` không, JWT secret từ env không hard-code.

3. Dep scan: `pip-audit` backend + `npm audit` frontend, filter ≥medium. Nếu có CVE liên quan đến comment library (bleach, slowapi) → highlight.

**Output**: `BTVN BUỔI 3/outputs/webapp/comment-security-audit.md` với findings + severity + fix gợi ý.

### Phần 2: Chiến dịch SEO (Team SEO)

#### `seo-content` agent

**Skills dùng**: `vn-keyword-research`, `content-brief-builder`, `seo-content-writer`

**Việc cụ thể:**

Cho mỗi bài trong 5 bài, lặp:
1. **Research keyword** với topic phù hợp:
   - Bài 1: "review váy hoa Hoa Xuân"
   - Bài 2: "UGC thời trang nữ Việt Nam"
   - Bài 3: "khách hàng review chân váy Hoa Xuân"
   - Bài 4: "trải nghiệm mua sắm online thời trang"
   - Bài 5: "cách viết review thời trang trên blog"

2. **Build brief** cho mỗi topic (intent, content type, outline, internal links, FAQ).

3. **Write article.md** theo content type:
   - Bài 1-3: `product_review` template
   - Bài 4: `behind_scenes` template
   - Bài 5: `how_to` template

4. **Save artifacts** vào `BTVN BUỔI 3/outputs/seo/<date>_<slug>/`:
   - `keywords.json`
   - `brief.md`
   - `article.md`
   - `meta.json`

**Output**: 5 folder với 4 file mỗi folder = 20 files.

#### `seo-technical` agent

**Skills dùng**: `technical-seo-audit`, `schema-markup-generator`, `webapp-blog-publisher`

**Việc cụ thể:**
1. **Audit technical** toàn bộ blog:
   - Crawl `https://resilient-expression-production-1149.up.railway.app` (max 500 URLs)
   - Check sitemap.xml, robots.txt, canonical
   - Lighthouse top 10 page
   - Output: `BTVN BUỔI 3/outputs/seo/audit-2026-05-14/{crawl-report.json, broken-links.csv, lighthouse-scores.json, audit-summary.md}`

2. **Schema markup** cho 5 bài SEO mới + Article schema base:
   - Mỗi bài: Article schema + BreadcrumbList + FAQPage (nếu có FAQ)
   - 1 lần: Organization schema cho homepage (sameAs Facebook/Instagram/TikTok)
   - Output: inline schema cho từng bài + `schema-organization.json` cho homepage

3. **Publish 5 bài** lên Hoa Xuân webapp qua `webapp-blog-publisher`:
   - Auth → upload cover image qua Cloudinary → POST /posts (`is_published: false` cho draft)
   - Update Google Sheet tracker
   - Output: `publish_log.json` mỗi bài

**Output**: audit reports + 5 publish_log + schema files.

#### `seo-geo` agent

**Skills dùng**: `aeo-llm-optimizer`, `entity-knowledge-graph`, `google-doc-publisher`

**Việc cụ thể:**
1. **Pick top 3 bài top traffic** (manual hoặc từ Google Analytics export):
   - VD: "Cách phối váy hoa mùa xuân", "Xu hướng thời trang nữ xuân hè 2025", "Đầm hoa nhí mùa xuân"

2. **AEO rewrite** mỗi bài:
   - Thêm TL;DR 40-60 từ
   - FAQ structured ≥3 Q&A
   - Direct answer first cho mỗi H2
   - Semantic chunking
   - Citation cho fact
   - Output: `article-original.md` + `article-aeo.md` + `rewrite-diff.md`

3. **Entity knowledge graph** từ corpus 5 bài mới + 3 bài rewrite:
   - Extract entities (brand, product, event, location)
   - Lookup Wikidata (chỉ link nếu match exact)
   - Generate `entities.json`, `llm.txt`, `schema-additions.json`

4. **Google Doc export** 3 bài rewrite cho team marketing review:
   - Tạo Doc trong Drive folder "Hoa Xuân SEO Review"
   - Share `commenter` permission cho marketing@hoaxuan.com
   - Output: `doc_publish_log.json` mỗi bài

**Output**: 3 bài rewrite + entity graph folder + 3 Google Doc links.

## Workflow mong đợi (Claude Code tự suy)

```
User paste task lớn
│
├─ Claude Code đọc CLAUDE.md root → hiểu cấu trúc 2 team
│
├─ Claude Code chia task thành 2 song song:
│   ├─ FEATURE COMMENT (sequential trong team webapp):
│   │   1. webapp-backend (build API + migration)
│   │   2. webapp-frontend (build UI consume API)
│   │   3. webapp-security (audit trước merge)
│   │
│   └─ SEO CAMPAIGN (sequential trong team seo):
│       1. seo-content (research + write 5 bài)
│       2. seo-technical (audit + schema + publish 5 bài)
│       3. seo-geo (rewrite top 3 + entity graph + Doc export)
│
└─ Claude Code aggregate artifacts vào BTVN BUỔI 3/outputs/
```

## Acceptance criteria (chấm điểm BTVN)

| # | Criteria | Status |
|---|---|---|
| 1 | `.claude/agents/` có 6 file `.md` với frontmatter hợp lệ | ☐ |
| 2 | `.claude/skills/` có 15 folder, mỗi folder có `SKILL.md` hợp lệ | ☐ |
| 3 | Claude Code recognize đủ 6 agents khi gõ `/agents` | ☐ |
| 4 | Task lớn được phân bổ cho 6 agents (xem conversation log) | ☐ |
| 5 | Code feature Comment commit được vào `hoa-xuan-fashion/` (backend + frontend) | ☐ |
| 6 | Security audit report có ≥3 findings có severity | ☐ |
| 7 | 5 bài SEO mới có đủ keywords.json + brief.md + article.md + meta.json | ☐ |
| 8 | Technical SEO audit report có recommendations theo ROI | ☐ |
| 9 | 3 bài AEO rewrite có article-aeo.md + rewrite-diff.md | ☐ |
| 10 | Entity graph có entities.json + llm.txt + schema-additions.json | ☐ |
| 11 | Conversation history exported vào `conversation-log.txt` (≥1MB) | ☐ |
| 12 | Repo Github có `.claude/`, README, push thành công | ☐ |

## Mẹo khi chạy

1. **Mở Claude Code tại root** `Claude Code (SEONGON)/`, KHÔNG tại `hoa-xuan-fashion/` (để agent thấy được cả 2 team).
2. **Confirm agents loaded** trước khi paste task: gõ `/agents` → list ra 6.
3. **Paste task lớn nguyên đoạn** trong section đầu file này.
4. **Đừng can thiệp** lúc Claude Code phân bổ — để nó tự delegate. Nếu thấy nhầm agent, redirect ngắn ("Cái này nên giao cho seo-content").
5. **Confirm migration** trước khi `alembic upgrade head` (tránh nhầm autogen).
6. **Test publish draft mode** (`is_published: false`) trước khi go live.
7. **`/export`** sau khi xong → `BTVN BUỔI 3/conversation-log.txt`.
