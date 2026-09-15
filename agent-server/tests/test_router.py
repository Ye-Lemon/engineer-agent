import asyncio

from services.router import IntentRouter, RouteLabel


class FakeRedis:
    def __init__(self): self.values = {}
    async def get(self, key): return self.values.get(key)
    async def setex(self, key, ttl, value): self.values[key] = value


class FakeClient:
    def __init__(self, content="KB"):
        self.content = content
        self.calls = 0
        self.chat = self
        self.completions = self
    async def create(self, **kwargs):
        self.calls += 1
        class Message: pass
        class Choice: pass
        class Response: pass
        message, choice, response = Message(), Choice(), Response()
        message.content = self.content
        choice.message = message
        response.choices = [choice]
        return response


def test_rules_chat_and_meta():
    router = IntentRouter(FakeClient(), FakeRedis(), "test")
    assert router._match_rule("你好") == RouteLabel.CHAT
    assert router._match_rule("你会什么") == RouteLabel.CHAT
    assert router._match_rule("不用查询知识库，请帮我解释原理") == RouteLabel.CHAT
    assert router._match_rule("清空对话历史") == RouteLabel.META


def test_cache_hit():
    client, redis = FakeClient("CHAT"), FakeRedis()
    router = IntentRouter(client, redis, "test")
    assert asyncio.run(router.classify_with_cache("天气如何", [])) == RouteLabel.CHAT
    assert asyncio.run(router.classify_with_cache("天气如何", [])) == RouteLabel.CHAT
    assert client.calls == 1


def test_llm_timeout_fallback_kb():
    class Broken(FakeClient):
        async def create(self, **kwargs): raise TimeoutError()
    assert asyncio.run(IntentRouter(Broken(), FakeRedis(), "test").classify("任意问题", [])) == RouteLabel.KB


def test_followup_without_history_falls_back_kb():
    router = IntentRouter(FakeClient("FOLLOWUP"), FakeRedis(), "test")
    assert asyncio.run(router.classify("为什么？", [])) == RouteLabel.KB


def test_parse_label_tolerant():
    router = IntentRouter(FakeClient(), FakeRedis(), "test")
    assert router._parse_label("答案是KB。") == RouteLabel.KB
