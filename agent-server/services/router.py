"""用户问题意图分类：在检索前决定请求应该走哪条处理链路。"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import time
import asyncio
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class RouteLabel(str, Enum):
    """问题处理路径标签。"""

    KB = "KB"
    CHAT = "CHAT"
    META = "META"
    FOLLOWUP = "FOLLOWUP"


ROUTER_SYSTEM_PROMPT = """你是意图分类器，只能输出一个标签词：KB、CHAT、META 或 FOLLOWUP。
KB：涉及具体事实、政策、流程、工程规范、技术细节，或需要查询知识库。
CHAT：闲聊、寒暄、问候、感谢，或询问助手能力。
META：对当前对话执行清空、重置、忘记历史、结束或换话题等系统操作。
FOLLOWUP：明显依赖上一轮回答的追问，如“为什么”“还有呢”“上面第二点是什么”。
优先级：META > FOLLOWUP > CHAT > KB；无法确定时输出 KB。
只输出一个标签，不要解释理由，不要输出 Markdown 或其它文字。
示例：
你好 -> CHAT
清空刚才的对话 -> META
为什么？ -> FOLLOWUP
混凝土养护流程是什么 -> KB
"""

_RULES: list[tuple[str, RouteLabel]] = [
    (r"^(你好|您好|hi|hello|嗨|早上好|下午好|晚上好)\b?", RouteLabel.CHAT),
    (r"^(谢谢|感谢|thanks|thx)", RouteLabel.CHAT),
    (r"^(你是谁|你能做什么|有什么能力)", RouteLabel.CHAT),
    (r"(清空|重置|忘记|删除).*(对话|历史|上下文|记录)", RouteLabel.META),
    (r"^(换个话题|结束对话|退出对话|重新开始)", RouteLabel.META),
]


class IntentRouter:
    """结合规则、Redis 缓存和轻量 LLM 的异步意图路由器。"""

    def __init__(self, client: Any, redis: Any, model: str, timeout: float = 5.0,
                 default_label: RouteLabel = RouteLabel.KB) -> None:
        self.client = client
        self.redis = redis
        self.model = model
        self.timeout = timeout
        self.default_label = default_label
        self.cache_ttl = 300

    async def classify(self, question: str, history: Optional[list[dict[str, Any]]] = None) -> RouteLabel:
        """执行规则或 LLM 分类；任何异常都返回安全的 KB。"""
        started = time.perf_counter()
        rule = self._match_rule(question)
        if rule:
            logger.info("intent classified question=%r label=%s elapsed_ms=%.1f cache_hit=false", question, rule.value, (time.perf_counter() - started) * 1000)
            return rule
        prompt = question[:500]
        try:
            messages = [{"role": "system", "content": ROUTER_SYSTEM_PROMPT}]
            if history:
                messages.append({"role": "user", "content": "上一轮对话：" + json.dumps(history[-4:], ensure_ascii=False)})
            messages.append({"role": "user", "content": prompt})
            request = {"model": self.model, "messages": messages, "temperature": 0.0, "max_tokens": 5}
            try:
                response = await asyncio.wait_for(self.client.chat.completions.create(**request, response_format={"type": "json_object"}), timeout=self.timeout)
            except (TypeError, ValueError):
                response = await asyncio.wait_for(self.client.chat.completions.create(**request), timeout=self.timeout)
            raw = response.choices[0].message.content
            label = self._parse_label(raw)
            if label == RouteLabel.FOLLOWUP and not history:
                label = self.default_label
        except Exception as exc:
            label = self.default_label
            logger.warning("intent classification failed (%s); fallback=%s", type(exc).__name__, label.value)
        logger.info("intent classified question=%r label=%s elapsed_ms=%.1f cache_hit=false", question, label.value, (time.perf_counter() - started) * 1000)
        return label

    async def classify_with_cache(self, question: str, history: Optional[list[dict[str, Any]]] = None) -> RouteLabel:
        """先规则，再读取五分钟 Redis 缓存，最后调用 LLM。"""
        started = time.perf_counter()
        rule = self._match_rule(question)
        if rule:
            return rule
        key = "intent_router:" + hashlib.sha256(question.strip().lower().encode()).hexdigest()
        try:
            cached = await self.redis.get(key)
            if isinstance(cached, bytes):
                cached = cached.decode()
            if cached:
                label = self._parse_label(cached)
                logger.info("intent classified question=%r label=%s elapsed_ms=%.1f cache_hit=true", question, label.value, (time.perf_counter() - started) * 1000)
                return label
        except Exception:
            logger.debug("intent cache read failed", exc_info=True)
        label = await self.classify(question, history)
        try:
            await self.redis.setex(key, self.cache_ttl, label.value)
        except Exception:
            try:
                await self.redis.set(key, label.value, ex=self.cache_ttl)
            except Exception:
                logger.debug("intent cache write failed", exc_info=True)
        return label

    def _parse_label(self, raw: Any) -> RouteLabel:
        """容忍 JSON、标点和模型附加文字，无法识别时返回 KB。"""
        text = str(raw or "").upper()
        try:
            data = json.loads(str(raw))
            if isinstance(data, dict):
                text = str(data.get("label", data.get("route", ""))).upper()
        except (TypeError, ValueError, json.JSONDecodeError):
            pass
        for label in RouteLabel:
            if re.search(rf"\b{label.value}\b", text):
                return label
        return self.default_label

    def _match_rule(self, question: str) -> Optional[RouteLabel]:
        """匹配零延迟规则；规则顺序体现元操作优先级。"""
        value = question.strip()
        lowered = value.lower()
        # 用户明确要求不要使用知识库时，直接走通用对话模型。
        if (any(token in value for token in ("不用查询", "无需查询", "不要查询", "不查", "不要检索", "无需检索"))
                and any(token in value for token in ("知识库", "数据库", "文档", "资料", "检索"))):
            return RouteLabel.CHAT
        if value.startswith(("\u4f60\u4f1a\u4ec0\u4e48", "\u4f60\u4f1a\u505a\u4ec0\u4e48", "\u4f60\u80fd\u505a\u4ec0\u4e48", "\u6709\u4ec0\u4e48\u80fd\u529b")):
            return RouteLabel.CHAT
        if any(token in value for token in ("清空", "重置", "忘记")) and any(token in value for token in ("对话", "历史", "上下文", "记录")):
            return RouteLabel.META
        if value.startswith(("换个话题", "结束对话", "退出对话", "重新开始")):
            return RouteLabel.META
        if value.startswith(("你好", "您好", "嗨", "早上好", "下午好", "晚上好")) or lowered.startswith(("hi", "hello")):
            return RouteLabel.CHAT
        if value.startswith(("谢谢", "感谢")) or lowered.startswith(("thanks", "thx")):
            return RouteLabel.CHAT
        if value.startswith(("你是谁", "你能做什么", "有什么能力")):
            return RouteLabel.CHAT
        return None
