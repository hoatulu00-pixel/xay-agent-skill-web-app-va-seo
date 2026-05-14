"""Google API auth — supports both Service Account (preferred) and OAuth Desktop fallback.

Auto-detects credential type by inspecting the JSON file:
  - Has top-level key "installed" or "web"  -> OAuth Desktop client (InstalledAppFlow)
  - Has top-level key "type": "service_account" -> Service Account

OAuth flow: first run pops a browser, user clicks Allow, token cached at
.cache/google_token.json. Subsequent runs refresh silently.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from googleapiclient.discovery import build

from .utils import CACHE_DIR, load_settings, log

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

TOKEN_PATH = CACHE_DIR / "google_token.json"


@dataclass
class GoogleClients:
    docs: any  # type: ignore[valid-type]
    sheets: any  # type: ignore[valid-type]
    drive: any  # type: ignore[valid-type]


def _resolve_creds_path(settings: dict) -> str:
    path = (
        settings.get("oauth_client_secret_path")
        or settings.get("service_account_path")
        or settings.get("google_credentials_path")
    )
    if not path:
        raise KeyError(
            "Missing credentials path in settings.json. Set 'oauth_client_secret_path' "
            "(for OAuth Desktop) or 'service_account_path' (for Service Account)."
        )
    return path


def _load_oauth_creds(client_secrets_path: str):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if TOKEN_PATH.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        except Exception as e:  # noqa: BLE001
            log.warning("Failed to load cached token (%s); re-authorizing.", e)
            creds = None

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
            TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
            return creds
        except Exception as e:  # noqa: BLE001
            log.warning("Token refresh failed (%s); re-authorizing.", e)

    log.info("Starting OAuth Desktop consent flow — a browser window will open.")
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent", open_browser=True)
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    log.info("OAuth token saved to %s", TOKEN_PATH)
    return creds


def _load_sa_creds(sa_path: str):
    from google.oauth2 import service_account

    return service_account.Credentials.from_service_account_file(sa_path, scopes=SCOPES)


def _detect_and_load(creds_path: str):
    p = Path(creds_path)
    if not p.exists():
        raise FileNotFoundError(f"Credentials file not found: {creds_path}")
    raw = json.loads(p.read_text(encoding="utf-8"))
    if "installed" in raw or "web" in raw:
        log.info("Detected OAuth Desktop client at %s", creds_path)
        return _load_oauth_creds(creds_path)
    if raw.get("type") == "service_account":
        log.info("Detected Service Account at %s", creds_path)
        return _load_sa_creds(creds_path)
    raise ValueError(
        f"Unrecognized credentials JSON at {creds_path}. "
        "Expected OAuth Desktop client (with 'installed') or Service Account (type=service_account)."
    )


def get_clients() -> GoogleClients:
    settings = load_settings()
    creds_path = _resolve_creds_path(settings)
    creds = _detect_and_load(creds_path)
    return GoogleClients(
        docs=build("docs", "v1", credentials=creds, cache_discovery=False),
        sheets=build("sheets", "v4", credentials=creds, cache_discovery=False),
        drive=build("drive", "v3", credentials=creds, cache_discovery=False),
    )


if __name__ == "__main__":
    g = get_clients()
    settings = load_settings()
    folder_id = settings.get("drive_folder_id")
    if folder_id and folder_id != "PASTE_FOLDER_ID_FROM_DRIVE_URL":
        result = g.drive.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            pageSize=5,
            fields="files(id, name, mimeType)",
        ).execute()
        files = result.get("files", [])
        print(f"OK. Folder accessible. Files in folder: {len(files)}")
        for f in files:
            print(f"  - {f['name']} ({f['mimeType']})")
    else:
        about = g.drive.about().get(fields="user(emailAddress,displayName)").execute()
        u = about.get("user", {})
        print(f"OK. Authenticated as {u.get('emailAddress')} ({u.get('displayName')})")
        print("Note: drive_folder_id not set yet — set it in settings.json next.")
