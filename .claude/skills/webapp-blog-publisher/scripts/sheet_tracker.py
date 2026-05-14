"""Google Sheets tracker — append/update rows."""
from __future__ import annotations

import re
from datetime import datetime

from .auth_google import GoogleClients, get_clients
from .utils import load_settings, log, retry, save_settings

TAB = "Posts"
HEADER = ["STT", "Ngày đăng", "Keyword", "Tiêu đề bài viết", "Link Google Doc",
          "Content Status", "Web Status", "Link Web", "Notes"]

HEADER_GREEN = {"green": 1.0}
HEADER_TEXT = {"green": 0.247}
WHITE = {"red": 1.0, "green": 1.0, "blue": 1.0}
BORDER_LIGHT = {"red": 0.78, "green": 0.78, "blue": 0.78}
N_COLS = len(HEADER)
DATE_PATTERN = "dd/MM/yyyy"

CONTENT_STATUSES = ["Pending", "Done", "Failed"]
WEB_STATUSES = ["Not yet", "Published", "Failed"]

STATUS_COLOR_GREEN = {"red": 0.71, "green": 0.88, "blue": 0.70}   # Done, Published
STATUS_COLOR_RED = {"red": 0.96, "green": 0.78, "blue": 0.77}     # Failed
STATUS_COLOR_GRAY = {"red": 0.93, "green": 0.93, "blue": 0.93}    # Pending, Not yet


def _strip_hyperlink(val: str) -> str:
    """Convert =HYPERLINK("url","label") back to plain url."""
    s = str(val).strip()
    m = re.match(r'^=HYPERLINK\(\s*"([^"]+)"', s, re.IGNORECASE)
    if m:
        return m.group(1)
    return val


def _validation_request(sheet_tab_id: int, col_index: int, values: list[str], max_row: int) -> dict:
    return {"setDataValidation": {
        "range": {"sheetId": sheet_tab_id, "startRowIndex": 1, "endRowIndex": max_row,
                  "startColumnIndex": col_index, "endColumnIndex": col_index + 1},
        "rule": {
            "condition": {"type": "ONE_OF_LIST",
                          "values": [{"userEnteredValue": v} for v in values]},
            "strict": False,
            "showCustomUi": True,
        },
    }}


def _conditional_format_rule(sheet_tab_id: int, col_index: int, value: str, color: dict, max_row: int) -> dict:
    return {"addConditionalFormatRule": {
        "rule": {
            "ranges": [{"sheetId": sheet_tab_id, "startRowIndex": 1, "endRowIndex": max_row,
                        "startColumnIndex": col_index, "endColumnIndex": col_index + 1}],
            "booleanRule": {
                "condition": {"type": "TEXT_EQ", "values": [{"userEnteredValue": value}]},
                "format": {"backgroundColor": color},
            },
        },
        "index": 0,
    }}


def _delete_all_conditional_format_rules(g, sheet_id: str, sheet_tab_id: int) -> None:
    spreadsheet = g.sheets.spreadsheets().get(spreadsheetId=sheet_id).execute()
    rules = []
    for s in spreadsheet["sheets"]:
        if s["properties"]["sheetId"] != sheet_tab_id:
            continue
        rules = s.get("conditionalFormats", [])
        break
    if not rules:
        return
    requests = [{"deleteConditionalFormatRule": {"sheetId": sheet_tab_id, "index": 0}} for _ in rules]
    if requests:
        g.sheets.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body={"requests": requests}).execute()


