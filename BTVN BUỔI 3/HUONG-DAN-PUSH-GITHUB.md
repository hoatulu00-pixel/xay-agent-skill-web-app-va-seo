# Hướng dẫn export conversation + push lên Github

> Làm theo thứ tự 3 phase dưới đây. Mỗi bước copy/paste vào terminal.

---

## PHASE 1 — Export conversation (PHẢI làm trong Claude Code CLI)

### Bước 1.1: Trong Claude Code CLI hiện tại, gõ:

```
/export
```

Claude Code sẽ hỏi format (markdown / json / clipboard). **Chọn markdown** hoặc **clipboard**.

### Bước 1.2: Lưu file vào đúng path

- Nếu chọn **markdown**: Claude Code tạo file `.md` ở thư mục tạm. Copy nội dung sang file `BTVN BUỔI 3/conversation-log.txt` (overwrite placeholder).
- Nếu chọn **clipboard**: mở Notepad, paste, save as `BTVN BUỔI 3/conversation-log.txt` (encoding UTF-8).

### Bước 1.3: Verify

Mở PowerShell tại root workspace:

```powershell
(Get-Content "BTVN BUỔI 3/conversation-log.txt" | Measure-Object -Line).Lines
```

Kết quả phải > 100 (nhiều dòng) — không còn là placeholder 16 dòng.

---

## PHASE 2 — Git init + commit local (Claude đã chuẩn bị sẵn .gitignore)

Mở PowerShell tại root workspace `C:\Users\yingt\Downloads\Claude Code (SEONGON)`. Copy paste lần lượt:

### Bước 2.1: Init repo

```powershell
git init
git branch -M main
```

### Bước 2.2: Cấu hình user (nếu chưa)

```powershell
git config user.name "Hoa Tu Lu"
git config user.email "hoatulu00@gmail.com"
```

### Bước 2.3: Verify .gitignore hoạt động

```powershell
git status --short | Select-Object -First 30
```

→ Không thấy `node_modules`, `.venv`, `__pycache__`, `settings.json` (secrets). Nếu thấy → báo lại.

### Bước 2.4: Add + commit

```powershell
git add .
git commit -m "BTVN Buổi 3: 6 sub-agents + 15 atomic skills + Comment feature + SEO campaign"
```

→ Commit thành công sẽ in ra số file changed (kỳ vọng 200+ file).

### Bước 2.5: Verify

```powershell
git log --oneline
git ls-files | Measure-Object -Line
```

---

## PHASE 3 — Tạo repo Github + push (user làm)

### Bước 3.1: Tạo repo TRỐNG trên Github

1. Mở https://github.com/new
2. Repository name: `claude-code-seongon-btvn-buoi-3` (hoặc tên bạn thích)
3. Description: `BTVN Buổi 3 — 6 sub-agents + 15 atomic skills cho Hoa Xuân Fashion + SEO campaign`
4. **KHÔNG tick** "Add a README", "Add .gitignore", "Choose a license" (vì local đã có)
5. **Public** (để thầy review được) hoặc Private cũng OK
6. Click **Create repository**

### Bước 3.2: Github sẽ hiển thị 2 lệnh — copy URL repo

URL có dạng: `https://github.com/<username>/claude-code-seongon-btvn-buoi-3.git`

### Bước 3.3: Push từ PowerShell

```powershell
# Thay <URL> bằng URL repo của bạn
git remote add origin https://github.com/<username>/claude-code-seongon-btvn-buoi-3.git
git push -u origin main
```

→ Lần đầu push, Github sẽ hiện popup login. Đăng nhập bằng:
- Github username
- **Personal Access Token** (KHÔNG phải password Github)

### Bước 3.4: Nếu chưa có Personal Access Token

1. https://github.com/settings/tokens/new
2. Note: `claude-code-cli`
3. Expiration: 90 days
4. Scopes: tick **repo** (full)
5. Click **Generate token** → copy ngay (chỉ hiện 1 lần)
6. Paste làm password khi git push hỏi

### Bước 3.5: Verify push thành công

Mở URL repo trên Github → phải thấy:

- `.claude/agents/` (6 files)
- `.claude/skills/` (15 folders)
- `BTVN BUỔI 3/` (README, orchestration-plan, conversation-log, outputs/)
- `hoa-xuan-fashion/`
- `CLAUDE.md`

---

## Checklist nộp bài

- [ ] Phase 1: `BTVN BUỔI 3/conversation-log.txt` không còn là placeholder
- [ ] Phase 2: `git log` có ít nhất 1 commit
- [ ] Phase 3: URL Github repo public và truy cập được
- [ ] Verify: trên Github thấy đủ `.claude/agents/` (6 files) + `.claude/skills/` (15 folders)
- [ ] Verify: `BTVN BUỔI 3/outputs/` có đủ webapp/ + seo/ artifacts
- [ ] Submit: gửi URL Github + screenshot kết quả cho thầy

---

## Lệnh cứu hộ (troubleshooting)

### Lỡ commit secrets (`.env`, `settings.json`)?

```powershell
git rm --cached <file-secrets>
git commit -m "Remove leaked secrets"
# Sau đó rotate secret đó ngay
```

### Lỡ push lên Github rồi mới phát hiện secrets?

```powershell
# Xóa file khỏi history (chỉ cho file nhỏ)
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch <file>" --prune-empty --tag-name-filter cat -- --all
git push --force origin main
# QUAN TRỌNG: rotate secret ngay vì đã public trên Github
```

### Repo quá lớn không push được?

```powershell
# Check size
git count-objects -vH

# Nếu lớn do seo-content-workspace backup, bỏ comment dòng trong .gitignore:
# seo-content-workspace/.claude/skills/seo-content-publisher/outputs/
# Sau đó:
git rm -r --cached seo-content-workspace/.claude/skills/seo-content-publisher/outputs/
git add .gitignore
git commit -m "Exclude historical SEO outputs from repo"
git push
```

### Chưa cài git trên máy?

Download: https://git-scm.com/download/win → install với default options → restart PowerShell.
