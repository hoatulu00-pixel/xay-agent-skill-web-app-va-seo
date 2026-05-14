"""Create + populate a Google Doc in shared Drive folder.

Supports:
  - Markdown headings (#, ##, ###), bullet (-, *), numbered (1., 2.), quote (>)
  - Markdown image syntax: `![alt](public_url)` -> inline embed
  - Markdown TABLES (| col | col |) -> real Google Docs native table with bold header
  - Optional cover_image_url -> top of doc

Image URLs must be publicly reachable (Cloudinary URLs work).
"""
from __future__ import annotations

import re

from .auth_google import GoogleClients
from .utils import load_settings, log, retry

IMG_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$")
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?\s*(:?-+:?\s*\|)+\s*:?-+:?\s*\|?\s*$")
IMG_WIDTH_PT = 450
IMG_HEIGHT_PT = 300


def _create_empty_doc(g: GoogleClients, title: str, folder_id: str) -> str:
    metadata = {
        "name": title,
        "mimeType": "application/vnd.google-apps.document",
        "parents": [folder_id],
    }
    doc = g.drive.files().create(body=metadata, fields="id").execute()
    return doc["id"]


def _is_table_row(line: str) -> bool:
    s = line.strip()
    return s.startswith("|") and s.endswith("|") and s.count("|") >= 2


def _parse_table_row(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def _parse_blocks(markdown_body: str) -> list[dict]:
    """Split markdown into ordered blocks: {'type': 'text', 'lines': [...]} or {'type': 'table', 'rows': [[...]]}."""
    lines = markdown_body.splitlines()
    blocks: list[dict] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if _is_table_row(line):
            # Collect table block
            table_lines = []
            while i < len(lines) and _is_table_row(lines[i]):
                table_lines.append(lines[i])
                i += 1
            rows = []
            for tl in table_lines:
                if TABLE_SEPARATOR_RE.match(tl):
                    continue
                rows.append(_parse_table_row(tl))
            if rows:
                # Normalize column count
                max_cols = max(len(r) for r in rows)
                rows = [r + [""] * (max_cols - len(r)) for r in rows]
                blocks.append({"type": "table", "rows": rows})
        else:
            # Collect text block until next table
            text_lines = []
            while i < len(lines) and not _is_table_row(lines[i]):
                text_lines.append(lines[i])
                i += 1
            blocks.append({"type": "text", "lines": text_lines})
    return blocks


def _doc_end_index(doc: dict) -> int:
    """Return the index where new content can be appended (1 before final newline)."""
    content = doc.get("body", {}).get("content", [])
    if not content:
        return 1
    return content[-1]["endIndex"] - 1


def _build_text_requests(text_lines: list[str], start_index: int) -> list[dict]:
    """Convert text lines to insertText + paragraph style requests starting at start_index."""
    text_blocks: list[tuple] = []
    for raw in text_lines:
        line = raw.rstrip()
        m_img = IMG_RE.match(line)
        if m_img:
            text_blocks.append(("IMAGE", "\n", m_img.group(2), m_img.group(1)))
        elif line.startswith("# "):
            text_blocks.append(("HEADING_1", line[2:].strip() + "\n"))
        elif line.startswith("## "):
            text_blocks.append(("HEADING_2", line[3:].strip() + "\n"))
        elif line.startswith("### "):
            text_blocks.append(("HEADING_3", line[4:].strip() + "\n"))
        elif line.startswith("> "):
            text_blocks.append(("QUOTE", line[2:].strip() + "\n"))
        elif line.startswith(("- ", "* ")):
            text_blocks.append(("BULLET", line[2:].strip() + "\n"))
        elif re.match(r"^\d+\.\s", line):
            text_blocks.append(("NUMBERED", re.sub(r"^\d+\.\s", "", line) + "\n"))
        elif line.strip() == "":
            text_blocks.append(("NORMAL", "\n"))
        else:
            text_blocks.append(("NORMAL", line + "\n"))

    full_text = "".join(b[1] for b in text_blocks)
    if not full_text:
        return []

    requests: list[dict] = [
        {"insertText": {"location": {"index": start_index}, "text": full_text}}
    ]

    image_requests: list[dict] = []
    cursor = start_index
    for block in text_blocks:
        style, content, *extras = block
        length = len(content)
        start, end = cursor, cursor + length

        if style == "IMAGE":
            url = extras[0]
            image_requests.append({
                "insertInlineImage": {
                    "location": {"index": start},
                    "uri": url,
                    "objectSize": {
                        "width": {"magnitude": IMG_WIDTH_PT, "unit": "PT"},
                        "height": {"magnitude": IMG_HEIGHT_PT, "unit": "PT"},
                    },
                },
            })
        elif style.startswith("HEADING"):
            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": start, "endIndex": end},
                    "paragraphStyle": {"namedStyleType": style},
                    "fields": "namedStyleType",
                },
            })
        elif style == "QUOTE":
            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": start, "endIndex": end},
                    "paragraphStyle": {
                        "namedStyleType": "NORMAL_TEXT",
                        "indentStart": {"magnitude": 36, "unit": "PT"},
                    },
                    "fields": "namedStyleType,indentStart",
                },
            })
        elif style == "BULLET":
            requests.append({
                "createParagraphBullets": {
                    "range": {"startIndex": start, "endIndex": end},
                    "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE",
                },
            })
        elif style == "NUMBERED":
            requests.append({
                "createParagraphBullets": {
                    "range": {"startIndex": start, "endIndex": end},
                    "bulletPreset": "NUMBERED_DECIMAL_NESTED",
                },
            })
        cursor = end

    image_requests.sort(key=lambda r: -r["insertInlineImage"]["location"]["index"])
    return requests + image_requests


