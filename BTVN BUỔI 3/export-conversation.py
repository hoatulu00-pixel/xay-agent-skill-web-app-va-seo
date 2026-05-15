"""Export Claude Code transcript JSONL -> human-readable conversation log.

Doc tu file JSONL trong ~/.claude/projects/ va xuat ra conversation-log.txt
de luu lai lich su cuoc tro chuyen truoc khi /compact.

Lenh:
  python "BTVN BUOI 3/export-conversation.py"
"""
from __future__ import annotations

import io
import json
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "buffer"):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent.parent
TRANSCRIPT = Path(
    r"C:/Users/yingt/.claude/projects/C--Users-yingt-Downloads-Claude-Code--SEONGON-/"
    r"cfd8d8ad-b64e-4915-8207-e509703272da.jsonl"
)
OUTPUT = ROOT / "BTVN BUỔI 3" / "conversation-log.txt"


def fmt_ts(ts: str) -> str:
    if not ts:
        return ""
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ts


def render_content(content) -> str:
    """Render assistant/user message content (list of blocks) thanh text."""
    if isinstance(content, str):
        return content.strip()
    if not isinstance(content, list):
        return str(content)

    parts = []
    for block in content:
        if not isinstance(block, dict):
            parts.append(str(block))
            continue
        btype = block.get("type")
        if btype == "text":
            txt = (block.get("text") or "").strip()
            if txt:
                parts.append(txt)
        elif btype == "thinking":
            # Skip thinking blocks (internal reasoning) - too verbose
            continue
        elif btype == "tool_use":
            name = block.get("name") or "?"
            inp = block.get("input") or {}
            # Compact summary of tool call
            summary = ", ".join(
                f"{k}={json.dumps(v, ensure_ascii=False)[:80]}"
                for k, v in inp.items()
                if k not in ("content",)  # skip huge file contents
            )
            parts.append(f"[TOOL CALL: {name}]  {summary[:300]}")
        elif btype == "tool_result":
            result = block.get("content")
            if isinstance(result, list):
                text_results = []
                for r in result:
                    if isinstance(r, dict) and r.get("type") == "text":
                        text_results.append((r.get("text") or "")[:500])
                joined = " | ".join(text_results)
                parts.append(f"[TOOL RESULT]  {joined[:500]}")
            elif isinstance(result, str):
                parts.append(f"[TOOL RESULT]  {result[:500]}")
        else:
            parts.append(f"[{btype}]")
    return "\n".join(parts).strip()


def main():
    if not TRANSCRIPT.exists():
        print(f"ERROR: transcript not found: {TRANSCRIPT}")
        sys.exit(1)

    print(f"Doc transcript: {TRANSCRIPT.name}")
    print(f"Kich thuoc: {TRANSCRIPT.stat().st_size:,} bytes")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    lines_out = []
    lines_out.append("=" * 80)
    lines_out.append("CLAUDE CODE - CONVERSATION LOG")
    lines_out.append(f"Source: {TRANSCRIPT.name}")
    lines_out.append(f"Exported: {datetime.now().isoformat(timespec='seconds')}")
    lines_out.append(f"Session: cfd8d8ad-b64e-4915-8207-e509703272da")
    lines_out.append("=" * 80)
    lines_out.append("")

    n_user = 0
    n_assistant = 0
    n_total = 0
    n_skipped = 0

    with TRANSCRIPT.open("r", encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            n_total += 1
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                n_skipped += 1
                continue

            mtype = obj.get("type")
            if mtype not in ("user", "assistant"):
                continue

            msg = obj.get("message") or {}
            role = msg.get("role") or mtype
            content = msg.get("content")
            ts = obj.get("timestamp") or ""

            rendered = render_content(content)
            if not rendered:
                continue

            # Skip system reminders + tool result wrappers as standalone "user" turns
            # (they bloat the log; keep only genuine user prompts)
            if role == "user" and rendered.startswith("[TOOL RESULT]"):
                continue

            sep = "-" * 80
            lines_out.append(sep)
            lines_out.append(f"[{role.upper()}]  {fmt_ts(ts)}")
            lines_out.append(sep)
            lines_out.append(rendered)
            lines_out.append("")

            if role == "user":
                n_user += 1
            else:
                n_assistant += 1

    lines_out.append("=" * 80)
    lines_out.append(f"Tong: {n_total} dong | User: {n_user} | Assistant: {n_assistant} | Skip: {n_skipped}")
    lines_out.append("=" * 80)

    OUTPUT.write_text("\n".join(lines_out), encoding="utf-8")
    print(f"\nXuat thanh cong: {OUTPUT}")
    print(f"  - {n_user} user messages")
    print(f"  - {n_assistant} assistant messages")
    print(f"  - File size: {OUTPUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
