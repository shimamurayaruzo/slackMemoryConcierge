import json
from typing import Dict, List

from app.config import settings
from app.decision_extractor import extract_decisions
from app.faq_manager import get_faq_answer, record_question
from app.memu_client import memorize_conversation, save_memory, search_memory
from app.rag_answer import build_answer


DECISION_QUERY_KEYWORDS = ["宿題", "決定事項", "ToDo", "Action Items", "未完了"]


def _is_decision_query(question: str) -> bool:
    return any(keyword.lower() in question.lower() for keyword in DECISION_QUERY_KEYWORDS)


def _format_decisions(items: List[Dict[str, str]]) -> str:
    if not items:
        return "前回の宿題を覚えています。\n未完了ToDoは見つかりませんでした。"
    lines = ["前回の宿題を覚えています。"]
    for item in items:
        owner = f"（担当: {item.get('owner')}）" if item.get("owner") else ""
        due = f"（期限: {item.get('due')}）" if item.get("due") else ""
        source = item.get("source_doc", "")
        line = f"- {item.get('todo')}{owner}{due}"
        if source:
            line = f"{line} {source}"
        lines.append(line)
    return "\n".join(lines)


def _parse_decision_item(content: str) -> Dict[str, str]:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        return {}
    if payload.get("category") != "decisions":
        return {}
    return payload


def _extract_and_store_decisions(documents: List[Dict[str, str]]) -> None:
    for doc in documents:
        text = doc.get("text", "")
        if not text:
            continue
        items = extract_decisions(text)
        for item in items:
            payload = {
                "category": "decisions",
                "meeting_title": doc.get("title", ""),
                "todo": item.get("todo", ""),
                "owner": item.get("owner", ""),
                "due": item.get("due", ""),
                "source_doc": doc.get("url", ""),
            }
            save_memory(payload, settings.memu_team_id, settings.memu_agent_id)


def handle_slack_question(question: str, documents: List[Dict[str, str]], user_id: str) -> str:
    _extract_and_store_decisions(documents)
    if _is_decision_query(question):
        items = search_memory("category:decisions todo 未完了 宿題", settings.memu_team_id, settings.memu_agent_id)
        parsed = [item for item in (_parse_decision_item(it.get("content", "")) for it in items) if item]
        answer = _format_decisions(parsed)
        memorize_conversation(
            [
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer},
                {"role": "assistant", "content": "決定事項を参照しました。"},
            ],
            user_id,
            settings.memu_agent_id,
        )
        return answer
    faq_payload = get_faq_answer(question)
    if faq_payload:
        answer = "これはFAQとして記憶しています。\n" + faq_payload.get("answer", "")
        memorize_conversation(
            [
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer},
                {"role": "assistant", "content": "FAQ記憶を参照しました。"},
            ],
            user_id,
            settings.memu_agent_id,
        )
        return answer
    answer = build_answer(question, documents)
    source_doc = ""
    if documents:
        source_doc = documents[0].get("url", "")
    record_question(question, answer, source_doc)
    memorize_conversation(
        [
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
            {"role": "assistant", "content": "参照資料を付与した回答を返しました。"},
        ],
        user_id,
        settings.memu_agent_id,
    )
    return answer
