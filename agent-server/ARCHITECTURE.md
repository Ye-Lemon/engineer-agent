# 四存储 RAG 服务

后端现在按 API 网关、RAG 管线和四存储适配器组织：

```
router/rag.py -> services/rag_pipeline.py -> storage/adapters.py
                                      |-> MySQLMetadata（关系元数据）
                                      |-> RedisCache（会话/缓存/限流）
                                      |-> MongoDocumentStore（文档、分块、消息）
                                      `-> VectorStore（Qdrant 可替换适配器）
```

默认使用 `storage.memory.memory_store` 降级，便于没有外部服务时运行；设置
`DATABASE_URL`、`REDIS_URL`、`MONGODB_URL` 和向量库配置后可逐步替换为真实实现。

## API

- `POST /doc/upload`：上传并执行解析、分块、索引。
- `POST /chat/ask`：向量检索（当前为词法回退）并保存会话消息。
- `GET /chat/history/{session_id}`：读取 Mongo/内存中的消息历史。
- `GET|POST /kb/manage`：知识库元数据管理。
- `GET /health`、`GET /health/stores`：服务和各存储健康检查。

`services/rag_pipeline.py` 中的 `index_document` 和 `lexical_search` 是接入真实
Embedding、Qdrant、重排模型和 DeepSeek 流式生成的稳定扩展点。
