# BTVN Buổi 3 — 2 Team Sub-Agents + 15 Skills

> Bài tập về nhà buổi 3 khóa **Claude Code @ SEONGON**.

## Yêu cầu bài tập (từ slide thầy)

- Nâng cấp workspace bằng cách xây dựng:
  - **≥ 2 sub-agents**
  - **≥ 2 SKILLs mỗi agent**
- Sau đó **giao 1 nhiệm vụ lớn** cho Claude Code và để nó **tự phân bổ** cho các sub-agent phù hợp.

**3 output bắt buộc:**

| STT | Output | Format |
|---|---|---|
| 1 | Files và folder code nằm trên 1 repo Github (có `.claude/` chứa `/skills` và `/agents`) | Github repo |
| 2 | File ghi chép lịch sử trò chuyện với Claude Code (`/export`) | `.txt` |
| 3 | Các file output từ việc giao việc cho Agent và sử dụng SKILLs | — |

## Cấu trúc deliverable

```
Claude Code (SEONGON)/                       # root workspace
├── CLAUDE.md                                # ROOT context (orchestration guide)
├── .claude/
│   ├── settings.local.json
│   ├── agents/                              # 6 agents
│   │   ├── webapp-frontend.md
│   │   ├── webapp-backend.md
│   │   ├── webapp-security.md
│   │   ├── seo-content.md
│   │   ├── seo-technical.md
│   │   └── seo-geo.md
│   └── skills/                              # 15 atomic skills
│       ├── nextjs-component-scaffolder/
│       ├── ui-a11y-audit/
│       ├── fastapi-router-generator/
│       ├── alembic-migration-helper/
│       ├── jwt-hardening-audit/
│       ├── dep-vulnerability-scan/
│       ├── vn-keyword-research/             # tách từ skill cũ
│       ├── content-brief-builder/
│       ├── seo-content-writer/              # tách từ skill cũ
│       ├── technical-seo-audit/
│       ├── schema-markup-generator/
│       ├── webapp-blog-publisher/           # tách từ skill cũ
│       ├── aeo-llm-optimizer/
│       ├── entity-knowledge-graph/
│       └── google-doc-publisher/            # tách từ skill cũ
├── BTVN BUỔI 3/                             # ← bạn đang ở đây
│   ├── README.md                            # file này
│   ├── orchestration-plan.md                # task lớn + cách Claude phân bổ
│   ├── conversation-log.txt                 # export /export sau khi chạy task
│   ├── outputs/                             # artifact từ việc giao agent
│   │   ├── webapp/                          # code diff, audit report cho Hoa Xuân
│   │   └── seo/                             # bài blog mới, schema, audit
│   └── screenshots/                         # ảnh agents được invoke
├── hoa-xuan-fashion/                        # web app target (Next.js + FastAPI)
└── seo-content-workspace/                   # backup skill cũ (read-only)
```

## 2 team agent

### Team WEB-APP (target: `hoa-xuan-fashion/`)

| Agent | Vai trò |
|---|---|
| `webapp-frontend` | Next.js 14 App Router, Tailwind brand-* palette, TipTap, React Query |
| `webapp-backend` | FastAPI 0.111 + SQLAlchemy 2.0, Pydantic v2, Alembic, JWT |
| `webapp-security` | OWASP Top 10, JWT hardening, dep vulnerability scan |

### Team SEO (target: blog Hoa Xuân + content marketing)

| Agent | Vai trò |
|---|---|
| `seo-content` | Keyword research VN, content brief, SEO content writing (7 templates) |
| `seo-technical` | Site audit, JSON-LD schema, sitemap, publish API |
| `seo-geo` | AEO/GEO optimization cho LLM citation, entity knowledge graph, Google Doc export |

## Nhiệm vụ lớn

Xem chi tiết tại [`orchestration-plan.md`](./orchestration-plan.md).

**Tóm tắt:**
> "Phát triển feature **Comment** cho blog Hoa Xuân Fashion: backend API có rate-limit + frontend UI có moderation + audit bảo mật trước khi merge. Song song, lên **chiến dịch SEO**: 5 bài review/UGC fashion, audit technical SEO blog hiện tại, rewrite top 3 bài top traffic theo GEO."

Task này chạm cả 6 agents — minh hoạ rõ khả năng Claude Code tự phân bổ.

