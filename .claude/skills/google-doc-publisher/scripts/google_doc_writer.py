"""Create + populate a Google Doc in shared Drive folder.

Supports markdown image syntax: `![alt](public_url)` → inline image embed.
Image URLs must be publicly reachable (Cloudinary URLs work).
"""
from __future__ import annotations

import re

from .auth_google import GoogleClients
from .utils import load_settings, log, retry

IMG_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$")
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


def _md_to_requests(markdown_body: str) -> tuple[list[dict], list[dict]]:
    """Return (text_requests, image_requests). Image inserts are sorted desc by index."""
    lines = markdown_body.splitlines()

    text_blocks: list[tuple] = []  # (style, content, *extras)
    for raw in lines:
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
    if not full_text.endswith("\n"):
        full_text += "\n"

    text_requests: list[dict] = [
        {"insertText": {"location": {"index": 1}, "text": full_text}},
    ]
    image_requests: list[dict] = []

    cursor = 1
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
            text_requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": start, "endIndex": end},
                    "paragraphStyle": {"namedStyleType": style},
                    "fields": "namedStyleType",
                },
            })
        elif style == "QUOTE":
            text_requests.append({
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
            text_requests.append({
                "createParagraphBullets": {
                    "range": {"startIndex": start, "endIndex": end},
                    "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE",
                },
            })
        elif style == "NUMBERED":
            text_requests.append({
                "createParagraphBullets": {
                    "range": {"startIndex": start, "endIndex": end},
                    "bulletPreset": "NUMBERED_DECIMAL_NESTED",
                },
            })
        cursor = end

    image_requests.sort(key=lambda r: -r["insertInlineImage"]["location"]["index"])
    return text_requests, image_requests


def create_doc(g: GoogleClients, title: str, markdown_body: str,
               cover_image_url: str | None = None) -> tuple[str, str]:
    settings = load_settings()
    folder_id = settings["drive_folder_id"]
    if not folder_id or folder_id.startswith("PASTE_"):
        raise RuntimeError("drive_folder_id not configured. See SETUP.md.")

    log.info("Creating Google Doc: %s", title)
    doc_id = retry(lambda: _create_empty_doc(g, title, folder_id), label="drive.create_doc")

    text_requests, image_requests = _md_to_requests(markdown_body)

    retry(
        lambda: g.docs.documents().batchUpdate(documentId=doc_id, body={"requests": text_requests}).execute(),
        label="docs.batchUpdate.text",
    )

    if cover_image_url:
        image_requests.append({
            "insertInlineImage": {
                "location": {"index": 1},
                "uri": cover_image_url,
                "objectSize": {
                    "width": {"magnitude": IMG_WIDTH_PT, "unit": "PT"},
                    "height": {"magnitude": IMG_HEIGHT_PT, "unit": "PT"},
                },
            },
        })
        image_requests.sort(key=lambda r: -r["insertInlineImage"]["location"]["index"])

    if image_requests:
        try:
            retry(
                lambda: g.docs.documents().batchUpdate(documentId=doc_id, body={"requests": image_requests}).execute(),
                label="docs.batchUpdate.images",
            )
            log.info("Embedded %d image(s) into Doc%s", len(image_requests),
                     " (incl. cover)" if cover_image_url else "")
        except Exception as e:  # noqa: BLE001
            log.warning("Image embedding failed (%s); Doc has text only", e)

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
