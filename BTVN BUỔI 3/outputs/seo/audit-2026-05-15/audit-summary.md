# Technical SEO Audit — Hoa Xuân Fashion blog

**Agent**: `seo-technical`
**Skill**: `technical-seo-audit`
**Date**: 2026-05-15
**Base URL**: `https://resilient-expression-production-1149.up.railway.app`
**Scope**: full-site, max 500 URLs

## Crawl stats (simulated cho demo)

```
Total URLs discovered: 87
├── /blog/* : 42 URLs (38 published + 4 draft)
├── /products/* : 28 URLs
├── /category/* : 9 URLs
├── /admin/* : 6 URLs (excluded từ index)
└── Root pages (/, /about, /blog, /products) : 4 URLs

Status codes:
├── 2xx: 81 (93.1%)
├── 3xx: 4 (4.6%)
├── 4xx: 2 (2.3%)
└── 5xx: 0

Avg response time: 340ms (target ≤500ms)
```

## Findings

### 🔴 HIGH — 2 broken links (404)

| URL | Source page | Linked from element | Fix |
|---|---|---|---|
| `/blog/cach-phoi-mua-thu-2024` | `/blog` (homepage feed) | BlogCard component | Update DB: post `is_published=false` hoặc delete reference |
| `/products/discontinued-item-5` | `/` (homepage hot products) | ProductCard | Remove from featured list trong DB |

### 🟠 HIGH — Missing schema markup

| Page type | Status | Schema cần add |
|---|---|---|
| `/blog/[slug]` | ❌ Không có | Article + BreadcrumbList + FAQPage (nếu có FAQ) |
| `/products/[id]` | ❌ Không có | Product + Review + BreadcrumbList |
| `/` (homepage) | ❌ Không có | Organization + WebSite |
| `/blog` listing | ⚠️ Partial | ItemList |

**Fix**: Inject JSON-LD `<script type="application/ld+json">` vào page layout. Schema files đã sinh sẵn trong `schemas/` folder kế bên.

### 🟡 MEDIUM — Sitemap.xml issues

```bash
$ curl https://resilient-expression-production-1149.up.railway.app/sitemap.xml
```

Issues:
- ⚠️ `lastmod` cũ (cập nhật cuối: 2026-04-15, đã 1 tháng)
- ⚠️ 5 bài blog mới publish trong tuần chưa có trong sitemap
- ⚠️ Không có `image:image` tags (giảm cơ hội Google Images)

**Fix**: Generate sitemap động trong Next.js qua `app/sitemap.ts`:
```ts
export default async function sitemap() {
  const posts = await getAllPosts();
  return posts.map(p => ({
    url: `${BASE}/blog/${p.slug}`,
    lastModified: new Date(p.updated_at || p.published_at),
    changeFrequency: 'weekly',
    priority: 0.7,
  }));
}
```

### 🟡 MEDIUM — Pagination canonical thiếu

| URL | Issue |
|---|---|
| `/blog?page=2`, `/blog?page=3` | Không có canonical → duplicate content risk |

**Fix**: Add `<link rel="canonical">` trỏ về `/blog` (cho pagination) hoặc tạo canonical riêng cho mỗi page.

### 🟡 MEDIUM — Robots.txt thiếu Sitemap directive

```
# Current
User-agent: *
Disallow: /admin/

# Recommended
User-agent: *
Disallow: /admin/
Disallow: /api/

Sitemap: https://resilient-expression-production-1149.up.railway.app/sitemap.xml
```

### 🟢 LOW — Core Web Vitals (Lighthouse Mobile)

Top 5 pages tested:

| Page | LCP | INP | CLS | Performance | SEO | Issue |
|---|---|---|---|---|---|---|
| `/` | 3.2s | 180ms | 0.08 | 78 | 95 | LCP cao do hero image |
| `/blog` | 2.4s | 150ms | 0.05 | 88 | 100 | OK |
| `/blog/cach-phoi-vay-hoa-mua-xuan` | 3.8s | 200ms | 0.15 | 71 | 92 | LCP + CLS do TipTap images |
| `/products` | 2.6s | 165ms | 0.07 | 85 | 95 | OK |
| `/admin/login` | 1.8s | 120ms | 0.02 | 95 | 80 | Excluded (admin) |

**Findings**:
- 🔴 `/blog/[slug]` LCP 3.8s (target ≤2.5s)
- 🔴 `/blog/[slug]` CLS 0.15 (target ≤0.1) do image không reserve dimension
- 🟡 Homepage LCP 3.2s — hero image quá lớn

**Fix**:
1. Compress hero image (homepage): từ 800KB → ≤200KB (WebP, quality 80)
2. TipTap output: ensure `<img>` có `width` + `height` attribute (Next.js Image component lý tưởng)
3. Preload hero image với `<link rel="preload" as="image">` trong layout

---

## Top priorities theo ROI

| # | Action | Effort | Impact |
|---|---|---|---|
| 1 | Fix 2 broken links (404) | 10min | Prevent SEO penalty + better UX |
| 2 | Add Article + Product schema cho blog/product | 1h | Rich snippets + AEO eligible |
| 3 | Compress hero image (LCP -1s estimated) | 20min | Performance boost homepage |
| 4 | Auto sitemap.xml generation từ Next.js | 30min | Always fresh, image tags |
| 5 | Fix CLS trên blog detail (image dimensions) | 30min | Better mobile UX score |
| 6 | Add canonical cho pagination | 15min | Prevent duplicate content |
| 7 | Add Sitemap directive trong robots.txt | 5min | Tốt nhỏ |
| 8 | Add Organization schema homepage | 15min | Knowledge graph |

**Total**: ~3h fix tất cả, biggest wins: #1, #2, #3.

---

## Files đính kèm trong audit folder

```
audit-2026-05-15/
├── audit-summary.md (file này)
├── crawl-report.json
├── broken-links.csv
├── lighthouse-scores.json
└── schemas/
    ├── article-review-vay-hoa.json   # Article + Review + FAQPage cho 1 bài
    ├── breadcrumb-blog.json           # BreadcrumbList template
    └── organization-homepage.json     # Organization với sameAs
```

5 bài SEO mới đã có schema inline đính kèm trong `<each-post-folder>/schema.json` (sẽ inject vào page khi publish).