def _find_last_table(doc: dict) -> tuple[int, dict] | None:
    """Return (element_index, table_element) for the last table in the body."""
    content = doc.get("body", {}).get("content", [])
    for i in range(len(content) - 1, -1, -1):
        if "table" in content[i]:
            return i, content[i]
    return None


def _cells_of_table(table_element: dict) -> list[tuple[int, int, int, int]]:
    """Return [(row_idx, col_idx, content_start_index, content_end_index), ...] for filling."""
    cells: list[tuple[int, int, int, int]] = []
    table = table_element["table"]
    for r_idx, row in enumerate(table["tableRows"]):
        for c_idx, cell in enumerate(row["tableCells"]):
            # cell.content is a list of paragraph elements; first one's startIndex is where text goes
            first_para = cell["content"][0]
            cell_start = first_para["startIndex"]
            cell_end = first_para["endIndex"]
            cells.append((r_idx, c_idx, cell_start, cell_end))
    return cells


def _insert_table_block(g: GoogleClients, doc_id: str, rows: list[list[str]]) -> None:
    """Insert one markdown table as a real Google Docs table with bold header row."""
    n_rows = len(rows)
    n_cols = len(rows[0])

    # Step 1: get current end-of-doc index
    doc = retry(lambda: g.docs.documents().get(documentId=doc_id).execute(), label="docs.get(pre-table)")
    end_index = _doc_end_index(doc)

    # Step 2: insert empty table
    retry(
        lambda: g.docs.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": [{
                "insertTable": {
                    "rows": n_rows,
                    "columns": n_cols,
                    "location": {"index": end_index},
                },
            }]},
        ).execute(),
        label="docs.insertTable",
    )

    # Step 3: refetch and find inserted table
    doc = retry(lambda: g.docs.documents().get(documentId=doc_id).execute(), label="docs.get(post-table)")
    found = _find_last_table(doc)
    if not found:
        log.warning("Inserted table not found in doc after insert; skipping fill")
        return
    _, table_elem = found
    cells = _cells_of_table(table_elem)

    # Step 4: insert text into each cell, sorted DESC by index so earlier inserts don't shift later
    fill_reqs: list[dict] = []
    for (r_idx, c_idx, cell_start, _) in cells:
        txt = str(rows[r_idx][c_idx]).strip()
        if not txt:
            continue
        fill_reqs.append({"insertText": {"location": {"index": cell_start}, "text": txt}})
    fill_reqs.sort(key=lambda req: -req["insertText"]["location"]["index"])

    if fill_reqs:
        retry(
            lambda: g.docs.documents().batchUpdate(
                documentId=doc_id, body={"requests": fill_reqs},
            ).execute(),
            label="docs.fillTable",
        )

    # Step 5: bold the header row (row 0)
    doc = retry(lambda: g.docs.documents().get(documentId=doc_id).execute(), label="docs.get(bold-header)")
    found = _find_last_table(doc)
    if not found:
        return
    _, table_elem = found
    header_cells = [c for c in _cells_of_table(table_elem) if c[0] == 0]
    bold_reqs: list[dict] = []
    for (_, _, cell_start, cell_end) in header_cells:
        if cell_end - cell_start <= 1:
            continue
        bold_reqs.append({
            "updateTextStyle": {
                "range": {"startIndex": cell_start, "endIndex": cell_end - 1},
                "textStyle": {"bold": True},
                "fields": "bold",
            },
        })
    if bold_reqs:
        try:
            retry(
                lambda: g.docs.documents().batchUpdate(
                    documentId=doc_id, body={"requests": bold_reqs},
                ).execute(),
                label="docs.boldHeader",
            )
        except Exception as e:  # noqa: BLE001
            log.warning("Bold header failed: %s", e)


