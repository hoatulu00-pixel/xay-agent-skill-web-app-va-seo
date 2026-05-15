"""Mo permission 'anyone with link can view' cho tat ca Google Doc trong Drive folder Hoa Xuan.

Lenh:
  python "BTVN BUỔI 3/share-all-docs.py"
"""
from __future__ import annotations

import io
import importlib
import sys
from pathlib import Path

if hasattr(sys.stdout, "buffer"):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / ".claude" / "skills"


def load_skill_module(skill_name: str, module_path: str):
    skill_root = SKILLS_DIR / skill_name
    to_remove = [k for k in sys.modules if k.startswith("scripts")]
    for k in to_remove:
        del sys.modules[k]
    sys.path[:] = [p for p in sys.path if str(SKILLS_DIR) not in p]
    sys.path.insert(0, str(skill_root))
    return importlib.import_module(module_path)


def main():
    auth = load_skill_module("google-doc-publisher", "scripts.auth_google")
    utils = load_skill_module("google-doc-publisher", "scripts.utils")

    settings = utils.load_settings()
    folder_id = settings["drive_folder_id"]
    print(f"Drive folder: {folder_id}\n")

    g = auth.get_clients()

    # List tat ca Google Doc trong folder (phan trang)
    docs = []
    page_token = None
    while True:
        resp = g.drive.files().list(
            q=f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.document' and trashed=false",
            pageSize=100,
            fields="nextPageToken, files(id, name)",
            pageToken=page_token,
        ).execute()
        docs.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    print(f"Tim thay {len(docs)} Google Doc trong folder.\n")

    # Apply anyone:reader permission cho moi doc
    ok = 0
    skipped = 0
    failed = 0
    for d in docs:
        doc_id = d["id"]
        name = d["name"]
        # Check existing perms
        try:
            existing = g.drive.permissions().list(
                fileId=doc_id, fields="permissions(id,type,role)"
            ).execute().get("permissions", [])
            has_anyone = any(p.get("type") == "anyone" and p.get("role") in ("reader", "writer", "commenter") for p in existing)
            if has_anyone:
                print(f"  [SKIP] {name[:60]} (da co anyone permission)")
                skipped += 1
                continue
        except Exception as e:
            print(f"  [WARN list perms] {name[:60]}: {e}")

        try:
            g.drive.permissions().create(
                fileId=doc_id,
                body={"type": "anyone", "role": "reader"},
                fields="id",
            ).execute()
            print(f"  [OK]   {name[:60]}")
            print(f"         https://docs.google.com/document/d/{doc_id}/edit")
            ok += 1
        except Exception as e:
            print(f"  [FAIL] {name[:60]}: {e}")
            failed += 1

    print(f"\nTong ket: {ok} mo moi, {skipped} bo qua (da mo), {failed} loi.")


if __name__ == "__main__":
    main()
