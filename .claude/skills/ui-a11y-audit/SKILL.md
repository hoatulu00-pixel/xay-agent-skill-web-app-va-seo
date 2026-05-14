---
name: ui-a11y-audit
description: Audit accessibility WCAG AA cho component React/Next.js trong Hoa Xuân Fashion frontend. Kiểm tra alt text, ARIA labels, keyboard navigation, color contrast, focus management. Kích hoạt khi user nói "audit a11y", "kiểm tra accessibility", "WCAG", "alt text", "keyboard nav", "screen reader". Output là report Markdown với findings + severity + fix gợi ý.
---

# Skill: UI Accessibility Audit

Audit accessibility WCAG 2.1 Level AA cho component và page Next.js.

## Khi nào kích hoạt

- "Audit a11y cho PostEditor.tsx"
- "Kiểm tra accessibility cho admin panel"
- "Check WCAG cho trang blog"
- Agent `webapp-frontend` request audit trước khi báo task xong

## Input

- **Target**: file path hoặc folder (vd: `frontend/components/admin/`, hoặc `frontend/app/admin/posts/page.tsx`)
- **Level**: AA (mặc định) hoặc AAA

## Output

Report Markdown `BTVN BUỔI 3/outputs/webapp/a11y-audit-<date>.md`:
```markdown
# A11y Audit — PostEditor.tsx (2026-05-14)

## Findings

### [HIGH] Missing alt text on TipTap image upload
- File: `frontend/components/admin/PostEditor.tsx:87`
- WCAG: 1.1.1 Non-text Content (Level A)
- Evidence: `<img src={url} />` không có `alt`
- Fix: prompt user nhập alt text khi upload, lưu vào TipTap node attrs

### [MEDIUM] Color contrast insufficient
- File: `frontend/app/blog/page.tsx:42`
- WCAG: 1.4.3 Contrast Minimum
- Evidence: `text-gray-400` trên `bg-white` = 2.85:1 (cần ≥4.5:1)
- Fix: đổi sang `text-gray-600` hoặc darker

## Summary
- HIGH: 2, MEDIUM: 4, LOW: 1
- Priority fixes: #1 (alt text), #4 (focus indicator)
```

## Files trong skill

- `scripts/check_a11y.py` — parse JSX, detect common issues (missing alt, missing label, ARIA misuse)
- `references/wcag-checklist.md` — WCAG 2.1 AA checklist với code examples
- `references/aria-patterns.md` — ARIA Authoring Practices Guide patterns (combobox, modal, tabs, ...)

## Workflow

1. **Scan files** target (glob `**/*.tsx`).
2. **AST parse** JSX để detect:
   - `<img>` thiếu `alt` (lưu ý: empty string `alt=""` OK cho decorative)
   - `<input>` thiếu `<label htmlFor>`
   - `<button>` icon-only thiếu `aria-label`
   - Sai `role` (vd: `role="button"` trên `<div>` thay vì dùng `<button>`)
   - `onClick` trên non-interactive element (cần `onKeyDown` + `role` + `tabIndex`)
3. **Check color contrast** (manual, không tự động — flag class Tailwind đáng nghi như `text-gray-400`).
4. **Generate report** với severity + WCAG criterion + fix code snippet.

## Quy tắc

1. **Severity mapping**:
   - WCAG Level A failure → HIGH
   - Level AA failure → MEDIUM
   - Level AAA / best practice → LOW
2. **Mọi finding** phải có file:line bằng chứng.
3. **Fix gợi ý** phải actionable (code snippet, không generic "add alt text").
4. **Không tự fix** — đây là audit skill, fix thuộc về `webapp-frontend` agent.

## Anti-patterns

- ❌ Suggest dùng `tabindex="-1"` để "fix" focus (sai trong nhiều case)
- ❌ Bỏ qua decorative images (`alt=""` là đúng, không phải lỗi)
- ❌ Recommend ARIA khi semantic HTML đủ (luôn ưu tiên semantic)
- ❌ Audit mà không có severity rating

## Liên kết

- Agent dùng: `webapp-frontend`
- Tài liệu: WCAG 2.1 Quick Reference, ARIA Authoring Practices Guide
