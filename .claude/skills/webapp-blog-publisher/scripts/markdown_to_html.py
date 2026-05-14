"""Convert Markdown body -> HTML for web app `content` field."""
from __future__ import annotations

import markdown


def to_html(markdown_body: str) -> str:
    md = markdown.Markdown(extensions=["extra", "sane_lists", "tables", "toc"])
    html = md.convert(markdown_body)
    return html