def _format_requests(sheet_tab_id: int, max_data_row: int = 1000) -> list[dict]:
    """Wipe all formatting, then green header + white rows + thick borders + dropdowns."""
    wipe_range = {"sheetId": sheet_tab_id}
    base_range = {"sheetId": sheet_tab_id, "startRowIndex": 0, "endRowIndex": max_data_row,
                  "startColumnIndex": 0, "endColumnIndex": N_COLS}
    header_range = {"sheetId": sheet_tab_id, "startRowIndex": 0, "endRowIndex": 1,
                    "startColumnIndex": 0, "endColumnIndex": N_COLS}
    data_range = {"sheetId": sheet_tab_id, "startRowIndex": 1, "endRowIndex": max_data_row,
                  "startColumnIndex": 0, "endColumnIndex": N_COLS}
    thin = {"style": "SOLID", "color": BORDER_LIGHT}
    return [
        {"repeatCell": {
            "range": wipe_range,
            "cell": {"userEnteredFormat": {
                "backgroundColor": WHITE,
                "textFormat": {"bold": False, "italic": False, "underline": False,
                               "foregroundColor": {"red": 0, "green": 0, "blue": 0}},
                "horizontalAlignment": "LEFT",
                "verticalAlignment": "MIDDLE",
            }},
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)",
        }},
        {"repeatCell": {
            "range": header_range,
            "cell": {"userEnteredFormat": {
                "textFormat": {"bold": True, "foregroundColor": HEADER_TEXT},
                "backgroundColor": HEADER_GREEN,
                "horizontalAlignment": "CENTER",
                "verticalAlignment": "MIDDLE",
            }},
            "fields": "userEnteredFormat(textFormat,backgroundColor,horizontalAlignment,verticalAlignment)",
        }},
        {"repeatCell": {
            "range": data_range,
            "cell": {"userEnteredFormat": {
                "textFormat": {"bold": False, "foregroundColor": {"red": 0, "green": 0, "blue": 0}},
                "backgroundColor": WHITE,
                "verticalAlignment": "MIDDLE",
                "wrapStrategy": "WRAP",
            }},
            "fields": "userEnteredFormat(textFormat,backgroundColor,verticalAlignment,wrapStrategy)",
        }},
        {"updateBorders": {
            "range": base_range,
            "top": thin, "bottom": thin, "left": thin, "right": thin,
            "innerHorizontal": thin, "innerVertical": thin,
        }},
        {"repeatCell": {
            "range": {"sheetId": sheet_tab_id, "startRowIndex": 1, "endRowIndex": max_data_row,
                      "startColumnIndex": 1, "endColumnIndex": 2},
            "cell": {"userEnteredFormat": {
                "numberFormat": {"type": "DATE", "pattern": DATE_PATTERN},
                "horizontalAlignment": "CENTER",
            }},
            "fields": "userEnteredFormat(numberFormat,horizontalAlignment)",
        }},
        # Style link columns E (Doc) and H (Web) as blue + underlined
        {"repeatCell": {
            "range": {"sheetId": sheet_tab_id, "startRowIndex": 1, "endRowIndex": max_data_row,
                      "startColumnIndex": 4, "endColumnIndex": 5},
            "cell": {"userEnteredFormat": {
                "textFormat": {"foregroundColor": {"red": 0.07, "green": 0.33, "blue": 0.80}, "underline": True},
            }},
            "fields": "userEnteredFormat.textFormat",
        }},
        {"repeatCell": {
            "range": {"sheetId": sheet_tab_id, "startRowIndex": 1, "endRowIndex": max_data_row,
                      "startColumnIndex": 7, "endColumnIndex": 8},
            "cell": {"userEnteredFormat": {
                "textFormat": {"foregroundColor": {"red": 0.07, "green": 0.33, "blue": 0.80}, "underline": True},
            }},
            "fields": "userEnteredFormat.textFormat",
        }},
        _validation_request(sheet_tab_id, 5, CONTENT_STATUSES, max_data_row),  # F: Content Status
        _validation_request(sheet_tab_id, 6, WEB_STATUSES, max_data_row),      # G: Web Status
        {"updateSheetProperties": {
            "properties": {"sheetId": sheet_tab_id, "gridProperties": {"frozenRowCount": 1}},
            "fields": "gridProperties.frozenRowCount",
        }},
    ]


def reformat_existing_sheet() -> None:
    """Convert existing rows (date → DD/MM/YYYY, raw URLs → HYPERLINK), apply formatting + dropdowns."""
    sheet_id = _ensure_sheet_id()
    g = _get_clients()
    spreadsheet = g.sheets.spreadsheets().get(spreadsheetId=sheet_id).execute()
    sheet_tab_id = None
    for s in spreadsheet["sheets"]:
        if s["properties"]["title"] == TAB:
            sheet_tab_id = s["properties"]["sheetId"]
            break
    if sheet_tab_id is None:
        raise RuntimeError(f"Tab {TAB!r} not found in tracker spreadsheet")

    r = g.sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id, range=f"{TAB}!E2:H", valueRenderOption="FORMULA",
    ).execute()
    rows = r.get("values", [])
    updates: list[dict] = []
    for idx, row in enumerate(rows, start=2):
        padded = row + [""] * (4 - len(row))
        doc_raw, web_raw = padded[0], padded[3]
        new_doc = _strip_hyperlink(doc_raw)
        new_web = _strip_hyperlink(web_raw)
        if new_doc != doc_raw:
            updates.append({"range": f"{TAB}!E{idx}", "values": [[new_doc]]})
        if new_web != web_raw:
            updates.append({"range": f"{TAB}!H{idx}", "values": [[new_web]]})
    if updates:
        g.sheets.spreadsheets().values().batchUpdate(
            spreadsheetId=sheet_id,
            body={"valueInputOption": "USER_ENTERED", "data": updates},
        ).execute()
        log.info("Stripped HYPERLINK formula in %d cells, replaced with plain URLs", len(updates))

    _delete_all_conditional_format_rules(g, sheet_id, sheet_tab_id)

    g.sheets.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={"requests": _format_requests(sheet_tab_id)},
    ).execute()
    log.info("Reformatted: green header + white rows + light borders + 3-value dropdowns + status colors")


def _ensure_sheet_id() -> str:
    settings = load_settings()
    sheet_id = settings.get("tracker_sheet_id", "").strip()
    if not sheet_id:
        raise RuntimeError("tracker_sheet_id not set. Run: python -m scripts.seed_categories")
    return sheet_id