## Cách reproduce

### 1. Setup workspace

```bash
# Clone repo
git clone <repo-url> "Claude Code (SEONGON)"
cd "Claude Code (SEONGON)"

# Cài dependency (cho skill webapp-blog-publisher)
cd .claude/skills/webapp-blog-publisher
pip install requests python-frontmatter markdown cloudinary google-api-python-client google-auth

# Setup config (skill cũ + atomic skill mới đều cần)
cp config/settings.example.json config/settings.json
# → fill webapp_email, webapp_password, cloudinary_url, google_service_account, google_sheet_id, drive_folder_id
```

### 2. Verify cấu trúc

```bash
# Đếm agents (kỳ vọng = 6)
ls .claude/agents/*.md | wc -l

# Đếm skills (kỳ vọng = 15)
ls -d .claude/skills/*/ | wc -l

# Hoặc trên Windows PowerShell:
(Get-ChildItem .claude/agents/*.md).Count
(Get-ChildItem .claude/skills -Directory).Count
```

### 3. Mở Claude Code tại root workspace

```bash
cd "Claude Code (SEONGON)"
claude
```

Claude Code sẽ tự đọc:
- `CLAUDE.md` (root orchestration)
- `.claude/agents/*.md` (6 agents)
- `.claude/skills/*/SKILL.md` (15 skills)

### 4. Giao task lớn

Trong Claude Code, paste nguyên đoạn task trong `orchestration-plan.md` (section "Task lớn"). Claude Code sẽ tự delegate cho 6 agents tương ứng.

### 5. Export conversation

Sau khi task chạy xong:
```
/export
```
Lưu file `.txt` vào `BTVN BUỔI 3/conversation-log.txt`.

### 6. Verify outputs

```
BTVN BUỔI 3/outputs/
├── webapp/
│   ├── comment-backend-summary.md           # [webapp-backend] Comment model + router + migration
│   ├── comment-frontend-summary.md          # [webapp-frontend] CommentBox + CommentList + admin
│   └── comment-security-audit.md            # [webapp-security] 4 HIGH + 5 MEDIUM findings
└── seo/
    ├── 2026-05-15_<slug>/                   # [seo-content] 5 article folders (keyword + brief + article + meta + publish_log)
    │   ├── keywords.json
    │   ├── brief.md
    │   ├── article.md
    │   ├── meta.json
    │   └── publish_log.json                 # [seo-technical] webapp-blog-publisher output
    ├── audit-2026-05-15/                    # [seo-technical] crawl + schema + Lighthouse
    │   ├── audit-summary.md
    │   ├── crawl-report.json
    │   ├── broken-links.csv
    │   ├── lighthouse-scores.json
    │   └── schemas/
    │       ├── article-review-vay-hoa.json
    │       ├── breadcrumb-blog.json
    │       └── organization-homepage.json
    └── geo-2026-05-15/                      # [seo-geo] AEO rewrite + entity graph + Google Doc
        ├── summary.md
        ├── <slug>/                          # 3 rewrite folders
        │   ├── article-original.md
        │   ├── article-aeo.md
        │   ├── rewrite-diff.md
        │   └── doc_publish_log.json
        └── entity-graph/
            ├── entities.json
            ├── llm.txt
            └── schema-additions.json
```

## Notes

- **Skill cũ `seo-content-publisher`** trong `seo-content-workspace/` là backup read-only. 4 atomic skill mới đã copy code Python cần thiết.
- **Hoa Xuân Fashion** đã deploy Railway production. Khi test publish bài, dùng draft mode (`is_published: false`) trước khi go live.
- **Permission**: `.claude/settings.local.json` đã allowlist các Bash command cần thiết (python, npm, alembic, ...).

## Liên kết

- [orchestration-plan.md](./orchestration-plan.md) — chi tiết task lớn + phân bổ
- [../CLAUDE.md](../CLAUDE.md) — root context cho Claude Code
- [../hoa-xuan-fashion/CLAUDE.md](../hoa-xuan-fashion/CLAUDE.md) — convention dự án Hoa Xuân
- [../seo-content-workspace/.claude/skills/seo-content-publisher/SKILL.md](../seo-content-workspace/.claude/skills/seo-content-publisher/SKILL.md) — skill cũ (reference)
