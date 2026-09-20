# Engineering Agent

Engineering Agent 是一个面向工程资料的知识助手后端。它提供用户认证、工程文档上传与解析、知识库索引、基于检索增强生成（RAG）的问答、会话历史、知识库管理和工程报告草稿生成等能力。

当前仓库包含 Python 后端服务；未发现独立的前端源码、`package.json` 或前端构建配置。前端可以通过 REST API 和 SSE 接口接入，开发环境默认允许 `localhost:3000`、`localhost:3001` 和 `localhost:5173` 的跨域请求。

## 功能概览

- 用户注册、登录、用户信息维护和 Bearer Token 鉴权
- 多格式工程文档上传：PDF、DOCX、TXT、Markdown、CSV/TSV、JSON、HTML、XLSX、PPTX
- 文档文本抽取、清洗、分块和索引
- 知识库问答：向量检索优先，词法检索和内存存储作为降级路径
- DeepSeek/OpenAI 兼容接口调用，支持模型列表和流式响应接口
- 会话历史保存、清空和意图路由（`KB`、`CHAT`、`META`、`FOLLOWUP`）
- Redis 任务状态/意图缓存
- MySQL 元数据、MongoDB 文档与消息、Chroma 向量库适配
- 健康检查和存储组件状态检查
- 基于参数生成工程报告草稿

## 技术栈

| 层次 | 技术 | 用途 |
| --- | --- | --- |
| Web/API | Python 3.10+、FastAPI、Uvicorn | 异步 HTTP API、OpenAPI 文档、服务启动 |
| 数据校验 | Pydantic | 请求体、响应体和配置校验 |
| 关系数据 | SQLAlchemy 2.x Async、aiomysql、MySQL | 用户、Token 和关系型元数据 |
| 缓存 | Redis 5.x（`redis.asyncio`） | 意图缓存、任务状态和 TTL |
| 文档数据 | MongoDB、Motor | 文档元数据、分块和聊天消息持久化 |
| 向量检索 | ChromaDB | 文档向量持久化和相似度搜索 |
| LLM | OpenAI Python SDK、httpx | 调用 DeepSeek 或其他 OpenAI 兼容服务 |
| 文档解析 | PyMuPDF、python-docx、openpyxl、python-pptx、Python 标准库 | PDF、DOCX、XLSX、PPTX 及文本格式解析 |
| 鉴权与安全 | PyJWT、passlib、bcrypt | JWT、密码哈希和 Token 撤销 |
| 文件处理 | aiofiles、python-multipart | 异步文件写入和 multipart 上传 |
| 测试 | pytest、asyncio | 意图路由、缓存和降级逻辑测试 |

## 系统架构

```text
客户端/前端
    |
    v
FastAPI (main.py)
    |
    +-- router/user.py       用户认证
    +-- router/rag.py        文档索引、聊天、知识库、健康检查
    +-- router/content.py    文件、查询、报告 API
    +-- router/file.py       兼容文件接口
    +-- router/task.py       任务查询接口
    |
    +-- services/router.py       意图路由与 Redis 缓存
    +-- services/document_parser.py
    +-- services/rag_pipeline.py 文档分块、索引、词法排序
    +-- services/llm_service.py  OpenAI 兼容 LLM 调用
    |
    +-- storage/adapters.py
          +-- MySQLMetadata
          +-- RedisCache
          +-- MongoDocumentStore
          +-- VectorStore (ChromaDB)
          +-- MemoryStore (本地降级)
```

### RAG 请求流程

1. `POST /doc/upload` 接收文件，按扩展名抽取文本和解析元数据。
2. 文档被切分为约 800 字符的文本块，默认重叠 120 字符。
3. 文档元数据和分块尝试写入 MongoDB，并写入 ChromaDB 向量集合。
4. `POST /chat/ask` 先执行固定规则和 Redis 缓存的意图分类。
5. `KB` 请求执行向量检索；向量库不可用时回退到内存词法检索。
6. 若配置了 LLM API Key，将检索结果和最近会话历史发送给 DeepSeek/OpenAI 兼容模型；否则返回本地检索结果或兜底提示。

## 目录说明

```text
main.py                 FastAPI 应用入口
router/                 HTTP 路由
services/               业务服务、RAG、LLM、解析和意图路由
storage/                外部存储适配器和内存降级实现
config/                 数据库、Redis、JWT、文件配置
crud/                   用户及持久化操作
model/、db/             ORM/数据模型
schemas/                Pydantic 请求与响应模型
utils/                  鉴权、响应封装和异常处理
tests/                  自动化测试
uploads/                旧版文件接口使用的上传目录
data/uploads/           新版按用户隔离的上传目录
```

## 快速开始

### 1. 创建环境并安装依赖

建议使用 Python 3.10 或更高版本：

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

`config/jwt.py` 依赖 `pydantic-settings`，鉴权代码依赖 `PyJWT`。如果当前环境未通过其他依赖间接安装，请补充：

```bash
pip install pydantic-settings PyJWT
```

