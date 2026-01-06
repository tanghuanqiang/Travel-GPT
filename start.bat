@echo off
REM TravelPlanGPT 启动脚本 (Windows)

echo 🚀 启动 TravelPlanGPT...

REM 检查目录
if not exist "frontend" (
    echo ❌ 请在项目根目录运行此脚本
    exit /b 1
)

REM 启动后端
echo 📡 启动后端服务...
cd backend

REM 激活 conda travel 环境
call conda activate travel

REM 安装依赖（如果需要）
pip install -r requirements.txt -q

if not exist ".env" (
    echo ⚠️  未找到 .env 文件，从 .env.example 复制...
    copy .env.example .env
    echo 请编辑 backend\.env 文件，填入你的 API Keys
    pause
)

start "Backend" cmd /k "conda activate travel && python main.py"
cd ..

REM 启动前端
echo 🎨 启动前端服务...
cd frontend

if not exist "node_modules" (
    echo 安装依赖...
    call npm install
)

start "Frontend" cmd /k npm run dev
cd ..

echo.
echo ✅ 启动成功！
echo 前端: http://localhost:3000
echo 后端: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.
pause
