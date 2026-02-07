from typing import List


def _extract_paragraph_text(paragraph: dict) -> str:
    elements: List[str] = []
    for element in paragraph.get("elements", []):
        text_run = element.get("textRun")
        if text_run and "content" in text_run:
            elements.append(text_run["content"])
    return "".join(elements)


def extract_document_text(docs_service: object, document_id: str) -> str:
    document = docs_service.documents().get(documentId=document_id).execute()
    body = document.get("body", {})
    content = body.get("content", [])
    lines: List[str] = []
    for item in content:
        paragraph = item.get("paragraph")
        if paragraph:
            text = _extract_paragraph_text(paragraph).strip()
            if text:
                lines.append(text)
    return "\n".join(lines)
