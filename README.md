# Engineering AI Agent

Engineering AI Agent 是一个面向工程资料的智能知识助手。用户可以注册登录、上传工程文档、建立可检索的知识内容，并通过对话式问答获取答案或生成工程报告。

项目采用前后端分离架构：前端负责认证、文档管理、智能问答和报告生成等交互；后端负责用户体系、文件解析、RAG 检索、LLM 调用以及数据持久化。

## 功能概览

- 用户注册、登录、当前用户信息维护和 JWT Bearer Token 鉴权
- PDF、DOCX、TXT、Markdown、CSV/TSV、JSON、HTML、XLSX、PPTX 文档上传与文本抽取
- 文档分块、向量索引、关键词检索和检索增强生成（RAG）问答
- 普通 JSON 问答和 SSE 问答接口，支持会话历史、清空历史和模型列表
- 文件列表、文件详情、下载、删除及上传任务状态查询
- 工程报告参数表单、报告生成、预览、复制和下载
- MySQL、Redis、MongoDB、ChromaDB 的存储健康检查
- 前端响应式布局，适配桌面、平板和移动端

## 项目结构

```text
engineering-agent/
├── agent-client/                 # Vue 3 前端
│   ├── src/
│   │   ├── api/                  # Axios API 封装
│   │   ├── components/           # 公共布局和业务组件
│   │   ├── composables/          # useAuth、任务轮询、响应式逻辑
│   │   ├── layouts/              # 登录布局、主布局
│   │   ├── router/               # 路由和登录鉴权守卫
│   │   ├── stores/               # Pinia 状态
│   │   ├── types/                # TypeScript 类型
│   │   ├── views/                # 登录、上传、文件、问答、报告页面
│   │   └── main.ts
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── vite.config.ts
├── agent-server/                 # FastAPI 后端
│   ├── main.py                   # 应用入口、CORS、路由注册
│   ├── router/                   # 认证、文件、任务、RAG 路由
│   ├── services/                 # 文档解析、RAG、LLM、文件和意图路由
│   ├── storage/                  # MySQL、Redis、MongoDB、向量库适配器
│   ├── config/                   # 数据库、Redis、JWT、文件配置
│   ├── crud/、model/、db/        # 持久化和 ORM 逻辑
│   ├── schemas/                  # Pydantic 请求/响应模型
│   ├── tests/                    # pytest 测试
│   └── requirements.txt
└── README.md
```

## 技术栈

### 前端（`agent-client`）

| 分类 | 技术 |
| --- | --- |
| 应用框架 | Vue 3.5、TypeScript 5.7 |
| 构建工具 | Vite 6 |
| UI 组件 | Element Plus、`@element-plus/icons-vue` |
| 状态与路由 | Pinia、Vue Router |
| 网络请求 | Axios，配合请求/响应拦截器 |
| 交互工具 | `@vueuse/core` |
| 内容展示 | `marked`、`highlight.js` |
| 样式 | Sass |
| 生产静态服务 | Nginx（Docker 多阶段构建） |

### 后端（`agent-server`）

| 分类 | 技术 |
| --- | --- |
| Web/API | Python 3.10+、FastAPI、Uvicorn |
| 数据校验 | Pydantic |
| 关系型数据 | SQLAlchemy 2.x Async、aiomysql、MySQL |
| 缓存与任务状态 | Redis 5+、`redis.asyncio` |
| 文档与会话数据 | MongoDB、Motor |
| 向量检索 | ChromaDB；不可用时回退到关键词检索/内存存储 |
| LLM | OpenAI Python SDK，兼容 DeepSeek 或其他 OpenAI Compatible 服务 |
| 文档解析 | PyMuPDF、python-docx、openpyxl、python-pptx、Python 标准库 |
| 安全 | PyJWT、Passlib、bcrypt、CORS |
| 测试 | pytest、pytest-asyncio/httpx |

## 系统架构与数据流

```text
Vue 3 SPA
   │ Axios / Fetch（JSON、Multipart、SSE）
   ▼
FastAPI API
   ├─ 用户认证与文件路由
   ├─ 文档解析 → 文本清洗 → 分块（默认 800 字符，重叠 120）
   ├─ ChromaDB 向量检索
   ├─ MongoDB 文档、分块、会话消息
   ├─ Redis 缓存、意图分类缓存、任务状态
   ├─ MySQL 用户与关系型元数据
   └─ DeepSeek/OpenAI Compatible LLM
```

一次知识库问答通常经历：上传文档、按扩展名解析文本、分块并写入文档存储/向量库；用户提问后进行意图判断，知识库问题优先检索相关分块，再将检索结果和会话上下文提交给 LLM。外部存储或模型未配置时，服务会尽可能回退到内存存储、关键词检索或本地固定回复，便于本地开发。

## 环境要求

- Node.js 20+ 和 npm
- Python 3.10+
- 生产或完整开发环境：MySQL、Redis、MongoDB、可选 ChromaDB 持久化目录
- 可选 LLM API Key（DeepSeek 或其他 OpenAI Compatible 服务）

