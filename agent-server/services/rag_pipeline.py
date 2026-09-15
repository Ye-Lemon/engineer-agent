from __future__ import annotations

import re
from typing import Any

from storage.memory import memory_store


def should_retrieve(question: str) -> bool:
    """Avoid needless knowledge-base retrieval for greetings and small talk."""
    normalized = re.sub(r"[\s，。！？!?,.]+", "", question).lower()
    small_talk = {
        "你好", "您好", "嗨", "hello", "hi", "早上好", "下午好", "晚上好",
        "你是谁", "你能做什么", "谢谢", "再见",
    }
    return normalized not in small_talk


def split_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def _terms(value: str) -> set[str]:
    return {x.lower() for x in re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]{2,}", value)}


def lexical_search(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    wanted = _terms(query)
    return rank_chunks(query, [chunk for chunks in memory_store.chunks.values() for chunk in chunks], top_k)


def rank_chunks(query: str, chunks: list[dict[str, Any]], top_k: int = 5) -> list[dict[str, Any]]:
    wanted = _terms(query)
    found = []
    for chunk in chunks:
        terms = _terms(chunk["content"])
        score = len(wanted & terms) / max(len(wanted), 1)
        if score > 0:
            found.append({**chunk, "similarity": round(score, 4)})
    return sorted(found, key=lambda x: x["similarity"], reverse=True)[:top_k]


async def index_document(document_id: str, filename: str, content: str, metadata: dict[str, Any] | None = None) -> int:
    chunks = [{"id": f"{document_id}:{i}", "document_id": document_id, "source": filename, "content": part, "metadata": metadata or {}}
              for i, part in enumerate(split_text(content))]
    await memory_store.save_chunks(document_id, chunks)
    try:
        from storage.adapters import vector_store
        await vector_store.upsert(chunks)
    except Exception:
        pass
    return len(chunks)
