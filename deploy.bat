@echo off
REM Travel-GPT Docker Compose 一键部署脚本
REM 适用于 Windows

echo ==========================================
echo 🚀 Travel-GPT Docker Compose 部署脚本
echo ==========================================
echo.

REM 检查 Docker 是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未检测到 Docker，请先安装 Docker Desktop
    pause
    exit /b 1
)

REM 检查 Docker Compose 是否可用
docker compose version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：Docker Compose 不可用，请确保 Docker Desktop 已启动
    pause
    exit /b 1
)

REM 检查 .env 文件是否存在
if not exist .env (
    echo 📝 未找到 .env 文件，正在从 .env.example 创建...
    copy .env.example .env
    echo ⚠️  请编辑 .env 文件，填入必需的配置（特别是 SECRET_KEY 和 LLM API密钥）
    echo ⚠️  按任意键继续...
    pause >nul
)

REM 检查必需的环境变量（简单检查）
findstr /C:"your-super-secret-key" .env >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  警告：.env 文件中仍包含示例值，请确保已填入实际配置
    echo ⚠️  按任意键继续...
    pause >nul
)

echo 🔨 开始构建和启动服务...
echo.

REM 构建并启动服务
docker compose up -d --build

echo.
echo ==========================================
echo ✅ 部署完成！
echo ==========================================
echo.
echo 📍 访问地址：
echo    - 前端：http://localhost:18891
echo    - 后端API：http://localhost:18890
echo    - API文档：http://localhost:18890/docs
echo.
echo 📋 常用命令：
echo    - 查看日志：docker compose logs -f
echo    - 停止服务：docker compose down
echo    - 重启服务：docker compose restart
echo    - 查看状态：docker compose ps
echo.
echo ⚠️  注意：确保端口 18890 和 18891 未被占用
echo.

pause
