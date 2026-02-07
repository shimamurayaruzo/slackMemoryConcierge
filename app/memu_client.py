import json
from typing import Any, Dict, List, Optional

import requests

from app.config import settings


def memorize_conversation(conversation: List[dict], user_id: str, agent_id: str) -> Optional[dict]:
    if not settings.memu_api_key:
        return None
    response = requests.post(
        "https://api.memu.so/api/v3/memory/memorize",
        headers={
            "Authorization": f"Bearer {settings.memu_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "conversation": conversation,
            "user_id": user_id,
            "agent_id": agent_id,
        },
        timeout=15,
    )
    if response.status_code >= 400:
        return None
    return response.json()


def save_memory(payload: Dict[str, Any], user_id: str, agent_id: str) -> Optional[dict]:
    content = json.dumps(payload, ensure_ascii=False)
    conversation = [
        {"role": "user", "content": content},
        {"role": "assistant", "content": "記憶を保存しました。"},
        {"role": "assistant", "content": f"category={payload.get('category', 'general')}"},
    ]
    return memorize_conversation(conversation, user_id, agent_id)


def search_memory(query: str, user_id: str, agent_id: str) -> List[dict]:
    if not settings.memu_api_key:
        return []
    response = requests.post(
        "https://api.memu.so/api/v3/memory/retrieve",
        headers={
            "Authorization": f"Bearer {settings.memu_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "user_id": user_id,
            "agent_id": agent_id,
            "query": query,
        },
        timeout=15,
    )
    if response.status_code >= 400:
        return []
    data = response.json()
    return data.get("items", [])
