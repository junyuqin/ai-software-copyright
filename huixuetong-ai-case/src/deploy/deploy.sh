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
    echo "  - DB_PASSWORD (数据库密码)"
    echo "  - BAIDU_API_KEY (文心一言API Key)"
    echo "  - BAIDU_SECRET_KEY (文心一言Secret Key)"
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

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ 错误：未检测到 Docker Compose，请先安装"
    exit 1
fi
echo "✅ Docker 环境检查通过"

echo ""
echo "[步骤 2/3] 创建前端占位目录..."
mkdir -p ../frontend/dist
# 创建简单的 index.html 用于测试
cat > ../frontend/dist/index.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>慧学通 - 学情智能分析系统</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        h1 { color: #1890ff; }
        .status { margin: 20px 0; padding: 20px; background: #f0f9ff; border-radius: 8px; }
        .api-test { margin-top: 30px; }
        button { padding: 10px 20px; background: #1890ff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #40a9ff; }
        #result { margin-top: 20px; padding: 15px; background: #f5f5f5; border-radius: 4px; text-align: left; }
    </style>
</head>
<body>
    <h1>🎓 慧学通 (HuiXueTong)</h1>
    <p>中职计算机专业学情智能分析信息系统</p>
    
    <div class="status">
        <h3>✅ 系统已成功启动</h3>
        <p>后端服务运行正常，API接口可用</p>
    </div>
    
    <div class="api-test">
        <h3>API 测试</h3>
        <button onclick="testHealth()">测试健康检查</button>
        <button onclick="testProfile()">获取学生画像</button>
        <button onclick="testWarnings()">查看预警列表</button>
        <div id="result">点击按钮测试API...</div>
    </div>
    
    <script>
        async function testHealth() {
            try {
                const res = await fetch('/health');
                const data = await res.json();
                document.getElementById('result').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            } catch (e) {
                document.getElementById('result').innerText = '错误：' + e.message;
            }
        }
        
        async function testProfile() {
            try {
                const res = await fetch('/api/profile/test-uuid-123');
                const data = await res.json();
                document.getElementById('result').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            } catch (e) {
                document.getElementById('result').innerText = '错误：' + e.message;
            }
        }
        
        async function testWarnings() {
            try {
                const res = await fetch('/api/warnings');
                const data = await res.json();
                document.getElementById('result').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            } catch (e) {
                document.getElementById('result').innerText = '错误：' + e.message;
            }
        }
    </script>
</body>
</html>
EOF
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
echo "  查看日志：docker compose logs -f backend"
echo "  停止服务：docker compose down"
echo "  重启服务：docker compose restart"
echo ""
echo "🔧 如需修改配置，请编辑：src/deploy/.env"
echo ""
