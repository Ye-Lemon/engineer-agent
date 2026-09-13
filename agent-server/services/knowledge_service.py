import re
import time

from schemas.content import QueryResponse, ReportResponse
from services.file_service import text_files


def _terms(value: str) -> set[str]:
    return {term.lower() for term in re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]{2,}", value)}


def query_documents(user_id: int, question: str, top_k: int) -> QueryResponse:
    started = time.perf_counter()
    question_terms = _terms(question)
    matches = []

    for path in text_files(user_id):
        content = path.read_text(encoding="utf-8", errors="ignore")
        score = len(question_terms & _terms(content))
        if score:
            excerpt = content[:600].strip()
            matches.append((score, path.name, excerpt))

    matches.sort(key=lambda item: item[0], reverse=True)
    sources = [
        {"source": filename, "content": excerpt, "similarity": min(score / max(len(question_terms), 1), 1.0)}
        for score, filename, excerpt in matches[:top_k]
    ]
    if sources:
        answer = "Retrieved relevant local document excerpts. Review the cited sources for the complete context."
    else:
        answer = "No matching text documents were found. Upload a .txt engineering document or connect an AI retrieval service."

    return QueryResponse(
        answer=answer,
        sources=sources,
        processing_time_ms=round((time.perf_counter() - started) * 1000),
    )


def generate_report(report_type: str, parameters: dict) -> ReportResponse:
    title = report_type.replace("_", " ").title()
    sections = "\n".join(f"- **{key.replace('_', ' ').title()}**: {value}" for key, value in parameters.items())
    content = f"# {title}\n\n## Input Parameters\n{sections or '- No parameters provided'}\n\n## Engineering Notes\nThis report is a parameter-based draft. Verify calculations, standards, and site-specific assumptions before use."
    return ReportResponse(content=content, references=[], generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
