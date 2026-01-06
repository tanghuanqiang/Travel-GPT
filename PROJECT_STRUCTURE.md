# TravelPlanGPT 项目结构

```
Travel-GPT/
│
├── 📁 frontend/                      # Next.js 前端应用
│   ├── 📁 app/                       # Next.js App Router
│   │   ├── page.tsx                  # 首页 - 旅行参数输入表单
│   │   ├── layout.tsx                # 根布局
│   │   ├── globals.css               # 全局样式（Tailwind）
│   │   ├── 📁 plan/
│   │   │   └── page.tsx              # Agent运行页 - 实时日志
│   │   └── 📁 result/
│   │       └── page.tsx              # 结果页 - 完整行程展示
│   │
│   ├── 📁 components/                # React组件
│   │   └── 📁 ui/                    # shadcn/ui 组件
│   │       ├── button.tsx            # 按钮组件
│   │       ├── card.tsx              # 卡片组件
│   │       ├── input.tsx             # 输入框组件
│   │       ├── label.tsx             # 标签组件
│   │       └── textarea.tsx          # 文本域组件
│   │
│   ├── 📁 lib/                       # 工具函数
│   │   └── utils.ts                  # cn() 等工具函数
│   │
│   ├── package.json                  # 前端依赖
│   ├── tsconfig.json                 # TypeScript配置
│   ├── tailwind.config.ts            # Tailwind配置
│   ├── next.config.js                # Next.js配置
│   ├── postcss.config.js             # PostCSS配置
│   ├── components.json               # shadcn/ui配置
│   └── .gitignore
│
├── 📁 backend/                       # FastAPI 后端服务
│   ├── 📁 app/                       # 应用代码
│   │   ├── __init__.py
│   │   ├── agent.py                  # LangChain Agent核心逻辑
│   │   ├── models.py                 # Pydantic数据模型
│   │   └── tools.py                  # 外部API工具集成
│   │
│   ├── main.py                       # FastAPI入口文件
│   ├── requirements.txt              # Python依赖
│   ├── .env.example                  # 环境变量模板
│   └── .gitignore
│
├── 📁 docs/                          # 文档（可选）
│
├── README.md                         # 项目主文档
├── QUICKSTART.md                     # 快速开始指南
├── API.md                            # API使用文档
├── DEPLOYMENT.md                     # 部署指南
├── CONTRIBUTING.md                   # 贡献指南
├── CHANGELOG.md                      # 更新日志
├── LICENSE                           # MIT许可证
├── start.sh                          # Linux/Mac启动脚本
├── start.bat                         # Windows启动脚本
└── .gitignore                        # Git忽略文件
```

## 📁 核心文件说明

### 前端关键文件

| 文件 | 作用 | 技术栈 |
|------|------|--------|
| `app/page.tsx` | 首页，旅行参数输入表单 | React, shadcn/ui |
| `app/plan/page.tsx` | Agent运行页，实时日志 | React, Axios |
| `app/result/page.tsx` | 行程展示页，包含图表和时间轴 | React, Recharts |
| `components/ui/*` | 可复用UI组件 | shadcn/ui, Radix UI |
| `lib/utils.ts` | 工具函数（cn等） | clsx, tailwind-merge |
| `globals.css` | 全局样式，CSS变量 | Tailwind CSS |

### 后端关键文件

| 文件 | 作用 | 技术栈 |
|------|------|--------|
| `main.py` | FastAPI应用入口，路由定义 | FastAPI |
| `app/agent.py` | LangChain Agent，核心AI逻辑 | LangChain, OpenAI |
| `app/models.py` | Pydantic数据模型 | Pydantic |
| `app/tools.py` | 外部API工具（搜索、图片等） | Requests, APIs |
| `.env.example` | 环境变量模板 | dotenv |

## 🔄 数据流

```
用户输入
    ↓
[frontend/app/page.tsx]
    ↓
localStorage保存
    ↓
[frontend/app/plan/page.tsx]
    ↓
POST /api/generate-plan
    ↓
[backend/main.py]
    ↓
[backend/app/agent.py]
    ↓
LangChain Agent调用
    ↓
- OpenAI GPT-4
- Tavily Search
- Unsplash API
- Weather API
    ↓
生成行程数据
    ↓
[frontend/app/result/page.tsx]
    ↓
美观展示
```

## 🎨 UI组件层次

```
app/page.tsx (首页)
├── Card (表单卡片)
│   ├── Input (目的地、预算等)
│   ├── Button (偏好标签)
│   └── Textarea (额外要求)
└── Card (预设示例)

app/plan/page.tsx (运行页)
├── Card (日志面板)
│   └── LogEntry[] (日志条目)
└── Card (进度面板)
    └── ProgressBar (进度条)

app/result/page.tsx (结果页)
├── Card (预算概览)
│   └── PieChart (预算饼图)
├── Card[] (每日行程)
│   └── Activity[] (活动时间轴)
├── Card (隐藏宝石)
└── Card (实用建议)
```

## 🔧 配置文件

| 文件 | 用途 |
|------|------|
| `frontend/tsconfig.json` | TypeScript编译配置 |
| `frontend/tailwind.config.ts` | Tailwind CSS主题配置 |
| `frontend/next.config.js` | Next.js构建配置 |
| `frontend/components.json` | shadcn/ui组件配置 |
| `backend/.env` | 环境变量（API Keys） |

## 📦 主要依赖

### 前端
- Next.js 14
- React 18
- Tailwind CSS 3
- shadcn/ui
- Radix UI
- Recharts
- Axios
- Lucide React

### 后端
- FastAPI
- LangChain
- OpenAI
- Pydantic
- Uvicorn
- python-dotenv

## 🚀 扩展点

想添加新功能？这里是主要扩展点：

1. **新页面**: 在 `frontend/app/` 下创建新目录
2. **新组件**: 在 `frontend/components/` 下创建
3. **新API工具**: 在 `backend/app/tools.py` 添加函数
4. **新路由**: 在 `backend/main.py` 添加endpoint
5. **新数据模型**: 在 `backend/app/models.py` 定义

## 📊 性能考虑

- **前端**: 使用Next.js SSG/SSR优化首屏加载
- **后端**: FastAPI异步处理，支持并发请求
- **缓存**: 可在 `app/agent.py` 添加Redis缓存
- **CDN**: Unsplash图片使用CDN加速

## 🔒 安全注意

- ✅ API Keys存储在 `.env`（不提交到Git）
- ✅ CORS配置限制来源
- ✅ 输入验证（Pydantic）
- ⚠️ 生产环境需添加认证和速率限制
