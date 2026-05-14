# Code snapshots — Comment feature

Snapshot file code Comment feature mà agents `webapp-backend` + `webapp-frontend` đã viết vào project target `hoa-xuan-fashion/`.

Đây là COPY (không phải symlink) để output BTVN tự đứng một mình, không phụ thuộc folder Hoa Xuân.

## Backend (4 files) — agent `webapp-backend`

| File | Skill dùng | Mô tả |
|---|---|---|
| `backend/app/models/comment.py` | `fastapi-router-generator` | SQLAlchemy model với FK CASCADE post + SET NULL user, index trên post_id + is_approved |
| `backend/app/schemas/comment.py` | `fastapi-router-generator` | Pydantic v2: CommentCreate, CommentModerate, CommentOut, CommentAdminOut |
| `backend/app/routers/comments.py` | `fastapi-router-generator` | 5 endpoints: GET/POST public, GET admin, PATCH moderate, DELETE. Bleach XSS sanitization |
| `backend/alembic/versions/002_add_comments_table.py` | `alembic-migration-helper` | Migration với FK ondelete + 2 indexes |

## Frontend (4 files) — agent `webapp-frontend`

| File | Skill dùng | Mô tả |
|---|---|---|
| `frontend/components/blog/CommentList.tsx` | `nextjs-component-scaffolder` | Server component, fetch với `next.revalidate: 30` + tags |
| `frontend/components/blog/CommentBox.tsx` | `nextjs-component-scaffolder` | Client component, form + React useTransition + toast |
| `frontend/app/admin/comments/page.tsx` | `nextjs-component-scaffolder` | Admin moderation với status tabs (pending/approved/flagged/all) |
| `frontend/app/blog/[slug]/page.tsx` | `nextjs-component-scaffolder` | Tích hợp CommentList + CommentBox vào trang chi tiết blog |

## Security audit

Xem `../comment-security-audit.md` cho 4 HIGH + 5 MEDIUM + 3 LOW findings từ agent `webapp-security`.
