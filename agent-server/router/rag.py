from __future__ import annotations

import time
import uuid
import json
import os

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse

from schemas.rag import ChatRequest, KnowledgeBaseRequest
from services.file_service import MAX_UPLOAD_SIZE, safe_filename
from services.rag_pipeline import index_document, should_retrieve
from services.document_parser import DocumentParseError, parse_document
from services.llm_service import available_models, generate_answer_details, llm_configured
from storage.adapters import mongo_store, vector_store
from services.router import IntentRouter, RouteLabel
from config.redis_session import redis_client

router = APIRouter(tags=["RAG"])
_knowledge_bases: dict[str, dict] = {}


def _fast_answer(question: str) -> str | None:
    """Return local replies for fixed greetings before any remote work."""
    text = question.strip().lower().strip(" \t\r\n,.!?")
    greetings = {"\u4f60\u597d", "\u60a8\u597d", "\u55e8", "hi", "hello"}
    if text in greetings:
        return "\u4f60\u597d\uff01\u6211\u662f\u5de5\u7a0b\u77e5\u8bc6\u52a9\u624b\uff0c\u5f88\u9ad8\u5174\u4e3a\u4f60\u670d\u52a1\u3002"
    if text in {"\u4f60\u4f1a\u4ec0\u4e48", "\u4f60\u4f1a\u505a\u4ec0\u4e48", "\u4f60\u80fd\u505a\u4ec0\u4e48", "\u6709\u4ec0\u4e48\u80fd\u529b"}:
        return "我是工程知识助手，可以进行日常问答，也可以基于你上传的工程文档进行检索和回答。"
    return None


def _quick_chat_answer(question: str) -> str | None:
    """对固定寒暄直接本地响应，避免为简单消息调用远程模型。"""
    normalized = question.strip().lower().strip("，。！？!? ")
    if normalized in {"你好", "您好", "嗨", "hi", "hello"}:
        return "你好！我是工程知识助手，很高兴为你服务。"
    if normalized in {"谢谢", "感谢", "thanks"}:
        return "不客气！"
    if normalized in {"你是谁", "你能做什么", "有什么能力"}:
        return "我是工程知识助手，可以进行日常问答，也可以基于你上传的工程文档检索和回答。"
    return None


def _quick_chat_answer(question: str) -> str | None:
    """本地处理固定问候，避免远程调用。"""
    normalized = question.strip().lower().strip("，。！？!?,. ")
    if normalized in {"你好", "您好", "嗨", "hi", "hello"}:
        return "你好！我是工程知识助手，很高兴为你服务。"
    if normalized in {"谢谢", "感谢", "thanks"}:
        return "不客气！"
    if normalized in {"你是谁", "你能做什么", "有什么能力"}:
        return "我是工程知识助手，可以进行日常问答，也可以基于你上传的工程文档回答。"
    return None


def _intent_router() -> IntentRouter:
    from services.llm_service import _model, _base_url
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY"), base_url=_base_url())
    return IntentRouter(client, redis_client, _model(), timeout=5.0)


@router.post("/doc/upload")
@router.post("/api/v1/doc/upload", include_in_schema=False)
async def upload_document(file: UploadFile = File(...)):
    filename = safe_filename(file.filename or "")
    raw = await file.read(MAX_UPLOAD_SIZE + 1)
    if len(raw) > MAX_UPLOAD_SIZE:
        raise HTTPException(413, "file exceeds 100MB")
    try:
        content, parse_metadata = parse_document(filename, raw)
    except DocumentParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    document_id = str(uuid.uuid4())
    await mongo_store.save_document({"id": document_id, "filename": filename, "size": len(raw), "created_at": time.time(), "parse_metadata": parse_metadata, "status": "parsed"})
    chunks = await index_document(document_id, filename, content, parse_metadata)
    return {"document_id": document_id, "filename": filename, "chunks": chunks, "status": "indexed", "parse_metadata": parse_metadata}