### 2. 配置环境变量

在项目根目录创建 `.env`（不要提交真实密钥）：

```dotenv
# 必填：SQLAlchemy 异步数据库连接
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/engineering_agent

# JWT
JWT_SECRET_KEY=replace-with-a-long-random-secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7

# Redis（默认 redis://localhost:6379/0）
REDIS_URL=redis://localhost:6379/0

# MongoDB（默认 mongodb://localhost:27017，库名默认 engineering_agent）
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=engineering_agent

# ChromaDB
CHROMA_PERSIST_DIR=./data/chroma
CHROMA_COLLECTION=engineering_documents
CHROMA_MIN_SIMILARITY=0.15

# DeepSeek 或其他 OpenAI 兼容服务
DEEPSEEK_API_KEY=your-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
# 可选：逗号分隔的模型列表
LLM_MODELS=deepseek-chat,deepseek-reasoner
```

数据库 URL 在应用导入时会被校验。MySQL 不可用时，启动钩子会忽略建表失败；RAG 的内存降级仍可用于本地调试，但用户认证相关接口仍需要数据库。

### 3. 启动服务

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

服务地址：

- 健康检查：`http://localhost:8000/health`
- Swagger UI：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`

也可以直接运行：

```bash
python main.py
```

## API 速览

除特别说明外，`/api/v1/*` 用户接口需要 `Authorization: Bearer <token>`。

### 认证

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `POST` | `/api/v1/auth/register` | 注册用户 |
| `POST` | `/api/v1/auth/login` | 登录并返回 Token |
| `GET` | `/api/v1/auth/info` | 获取当前用户 |
| `POST` | `/api/v1/auth/info` | 更新用户信息 |
| `POST` | `/api/v1/auth/logout` | 撤销 Token |

### RAG 与对话

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `POST` | `/doc/upload` | 上传、解析并索引文档，单文件上限 100 MB |
| `POST` | `/chat/ask` | 普通 JSON 问答 |
| `POST` | `/chat/stream` | SSE 问答接口，返回事件流 |
| `GET` | `/chat/models` | 获取可用模型 |
| `GET` | `/chat/history/{session_id}` | 获取会话历史 |
| `DELETE` | `/chat/history/{session_id}` | 清空会话历史 |
| `GET/POST` | `/kb/manage` | 查看或创建知识库记录 |
| `GET` | `/health/stores` | 检查 MySQL、Redis、MongoDB、向量库 |

### 文件、查询与报告

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `POST` | `/api/v1/upload/` | 登录用户上传文件 |
| `GET` | `/api/v1/files/` | 获取当前用户文件列表 |
| `GET` | `/api/v1/download/{filename}` | 下载文件 |
| `DELETE` | `/api/v1/files/{filename}` | 删除文件 |
| `GET` | `/api/v1/upload/task/{task_id}` | 查询上传任务 |
| `POST` | `/api/v1/query/` | 查询当前用户 TXT 文档 |
| `POST` | `/api/v1/report/` | 生成参数化工程报告草稿 |

## 调用示例

```bash
# 健康检查
curl http://localhost:8000/health

# 上传并建立索引
curl -X POST http://localhost:8000/doc/upload \
  -F "file=@./docs/design.pdf"

# 基于知识库问答
curl -X POST http://localhost:8000/chat/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"设计文档中的关键约束是什么？","top_k":5}'
```

## 测试

```bash
pytest -q
```

当前测试重点覆盖 `services/router.py` 的规则路由、Redis 缓存命中、LLM 超时降级、FOLLOWUP 无历史时的回退和标签解析。涉及真实 MySQL、Redis、MongoDB、ChromaDB 或外部 LLM 的集成测试需要另外准备对应服务。

## 运行与部署注意事项

- `data/uploads`、`data/chroma` 和数据库/Redis/MongoDB 应使用持久化卷；容器重启会清除内存降级数据。
- 上传文件名会被清洗，支持格式和单文件大小由后端统一限制。
- 生产环境应将 CORS 白名单改为实际前端域名，并通过 HTTPS 传输 Token。
- 不要把 `.env`、API Key、数据库密码或上传文档提交到版本库。
- 当前 `kb/manage` 知识库记录保存在进程内存中，重启后会清空；如需生产级管理，应接入持久化存储。
- `POST /chat/stream` 当前将完整问答结果包装为 SSE 事件，并非逐 Token 流式生成。
- 旧版 `/uploads` 文件接口和新版 `/data/uploads/{user_id}` 文件接口并存，接入新前端时建议优先使用 `/api/v1/*` 用户隔离接口。

## 后续演进方向

- 增加独立前端工程（例如 React/Vue）和统一 API 客户端。
- 将文档索引、解析和报告生成拆分为后台任务队列。
- 引入真正的 embedding 模型、重排序模型和增量索引策略。
- 为 MongoDB、ChromaDB、Redis 和 LLM 增加可重复的集成测试。
- 将知识库元数据、权限和会话管理从内存实现迁移到持久化数据库。