def create_tracker_sheet(g: GoogleClients) -> str:
    """Create the tracker spreadsheet inside Drive folder, write headers, share with user. Returns sheet_id."""
    settings = load_settings()
    folder_id = settings["drive_folder_id"]
    if not folder_id or folder_id.startswith("PASTE_"):
        raise RuntimeError("drive_folder_id not set in settings.json")

    metadata = {
        "name": "Hoa Xuan Blog Tracker",
        "mimeType": "application/vnd.google-apps.spreadsheet",
        "parents": [folder_id],
    }
    sf = g.drive.files().create(body=metadata, fields="id").execute()
    sheet_id = sf["id"]

    spreadsheet = g.sheets.spreadsheets().get(spreadsheetId=sheet_id).execute()
    default_sheet_id = spreadsheet["sheets"][0]["properties"]["sheetId"]
    g.sheets.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={"requests": [{"updateSheetProperties": {
            "properties": {"sheetId": default_sheet_id, "title": TAB},
            "fields": "title",
        }}]},
    ).execute()

    g.sheets.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=f"{TAB}!A1:I1",
        valueInputOption="RAW",
        body={"values": [HEADER]},
    ).execute()

    g.sheets.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={"requests": _format_requests(default_sheet_id)},
    ).execute()

    share_email = settings.get("share_sheet_with_email")
    if share_email:
        try:
            g.drive.permissions().create(
                fileId=sheet_id,
                body={"type": "user", "role": "writer", "emailAddress": share_email},
                sendNotificationEmail=True,
                fields="id",
            ).execute()
            log.info("Shared sheet with %s", share_email)
        except Exception as e:  # noqa: BLE001
            log.warning("Share sheet failed: %s", e)

    settings["tracker_sheet_id"] = sheet_id
    settings["tracker_sheet_url"] = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
    save_settings(settings)
    log.info("Tracker sheet created: %s", settings["tracker_sheet_url"])
    return sheet_id


def _get_clients() -> GoogleClients:
    return get_clients()


def next_stt(g: GoogleClients, sheet_id: str) -> int:
    r = g.sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id, range=f"{TAB}!A2:A",
    ).execute()
    rows = r.get("values", [])
    return len(rows) + 1


def append_row(keyword: str, title: str, doc_link: str,
               content_status: str, web_status: str, web_link: str,
               notes: str = "") -> int:
    sheet_id = _ensure_sheet_id()
    g = _get_clients()
    stt = next_stt(g, sheet_id)
    today = datetime.now().strftime("%Y-%m-%d")
    row = [stt, today, keyword, title, doc_link, content_status, web_status, web_link, notes]

    retry(
        lambda: g.sheets.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=f"{TAB}!A:I",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": [row]},
        ).execute(),
        label="sheets.append",
    )
    log.info("Tracker row #%d appended", stt)
    return stt


def update_row(stt: int, **fields) -> None:
    """Update specific cells of an existing row identified by STT."""
    sheet_id = _ensure_sheet_id()
    g = _get_clients()

    r = g.sheets.spreadsheets().values().get(spreadsheetId=sheet_id, range=f"{TAB}!A2:A").execute()
    rows = r.get("values", [])
    target_row = None
    for idx, row in enumerate(rows, start=2):
        if row and str(row[0]) == str(stt):
            target_row = idx
            break
    if not target_row:
        log.warning("STT %s not found in tracker", stt)
        return

    col_map = {"date": "B", "keyword": "C", "title": "D", "doc_link": "E",
               "content_status": "F", "web_status": "G", "web_link": "H", "notes": "I"}
    data = []
    for key, val in fields.items():
        if key in col_map:
            data.append({"range": f"{TAB}!{col_map[key]}{target_row}", "values": [[val]]})

    if data:
        g.sheets.spreadsheets().values().batchUpdate(
            spreadsheetId=sheet_id,
            body={"valueInputOption": "USER_ENTERED", "data": data},
        ).execute()
        log.info("Tracker row #%d updated: %s", stt, list(fields.keys()))


def read_all_rows() -> list[dict]:
    """Return every data row in the tracker, regardless of status."""
    sheet_id = _ensure_sheet_id()
    g = _get_clients()
    r = g.sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id, range=f"{TAB}!A2:I",
    ).execute()
    rows = r.get("values", [])
    out: list[dict] = []
    for row in rows:
        padded = row + [""] * (N_COLS - len(row))
        try:
            stt = int(padded[0])
        except (ValueError, TypeError):
            continue
        out.append({
            "stt": stt,
            "date": padded[1],
            "keyword": padded[2],
            "title": padded[3],
            "doc_link": padded[4],
            "content_status": padded[5],
            "web_status": padded[6],
            "web_link": padded[7],
            "notes": padded[8],
        })
    return out


def read_queue() -> list[dict]:
    """Return rows with Content Status == 'Pending', sorted by STT."""
    sheet_id = _ensure_sheet_id()
    g = _get_clients()
    r = g.sheets.spreadsheets().values().get(spreadsheetId=sheet_id, range=f"{TAB}!A2:I").execute()
    rows = r.get("values", [])
    queue = []
    for row in rows:
        padded = row + [""] * (9 - len(row))
        if padded[5].strip().lower() == "pending":
            queue.append({
                "stt": int(padded[0]) if padded[0].isdigit() else None,
                "keyword": padded[2],
                "title": padded[3],
                "notes": padded[8],
            })
    return queue
