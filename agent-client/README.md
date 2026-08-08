# Engineering AI Agent Frontend

工程AI智能体前端Web应用，基于Vue 3 + TypeScript + Element Plus构建的现代化单页应用。

## 🚀 技术栈

| 类别 | 技术 |
|------|------|
| 框架 | Vue 3.5 |
| 构建工具 | Vite 6 |
| UI组件库 | Element Plus 2.9 |
| 状态管理 | Pinia 2.3 |
| 路由 | Vue Router 4.5 |
| HTTP客户端 | Axios 1.8 |
| 工具函数 | @vueuse/core 12 |
| Markdown渲染 | marked 15 + highlight.js |
| 样式预处理 | Sass |

## 📁 项目结构

```
frontend-web/
├── src/
│   ├── api/                      # API层
│   │   ├── client.ts             # Axios实例和拦截器
│   │   ├── auth.ts               # 认证接口
│   │   ├── upload.ts             # 文档上传接口
│   │   ├── query.ts              # 问答接口
│   │   └── report.ts             # 报告接口
│   ├── assets/                   # 静态资源
│   ├── components/               # 公共组件
│   │   ├── layout/
│   │   │   ├── AppHeader.vue     # 顶部栏
│   │   │   ├── AppSidebar.vue    # 侧边栏
│   │   │   └── AppFooter.vue     # 底部
│   ├── composables/              # 组合式函数
│   │   ├── useAuth.ts            # 认证逻辑
│   │   ├── useTaskPolling.ts     # 任务轮询
│   │   └── useResponsive.ts      # 响应式
│   ├── layouts/                  # 布局组件
│   │   ├── AuthLayout.vue        # 认证页布局
│   │   └── MainLayout.vue        # 主布局
│   ├── router/                   # 路由配置
│   ├── stores/                   # Pinia状态管理
│   │   ├── auth.ts               # 认证状态
│   │   └── knowledge.ts          # 知识库状态
│   ├── types/                    # TypeScript类型
│   ├── utils/                    # 工具函数
│   │   ├── format.ts             # 格式化
│   │   └── storage.ts            # 本地存储
│   ├── views/                    # 页面视图
│   │   ├── LoginView.vue         # 登录页
│   │   ├── RegisterView.vue      # 注册页
│   │   ├── HomeView.vue          # 首页
│   │   ├── UploadView.vue        # 文档上传
│   │   ├── QueryView.vue         # 智能问答
│   │   ├── ReportView.vue        # 报告生成
│   │   └── NotFound.vue          # 404
│   ├── App.vue                   # 根组件
│   └── main.ts                   # 应用入口
├── public/                       # 公共资源
├── .env.development              # 开发环境变量
├── .env.production               # 生产环境变量
├── Dockerfile                    # Docker配置
├── nginx.conf                    # Nginx配置
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## 🎯 核心功能

### 1. 用户认证
- ✅ 用户注册/登录
- ✅ JWT Token管理
- ✅ 自动刷新Token
- ✅ 路由守卫保护

### 2. 文档管理
- ✅ 拖拽上传文件
- ✅ 文件类型验证
- ✅ 上传进度显示
- ✅ 任务状态轮询

### 3. 智能问答
- ✅ RAG检索增强生成
- ✅ Markdown渲染答案
- ✅ 引用来源展示
- ✅ 相似度显示

### 4. 报告生成
- ✅ 多种报告模板
- ✅ 动态参数表单
- ✅ 实时生成预览
- ✅ 导出下载功能

## 🚀 快速开始

### 方式一：本地开发

#### 1. 安装依赖

```bash
npm install
```

#### 2. 配置环境变量

编辑 `.env.development` 文件：

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=工程AI智能体
```

#### 3. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

#### 4. 生产构建

```bash
npm run build
npm run preview
```

### 方式二：Docker部署

#### 1. 构建镜像

```bash
docker build -t eng-ai-frontend .
```

#### 2. 运行容器

```bash
docker run -d -p 3000:80 --name eng-ai-frontend eng-ai-frontend
```

#### 3. 使用Docker Compose

```bash
docker-compose up -d
```

## 📡 API集成

### 后端服务要求

前端需要连接到Engineering AI Backend服务：

- **后端地址**: `http://localhost:8000`
- **API前缀**: `/api/v1`

### 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/auth/login` | POST | 用户登录 |
| `/auth/register` | POST | 用户注册 |
| `/upload/` | POST | 文档上传 |
| `/query/` | POST | RAG问答 |
| `/report/` | POST | 报告生成 |

## 🎨 界面设计

### 响应式断点

- **移动端**: < 768px
- **平板**: 768px - 992px
- **桌面**: ≥ 992px

### 布局适配

**桌面端 (≥992px)**:
- 侧边栏完整显示 (240px)
- 多列网格布局

**平板 (768-992px)**:
- 侧边栏图标模式 (64px)
- 自适应列数

**移动端 (<768px)**:
- 侧边栏隐藏，抽屉式菜单
- 单列堆叠布局

## 🔐 认证机制

### Token管理

1. **登录**: 
   - 调用 `/auth/login` 获取 `access_token` 和 `refresh_token`
   - 存储到 Pinia Store 和 LocalStorage

2. **请求拦截**:
   - Axios自动添加 `Authorization: Bearer <token>` 头

3. **Token刷新**:
   - 响应拦截器捕获401错误
   - 自动调用 `/auth/refresh` 刷新Token
   - 刷新失败则强制登出

4. **路由守卫**:
   - 未登录用户访问受保护页面重定向到登录页
   - 已登录用户访问登录页重定向到首页

## 📦 构建优化

### Vite配置亮点

- ✅ Element Plus自动导入
- ✅ 代码分割和懒加载
- ✅ Gzip压缩
- ✅ 路径别名 (`@/`)
- ✅ 开发代理到后端

### Docker优化

- ✅ 多阶段构建减小镜像
- ✅ Nginx静态资源缓存
- ✅ Gzip压缩启用
- ✅ 安全头配置

## 🔧 开发指南

### 添加新页面

1. 在 `src/views/` 创建Vue组件
2. 在 `src/router/index.ts` 添加路由
3. 在侧边栏菜单添加导航项（如需要）

### 添加新API

1. 在 `src/api/` 创建API模块
2. 定义TypeScript类型（`src/types/`）
3. 使用Axios实例发起请求

### 状态管理

使用Pinia Store管理全局状态：

```typescript
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
```

## 📝 环境配置

### 开发环境 (.env.development)

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=工程AI智能体
VITE_APP_VERSION=1.0.0
```

### 生产环境 (.env.production)

```env
VITE_API_BASE_URL=/api/v1
VITE_APP_TITLE=工程AI智能体
VITE_APP_VERSION=1.0.0
```

## 🐛 故障排查

### 常见问题

**1. 无法连接后端**

检查 `.env.development` 中的 `VITE_API_BASE_URL` 是否正确。

**2. 路由404**

确保Nginx配置支持History模式。

**3. Token失效**

检查LocalStorage中是否有token，确认刷新逻辑正常。

## 📈 性能优化

- ✅ 路由懒加载
- ✅ 组件按需加载
- ✅ 图片懒加载（可扩展）
- ✅ API请求缓存
- ✅ Gzip压缩

## 🔮 未来扩展

- [ ] 国际化 (i18n)
- [ ] PWA支持
- [ ] ECharts图表集成
- [ ] 多知识库切换
- [ ] 团队协作功能
- [ ] 单元测试 (Vitest)

## 📄 许可证

MIT License

---

**Engineering AI Frontend** - 让工程技术更智能 🚀
