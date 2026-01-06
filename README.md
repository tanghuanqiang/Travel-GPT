# Travel-GPT 🌍✈️
AI 驱动的旅行规划助手 - 使用通义千问 LLM 生成个性化的旅行行程。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-green)

## ✨ 核心功能
- 🤖 **AI 智能规划**：基于通义千问大模型，根据目的地、天数、预算和偏好生成详细行程。
- 👤 **用户系统**：完整的注册登录流程，基于 JWT 的身份认证，支持历史行程管理。
- 🖼️ **真实图片**：集成 Unsplash/Pexels API，自动匹配并展示景点的真实照片。
- 📱 **响应式设计**：使用 Tailwind CSS 构建，完美适配桌面端和移动端。
- 🔒 **数据持久化**：使用 SQLite 数据库存储用户信息和历史行程，实现数据本地化。

## 🛠️ 技术框架
### 后端 (Backend)
- **FastAPI**: 现代 Python Web 框架，提供高性能 API 服务。
- **SQLAlchemy**: 强大的 ORM 工具，简化数据库操作。
- **DashScope**: 集成阿里云通义千问 (Qwen-plus) 大模型。
- **Python-JOSE**: 处理 JWT 认证，保障系统安全性。

### 前端 (Frontend)
- **Next.js 14**: 使用 App Router 的 React 框架。
- **TypeScript**: 全面采用强类型开发。
- **Tailwind CSS & Shadcn UI**: 用于构建美观且响应式的用户界面。
- **Zustand**: 轻量级、高效的状态管理库。

## 🚀 快速开始
### 1. 环境准备
- Node.js 18+
- Python 3.12+
- 通义千问 API Key ([申请地址](https://dashscope.aliyuncs.com/))

### 2. 配置环境变量
在 `backend/` 目录下创建 `.env` 文件：
```env
LLM_API_KEY=your_dashscope_api_key
# 推荐配置，用于显示景点图片
UNSPLASH_ACCESS_KEY=your_unsplash_access_key
```

### 3. 启动项目

**方式一：一键启动 (推荐)**
- Windows: 双击运行 `start.bat`
- Linux/Mac: 运行 `bash start.sh`

**方式二：手动启动**

*   **后端**:
    ```bash
    cd backend
    pip install -r requirements.txt
    python init_db.py
    python run_server.py
    ```
*   **前端**:
    ```bash
    cd frontend
    pnpm install
    pnpm dev
    ```

### 4. 访问应用
- 前端：[http://localhost:3000](http://localhost:3000)
- API 文档：[http://localhost:8000/docs](http://localhost:8000/docs)

---

⭐ **如果你喜欢这个项目，请给个 Star！**
Last Updated: 2026-01-07
