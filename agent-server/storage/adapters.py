from __future__ import annotations
import os
from typing import Any
from urllib.parse import quote_plus
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from config.db_session import async_engine
from config.redis_session import ping_redis,redis_client
from .memory import memory_store
load_dotenv()


class MySQLMetadata:
    """Relational metadata facade. SQLAlchemy integration can replace methods."""

    async def ping(self) -> bool:
        try:
            async with async_engine.connect() as conn:
                await conn.exec_driver_sql("SELECT 1")
            return True
        except Exception:
            return False


class RedisCache:
    async def ping(self) -> bool:
        try:
            return await ping_redis()
        except Exception:
            return await memory_store.ping()

    async def get(self, key: str) -> Any:
        try:
            value = await redis_client.get(key)
            return value if value is not None else await memory_store.get_cache(key)
        except Exception:
            return await memory_store.get_cache(key)

    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        try:
            await redis_client.setex(key, ttl, value)
        except Exception:
            await memory_store.set_cache(key, value, ttl)


class MongoDocumentStore:
    def __init__(self) -> None:
        self._client = None

    def _url(self) -> str:
        configured = os.getenv("MONGODB_URL")
        if configured:
            return configured
        username = os.getenv("MONGODB_USERNAME")
        password = os.getenv("MONGODB_PASSWORD")
        auth_source = os.getenv("MONGODB_AUTH_SOURCE", "admin")
        if username and password:
            return f"mongodb://{quote_plus(username)}:{quote_plus(password)}@localhost:27017/?authSource={auth_source}"
        if username:
            return f"mongodb://{quote_plus(username)}@localhost:27017/?authSource={auth_source}"
        return "mongodb://localhost:27017"

    async def db(self):
        if self._client is None:
            self._client = AsyncIOMotorClient(self._url(), serverSelectionTimeoutMS=800)
        return self._client[os.getenv("MONGODB_DB", "engineering_agent")]

    async def ping(self) -> bool:
        try:
            db = await self._db()
            await db.command("ping")
            return True
        except Exception:
            return False

    async def save_document(self, document: dict[str, Any]) -> None:
        try:
            db = await self._db()
            await db.documents.replace_one({"id": document["id"]}, document, upsert=True)
        except Exception:
            await memory_store.save_document(document)

    async def save_chunks(self, document_id: str, chunks: list[dict[str, Any]]) -> None:
        try:
            db = await self._db()
            await db.chunks.delete_many({"document_id": document_id})
            if chunks:
                await db.chunks.insert_many(chunks)
        except Exception:
            await memory_store.save_chunks(document_id, chunks)

    async def add_message(self, session_id: str, message: dict[str, Any]) -> None:
        try:
            db = await self._db()
            await db.messages.insert_one({"session_id": session_id, **message})
        except Exception:
            await memory_store.add_message(session_id, message)

    async def history(self, session_id: str) -> list[dict[str, Any]]:
        try:
            db = await self._db()
            cursor = db.messages.find({"session_id": session_id}, {"_id": 0, "session_id": 0}).sort("created_at", 1)
            return await cursor.to_list(length=20)
        except Exception:
            return await memory_store.history(session_id)

    async def clear_history(self, session_id: str) -> None:
        try:
            db = await self._db()
            await db.messages.delete_many({"session_id": session_id})
        except Exception:
            await memory_store.clear_history(session_id)

    async def search_chunks(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Fallback lexical search over persisted Mongo chunks."""
        try:
            db = await self._db()
            chunks = await db.chunks.find({}, {"_id": 0}).to_list(length=10000)
            from services.rag_pipeline import rank_chunks
            return rank_chunks(query, chunks, top_k)
        except Exception:
            return []


class VectorStore:
    def __init__(self) -> None:
        self._client = None
        self._collection = None

    @staticmethod
    def _embedding(text: str, dimensions: int = 384) -> list[float]:
        """Small deterministic embedding fallback with no model download."""
        import hashlib
        vector = [0.0] * dimensions
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % dimensions
            vector[index] += 1.0
        norm = sum(x * x for x in vector) ** 0.5 or 1.0
        return [x / norm for x in vector]

    def _get_collection(self):
        if self._collection is not None:
            return self._collection
        import chromadb
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
        self._client = chromadb.PersistentClient(path=persist_dir)
        self._collection = self._client.get_or_create_collection(
            name=os.getenv("CHROMA_COLLECTION", "engineering_documents"),
            metadata={"hnsw:space": "cosine"},
        )
        return self._collection

    async def upsert(self, chunks: list[dict[str, Any]]) -> None:
        try:
            collection = self._get_collection()
            if not chunks:
                return
            collection.upsert(
                ids=[item["id"] for item in chunks],
                documents=[item["content"] for item in chunks],
                metadatas=[{"document_id": item["document_id"], "source": item["source"]} for item in chunks],
                embeddings=[self._embedding(item["content"]) for item in chunks],
            )
        except Exception:
            # Chroma is optional for local development.
            await memory_store.save_chunks(chunks[0]["document_id"], chunks)

    async def ping(self) -> bool:
        try:
            self._get_collection().count()
            return True
        except Exception:
            return False

    async def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        try:
            collection = self._get_collection()
            result = collection.query(query_embeddings=[self._embedding(query)], n_results=top_k, include=["documents", "metadatas", "distances"])
            documents = result.get("documents", [[]])[0]
            metadatas = result.get("metadatas", [[]])[0]
            distances = result.get("distances", [[]])[0]
            minimum_similarity = float(os.getenv("CHROMA_MIN_SIMILARITY", "0.15"))
            matches = []
            for i, (doc, meta) in enumerate(zip(documents, metadatas)):
                similarity = max(0.0, 1.0 - float(distances[i]))
                if similarity >= minimum_similarity:
                    matches.append({"id": f"chroma:{i}", "source": meta.get("source", "unknown"), "content": doc,
                                    "metadata": meta, "similarity": round(similarity, 4)})
            return matches
        except Exception:
            from services.rag_pipeline import lexical_search
            local = lexical_search(query, top_k)
            return local or await mongo_store.search_chunks(query, top_k)


mysql_store = MySQLMetadata()
redis_store = RedisCache()
mongo_store = MongoDocumentStore()
vector_store = VectorStore()
