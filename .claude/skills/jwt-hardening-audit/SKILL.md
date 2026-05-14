---
name: jwt-hardening-audit
description: Audit JWT implementation cho Hoa Xuân Fashion — kiểm tra algorithm, secret strength, expiry, refresh flow, claim validation, lưu trữ token client-side. Kích hoạt khi user nói "audit JWT", "kiểm tra token security", "JWT hardening", "auth security review", "OWASP JWT". Output là report Markdown với findings + severity + CWE + fix gợi ý.
---

# Skill: JWT Hardening Audit

Audit JWT implementation theo OWASP ASVS Level 1 + JWT best practices.

## Khi nào kích hoạt

- "Audit JWT toàn bộ backend"
- "Kiểm tra `auth_service.py` có hardening đúng không"
- "JWT có an toàn không?"
- Agent `webapp-security` chạy pre-deploy gate

## Input

- **Scope**: `backend` | `frontend` | `both`
- **Path**: optional, default scan toàn bộ `hoa-xuan-fashion/`

## Output

Report Markdown `BTVN BUỔI 3/outputs/webapp/jwt-audit-<date>.md`:
```markdown
# JWT Hardening Audit (2026-05-14)

## Findings

### [HIGH] CWE-326 Algorithm allowed downgrade
- File: `backend/app/services/auth_service.py:18`
- Issue: jwt.decode không restrict algorithms whitelist
- Evidence: `jwt.decode(token, secret)` → có thể accept `alg: none`
- Fix: `jwt.decode(token, secret, algorithms=["HS256"])`

### [MEDIUM] CWE-613 Long token expiry
- File: `services/auth_service.py:33`
- Issue: `expires_delta = timedelta(days=7)` quá dài cho access token
- Fix: access token ≤30 phút + refresh token 7 ngày

### [HIGH] CWE-522 Token in localStorage (XSS risk)
- File: `frontend/lib/auth.ts:24`
- Issue: `localStorage.setItem('token', jwt)` — JS đọc được, XSS hijack
- Fix: dùng httpOnly cookie (đã thấy `hx_token` cookie 7 ngày) — verify backend set cookie với `httpOnly: True, secure: True, samesite: 'strict'`

## Summary
- HIGH: 2, MEDIUM: 3, LOW: 1
- Top fixes: #1 (algorithm whitelist), #3 (httpOnly cookie verify)
```

## Files trong skill

- `scripts/scan_jwt.py` — grep JWT-related patterns, parse Python/TS for jwt.encode/decode usage
- `references/jwt-checklist.md` — JWT security checklist (12 items)
- `references/owasp-asvs-auth.md` — OWASP ASVS V2 (authentication) requirements

## JWT Security Checklist (12 items)

1. ✅ **Algorithm whitelist**: `algorithms=["HS256"]` hoặc `["RS256"]` — không cho phép `alg: none`
2. ✅ **Secret strength**: ≥256 bit random (HS256) hoặc RSA 2048+ (RS256)
3. ✅ **Secret từ env**: không hard-code trong code
4. ✅ **Access token expiry ≤30 phút**
5. ✅ **Refresh token flow**: refresh token riêng, lưu DB (revocable)
6. ✅ **Audience claim** (`aud`) validation
7. ✅ **Issuer claim** (`iss`) validation
8. ✅ **No sensitive data trong payload** (password, SSN, ...) — JWT KHÔNG encrypted
9. ✅ **Token storage client**: httpOnly cookie (preferred) hoặc memory; KHÔNG localStorage
10. ✅ **Logout invalidate token**: blacklist hoặc rotate secret
11. ✅ **HTTPS only**: `secure: True` cookie, redirect HTTP → HTTPS
12. ✅ **Rate limit /login**: brute force protection (SlowAPI hoặc Cloudflare)

## Workflow

1. **Scan backend** Python files có `jwt.encode`, `jwt.decode`, `pyjwt`, `python-jose`.
2. **Scan frontend** TS files có `localStorage`, `sessionStorage`, `cookie`, `Authorization: Bearer`.
3. **Check config**: `SECRET_KEY` trong `.env`, không trong git history.
4. **Test token decode** thử với `alg: none` payload (nếu accepted → CRITICAL).
5. **Build report** với severity + CWE + fix code snippet.

## Quy tắc

1. **Read-only audit** — không tự edit code.
2. **Severity mapping**:
   - Algorithm none accepted, secret leaked → CRITICAL
   - Algorithm whitelist missing, long expiry → HIGH
   - Missing aud/iss → MEDIUM
   - Best practice violation → LOW
3. **Mọi finding** có file:line + CWE ID + evidence + fix snippet.
4. **Không suggest** offensive exploit code — chỉ defensive fix.

## Anti-patterns

- ❌ Recommend dùng `localStorage` cho JWT (XSS hijack risk)
- ❌ Skip backend audit, chỉ check frontend
- ❌ Finding generic "JWT có vulnerability" mà không có severity
- ❌ Suggest dùng `alg: none` để "đơn giản hoá test" — sai hoàn toàn

## Liên kết

- Agent dùng: `webapp-security`
- Sister skill: `dep-vulnerability-scan` (check pyjwt CVE)
- Pattern target: `hoa-xuan-fashion/backend/app/services/auth_service.py`, `frontend/lib/auth.ts`
