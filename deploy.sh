#!/bin/bash

# Travel-GPT Docker Compose 一键部署脚本
# 适用于 Linux/macOS

set -e

echo "=========================================="
echo "🚀 Travel-GPT Docker Compose 部署脚本"
echo "=========================================="
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误：未检测到 Docker，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ 错误：未检测到 Docker Compose，请先安装 Docker Compose"
    exit 1
fi

# 检查 .env 文件是否存在
if [ ! -f .env ]; then
    echo "📝 未找到 .env 文件，正在从 .env.example 创建..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件，填入必需的配置（特别是 SECRET_KEY 和 LLM API密钥）"
    echo "⚠️  按 Enter 继续，或按 Ctrl+C 取消..."
    read
fi

# 检查必需的环境变量
if grep -q "your-super-secret-key" .env || grep -q "your-nvidia-api-key" .env; then
    echo "⚠️  警告：.env 文件中仍包含示例值，请确保已填入实际配置"
    echo "⚠️  按 Enter 继续，或按 Ctrl+C 取消..."
    read
fi

echo "🔨 开始构建和启动服务..."
echo ""

# 使用 docker-compose 或 docker compose（取决于版本）
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

# 构建并启动服务
$COMPOSE_CMD up -d --build

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "📍 访问地址："
echo "   - 前端：http://localhost:18891"
echo "   - 后端API：http://localhost:18890"
echo "   - API文档：http://localhost:18890/docs"
echo ""
echo "📋 常用命令："
echo "   - 查看日志：$COMPOSE_CMD logs -f"
echo "   - 停止服务：$COMPOSE_CMD down"
echo "   - 重启服务：$COMPOSE_CMD restart"
echo "   - 查看状态：$COMPOSE_CMD ps"
echo ""
echo "⚠️  注意：确保端口 18890 和 18891 未被占用"
echo ""
