---
name: nextjs-component-scaffolder
description: Sinh nhanh component Next.js 14 App Router với boilerplate Tailwind brand-* palette + TypeScript đúng convention Hoa Xuân Fashion. Kích hoạt khi user nói "tạo component", "scaffold UI", "thêm page admin", "tạo form", "tạo card listing". Output là file .tsx hoàn chỉnh với imports + types + export. Có 3 template: server-component, client-form, admin-page.
---

# Skill: Next.js Component Scaffolder

Sinh component Next.js 14 App Router với boilerplate đúng convention Hoa Xuân Fashion (brand pink-400, Playfair + Inter font, btn-primary/card utilities).

## Khi nào kích hoạt

- "Tạo component CommentBox cho blog"
- "Thêm page admin /admin/comments"
- "Scaffold form ProductForm"
- "Tạo card listing component"
- Agent `webapp-frontend` cần boilerplate nhanh

## Input

```json
{
  "type": "server-component | client-form | admin-page | listing-card",
  "name": "CommentBox",
  "path": "frontend/components/blog/",
  "props": [
    { "name": "postId", "type": "number", "required": true },
    { "name": "initialComments", "type": "Comment[]", "required": false }
  ],
  "fetch_data": false,
  "uses_react_query": true
}
```

## Output

File `.tsx` lưu vào `hoa-xuan-fashion/<path>/<Name>.tsx`:
```tsx
// Component theo template phù hợp type, có:
// - 'use client' nếu cần
// - Imports (React, hooks, lib/api, types)
// - TypeScript Props interface
// - Tailwind classes theo brand
// - Loading/error states (nếu fetch data)
// - Export default
```

## Files trong skill

- `templates/server-component.tsx` — async server component, fetch data với revalidate
- `templates/client-form.tsx` — `"use client"` + useState + React Query mutation
- `templates/admin-page.tsx` — admin page với layout sidebar guard
- `templates/listing-card.tsx` — card component (giống BlogCard, ProductCard)
- `references/brand-tokens.md` — toàn bộ brand color, font, spacing tokens
- `references/conventions.md` — Next.js App Router patterns, naming, file structure

## Workflow

1. **Đọc** `hoa-xuan-fashion/CLAUDE.md` + `frontend/tailwind.config.ts` để confirm brand tokens hiện tại.
2. **Pick template** theo `type` input.
3. **Fill placeholders** trong template:
   - `{{ComponentName}}` → PascalCase
   - `{{props}}` → TypeScript interface
   - `{{imports}}` → tự suy từ deps
4. **Write file** vào path.
5. **Report**: file path + những gì cần làm thủ công sau (vd: thêm route, import vào layout).

## Quy tắc

1. **Server components mặc định**. `"use client"` chỉ khi cần state/effect/event handler.
2. **Brand classes**: dùng `brand-primary`, `brand-pink`, không tạo custom color.
3. **Data fetching**: server component dùng `fetch` với `{ next: { revalidate: 60 } }`; client component dùng `useQuery` từ React Query.
4. **Form**: dùng React Hook Form + Zod (nếu phức tạp); đơn giản thì useState.
5. **A11y**: mọi input có `<label htmlFor>`, button có ARIA label nếu icon-only.
6. **Imports order**: React → external libs → `@/lib/*` → `@/components/*` → relative.

## Anti-patterns

- ❌ Inline style `style={{ color: '#ec4899' }}` (dùng `text-brand-pink`)
- ❌ `useEffect` để fetch khi có thể fetch trong server component
- ❌ Quên `"use client"` khi có `useState` / event handler
- ❌ Hardcode API URL thay vì `process.env.NEXT_PUBLIC_API_URL`
- ❌ Bỏ qua loading/error states trong React Query

## Liên kết

- Pattern reference: `hoa-xuan-fashion/components/admin/PostEditor.tsx`, `BlogCard.tsx`, `ProductCard.tsx`
- Agent dùng: `webapp-frontend`
