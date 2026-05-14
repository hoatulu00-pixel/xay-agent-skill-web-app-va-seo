---
name: schema-markup-generator
description: Sinh JSON-LD Schema.org markup cho Hoa Xuân Fashion — Article, Product, BreadcrumbList, FAQPage, Organization, Person, Review. Kích hoạt khi user nói "tạo schema", "JSON-LD", "structured data", "schema.org", "rich snippet", "Article schema cho bài blog", "Product schema cho sản phẩm". Output là JSON-LD object inline trong page Next.js hoặc separate JSON file.
---

# Skill: Schema Markup Generator

Sinh JSON-LD Schema.org cho bài blog, sản phẩm, organization, FAQ.

## Khi nào kích hoạt

- "Tạo Article schema cho bài [slug]"
- "Thêm Product schema cho /products/[id]"
- "Sinh FAQ schema cho bài này"
- "Schema cho homepage Hoa Xuân"
- Agent `seo-technical` cần inject schema sau khi `seo-content` viết xong

## Input

```json
{
  "type": "Article | Product | BreadcrumbList | FAQPage | Organization | Review",
  "data": {
    // payload phụ thuộc type, vd cho Article:
    "headline": "...",
    "datePublished": "2026-05-14",
    "author": "...",
    "image": "https://...",
    "description": "..."
  },
  "output_format": "inline" | "file"
}
```

## Output

**Mode `inline`**: trả JSON-LD string để inject vào Next.js page:
```tsx
<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
/>
```

**Mode `file`**: lưu `schema.json` vào `BTVN BUỔI 3/outputs/seo/<date>_<slug>/`.

Ví dụ Article schema:
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Cách phối váy hoa mùa hè 2026: 5 outfit gợi ý",
  "image": ["https://res.cloudinary.com/.../vay-hoa-cover.jpg"],
  "datePublished": "2026-05-14T10:00:00+07:00",
  "dateModified": "2026-05-14T10:00:00+07:00",
  "author": {
    "@type": "Person",
    "name": "Hoa Xuân Editorial Team",
    "url": "https://resilient-expression-production-1149.up.railway.app/about"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Hoa Xuân Fashion",
    "logo": {
      "@type": "ImageObject",
      "url": "https://resilient-expression-production-1149.up.railway.app/logo.png"
    }
  },
  "description": "Khám phá 5 cách phối váy hoa mùa hè 2026...",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://resilient-expression-production-1149.up.railway.app/blog/cach-phoi-vay-hoa-mua-he-2026"
  }
}
```

## Files trong skill

- `templates/article-schema.json` — Article skeleton
- `templates/product-schema.json` — Product skeleton (price, availability, brand, sku)
- `templates/faq-schema.json` — FAQPage với mainEntity = Question[]
- `templates/breadcrumb-schema.json` — BreadcrumbList với itemListElement
- `templates/organization-schema.json` — Organization với sameAs (Facebook, Instagram)
- `templates/review-schema.json` — Review/AggregateRating
- `references/schema-org.md` — quy ước, các property bắt buộc/khuyến nghị, validator URL

## 6 Schema types ưu tiên cho Hoa Xuân

| Type | Trang nào dùng | Property bắt buộc |
|---|---|---|
| Article | `/blog/[slug]` | headline, image, datePublished, author, publisher |
| BreadcrumbList | mọi page con | itemListElement (position, name, item) |
| FAQPage | bài có FAQ section | mainEntity (Question + acceptedAnswer) |
| Product | `/products/[id]` | name, image, description, sku, offers (price, availability) |
| Organization | `/` (homepage) | name, url, logo, sameAs, contactPoint |
| Review | bài review sản phẩm | itemReviewed, reviewRating, author |

## Workflow

1. **Pick template** theo `type`.
2. **Fill data** từ input — giữ format JSON-LD đúng (`@context`, `@type`, `@id`).
3. **Validate** với Schema Markup Validator (offline check via library `schema-org` Python hoặc manual rule check).
4. **Output** theo `output_format`:
   - inline → string JSON cho Next.js `<script>`
   - file → save JSON file để agent `webapp-frontend` inject sau

## Quy tắc

1. **Bắt buộc** `@context: "https://schema.org"` và `@type` cho mọi schema.
2. **Datetime ISO 8601** với timezone (`+07:00` cho Vietnam).
3. **Image URL absolute** (https://...), không relative.
4. **mainEntityOfPage** cho Article phải match canonical URL.
5. **Nested objects** cũng có `@type` (vd: `author: { "@type": "Person", ... }`).
6. **Test trên Schema Markup Validator** (validator.schema.org) trước deploy.

## Anti-patterns

- ❌ Schema không có `@context`
- ❌ `datePublished` không có timezone (Google reject)
- ❌ Image URL relative thay vì absolute
- ❌ FAQ schema mà content thực tế không có FAQ visible (Google phạt spam)
- ❌ Product schema với `availability` sai (`InStock` khi thực tế hết hàng)
- ❌ Stuff keyword vào `headline` (Google ignore + có thể phạt)

## Liên kết

- Agent dùng: `seo-technical`
- Sister skill: `webapp-blog-publisher` (publish bài có schema inline)
- Tool validate: validator.schema.org, Google Rich Results Test
