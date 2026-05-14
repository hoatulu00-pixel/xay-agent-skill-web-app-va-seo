---
name: technical-seo-audit
description: Audit kỹ thuật SEO toàn bộ Hoa Xuân Fashion blog/site — crawl tất cả URL, check status codes, broken links, redirect chain, sitemap.xml, robots.txt, canonical, Core Web Vitals qua Lighthouse. Kích hoạt khi user nói "audit technical SEO", "crawl site Hoa Xuân", "kiểm tra sitemap", "Core Web Vitals", "Lighthouse audit", "broken link check". Output là audit report Markdown + CSV broken links + Lighthouse JSON.
---

# Skill: Technical SEO Audit

Audit kỹ thuật SEO end-to-end cho website.

## Khi nào kích hoạt

- "Audit technical SEO blog Hoa Xuân"
- "Crawl toàn bộ site, check broken link"
- "Lighthouse cho 5 page chính"
- "Sitemap.xml có đúng không?"
- Agent `seo-technical` chạy định kỳ hàng tháng

## Input

- **Base URL**: `https://resilient-expression-production-1149.up.railway.app` (default)
- **Scope**: `blog-only` | `full-site` (default: full-site)
- **Max URLs**: 500 (default), tránh crawl quá dài

## Output

3 files lưu vào `BTVN BUỔI 3/outputs/seo/audit-<date>/`:

1. **`crawl-report.json`** — tất cả URLs crawled + status codes + response time
2. **`broken-links.csv`** — chỉ URLs trả 4xx/5xx + source page
3. **`lighthouse-scores.json`** — Lighthouse scores top 10 page (Performance, Accessibility, Best Practices, SEO)
4. **`audit-summary.md`** — tổng hợp + priorities + recommendations

```markdown
# Technical SEO Audit Summary (2026-05-14)

## Crawl Stats
- Total URLs: 142
- 2xx: 138, 3xx: 2, 4xx: 2, 5xx: 0
- Avg response time: 320ms

## Issues found

### [HIGH] 2 broken links (404)
- /blog/old-post → linked from /blog (BlogCard component)
- /products/discontinued → linked from homepage

### [MEDIUM] Missing canonical on 12 pages
- /blog/page/2, /blog/page/3, ... pagination không có canonical → duplicate content risk

### [MEDIUM] Sitemap.xml issue
- /sitemap.xml: missing 5 blog posts đã publish trong tuần
- lastmod cũ (1 tháng trước)

### [HIGH] Core Web Vitals (Lighthouse)
- Homepage: LCP 3.8s (target ≤2.5s) — cover image hero quá lớn
- /blog/[slug]: CLS 0.15 (target ≤0.1) — TipTap image lazy load gây shift

## Top 5 priorities theo ROI
1. Fix 2 broken links (10 min, prevent SEO penalty)
2. Compress hero images (LCP -1.5s estimated)
3. Add canonical to pagination
4. Regenerate sitemap.xml (automate via Next.js)
5. Reserve image dimensions để fix CLS
```

## Files trong skill

- `scripts/crawler.py` — requests + bs4 crawl all internal URLs từ homepage, build URL graph
- `scripts/lighthouse_runner.ps1` — chạy `lighthouse <url> --output=json` cho top 10 page
- `scripts/sitemap_validator.py` — fetch sitemap.xml, validate structure + freshness
- `references/audit-checklist.md` — 25 items technical SEO checklist

## Workflow

1. **Crawl**:
   ```python
   # crawler.py
   queue = [base_url]
   visited = set()
   while queue and len(visited) < max_urls:
       url = queue.pop(0)
       if url in visited: continue
       r = requests.get(url)
       # parse r.text với bs4, extract <a href>
       # add internal URLs vào queue
   ```
2. **Status check**: log 4xx/5xx vào broken-links.csv
3. **Sitemap validate**: GET /sitemap.xml, parse XML, đối chiếu với crawl result (URL nào có trong crawl mà thiếu sitemap = miss)
4. **Robots.txt validate**: GET /robots.txt, check syntax + Sitemap directive
5. **Lighthouse top 10**: pick homepage + 5 top traffic pages + 4 sample page templates → chạy Lighthouse → parse score
6. **Canonical check**: bs4 parse `<link rel="canonical">` mỗi page, flag missing
7. **Build summary** report với priority theo ROI (fix effort vs impact)

## Quy tắc

1. **Rate limit crawl**: 1 req/sec để không DDoS chính site (production).
2. **User-Agent** rõ ràng: `HoaXuanSEOAudit/1.0 (+admin@hoaxuan.com)` — không giả Googlebot.
3. **Respect robots.txt** — nếu user-agent bị disallow path, skip.
4. **Lighthouse run desktop + mobile** (mobile weight cao hơn cho Google rank).
5. **Báo cáo priority theo ROI**: effort thấp + impact cao = top.

## Anti-patterns

- ❌ Crawl không rate limit → DoS chính site
- ❌ User-Agent giả Googlebot (vi phạm Google ToS)
- ❌ Lighthouse chỉ desktop (mobile weight cao hơn 60%)
- ❌ Báo cáo issue mà không suggest fix
- ❌ Crawl URL ngoài domain (không cần thiết)

## Liên kết

- Agent dùng: `seo-technical`
- Sister skill: `schema-markup-generator` (audit schema sau khi technical fix)
- Tools: Lighthouse CLI, requests, beautifulsoup4
