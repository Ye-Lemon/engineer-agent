from __future__ import annotations

import time
from collections import defaultdict
from typing import Any


class MemoryStore:
    def __init__(self) -> None:
        self.documents: dict[str, dict[str, Any]] = {}
        self.chunks: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.messages: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.sessions: dict[str, dict[str, Any]] = {}
        self.cache: dict[str, tuple[float, Any]] = {}

    async def save_document(self, document: dict[str, Any]) -> None:
        self.documents[document["id"]] = document

    async def save_chunks(self, document_id: str, chunks: list[dict[str, Any]]) -> None:
        self.chunks[document_id] = chunks

    async def add_message(self, session_id: str, message: dict[str, Any]) -> None:
        self.messages[session_id].append(message)

    async def history(self, session_id: str) -> list[dict[str, Any]]:
        return list(self.messages.get(session_id, []))[-20:]

    async def clear_history(self, session_id: str) -> None:
        self.messages.pop(session_id, None)

    async def set_cache(self, key: str, value: Any, ttl: int = 3600) -> None:
        self.cache[key] = (time.time() + ttl, value)

    async def get_cache(self, key: str) -> Any:
        item = self.cache.get(key)
        if not item:
            return None
        if item[0] < time.time():
            self.cache.pop(key, None)
            return None
        return item[1]

    async def ping(self) -> bool:
        return True


memory_store = MemoryStore()
