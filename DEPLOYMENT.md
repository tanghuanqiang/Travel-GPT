# TravelPlanGPT - 快速部署指南

## 本地开发

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问: http://localhost:3000

### 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 配置 .env 文件
cp .env.example .env
# 编辑 .env，添加 OPENAI_API_KEY

python main.py
```

访问: http://localhost:8000

## 部署到生产环境

### Vercel (前端)

1. 连接 GitHub 仓库
2. 选择 `frontend` 目录作为根目录
3. 自动检测 Next.js
4. 部署

### Render (后端)

1. 创建新的 Web Service
2. 连接 GitHub 仓库
3. 配置：
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. 添加环境变量：
   - `OPENAI_API_KEY`
   - `TAVILY_API_KEY` (可选)
5. 部署

### Railway (后端备选)

```bash
cd backend
railway login
railway init
railway up
```

## 环境变量

### 前端
无需特殊配置（如需自定义后端地址，修改 axios baseURL）

### 后端
必需：
- `OPENAI_API_KEY`

可选（增强功能）：
- `TAVILY_API_KEY`
- `UNSPLASH_ACCESS_KEY`
- `OPENWEATHER_API_KEY`

## 性能优化

- 前端使用 Next.js SSG/ISR
- 后端使用异步API调用
- 缓存常用搜索结果
- 图片使用 CDN（Unsplash）
