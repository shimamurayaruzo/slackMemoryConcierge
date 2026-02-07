import re
from typing import Dict, List


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9一-龥ぁ-んァ-ヶー]+", text.lower())


def _score_document(question: str, text: str) -> int:
    tokens = _tokenize(question)
    if not tokens:
        return 0
    normalized = text.lower()
    return sum(normalized.count(token) for token in tokens)


def build_answer(question: str, documents: List[Dict[str, str]]) -> str:
    if not documents:
        return "該当資料が見つかりませんでした。キーワードを変えて質問してください。"
    ranked = sorted(
        documents,
        key=lambda doc: _score_document(question, doc.get("text", "")),
        reverse=True,
    )
    top = ranked[0]
    excerpt = top.get("text", "").replace("\n", " ").strip()
    excerpt = excerpt[:200] + ("..." if len(excerpt) > 200 else "")
    title = top.get("title", "参照資料")
    url = top.get("url", "")
    conclusion = f"結論: {title} に関連情報があります。"
    evidence = f"根拠: {title} {url}".strip()
    quote = f"抜粋: {excerpt}" if excerpt else "抜粋: 取得できませんでした。"
    return "\n".join([conclusion, evidence, quote])
