# Travel-GPT Docker Compose 部署指南

本文档介绍如何使用 Docker Compose 一键部署 Travel-GPT 项目。

## 📋 前置要求

- **Docker** 20.10+ 
- **Docker Compose** 2.0+（或 Docker Desktop，已包含 Compose）

## 🚀 快速部署

### 方法一：使用部署脚本（推荐）

**Linux/macOS:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Windows:**
```cmd
deploy.bat
```

### 方法二：手动部署

1. **复制环境变量文件**
   ```bash
   # Linux/macOS
   cp env.example .env
   
   # Windows
   copy env.example .env
   ```

2. **编辑 .env 文件**
   
   必须配置以下项：
   - `SECRET_KEY`: JWT密钥（必须修改为强随机字符串）
   - `LLM_PROVIDER` 和对应的 API Key（NVIDIA/DashScope/Ollama）
   
   可选配置：
   - `BACKEND_PORT`: 后端端口（默认 18890）
   - `FRONTEND_PORT`: 前端端口（默认 18891）
   - 其他 API Keys（图片搜索、天气等）

3. **启动服务**
   ```bash
   docker compose up -d --build
   ```

## 📍 访问地址

部署成功后，可通过以下地址访问：

- **前端应用**: http://localhost:18891
- **后端API**: http://localhost:18890
- **API文档**: http://localhost:18890/docs

## 🔧 端口配置

为了避免与 Daily-News 项目冲突，Travel-GPT 使用以下端口：

| 服务 | Travel-GPT | Daily-News |
|------|------------|------------|
| 后端 | 18890 | 18888 |
| 前端 | 18891 | 18889 |

如需修改端口，请编辑 `.env` 文件中的 `BACKEND_PORT` 和 `FRONTEND_PORT`。

## 📋 常用命令

```bash
# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f backend
docker compose logs -f frontend

# 重启服务
docker compose restart

# 停止服务
docker compose down

# 停止并删除数据卷
docker compose down -v

# 重新构建并启动
docker compose up -d --build
```

## 🔍 故障排查

### 1. 端口被占用

如果遇到端口冲突错误：
```bash
# 检查端口占用（Linux/macOS）
lsof -i :18890
lsof -i :18891

# Windows
netstat -ano | findstr :18890
netstat -ano | findstr :18891
```

解决方案：
- 修改 `.env` 文件中的端口配置
- 或停止占用端口的其他服务

### 2. 构建失败

如果 Docker 构建失败：
```bash
# 清理构建缓存
docker compose build --no-cache

# 查看详细错误信息
docker compose build --progress=plain
```

### 3. 前端无法连接后端

检查：
1. 确保 `.env` 文件中的 `NEXT_PUBLIC_API_URL` 配置正确
2. 确保 `CORS_ORIGINS` 包含前端地址
3. 检查后端服务是否正常运行：`docker compose logs backend`

### 4. 数据库问题

如果使用 SQLite（默认）：
- 数据库文件存储在 `./backend/data/travel_gpt.db`
- 确保 `backend/data` 目录有写入权限

## 📦 项目结构

```
Travel-GPT/
├── backend/              # 后端服务
│   ├── Dockerfile       # 后端 Docker 镜像
│   ├── main.py          # FastAPI 应用入口
│   └── ...
├── frontend/            # 前端服务
│   ├── Dockerfile       # 前端 Docker 镜像
│   ├── next.config.js   # Next.js 配置
│   └── ...
├── docker-compose.yml    # Docker Compose 配置
├── env.example          # 环境变量示例
├── deploy.sh            # Linux/macOS 部署脚本
├── deploy.bat           # Windows 部署脚本
└── .env                 # 环境变量（需自行创建）
```

## 🔐 安全建议

1. **修改 SECRET_KEY**: 生产环境必须使用强随机密钥
2. **使用 HTTPS**: 生产环境建议使用反向代理（如 Nginx）配置 HTTPS
3. **保护 API Keys**: 不要将 `.env` 文件提交到 Git 仓库
4. **限制 CORS**: 在 `.env` 中配置 `CORS_ORIGINS`，只允许信任的域名

## 📚 更多信息

- [API 文档](API.md)
- [快速开始指南](QUICKSTART.md)
- [部署要求](REQUIREMENTS.md)

## ❓ 常见问题

**Q: 如何更新代码后重新部署？**

A: 
```bash
docker compose down
docker compose up -d --build
```

**Q: 如何查看实时日志？**

A:
```bash
docker compose logs -f
```

**Q: 数据会丢失吗？**

A: SQLite 数据库文件存储在 `./backend/data/` 目录，只要不删除该目录，数据不会丢失。

**Q: 如何备份数据？**

A: 复制 `./backend/data/travel_gpt.db` 文件即可。

---

如有问题，欢迎提交 Issue 或联系开发者。