def create_doc(g: GoogleClients, title: str, markdown_body: str,
               cover_image_url: str | None = None) -> tuple[str, str]:
    settings = load_settings()
    folder_id = settings["drive_folder_id"]
    if not folder_id or folder_id.startswith("PASTE_"):
        raise RuntimeError("drive_folder_id not configured. See SETUP.md.")

    log.info("Creating Google Doc: %s", title)
    doc_id = retry(lambda: _create_empty_doc(g, title, folder_id), label="drive.create_doc")

    blocks = _parse_blocks(markdown_body)
    log.info("Parsed %d block(s): %d table(s)", len(blocks),
             sum(1 for b in blocks if b["type"] == "table"))

    for block in blocks:
        if block["type"] == "text":
            doc = retry(lambda: g.docs.documents().get(documentId=doc_id).execute(), label="docs.get(pre-text)")
            end_index = _doc_end_index(doc)
            reqs = _build_text_requests(block["lines"], end_index)
            if reqs:
                retry(
                    lambda: g.docs.documents().batchUpdate(
                        documentId=doc_id, body={"requests": reqs},
                    ).execute(),
                    label="docs.batchUpdate.text",
                )
        elif block["type"] == "table":
            _insert_table_block(g, doc_id, block["rows"])

    if cover_image_url:
        try:
            retry(
                lambda: g.docs.documents().batchUpdate(
                    documentId=doc_id,
                    body={"requests": [{
                        "insertInlineImage": {
                            "location": {"index": 1},
                            "uri": cover_image_url,
                            "objectSize": {
                                "width": {"magnitude": IMG_WIDTH_PT, "unit": "PT"},
                                "height": {"magnitude": IMG_HEIGHT_PT, "unit": "PT"},
                            },
                        },
                    }]},
                ).execute(),
                label="docs.coverImage",
            )
            log.info("Cover image embedded at top of doc")
        except Exception as e:  # noqa: BLE001
            log.warning("Cover image embedding failed (%s); doc has no cover", e)

    share_link = f"https://docs.google.com/document/d/{doc_id}/edit"
    log.info("Doc created: %s", share_link)
    return doc_id, share_link


def delete_doc(g: GoogleClients, doc_id: str) -> bool:
    """Trash a Drive Doc by ID. Returns True on success."""
    try:
        retry(lambda: g.drive.files().delete(fileId=doc_id).execute(), label="drive.delete_doc")
        log.info("Deleted old Doc %s", doc_id)
        return True
    except Exception as e:  # noqa: BLE001
        log.warning("Could not delete Doc %s: %s", doc_id, e)
        return False
