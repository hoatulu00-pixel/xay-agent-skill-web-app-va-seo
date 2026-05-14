---
name: alembic-migration-helper
description: Hướng dẫn tạo + verify Alembic migration cho Hoa Xuân Fashion backend, phát hiện autogen sai (FK, index, naming, drop column nhầm). Kích hoạt khi user nói "tạo migration", "alembic revision", "đổi schema DB", "rollback migration", "merge head". Output là migration file đã review + checklist verify + lệnh upgrade/downgrade.
---

# Skill: Alembic Migration Helper

Quản lý Alembic migration cho `hoa-xuan-fashion/backend/`.

## Khi nào kích hoạt

- User vừa đổi model SQLAlchemy, cần generate migration
- "Tạo migration thêm Comment table"
- "Verify migration X có đúng không"
- "Rollback migration cuối"
- "Merge multi-head"

## Input

- **Mode**: `create` | `verify` | `rollback` | `merge-heads`
- **Message**: ngắn gọn mô tả change (vd: "add Comment table with FK to posts")
- **Model path**: file model vừa đổi (vd: `models/comment.py`)

## Output

**Mode `create`**:
- File `backend/alembic/versions/<rev>_<message>.py` (do `alembic revision --autogenerate` sinh)
- Verification report: checklist các pattern sai phổ biến
- Lệnh apply: `alembic upgrade head`

**Mode `verify`**:
- Phân tích migration file, flag các issue (xem checklist bên dưới)

## Files trong skill

- `scripts/diff_migration.py` — so sánh autogen output với model thực tế, flag inconsistency
- `references/migration-patterns.md` — patterns đúng (FK ondelete, index, server_default)
- `references/rollback-playbook.md` — playbook khi cần rollback an toàn

## Workflow

### Mode `create`

1. **Đọc model file** mới/sửa để hiểu change.
2. **Chạy autogen**:
   ```bash
   cd hoa-xuan-fashion/backend
   alembic revision --autogenerate -m "<message>"
   ```
3. **Đọc file vừa sinh** trong `alembic/versions/`.
4. **Verify checklist** (xem bên dưới).
5. **Báo cáo** cho user file path + verification result. KHÔNG tự apply, để user `alembic upgrade head` thủ công.

### Mode `verify`

Checklist phát hiện autogen sai:

| Pattern | Vấn đề | Fix |
|---|---|---|
| `op.drop_table(...)` không mong đợi | Model bị xoá nhầm hoặc rename → autogen hiểu thành drop+create | Sửa migration manual: dùng `op.rename_table` |
| `op.drop_column` không mong đợi | Tương tự rename | `op.alter_column` rename |
| FK thiếu `ondelete=` | Cascade behavior undefined | Thêm `ondelete='CASCADE'` hoặc `'RESTRICT'` |
| `op.create_index` thiếu | Field thường query (FK, slug, email) cần index | Add `op.create_index` manual |
| `op.add_column` cho NOT NULL không có default | Existing rows fail | Thêm `server_default=` hoặc nullable + backfill + alter |
| `op.alter_column` đổi type không safe | Postgres không cast tự động được | Add `postgresql_using=` |

### Mode `rollback`

1. Kiểm tra revision hiện tại: `alembic current`
2. Đọc migration sẽ rollback, đảm bảo `downgrade()` function đầy đủ
3. Backup DB trước: `pg_dump > backup-<date>.sql`
4. Rollback: `alembic downgrade -1`
5. Verify schema state

### Mode `merge-heads`

Khi nhiều branch merge gây multi-head:
```bash
alembic heads     # list các head
alembic merge -m "merge branches" <head1> <head2>
alembic upgrade head
```

## Quy tắc

1. **KHÔNG `alembic upgrade head` tự động** — luôn để user/agent verify migration file trước.
2. **Backup DB trước** khi rollback production.
3. **Migration message ngắn gọn** (≤72 ký tự, mô tả WHY).
4. **Mỗi PR 1 migration** — không gộp nhiều change vào 1 migration.
5. **Test migration** trên local trước khi commit (`alembic upgrade head` + `alembic downgrade -1` + `alembic upgrade head` 2 lần).

## Anti-patterns

- ❌ Edit migration đã commit (gây inconsistency với teammate)
- ❌ `alembic upgrade head` trên production mà chưa test local
- ❌ Skip `downgrade()` (chỉ implement `upgrade()`) — gây kẹt rollback
- ❌ Migration message dạng "fix db" (không mô tả gì)
- ❌ Gộp 5 model change vào 1 migration → khó review

## Liên kết

- Agent dùng: `webapp-backend`
- Sister skill: `fastapi-router-generator` (tạo model trước, migration sau)
- Reference: `hoa-xuan-fashion/backend/alembic/versions/001_initial.py`
