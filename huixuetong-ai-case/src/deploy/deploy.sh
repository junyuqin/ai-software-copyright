#!/bin/bash
# 慧学通一键部署脚本
# 功能：环境检查、配置初始化、服务启动
# 申报映射：操作简单易用/可复现

set -e

echo "=========================================="
echo "  慧学通 (HuiXueTong) 一键部署脚本"
echo "=========================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查 .env 文件是否存在
if [ ! -f ".env" ]; then
    echo "[提示] 未找到 .env 配置文件，正在从模板复制..."
    cp .env.example .env
    echo ""
    echo "=========================================="
    echo "  ⚠️  请编辑 src/deploy/.env 文件"
    echo "  必须配置以下变量："
    echo "  - BAIDU_API_KEY (文心一言 API Key)"
    echo "  - BAIDU_SECRET_KEY (文心一言 Secret Key)"
    echo "  注：如仅测试基础功能，可不配置 AI 密钥（将返回降级提示）"
    echo "=========================================="
    echo ""
    echo "修改完成后，请重新运行此脚本。"
    exit 1
fi

echo "[步骤 1/3] 检查 Docker 环境..."
if ! command -v docker &> /dev/null; then
    echo "❌ 错误：未检测到 Docker，请先安装 Docker"
    exit 1
fi

if ! docker compose version &> /dev/null && ! docker-compose version &> /dev/null; then
    echo "❌ 错误：未检测到 Docker Compose，请先安装"
    exit 1
fi
echo "✅ Docker 环境检查通过"

echo ""
echo "[步骤 2/3] 创建前端占位目录..."
mkdir -p ../frontend/dist

# 如果没有 index.html，创建简单的占位页面
if [ ! -f "../frontend/dist/index.html" ]; then
cat > ../frontend/dist/index.html << 'HTMLEOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>慧学通</title>
    <style>body{font-family:Arial;text-align:center;padding:50px}h1{color:#1890ff}</style>
</head>
<body>
    <h1>🎓 慧学通 (HuiXueTong)</h1>
    <p>系统已启动，API 接口可用</p>
    <p><a href="/health">健康检查</a> | <a href="/api/profile/test">学生画像</a> | <a href="/api/warnings">预警列表</a></p>
</body>
</html>
HTMLEOF
fi
echo "✅ 前端占位页面已创建"

echo ""
echo "[步骤 3/3] 启动 Docker 服务..."
# 兼容 docker compose 和 docker-compose
if docker compose version &> /dev/null; then
    docker compose up -d --build
else
    docker-compose up -d --build
fi

echo ""
echo "=========================================="
echo "  🎉 部署完成！"
echo "=========================================="
echo ""
echo "📍 访问地址：http://localhost"
echo ""
echo "📋 常用命令："
if docker compose version &> /dev/null; then
    echo "  查看日志：docker compose logs -f backend"
    echo "  停止服务：docker compose down"
    echo "  重启服务：docker compose restart"
else
    echo "  查看日志：docker-compose logs -f backend"
    echo "  停止服务：docker-compose down"
    echo "  重启服务：docker-compose restart"
fi
echo ""
echo "🔧 如需修改配置，请编辑：src/deploy/.env"
echo ""
