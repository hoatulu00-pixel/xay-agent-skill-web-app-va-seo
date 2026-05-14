---
name: fastapi-router-generator
description: Sinh FastAPI router CRUD chuẩn pattern Hoa Xuân Fashion (Pydantic v2 + Depends + slugify + JWT auth). Kích hoạt khi user nói "tạo router", "thêm endpoint", "API mới FastAPI", "CRUD endpoint", "POST/GET/PUT/DELETE backend". Output là 3 file: router.py + schema.py + model.py kèm migration Alembic gợi ý.
---

# Skill: FastAPI Router Generator

Scaffold router CRUD đúng convention Hoa Xuân Fashion backend (`hoa-xuan-fashion/backend/app/`).

## Khi nào kích hoạt

- "Tạo router /comments cho blog"
- "Thêm CRUD endpoint cho Order"
- "API mới: /tags với GET + POST"
- Agent `webapp-backend` cần scaffold nhanh

## Input

```json
{
  "resource": "Comment",
  "path": "/comments",
  "endpoints": ["GET_list", "GET_one", "POST", "PUT", "DELETE"],
  "auth": {
    "POST": "current_user",
    "PUT": "admin",
    "DELETE": "admin",
    "GET_list": "public",
    "GET_one": "public"
  },
  "fields": [
    { "name": "content", "type": "str", "max_length": 1000 },
    { "name": "post_id", "type": "int", "foreign_key": "posts.id" },
    { "name": "user_id", "type": "int", "foreign_key": "users.id" },
    { "name": "is_approved", "type": "bool", "default": false }
  ],
  "rate_limit": "10/minute"
}
```

## Output

3 file lưu vào `hoa-xuan-fashion/backend/app/`:

```
models/comment.py       # SQLAlchemy 2.0 Mapped[]
schemas/comment.py      # Pydantic v2 In/Out, model_config from_attributes=True
routers/comments.py     # APIRouter + Depends + CRUD endpoints
```

Plus instructions cho Alembic migration:
```bash
cd backend
alembic revision --autogenerate -m "add Comment model"
alembic upgrade head
```

## Files trong skill

- `templates/router.py.tmpl` — APIRouter skeleton với CRUD endpoints
- `templates/schema.py.tmpl` — CommentBase, CommentCreate, CommentUpdate, CommentOut
- `templates/model.py.tmpl` — SQLAlchemy 2.0 Mapped[] class
- `references/conventions.md` — quy ước naming, imports, response model, error handling
- `references/auth-patterns.md` — `get_current_user` vs `get_admin_user` use cases

## Workflow

1. **Đọc** `hoa-xuan-fashion/CLAUDE.md` để confirm convention hiện tại.
2. **Đọc reference router** đã có (vd: `routers/posts.py`) để copy pattern style.
3. **Fill template**:
   - `{{Resource}}` → PascalCase (Comment)
   - `{{resource}}` → snake_case (comment)
   - `{{resources}}` → plural snake_case (comments)
   - `{{fields}}` → SQLAlchemy/Pydantic fields generated
   - `{{auth}}` → `Depends(get_current_user)` / `Depends(get_admin_user)` per endpoint
4. **Write 3 files** vào path.
5. **Update** `models/__init__.py` + `schemas/__init__.py` + `routers/__init__.py` để register.
6. **Register router** trong `main.py`: `app.include_router(comments.router, prefix="/comments", tags=["comments"])`.

## Quy tắc

1. **Pydantic v2 only**: `model_dump()`, không `dict()`. `model_config = {"from_attributes": True}` cho response.
2. **Slug tự sinh** từ slugify(title) nếu resource có field title.
3. **Admin endpoints** dùng `Depends(get_admin_user)`. Public endpoints không có Depends.
4. **Response model bắt buộc**: `@router.get("/", response_model=List[CommentOut])`.
5. **Error handling**: dùng `HTTPException(status_code=..., detail=...)`. Không trả `{"error": ...}` raw.
6. **Rate limit**: nếu input có `rate_limit`, integrate SlowAPI middleware vào endpoint.
7. **Migration**: KHÔNG chạy `alembic upgrade head` tự động, chỉ generate revision file → user/agent review trước khi apply.

## Anti-patterns

- ❌ `.dict()` Pydantic v1 (deprecated trong v2)
- ❌ Quên `model_config = {"from_attributes": True}` → ORM object không parse
- ❌ Trả raw SQLAlchemy object thay vì Pydantic schema
- ❌ Hard-code admin check thay vì `Depends(get_admin_user)`
- ❌ Tạo slug manually (luôn dùng `python-slugify`)
- ❌ Quên register router trong `main.py`

## Liên kết

- Agent dùng: `webapp-backend`
- Sister skill: `alembic-migration-helper` (chạy sau khi tạo model)
- Pattern reference: `hoa-xuan-fashion/backend/app/routers/posts.py`, `products.py`
