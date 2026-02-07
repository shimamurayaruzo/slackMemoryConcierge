import re
from typing import Dict, List, Optional


SECTION_HEADERS = ["決定事項", "ToDo", "宿題", "Action Items"]


def _is_header(line: str) -> Optional[str]:
    for header in SECTION_HEADERS:
        if header.lower() in line.lower():
            return header
    return None


def _normalize_item(line: str) -> str:
    return re.sub(r"^[\-\*\・\s]+|^\d+[\.\)]\s*", "", line).strip()


def _extract_owner(text: str) -> Optional[str]:
    match = re.search(r"(担当|owner)[:：]\s*([^\s]+)", text, re.IGNORECASE)
    return match.group(2) if match else None


def _extract_due(text: str) -> Optional[str]:
    match = re.search(r"(期限|due)[:：]\s*([0-9/\-]+)", text, re.IGNORECASE)
    return match.group(2) if match else None


def extract_decisions(text: str) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []
    current_header: Optional[str] = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        header = _is_header(line)
        if header:
            current_header = header
            continue
        if not current_header:
            continue
        if not re.match(r"^[\-\*\・\d]", line):
            continue
        todo = _normalize_item(line)
        owner = _extract_owner(todo)
        due = _extract_due(todo)
        items.append(
            {
                "section": current_header,
                "todo": todo,
                "owner": owner or "",
                "due": due or "",
            }
        )
    return items
