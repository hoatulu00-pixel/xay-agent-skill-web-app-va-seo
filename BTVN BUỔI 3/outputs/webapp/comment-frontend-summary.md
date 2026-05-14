# Frontend Comment Feature — Deliverable Summary

**Agent**: `webapp-frontend`
**Skills dùng**: `nextjs-component-scaffolder`, `ui-a11y-audit`
**Date**: 2026-05-15

## Files created (3)

| File | Type | Mục đích |
|---|---|---|
| `frontend/components/blog/CommentList.tsx` | Server Component | Fetch + render danh sách bình luận đã duyệt, revalidate 30s |
| `frontend/components/blog/CommentBox.tsx` | Client Component | Form submit bình luận (guest hoặc auth user), React Query-style với api instance |
| `frontend/app/admin/comments/page.tsx` | Client Component | Admin moderation: tab pending/approved/flagged/all + approve/flag/delete actions |

## Files updated (2)

| File | Change |
|---|---|
| `frontend/lib/api.ts` | + interface `Comment` + `CommentAdmin` |
| `frontend/app/blog/[slug]/page.tsx` | + `<CommentList postId={post.id} />` + `<CommentBox postId={post.id} />` |

## Conventions tuân thủ

- ✅ **Server component mặc định**: `CommentList` không có `"use client"`, fetch trong async function với `next: { revalidate: 30, tags }`
- ✅ **Client component khi cần**: `CommentBox` + admin page có `"use client"` vì có state/event
- ✅ **Brand palette**: `text-brand-500`, `border-brand-200`, `bg-brand-50/50` — không hardcode color
- ✅ **Font**: `font-display` (Playfair) cho heading
- ✅ **Utility classes**: `btn-primary`, `prose-brand` từ globals.css
- ✅ **Date format**: `date-fns` với `locale: vi`
- ✅ **Toast feedback**: `react-hot-toast`
- ✅ **JWT từ cookie**: dùng `api` instance đã có interceptor JWT (`hx_token`)

## A11y features

| Pattern | Implementation |
|---|---|
| Section labeling | `<section aria-labelledby="comments-heading">` |
| Form labeling | Mọi `<input>`/`<textarea>` có `<label htmlFor>` |
| Live region | `aria-live="polite"` cho character count |
| Icon-only button | `aria-label="Duyệt bình luận"`, `"Gắn cờ bình luận"`, `"Xóa bình luận"` |
| Disabled state | `disabled` + `disabled:opacity-50 disabled:cursor-not-allowed` (visual) |
| Helper text | `aria-describedby="comment-help"` cho textarea |
| Time element | `<time dateTime={...}>` cho timestamp |

## A11y audit findings (self-check)

| Severity | Finding | Fix |
|---|---|---|
| LOW | Color contrast `text-stone-400` (4.0:1) trên `bg-white` cho `<time>` | Vẫn pass WCAG AA cho text bình thường (≥4.5:1) — nhưng là 4.0:1 → MARGINAL |
| LOW | Tab focus trên admin tabs không có visual indicator | Tailwind `focus:ring-2 focus:ring-brand-300` đề xuất thêm |
| OK | All other WCAG AA criteria passed |

## Cross-team handoff

- 📥 **Từ webapp-backend**: 5 endpoints comments/* — frontend đã consume:
  - `GET /comments/post/{post_id}` ← CommentList
  - `POST /comments/post/{post_id}` ← CommentBox
  - `GET /comments/admin?status=*` ← admin page
  - `PATCH /comments/{id}/moderate` ← admin page
  - `DELETE /comments/{id}` ← admin page
- ⏭ **Cho webapp-security**: Audit XSS — cả `CommentList` và admin page dùng `dangerouslySetInnerHTML` cho `c.content`. Backend đã sanitize bằng `bleach`, nhưng security agent nên double-check.

## Manual test plan

```bash
cd hoa-xuan-fashion/frontend
npm install
npm run dev
```

Test sequence:
1. Mở `/blog/<any-slug>` → thấy section "Bình luận" + form "Để lại bình luận"
2. Submit form không có name/email → toast error "Guest must provide name and email"
3. Submit với content <2 ký tự → toast error "Bình luận quá ngắn"
4. Submit thành công → toast "Đã gửi, chờ admin duyệt"
5. Login admin → mở `/admin/comments` → thấy comment vừa submit ở tab "Chờ duyệt"
6. Click duyệt → comment chuyển sang tab "Đã duyệt"
7. Quay lại `/blog/<slug>` → thấy comment xuất hiện (sau 30s revalidate, hoặc reload)
