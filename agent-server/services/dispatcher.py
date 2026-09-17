"""根据意图标签分发到聊天、追问、元操作或 RAG 链路。"""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Optional

from services.router import RouteLabel


def build_chat_prompt(question: str) -> list[dict[str, str]]:
    return [{"role": "system", "content": "你是友好的助手。"}, {"role": "user", "content": question}]


def build_followup_prompt(question: str, history: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [{"role": "system", "content": "根据历史对话简洁回答追问。"}, *history[-6:], {"role": "user", "content": question}]


def build_rag_prompt(question: str, contexts: list[dict[str, Any]]) -> list[dict[str, str]]:
    context = "\n\n".join(item.get("content", "") for item in contexts)
    return [{"role": "system", "content": "基于以下资料回答，不足时明确说明。\n" + context}, {"role": "user", "content": question}]


async def dispatch_by_route(label: RouteLabel, question: str, session_id: str, kb_id: Optional[str],
                            history: list[dict[str, Any]], *, llm: Any = None,
                            vector_store: Any = None, reranker: Any = None,
                            meta_handler: Optional[Callable[..., Awaitable[Any]]] = None) -> Any:
    """按标签执行处理。依赖通过关键字注入，未提供时返回可测试的 Prompt。"""
    if label == RouteLabel.META:
        return await meta_handler(session_id) if meta_handler else {"session_id": session_id, "cleared": True}
    if label == RouteLabel.CHAT:
        prompts = build_chat_prompt(question)
    elif label == RouteLabel.FOLLOWUP:
        if not history:
            label = RouteLabel.KB
        else:
            prompts = build_followup_prompt(question, history)
    if label == RouteLabel.KB:
        contexts = await vector_store.search(question, 5) if vector_store else []
        if reranker:
            contexts = await reranker.rerank(question, contexts)
        prompts = build_rag_prompt(question, contexts)
    if llm is None:
        return {"label": label.value, "messages": prompts, "sources": contexts if label == RouteLabel.KB else []}
    response = await llm.chat.completions.create(model=getattr(llm, "model", None), messages=prompts, stream=False)
    return response.choices[0].message.content