## 快速开始

### 1. 启动后端

```bash
cd agent-server
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

在 `agent-server/.env` 中配置至少一个可用的 MySQL 连接：

```dotenv
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/engineering_agent
JWT_SECRET_KEY=replace-with-a-long-random-secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7

REDIS_URL=redis://localhost:6379/0
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=engineering_agent

CHROMA_PERSIST_DIR=./data/chroma
CHROMA_COLLECTION=engineering_documents
CHROMA_MIN_SIMILARITY=0.15

DEEPSEEK_API_KEY=your-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
# 可选：逗号分隔的模型列表
# LLM_MODELS=deepseek-chat,deepseek-reasoner
```

启动 API：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

后端地址：

- 健康检查：`http://localhost:8000/health`
- Swagger UI：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`

### 2. 启动前端

```bash
cd agent-client
npm install
```

开发环境变量（`agent-client/.env.development`）：

```dotenv
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=工程AI智能体
VITE_APP_VERSION=1.0.0
```

启动开发服务器：

```bash
npm run dev
```

默认访问 `http://localhost:3000`。生产构建与预览：

```bash
npm run build
npm run preview
```

前端 Axios 实例会自动附加 `Authorization: Bearer <token>`。生产环境可将 `VITE_API_BASE_URL` 设置为 `/api/v1`，由 Nginx 反向代理到后端。

## 主要 API

除特别说明外， `/api/v1/*` 下的用户接口需要 Bearer Token；RAG 路由目前同时保留了不带前缀的兼容路径。

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| POST | `/api/v1/auth/register` | 注册用户 |
| POST | `/api/v1/auth/login` | 登录并获取 Token |
| GET/POST | `/api/v1/auth/info` | 获取或更新用户信息 |
| POST | `/api/v1/auth/logout` | 撤销 Token |
| POST | `/doc/upload` | 解析并索引文档（上限 100 MB） |
| POST | `/chat/ask` | JSON 问答 |
| POST | `/chat/stream` | SSE 问答 |
| GET | `/chat/models` | 获取可用模型 |
| GET/DELETE | `/chat/history/{session_id}` | 获取或清空会话历史 |
| GET/POST | `/kb/manage` | 查询或创建知识库记录 |
| POST | `/api/v1/upload/` | 用户文件上传 |
| GET | `/api/v1/files/` | 文件列表 |
| GET | `/api/v1/download/{filename}` | 下载文件 |
| DELETE | `/api/v1/files/{filename}` | 删除文件 |
| POST | `/api/v1/query/` | 兼容的知识库问答 |
| POST | `/api/v1/report/` | 生成工程报告 |
| GET | `/health/stores` | 检查各存储组件 |

## Docker 部署

前端已提供 Node 构建阶段和 Nginx 运行阶段：

```bash
cd agent-client
docker build -t eng-ai-frontend .
docker run -d --name eng-ai-frontend -p 3000:80 eng-ai-frontend
```

也可以使用 `docker-compose.yml`。该 Compose 文件默认使用外部网络 `eng-ai-network`，并引用名为 `eng-ai-backend:latest` 的后端镜像；实际部署前请按环境修改镜像名、网络和 Nginx 代理地址。当前仓库未提供后端 Dockerfile，后端通常直接使用 Python 虚拟环境或自行构建镜像运行。

## 开发与测试

```bash
# 前端类型检查和生产构建
cd agent-client
npm run build

# 后端测试
cd ../agent-server
pytest -q
```

新增前端页面时，通常需要同步更新 `src/views`、`src/router`、侧边栏菜单和对应 API 类型；新增后端能力时，建议按 `router → services → storage` 分层实现，并在 `schemas` 中定义请求/响应模型。

## 安全与运维注意事项

- `.env`、API Key、数据库密码和用户上传文件不要提交到版本库。
- 生产环境应将 CORS 白名单改为真实前端域名，并通过 HTTPS 传输 Token。
- `data/chroma`、上传目录以及 MySQL、Redis、MongoDB 应使用持久化卷。
- `kb/manage` 当前知识库记录保存在进程内存中，服务重启会丢失；生产环境应接入持久化存储。
- 当前 `/chat/stream` 返回的是封装后的 SSE 事件，是否逐 Token 流式生成取决于后端 LLM 服务实现。
- 老版本 `/uploads` 接口和新版按用户隔离的 `/api/v1/*` 文件接口并存，接入新前端时优先使用新版路径。

## 后续演进方向

- 将文档解析、索引和报告生成迁移到异步任务队列。
- 接入正式 embedding 模型、向量数据库和重排序模型。
- 完善 MongoDB、ChromaDB、Redis、LLM 的集成测试和可观测性。
- 将知识库元数据、权限和会话管理从内存实现迁移到持久化数据库。
- 统一兼容接口与新版 API 的响应模型，减少前后端适配代码。

