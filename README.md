# Travel-GPT 🌍✈️

> AI 驱动的旅行规划助手 - 使用通义千问 LLM 生成个性化的旅行行程

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-green)
![Python](https://img.shields.io/badge/Python-3.12+-blue)

## 📖 项目简介

Travel-GPT 是一个基于通义千问大模型的智能旅行规划系统，提供完整的用户系统和历史记录管理。

**核心功能：**
- 🤖 **AI 智能规划**：基于通义千问 (Qwen-plus) 大模型生成详细行程
- 👤 **用户系统**：完整的注册登录、JWT 认证、历史记录管理
- 🎯 **个性化定制**：根据预算、偏好和人数定制旅行方案
- 🖼️ **真实图片**：集成 Unsplash 显示景点真实照片
- 📱 **响应式设计**：支持桌面端和移动端
- 🌐 **简体中文**：完全本地化的中文界面
- 🔒 **数据持久化**：SQLite 数据库存储用户和行程数据

## 🎨 技术栈

### 前端
- **框架**: Next.js 14.2.35 (React 18.3.1)
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **组件库**: shadcn/ui
- **HTTP 客户端**: Axios
- **认证**: JWT + localStorage
- **图标**: Lucide React

### 后端
- **框架**: FastAPI (Python 3.12)
- **LLM**: 通义千问 (Qwen-plus) via DashScope
- **数据库**: SQLite + SQLAlchemy 2.0.25
- **认证**: JWT (python-jose) + Bcrypt
- **图片服务**: Unsplash Source API
- **服务器**: Uvicorn

## 🚀 快速开始

### 前置要求

- Node.js 18+
- Python 3.12+
- pnpm (推荐) 或 npm
- 通义千问 API Key (DashScope)

### 1️⃣ 克隆项目

```bash
git clone https://github.com/yourusername/Travel-GPT.git
cd Travel-GPT
```

### 2️⃣ 配置环境变量

创建 `backend/.env` 文件：

```env
# 必需：通义千问 API Key
LLM_API_KEY=your_dashscope_api_key

# 推荐：图片服务（显示真实景点照片）
UNSPLASH_ACCESS_KEY=your_unsplash_key    # 推荐首选
PEXELS_API_KEY=your_pexels_key           # 完美备份

# 可选：其他服务
TAVILY_API_KEY=your_tavily_key
```

**获取 API Key：**
- **通义千问**（必需）：https://dashscope.aliyuncs.com/
- **Unsplash**（推荐）：https://unsplash.com/developers - 数百万真实景点照片
- **Pexels**（推荐）：https://www.pexels.com/api/ - 完全免费无限制

> 💡 **图片 API 详细配置指南**：查看 [IMAGE_API_GUIDE.md](IMAGE_API_GUIDE.md)  
> 只需10分钟，让你的旅行计划显示真实的景点照片！

### 3️⃣ 前端设置

```bash
cd frontend
pnpm install
# 或
npm install
```

### 4️⃣ 后端设置

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python init_db.py
```

### 5️⃣ 启动服务

**方式一：使用启动脚本（推荐）**

Windows:
```bash
start.bat
```

Linux/Mac:
```bash
chmod +x start.sh
./start.sh
```

**方式二：手动启动**

后端（终端1）:
```bash
cd backend
python run_server.py
# 或
uvicorn main:app --reload --port 8000
```

前端（终端2）:
```bash
cd frontend
pnpm dev
# 或
npm run dev
```

### 6️⃣ 访问应用

- **前端**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 📱 使用指南

### 1. 注册/登录
- 访问 http://localhost:3000
- 点击右上角"登录"或"注册"按钮
- 创建账号（邮箱 + 密码）并登录

### 2. 生成旅行计划
1. **填写表单**
   - 目的地：如"北京"、"上海"、"成都"
   - 天数：1-7天
   - 预算：如"3000-5000元"
   - 人数：出行人数
   - 偏好：美食、文化、户外、购物等
   - 额外需求（可选）：特殊要求说明

2. **点击"生成行程"**
   - AI Agent 开始规划（约30-60秒）
   - 实时显示 Agent 思考过程
   - 自动搜索景点、餐厅、图片

3. **查看完美行程**
   - 每日详细时间表
   - 景点图片和推荐理由
   - 餐厅和住宿建议
   - 预算参考和实用建议

### 3. 查看历史记录
- 点击"历史记录"查看过往行程
- 点击"查看详情"重新浏览完整行程
- 点击"删除"清理不需要的记录

### 4. 示例输入

**示例1：美食之旅**
```
目的地：成都
天数：3
预算：4000-6000元
人数：2人
偏好：美食、文化
额外需求：想吃正宗火锅和串串
```

**示例2：户外探险**
```
目的地：黄山
天数：2
预算：2000-3000元
人数：4人
偏好：户外、摄影
额外需求：想看日出和云海
```

## 🏗️ 项目结构

```
Travel-GPT/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── __init__.py
│   │   ├── agent.py        # LLM Agent 核心逻辑
│   │   ├── models.py       # Pydantic 数据模型
│   │   ├── tools.py        # Agent 工具函数
│   │   ├── database.py     # 数据库配置
│   │   ├── db_models.py    # SQLAlchemy ORM 模型
│   │   ├── auth.py         # JWT 认证逻辑
│   │   └── image_search.py # 图片搜索服务
│   ├── main.py             # FastAPI 主应用
│   ├── requirements.txt    # Python 依赖
│   ├── init_db.py          # 数据库初始化脚本
│   ├── clean_duplicates.py # 清理重复记录工具
│   ├── run_server.py       # 服务器启动脚本
│   └── .env                # 环境变量配置
│
├── frontend/                # 前端应用
│   ├── app/
│   │   ├── page.tsx        # 首页
│   │   ├── plan/page.tsx   # 生成行程页面
│   │   ├── result/page.tsx # 行程结果展示
│   │   ├── history/page.tsx # 历史记录
│   │   ├── login/page.tsx  # 登录页面
│   │   ├── register/page.tsx # 注册页面
│   │   └── globals.css     # 全局样式
│   ├── components/ui/      # shadcn/ui 组件
│   ├── lib/
│   │   ├── auth-context.tsx # 认证上下文
│   │   ├── axios-config.ts  # Axios 配置
│   │   └── utils.ts         # 工具函数
│   ├── package.json
│   └── next.config.js
│
├── start.bat               # Windows 启动脚本
├── start.sh                # Linux/Mac 启动脚本
├── README.md               # 项目说明
├── API.md                  # API 文档
├── CHANGELOG.md            # 更新日志
└── DEPLOYMENT.md           # 部署指南
```

## 🎯 核心功能详解

### AI Agent 工作流程

1. **需求分析**：解析用户输入的目的地、天数、预算、偏好
2. **信息搜索**：调用 Tavily API 搜索景点、餐厅、活动信息
3. **图片获取**：通过 Unsplash API 获取目的地和景点的真实照片
4. **行程规划**：LLM 生成详细的每日行程安排
5. **数据持久化**：保存到数据库，支持历史记录查询

### 工具集成

- **Tavily Search**: 搜索最新的景点、餐厅、活动信息
- **Unsplash API**: 获取高质量的目的地和景点图片
- **通义千问 LLM**: 强大的中文理解和生成能力

### 用户系统

- **注册/登录**: JWT Token 认证
- **Token 验证**: 自动验证 Token 有效性，失效自动清除
- **历史记录**: 按用户存储所有生成的行程
- **去重机制**: 5分钟内相同目的地+天数自动去重

## 📊 API 接口

### 认证接口

```http
POST /api/auth/register      # 用户注册
POST /api/auth/login         # 用户登录
GET  /api/auth/me            # 获取当前用户信息
```

### 行程接口

```http
POST   /api/generate-plan    # 生成旅行行程
GET    /api/history          # 获取历史记录列表
GET    /api/history/{id}     # 获取行程详情
DELETE /api/history/{id}     # 删除行程记录
```

详细 API 文档请参考 [API.md](API.md) 或访问 http://localhost:8000/docs

## �️ 维护工具

### 初始化数据库
```bash
cd backend
python init_db.py
```
创建 SQLite 数据库文件和表结构（Users, Itineraries）

### 清理重复记录
```bash
cd backend
python clean_duplicates.py
```
交互式清理工具，按目的地+天数分组，保留最新记录

### 查看数据库
```bash
cd backend
sqlite3 travel_gpt.db
.tables
SELECT * FROM users;
SELECT * FROM itineraries;
.exit
```

## 🔮 未来扩展

- [ ] 导出PDF功能
- [ ] 分享链接生成
- [ ] 多人协作编辑
- [ ] 实时机票酒店查询
- [ ] 集成地图 API 显示路线
- [ ] 支持多语言（英文、日文）
- [ ] 移动端 App（React Native）

## 🐛 常见问题

**Q: 如何更换 LLM 模型？**  
A: 修改 `backend/.env` 中的模型名称：
```env
LLM_MODEL_NAME=qwen-plus    # 默认
# 或
LLM_MODEL_NAME=qwen-max     # 更强大
LLM_MODEL_NAME=qwen-turbo   # 更快速
```

**Q: Agent 生成失败怎么办？**  
A: 
1. 检查 `LLM_API_KEY` 是否正确
2. 确认 API 额度充足
3. 查看后端日志排查错误

**Q: 图片无法加载或显示占位图？**  
A: 
1. **配置图片 API**（推荐）：
   - 查看 [IMAGE_API_GUIDE.md](IMAGE_API_GUIDE.md) 详细指南
   - 只需10分钟配置 Unsplash 或 Pexels
   - 测试配置：`cd backend && python test_image_api.py`

2. **检查前端配置**：
   - 确认 `frontend/next.config.js` 配置了图片域名
   - 添加：`images.unsplash.com`, `images.pexels.com`

3. **网络问题**：
   - 确认能访问 Unsplash/Pexels（国内可访问）
   - 检查防火墙设置

**Q: 历史记录有重复？**  
A: 运行清理工具：
```bash
cd backend
python clean_duplicates.py
```

**Q: Token 验证失败？**  
A: 
1. Token 可能已过期（默认7天有效期）
2. 清除浏览器 localStorage 重新登录
3. 检查后端 `SECRET_KEY` 配置

**Q: 如何部署到生产环境？**  
A: 详见 [DEPLOYMENT.md](DEPLOYMENT.md)
- 前端：Vercel 一键部署
- 后端：Railway, Render, 或 VPS + Docker

## 📄 开源协议

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [通义千问](https://tongyi.aliyun.com/) - 强大的中文 LLM
- [Unsplash](https://unsplash.com/) - 高质量旅行图片
- [shadcn/ui](https://ui.shadcn.com/) - 优雅的 UI 组件库
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Python Web 框架
- [Next.js](https://nextjs.org/) - React 全栈框架

## 📧 联系方式

有问题或建议？欢迎提 Issue 或 Pull Request！

详细贡献指南请参考 [CONTRIBUTING.md](CONTRIBUTING.md)

---

⭐ **如果这个项目对你有帮助，请给个 Star！**

最后更新：2026年1月7日
