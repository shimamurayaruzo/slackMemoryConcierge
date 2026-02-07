import json
from typing import Dict, Optional

from app.config import settings
from app.memu_client import save_memory, search_memory


_question_counts: Dict[str, int] = {}


def normalize_question(text: str) -> str:
    return " ".join(text.lower().split())


def get_faq_answer(question: str) -> Optional[Dict[str, str]]:
    items = search_memory(f"category:faq question:{question}", settings.memu_team_id, settings.memu_agent_id)
    for item in items:
        content = item.get("content", "")
        try:
            payload = json.loads(content)
        except json.JSONDecodeError:
            continue
        if payload.get("category") == "faq" and payload.get("question"):
            return payload
    return None


def record_question(question: str, answer: str, source_doc: str) -> bool:
    key = normalize_question(question)
    _question_counts[key] = _question_counts.get(key, 0) + 1
    if _question_counts[key] < 2:
        return False
    payload = {
        "category": "faq",
        "question": question,
        "answer": answer,
        "source_doc": source_doc,
    }
    save_memory(payload, settings.memu_team_id, settings.memu_agent_id)
    return True
