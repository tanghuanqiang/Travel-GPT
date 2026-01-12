# Travel-GPT Docker 部署故障排查指南

## 快速排查步骤

### 1. 查看容器状态

```bash
docker compose ps
```

### 2. 查看后端容器日志

```bash
# 查看所有日志
docker compose logs backend

# 查看最近50行日志
docker compose logs --tail=50 backend

# 实时查看日志
docker compose logs -f backend
```

### 3. 查看前端容器日志

```bash
docker compose logs frontend
```

### 4. 检查容器是否正在运行

```bash
docker ps -a | grep travel-gpt
```

### 5. 尝试手动启动容器

```bash
# 停止所有容器
docker compose down

# 重新启动
docker compose up -d

# 或者前台运行查看详细输出
docker compose up
```

## 常见问题及解决方案

### 问题1: 后端容器启动失败

**可能原因：**
- 环境变量未配置（特别是 `SECRET_KEY`）
- 端口被占用
- 数据库连接失败
- 依赖包安装失败

**解决方案：**

1. **检查环境变量**
   ```bash
   # 确保 .env 文件存在
   ls -la .env
   
   # 检查必需的环境变量
   cat .env | grep SECRET_KEY
   cat .env | grep LLM_PROVIDER
   ```

2. **检查端口占用**
   ```bash
   # Linux/macOS
   lsof -i :18890
   
   # Windows
   netstat -ano | findstr :18890
   ```

3. **查看详细错误信息**
   ```bash
   docker compose logs backend --tail=100
   ```

4. **进入容器调试**
   ```bash
   docker compose exec backend sh
   # 或
   docker run -it --rm travel-gpt-backend sh
   ```

### 问题2: 前端容器启动失败

**可能原因：**
- Next.js 构建失败
- 端口被占用
- 环境变量配置错误

**解决方案：**

1. **检查构建日志**
   ```bash
   docker compose logs frontend | grep -i error
   ```

2. **重新构建前端**
   ```bash
   docker compose build --no-cache frontend
   docker compose up -d frontend
   ```

### 问题3: 容器健康检查失败

**可能原因：**
- 后端服务未正常启动
- 健康检查端点不可用
- 网络配置问题

**解决方案：**

1. **临时禁用健康检查（用于调试）**
   编辑 `docker-compose.yml`，注释掉 `healthcheck` 部分

2. **检查服务是否响应**
   ```bash
   # 进入容器
   docker compose exec backend sh
   
   # 测试健康检查端点
   curl http://localhost:8000/api/health
   ```

### 问题4: 数据库连接问题

**可能原因：**
- SQLite 数据库文件权限问题
- 数据目录不存在

**解决方案：**

1. **检查数据目录**
   ```bash
   ls -la backend/data/
   ```

2. **修复权限**
   ```bash
   # Linux/macOS
   chmod -R 755 backend/data
   
   # Windows (PowerShell)
   icacls backend\data /grant Everyone:F
   ```

3. **重新创建数据目录**
   ```bash
   rm -rf backend/data
   mkdir -p backend/data
   ```

### 问题5: 网络连接问题

**可能原因：**
- 容器间网络不通
- CORS 配置错误

**解决方案：**

1. **检查网络**
   ```bash
   docker network ls
   docker network inspect travel-gpt_travel-gpt-network
   ```

2. **测试容器间连接**
   ```bash
   docker compose exec frontend ping backend
   ```

## 调试命令集合

```bash
# 查看所有容器状态
docker compose ps -a

# 查看所有服务日志
docker compose logs

# 查看特定服务的日志（最后100行）
docker compose logs --tail=100 backend
docker compose logs --tail=100 frontend

# 重启服务
docker compose restart backend
docker compose restart frontend

# 停止所有服务
docker compose down

# 停止并删除数据卷
docker compose down -v

# 重新构建并启动
docker compose up -d --build

# 进入容器
docker compose exec backend sh
docker compose exec frontend sh

# 查看容器资源使用
docker stats

# 清理未使用的资源
docker system prune -a
```

## 环境变量检查清单

确保 `.env` 文件中至少配置了：

- [ ] `SECRET_KEY` - JWT 密钥（必须）
- [ ] `LLM_PROVIDER` - LLM 提供商（nvidia/dashscope/ollama）
- [ ] `NVIDIA_API_KEY` 或 `DASHSCOPE_API_KEY` - 根据 LLM_PROVIDER 配置
- [ ] `BACKEND_PORT` - 后端端口（默认 18890）
- [ ] `FRONTEND_PORT` - 前端端口（默认 18891）
- [ ] `NEXT_PUBLIC_API_URL` - 前端 API 地址

## 获取帮助

如果以上方法都无法解决问题，请提供以下信息：

1. `docker compose ps -a` 的输出
2. `docker compose logs backend` 的完整输出
3. `docker compose logs frontend` 的完整输出
4. `.env` 文件内容（隐藏敏感信息）
5. 操作系统和 Docker 版本
