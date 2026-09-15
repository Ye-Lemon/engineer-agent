from __future__ import annotations
import os
from typing import Any
import httpx
from dotenv import load_dotenv
load_dotenv()



def _base_url() -> str:
    value = os.getenv("DEEPSEEK_BASE_URL") or os.getenv("OPENAI_BASE_URL") or "https://api.deepseek.com"
    value = value.rstrip("/")
    # OpenAI-compatible providers expose the SDK endpoint under /v1.
    if not value.endswith("/v1") and not value.endswith("/chat/completions"):
        value = f"{value}/v1"
    return value


def _model() -> str:
    # Keep compatibility with the existing typo in .env.
    return os.getenv("DEEPSEEK_MODEL") or os.getenv("MODEL_NAME") or os.getenv("MODLE_NAME") or "deepseek-v3.2"

def available_models() -> list[str]:
    configured = os.getenv("LLM_MODELS")
    values = [item.strip() for item in configured.split(",") if item.strip()] if configured else [_model()]
    return list(dict.fromkeys(values))


async def generate_answer(question: str, sources: list[dict[str, Any]], history: list[dict[str, Any]] | None = None, model: str | None = None) -> str | None:
    result = await generate_answer_details(question, sources, history, model)
    return result["answer"] if result else None


async def generate_answer_details(question: str, sources: list[dict[str, Any]], history: list[dict[str, Any]] | None = None, model: str | None = None) -> dict[str, str] | None:
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    context = "\n\n".join(
        f"[Source: {item.get('source', 'unknown')}]\n{item.get('content', '')[:2000]}"
        for item in sources
    ) or "No indexed document context is available."
    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": (
                "You are an engineering knowledge assistant. Answer in the user's language. "
                "Use the supplied context, do not invent facts, and say when the context is insufficient. "
                "Cite sources by their source name when applicable.\n\nContext:\n" + context
            ),
        }
    ]
    if history:
        messages.extend(
            {"role": item["role"], "content": item["content"]}
            for item in history[-6:]
            if item.get("role") in {"user", "assistant"} and item.get("content")
        )
    messages.append({"role": "user", "content": question})

    url = f"{_base_url()}/chat/completions"
    payload = {"model": model or _model(), "messages": messages, "temperature": 0.2, "stream": False}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, connect=5.0)) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        message = data.get("choices", [{}])[0].get("message", {})
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            return None
        reasoning = message.get("reasoning_content") or message.get("reasoning") or ""
        return {"answer": content.strip(), "reasoning": reasoning.strip() if isinstance(reasoning, str) else ""}
    except (httpx.HTTPError, ValueError, KeyError, IndexError):
        return None


def llm_configured() -> bool:
    return bool(os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY"))
