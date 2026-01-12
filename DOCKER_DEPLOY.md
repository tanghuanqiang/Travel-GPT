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

**本地访问：**
- **前端应用**: http://localhost:18891
- **后端API**: http://localhost:18890
- **API文档**: http://localhost:18890/docs

**服务器访问（使用IP）：**
- **前端应用**: http://YOUR_SERVER_IP:18891
- **后端API**: http://YOUR_SERVER_IP:18890
- **API文档**: http://YOUR_SERVER_IP:18890/docs

⚠️ **重要：使用 IP 访问时，必须配置 CORS 和 API URL（见下方）**

## 🔧 端口配置

为了避免与 Daily-News 项目冲突，Travel-GPT 使用以下端口：

| 服务 | Travel-GPT | Daily-News |
|------|------------|------------|
| 后端 | 18890 | 18888 |
| 前端 | 18891 | 18889 |

如需修改端口，请编辑 `.env` 文件中的 `BACKEND_PORT` 和 `FRONTEND_PORT`。

## 🌐 使用 IP 地址访问配置

如果通过 IP 地址访问（而非域名），需要配置以下环境变量：

### 1. 配置 CORS_ORIGINS

在 `.env` 文件中，将 `CORS_ORIGINS` 设置为包含服务器 IP 地址：

```env
# 替换 YOUR_SERVER_IP 为实际服务器 IP
CORS_ORIGINS=http://YOUR_SERVER_IP:18891,http://localhost:18891,http://127.0.0.1:18891
```

**示例：**
```env
# 如果服务器 IP 是 192.168.1.100
CORS_ORIGINS=http://192.168.1.100:18891,http://localhost:18891,http://127.0.0.1:18891
```

### 2. 配置 NEXT_PUBLIC_API_URL

在 `.env` 文件中，将 `NEXT_PUBLIC_API_URL` 设置为后端 API 的完整地址：

```env
# 替换 YOUR_SERVER_IP 为实际服务器 IP
NEXT_PUBLIC_API_URL=http://YOUR_SERVER_IP:18890
```

**示例：**
```env
# 如果服务器 IP 是 192.168.1.100
NEXT_PUBLIC_API_URL=http://192.168.1.100:18890
```

### 3. 重新构建和启动

配置完成后，需要重新构建前端（因为 `NEXT_PUBLIC_API_URL` 在构建时注入）：

```bash
# 停止服务
docker compose down

# 重新构建前端（不使用缓存）
docker compose build --no-cache frontend

# 启动服务
docker compose up -d

# 查看日志
docker compose logs -f
```

### 4. 验证配置

访问前端后，打开浏览器开发者工具（F12），检查：
- **Network 标签**：API 请求应该指向正确的后端地址
- **Console 标签**：不应该有 CORS 错误

### 使用域名访问

如果使用域名访问，配置方式相同，只需将 IP 替换为域名：

```env
# 使用域名
CORS_ORIGINS=http://yourdomain.com:18891,https://yourdomain.com
NEXT_PUBLIC_API_URL=http://yourdomain.com:18890
```

**注意：** 使用 HTTPS 时，确保后端也支持 HTTPS 或配置反向代理。

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

### 3. 前端无法连接后端 / CORS 错误

**错误信息：** `strict-origin-when-cross-origin` 或 `CORS policy` 相关错误

**原因：** 使用 IP 地址访问时，CORS 配置未包含服务器 IP

**解决方案：**

1. **检查当前配置**
   ```bash
   cat .env | grep CORS_ORIGINS
   cat .env | grep NEXT_PUBLIC_API_URL
   ```

2. **更新 `.env` 文件**
   ```env
   # 替换 YOUR_SERVER_IP 为实际服务器 IP（例如：192.168.1.100）
   CORS_ORIGINS=http://YOUR_SERVER_IP:18891,http://localhost:18891,http://127.0.0.1:18891
   NEXT_PUBLIC_API_URL=http://YOUR_SERVER_IP:18890
   ```

3. **重新构建前端**
   ```bash
   docker compose down
   docker compose build --no-cache frontend
   docker compose up -d
   ```

4. **验证配置**
   - 访问前端：`http://YOUR_SERVER_IP:18891`
   - 打开浏览器开发者工具（F12）
   - 检查 Network 标签，API 请求应该成功
   - 检查 Console 标签，不应该有 CORS 错误

**其他检查：**
- 确保后端服务正常运行：`docker compose logs backend`
- 确保端口未被防火墙阻止
- 如果使用域名，确保 DNS 解析正确

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
