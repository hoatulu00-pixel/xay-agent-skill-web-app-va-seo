"""Vietnamese text capitalization normalizer for article body."""
from __future__ import annotations

import re

VIET_LOWER_RE = re.compile(r"[a-zà-ỹ]", re.UNICODE)
SENTENCE_TERMINATOR_RE = re.compile(
    r"([.!?…])(\s+)([a-zà-ỹ])",
    re.UNICODE,
)
LIST_PREFIX_RE = re.compile(r"^([\s>#*\-+]*\d*\.?\s*)(.*)$")


def _is_skipline(line: str) -> bool:
    s = line.strip()
    if not s:
        return True
    if s.startswith("---") or s.startswith("```"):
        return True
    if re.match(r"^[a-zA-Z_][\w-]*:\s", s):
        return True
    return False


_EMPHASIS_CHARS = set("*_~`")
_TYPOGRAPHY_REPLACEMENTS = [
    ("—", "-"),  # em dash
    ("–", "-"),  # en dash
]


def sanitize_typography(text: str) -> str:
    """Replace fancy dashes with ASCII hyphen for consistency in Doc + Web."""
    for src, dst in _TYPOGRAPHY_REPLACEMENTS:
        text = text.replace(src, dst)
    return text


def _cap_first_letter(text: str) -> str:
    """Idempotent: if first non-markup char is lowercase, uppercase it. Else leave alone."""
    i = 0
    while i < len(text) and text[i] in _EMPHASIS_CHARS:
        i += 1
    if i >= len(text):
        return text
    ch = text[i]
    if VIET_LOWER_RE.match(ch):
        return text[:i] + ch.upper() + text[i + 1:]
    return text


def _capitalize_sentences(text: str) -> str:
    return SENTENCE_TERMINATOR_RE.sub(
        lambda m: m.group(1) + m.group(2) + m.group(3).upper(),
        text,
    )


def normalize_capitalization(article_md: str) -> str:
    """Capitalize first letter of each line (heading/paragraph/bullet) + sentences."""
    parts = article_md.split("---", 2)
    if len(parts) >= 3 and article_md.startswith("---"):
        head = "---" + parts[1] + "---"
        body = parts[2]
    else:
        head = ""
        body = article_md

    out_lines: list[str] = []
    for line in body.splitlines():
        if _is_skipline(line):
            out_lines.append(line)
            continue
        m = LIST_PREFIX_RE.match(line)
        if not m:
            out_lines.append(line)
            continue
        prefix, rest = m.group(1), m.group(2)
        if not rest:
            out_lines.append(line)
            continue
        rest = _cap_first_letter(rest)
        rest = _capitalize_sentences(rest)
        out_lines.append(prefix + rest)

    fixed_body = "\n".join(out_lines)
    return (head + fixed_body) if head else fixed_body
