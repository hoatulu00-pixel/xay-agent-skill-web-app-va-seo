# Hoa Xuân Fashion API Reference

Base URL: `https://resilient-expression-production-1149.up.railway.app`

## Auth

### `POST /auth/login`

```json
// Request
{"email": "admin@hoaxuan.com", "password": "HoaXuan2024!"}

// Response 200
{"access_token": "eyJ...", "token_type": "bearer"}
```

Token TTL: 7 ngày. Cache vào `.cache/webapp_token.json` với timestamp; refresh nếu > 6 ngày.

Header cho các call admin: `Authorization: Bearer <token>`

## Categories

### `GET /categories`

Public. Trả `[{id, name, slug, description}, ...]`.

### `POST /categories` (admin)

```json
// Request
{"name": "Hướng dẫn & Mẹo", "description": "Tổng hợp cách phối đồ và mẹo thời trang"}

// Response 200
{"id": 1, "name": "Hướng dẫn & Mẹo", "slug": "huong-dan-meo", "description": "..."}
```

## Posts

### `POST /posts` (admin)

```json
// Request
{
  "title": "5 cách phối chân váy hoa mùa xuân chuẩn xu hướng 2026",
  "content": "<p>HTML content...</p>",
  "excerpt": "Meta description 150-160 ký tự, có CTA, có primary keyword.",
  "cover_image_url": "https://res.cloudinary.com/.../image.jpg",
  "category_id": 2,
  "is_published": true
}

// Response 200
{
  "id": 12,
  "title": "...",
  "slug": "5-cach-phoi-chan-vay-hoa-mua-xuan-chuan-xu-huong-2026",
  "content": "...",
  "excerpt": "...",
  "cover_image_url": "...",
  "is_published": true,
  "published_at": "2026-05-10T10:30:00",
  "category_id": 2,
  "author_id": 1
}
```

URL public: `https://resilient-expression-production-1149.up.railway.app/blog/<slug>`

### `GET /posts/admin?page=1&limit=20` (admin)

List all posts (cả draft + published). Dùng để check title/slug trùng trước khi tạo.

## Upload

### `POST /upload` (admin)

Multipart form data, field `file`. Allowed: JPEG/PNG/WebP/GIF, max 5MB.

```python
files = {"file": ("cover.jpg", open("cover.jpg", "rb"), "image/jpeg")}
headers = {"Authorization": f"Bearer {token}"}
r = requests.post(f"{BASE}/upload", files=files, headers=headers)
# r.json() = {"url": "https://res.cloudinary.com/.../cover.jpg"}
```

## Error codes

| Code | Ý nghĩa | Action |
|---|---|---|
| 401 | Token invalid/expired | Re-login, retry 1 lần |
| 403 | User không phải admin | Báo user check tài khoản |
| 422 | Payload invalid | In ra `detail` từ FastAPI để debug |
| 500 | Server error | Retry sau 5s, max 3 lần |
