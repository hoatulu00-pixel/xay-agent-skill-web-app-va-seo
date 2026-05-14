# Backend Comment Feature — Deliverable Summary

**Agent**: `webapp-backend`
**Skills dùng**: `fastapi-router-generator`, `alembic-migration-helper`
**Date**: 2026-05-14

## Files created (4)

| File | Mục đích |
|---|---|
| `backend/app/models/comment.py` | SQLAlchemy model với FK CASCADE post, SET NULL user, index post_id + is_approved |
| `backend/app/schemas/comment.py` | Pydantic v2: CommentCreate (validation), CommentModerate, CommentOut (public), CommentAdminOut (full) |
| `backend/app/routers/comments.py` | 5 endpoints: list/post public + admin list/moderate/delete; XSS sanitize bằng bleach |
| `backend/alembic/versions/002_add_comments_table.py` | Migration: create table, 2 index, FK ondelete CASCADE/SET NULL |

## Files updated (4)

| File | Change |
|---|---|
| `backend/app/models/__init__.py` | + `from app.models.comment import Comment` |
| `backend/app/models/post.py` | + `comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")` |
| `backend/app/models/user.py` | + `comments = relationship("Comment", back_populates="user")` |
| `backend/app/main.py` | + `app.include_router(comments.router)` |

## Endpoints

```
GET    /comments/post/{post_id}           # Public, only approved + unflagged
POST   /comments/post/{post_id}           # Public (guest cần name+email) hoặc auth user
GET    /comments/admin?status=pending     # Admin only
PATCH  /comments/{id}/moderate            # Admin: set is_approved/is_flagged
DELETE /comments/{id}                     # Admin only
```

## Security features đã implement

1. **XSS sanitize**: bleach whitelist tags `[b, i, em, strong, a, br]`, attributes `{a: [href, rel]}`, strip rest
2. **Auto linkify**: `bleach.linkify(parse_email=False)` để URL plain text thành link an toàn
3. **Guest validation**: Pydantic `EmailStr` + `min_length=2, max_length=1000` content
4. **Default unmoderated**: `is_approved=False` mặc định — admin phải approve
5. **FK CASCADE**: xoá post → xoá comments; xoá user → giữ comments (SET NULL user_id)
6. **Index**: `is_approved` + `post_id` để query list_for_post nhanh

## Dependencies cần thêm

Update `backend/requirements.txt`:
```
bleach==6.1.0
slowapi==0.1.9   # cho rate-limit (security agent sẽ wire trong main.py)
```

## Cách apply migration

```bash
cd hoa-xuan-fashion/backend
alembic upgrade head
```

Verify:
```bash
psql $DATABASE_URL -c "\d comments"
```

## Next steps (cross-agent)

- ⏭ `webapp-frontend`: Build CommentBox.tsx + CommentList.tsx + admin moderation page consuming các endpoint trên
- ⏭ `webapp-security`: Audit JWT trên `_optional_user` helper + verify bleach config + scan dep CVE
- ⏭ Rate-limit: chưa wire (cần slowapi + main.py setup `Limiter`) — security agent đề xuất fix

## Code review checklist (self)

- ✅ Pydantic v2 `model_dump()`, không `.dict()`
- ✅ `model_config = {"from_attributes": True}` cho mọi response
- ✅ Admin endpoints có `Depends(get_admin_user)`
- ✅ FK ondelete được set rõ ràng
- ✅ Index trên field thường query
- ✅ No hardcode secrets
- ⚠️ Rate-limit chưa wire (sẽ làm trong security pass)
- ✅ Sanitize HTML content (bleach)
