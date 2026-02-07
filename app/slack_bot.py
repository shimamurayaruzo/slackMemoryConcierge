import os
import re
from typing import Dict, List

from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler

from app.config import settings
from app.docs_reader import extract_document_text
from app.drive_loader import DOCS_MIME, create_services, list_drive_files
from app.slack_handlers import handle_slack_question

slack_env_ready = bool(settings.slack_bot_token and settings.slack_signing_secret)
slack_app = App(token=settings.slack_bot_token, signing_secret=settings.slack_signing_secret) if slack_env_ready else None
slack_handler = SlackRequestHandler(slack_app) if slack_app else None

_services: Dict[str, object] | None = None


def _get_services() -> Dict[str, object] | None:
    global _services
    if _services is not None:
        return _services
    if not settings.google_credentials_path:
        return None
    if not os.path.exists(settings.google_credentials_path):
        return None
    _services = create_services()
    return _services


def _sanitize_question(text: str) -> str:
    return re.sub(r"<@[^>]+>", "", text).strip()


def _build_documents() -> List[Dict[str, str]]:
    services = _get_services()
    drive_service = services["drive"] if services else None
    docs_service = services["docs"] if services else None
    if not drive_service or not settings.google_drive_folder_id:
        return []
    files = list_drive_files(drive_service, settings.google_drive_folder_id)
    documents: List[Dict[str, str]] = []
    for item in files:
        mime_type = item.get("mimeType")
        text = extract_document_text(docs_service, item["id"]) if mime_type == DOCS_MIME and docs_service else ""
        documents.append(
            {
                "id": item.get("id", ""),
                "title": item.get("name", ""),
                "url": item.get("webViewLink", ""),
                "mimeType": mime_type,
                "text": text,
            }
        )
    return documents


@slack_app.event("app_mention") if slack_app else lambda *args, **kwargs: None
def handle_app_mention(event, say):
    if not settings.google_drive_folder_id or not drive_service:
        say("Google Drive設定が未完了です。GOOGLE_DRIVE_FOLDER_ID と GOOGLE_API_CREDENTIALS を設定してください。")
        return
    question = _sanitize_question(event.get("text", ""))
    documents = _build_documents()
    answer = handle_slack_question(question, documents, event.get("user", "slack_user"))
    say(answer)
