# CLAUDE.md — Workspace SEONGON (Hoa Xuân + SEO)

> File context CHÍNH cho Claude Code. Đọc file này ĐẦU TIÊN khi bắt đầu session ở root workspace.

## Tổng quan workspace

Workspace này phục vụ học khóa **Claude Code @ SEONGON** + dự án thực tế **Hoa Xuân Fashion**.

| Folder | Mục đích | Trạng thái |
|---|---|---|
| `BTVN BUỔI 2/` | Tài liệu học buổi 2 (lập trình cơ bản Claude Code) | read-only reference |
| `BTVN BUỔI 3/` | **Output bài tập buổi 3** (2 team agent + skills) | active — đang xây |
| `hoa-xuan-fashion/` | Web app full-stack: Next.js 14 + FastAPI + PostgreSQL, deploy Railway | active production |
| `seo-content-workspace/` | Skill cũ `seo-content-publisher` (mega-workflow) | **backup read-only** — đã tách thành atomic skills |
| `.claude/agents/` | 6 sub-agents (2 team: webapp + seo) | active |
| `.claude/skills/` | 15 atomic skills (phân bổ qua trigger keywords) | active |

## 2 team agent

### Team WEB-APP (target: `hoa-xuan-fashion/`)

| Agent | File | Invoke khi user nói... | Skills primary |
|---|---|---|---|
| Frontend | `.claude/agents/webapp-frontend.md` | "tạo UI", "component Next.js", "Tailwind brand", "TipTap", "Lighthouse" | `nextjs-component-scaffolder`, `ui-a11y-audit` |
| Backend | `.claude/agents/webapp-backend.md` | "tạo router", "endpoint FastAPI", "model SQLAlchemy", "migration", "Cloudinary" | `fastapi-router-generator`, `alembic-migration-helper` |
| Security | `.claude/agents/webapp-security.md` | "audit security", "JWT", "OWASP", "scan dep", "vulnerability" | `jwt-hardening-audit`, `dep-vulnerability-scan` |

### Team SEO (target: blog Hoa Xuân + content marketing)

| Agent | File | Invoke khi user nói... | Skills primary |
|---|---|---|---|
| Content SEO | `.claude/agents/seo-content.md` | "viết bài", "research keyword", "content brief", "/seo-publish" | `vn-keyword-research`, `content-brief-builder`, `seo-content-writer` |
| Technical SEO | `.claude/agents/seo-technical.md` | "audit technical SEO", "schema markup", "sitemap", "publish bài lên web" | `technical-seo-audit`, `schema-markup-generator`, `webapp-blog-publisher` |
| GEO | `.claude/agents/seo-geo.md` | "tối ưu AEO", "GEO", "AI Overview", "LLM citation", "entity graph", "Google Doc" | `aeo-llm-optimizer`, `entity-knowledge-graph`, `google-doc-publisher` |

## 15 atomic skills (bảng map nhanh)

### Web-app (6)

- `nextjs-component-scaffolder` — sinh component Next.js 14 App Router với brand pink-400 Hoa Xuân
- `ui-a11y-audit` — audit accessibility WCAG AA cho component React
- `fastapi-router-generator` — sinh FastAPI router CRUD chuẩn Pydantic v2 + slugify
- `alembic-migration-helper` — tạo + verify Alembic migration, phát hiện autogen sai
- `jwt-hardening-audit` — audit JWT (rotation, expiry, algorithm, claim validation)
- `dep-vulnerability-scan` — pip-audit + npm audit, báo cáo CVE

### SEO content (3)

- `vn-keyword-research` — research keyword tiếng Việt (Google autocomplete + PAA + related)
- `content-brief-builder` — sinh content brief 1 trang cho writer
- `seo-content-writer` — viết bài Markdown theo 7 template + SEO/AEO checklist

### SEO technical (3)

- `technical-seo-audit` — crawl site, audit Core Web Vitals, sitemap, robots
- `schema-markup-generator` — sinh JSON-LD (Article, Product, FAQ, BreadcrumbList)
- `webapp-blog-publisher` — POST /posts lên Hoa Xuân webapp + update Google Sheet tracker

### SEO GEO (3)

- `aeo-llm-optimizer` — rewrite bài cho LLM trích dẫn (TL;DR, FAQ structured, direct answer)
- `entity-knowledge-graph` — extract entities + link Wikidata + sinh `llm.txt`
- `google-doc-publisher` — tạo Google Doc formatted trong Drive folder

## Decision tree — user nói gì → invoke ai

```
User input
│
├─ "feature mới" / "API" / "router" / "endpoint" / "model"
│   └─ webapp-backend
│
├─ "UI" / "component" / "page" / "Tailwind" / "React"
│   └─ webapp-frontend
│
├─ "security" / "JWT" / "OWASP" / "audit code" / "scan"
│   └─ webapp-security
│
├─ "viết bài" / "blog" / "content SEO" / "keyword" / "/seo-publish"
│   └─ seo-content
│
├─ "audit SEO" / "schema" / "sitemap" / "publish bài"
│   └─ seo-technical
│
├─ "AEO" / "GEO" / "AI Overview" / "LLM citation" / "entity"
│   └─ seo-geo
│
└─ "feature lớn / dự án": Claude Code tự phân chia cho NHIỀU agent
    Xem `BTVN BUỔI 3/orchestration-plan.md` cho ví dụ task lớn
```

## Quy ước project Hoa Xuân Fashion

Khi làm việc với `hoa-xuan-fashion/`, đọc `hoa-xuan-fashion/CLAUDE.md` để biết conventions chi tiết.

**Tóm tắt nhanh:**
- Backend: FastAPI 0.111 + SQLAlchemy 2.0 + Alembic + JWT. Pydantic v2 dùng `model_dump()`, không `dict()`.
- Frontend: Next.js 14 App Router. Server components mặc định, `"use client"` khi cần. JWT lưu cookie `hx_token`.
- Brand: pink-400 palette (`brand-*`). Font Playfair Display + Inter.
- Deploy: Railway. URL prod: `https://resilient-expression-production-1149.up.railway.app`
- Admin: `admin@hoaxuan.com`

## Task hiện tại (BTVN buổi 3)

Xem `BTVN BUỔI 3/orchestration-plan.md` cho nhiệm vụ lớn cần thực thi:
> Phát triển feature Comment + chiến dịch SEO 5 bài + audit technical SEO + GEO optimize top 3 bài.

Tất cả deliverables lưu vào `BTVN BUỔI 3/outputs/`.

## File backup quan trọng

- `seo-content-workspace/.claude/skills/seo-content-publisher/` — skill cũ (mega-workflow). **KHÔNG động vào**. Các atomic skill mới đã copy code cần thiết qua `.claude/skills/`.
- `seo-content-workspace/.claude/skills/seo-content-publisher/outputs/runs/` — 20+ bài blog đã publish lịch sử. Reference khi cần xem bài thực tế.