@router.post("/chat/ask")
@router.post("/api/v1/chat/ask", include_in_schema=False)
async def ask_chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    selected_model = request.model if request.model in available_models() else available_models()[0]
    # Fixed greetings bypass remote intent classification entirely.
    quick_answer = _fast_answer(request.question)
    if quick_answer is not None:
        label = RouteLabel.CHAT
        now = time.time()
        await mongo_store.add_message(session_id, {"role": "user", "content": request.question, "created_at": now})
        await mongo_store.add_message(session_id, {"role": "assistant", "content": quick_answer, "created_at": now})
        return {"session_id": session_id, "label": label.value, "answer": quick_answer, "sources": [], "model": "local-fast-path"}
    history = await mongo_store.history(session_id)
    label = await _intent_router().classify_with_cache(request.question, history)
    if label == RouteLabel.META:
        await mongo_store.clear_history(session_id)
        return {"session_id": session_id, "label": label.value, "cleared": True, "messages": []}
    quick_answer = _fast_answer(request.question) if label == RouteLabel.CHAT else None
    if quick_answer is not None:
        now = time.time()
        await mongo_store.add_message(session_id, {"role": "user", "content": request.question, "created_at": now})
        await mongo_store.add_message(session_id, {"role": "assistant", "content": quick_answer, "created_at": now})

        return {"session_id": session_id, "label": label.value, "answer": quick_answer, "sources": [], "model": "local-fast-path"}
    matches = await vector_store.search(request.question, request.top_k) if label == RouteLabel.KB else []
    llm_result = await generate_answer_details(request.question, matches, history, selected_model)
    answer = llm_result["answer"] if llm_result else None
    reasoning = llm_result.get("reasoning", "") if llm_result else ""
    if not answer:
        if matches:
            answer = "Based on the indexed documents: " + " ".join(x["content"][:300] for x in matches)
        elif not should_retrieve(request.question):
            answer = "你好！我是工程知识助手。你可以直接和我交流，也可以上传工程资料后让我基于知识库回答。"
        else:
            answer = "当前知识库中没有检索到相关资料。你可以换一种说法、上传相关文档，或直接提出一般问题。"
    now = time.time()
    await mongo_store.add_message(session_id, {"role": "user", "content": request.question, "created_at": now})
    await mongo_store.add_message(session_id, {"role": "assistant", "content": answer, "created_at": now})
    return {"session_id": session_id, "label": label.value, "answer": answer, "reasoning": reasoning, "sources": matches, "model": selected_model if llm_configured() else "local-fallback"}


@router.post("/chat/stream")
@router.post("/api/v1/chat/stream", include_in_schema=False)
async def stream_chat(request: ChatRequest):
    """SSE 入口；普通 /chat/ask 保持 JSON，避免客户端协议混用。"""
    result = await ask_chat(request)

    async def events():
        yield f"data: {json.dumps(result, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")


@router.get("/chat/models")
@router.get("/api/v1/chat/models", include_in_schema=False)
async def chat_models():
    models = available_models()
    return {"models": [{"id": model, "name": model} for model in models], "default": models[0]}


@router.get("/chat/history/{session_id}")
async def chat_history(session_id: str):
    return {"session_id": session_id, "messages": await mongo_store.history(session_id)}


@router.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    await mongo_store.clear_history(session_id)
    return {"session_id": session_id, "cleared": True}


@router.post("/kb/manage")
async def create_knowledge_base(request: KnowledgeBaseRequest):
    kb_id = str(uuid.uuid4())
    item = {"id": kb_id, **request.model_dump(), "created_at": time.time()}
    _knowledge_bases[kb_id] = item
    return item


@router.get("/kb/manage")
async def list_knowledge_bases():
    return {"items": list(_knowledge_bases.values())}


@router.get("/health/stores")
async def stores_health():
    from storage.adapters import mysql_store, redis_store, mongo_store, vector_store
    return {"mysql": await mysql_store.ping(), "redis": await redis_store.ping(), "mongodb": await mongo_store.ping(), "vector": await vector_store.ping()}
