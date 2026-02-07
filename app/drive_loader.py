from typing import Dict, List, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build

from app.config import settings

DOCS_MIME = "application/vnd.google-apps.document"


def create_services() -> Optional[Dict[str, object]]:
    if not settings.google_credentials_path:
        return None
    scopes = [
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/documents.readonly",
    ]
    credentials = service_account.Credentials.from_service_account_file(
        settings.google_credentials_path,
        scopes=scopes,
    )
    return {
        "drive": build("drive", "v3", credentials=credentials),
        "docs": build("docs", "v1", credentials=credentials),
    }


def list_drive_files(drive_service: object, folder_id: str) -> List[Dict[str, str]]:
    query = (
        f"'{folder_id}' in parents and trashed=false and "
        f"(mimeType='{DOCS_MIME}')"
    )
    response = (
        drive_service.files()
        .list(q=query, fields="files(id,name,mimeType,webViewLink)", pageSize=200)
        .execute()
    )
    return response.get("files", [])
