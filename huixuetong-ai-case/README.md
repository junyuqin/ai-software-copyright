# 慧学通 (HuiXueTong)

**中职计算机专业学情智能分析信息系统**

---

## 📖 项目简介

慧学通是一款面向中等职业教育计算机类专业的学情智能分析信息系统，接入国产大模型（文心一言 4.0），融合多源学习行为数据，自动构建学生"知识 - 技能 - 素养"三维能力画像，提供智能预警、AI 诊断报告生成、个性化资源推荐与数据可视化看板。

### 解决的三大痛点

| 痛点 | 传统方式 | 慧学通方案 |
|------|----------|------------|
| **数据碎片化** | 签到、测验、代码提交分散在不同平台 | 多源数据融合，统一画像计算 |
| **反馈滞后** | 教师逐一批改 40+ 份代码耗时超 3 小时 | AI 实时诊断，秒级生成报告 |
| **评价单一** | 重"运行结果"轻"调试过程" | 三维能力评价，过程性数据支撑 |

### 申报类别

**创 AI 案例征集指南 - 智能信息系统**

符合技术规范：数据分析、可视化、推理预测、策略辅助、内容生成

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端 (Nginx + HTML5)                  │
│                   健康检查 | API 测试 | 功能展示              │
└─────────────────────────────────────────────────────────────┘
                              ↓ HTTP/REST API
┌─────────────────────────────────────────────────────────────┐
│                     后端 (Flask 3.0 + SQLite3)               │
│  /api/profile  → 三维画像计算                               │
│  /api/diagnosis → AI 诊断报告生成 (文心一言 4.0)              │
│  /api/warnings  → 预警规则引擎                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   数据层 (SQLite3)                           │
│   students | behavior_data | ability_profile | warnings     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速部署（30 分钟 MVP 跑通）

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- Git

### 一键部署步骤

```bash
# 1. 进入部署目录
cd /workspace/huixuetong-ai-case/src/deploy

# 2. 运行部署脚本
chmod +x deploy.sh
./deploy.sh

# 3. 按提示编辑 .env 文件
# 可选配置：BAIDU_API_KEY, BAIDU_SECRET_KEY
# 注：如仅测试基础功能，可不配置 AI 密钥（将返回降级提示）

# 4. 重新运行部署脚本
./deploy.sh
```

### 访问地址

- **前端界面**: http://localhost
- **健康检查**: http://localhost/health
- **API 测试**: 点击前端页面按钮测试

---

## 📁 目录结构

```
huixuetong-ai-case/
├── src/
│   ├── backend/
│   │   ├── app.py                  # Flask 主入口
│   │   ├── requirements.txt        # Python 依赖
│   │   ├── Dockerfile              # 后端容器镜像
│   │   ├── config/
│   │   │   └── __init__.py         # 配置管理 (SQLite3)
│   │   ├── services/
│   │   │   └── llm_service.py      # 文心一言服务
│   │   └── utils/
│   │       └── data_fusion.py      # 数据融合工具
│   ├── frontend/
│   │   └── dist/
│   │       └── index.html          # 前端占位页面
│   └── deploy/
│       ├── docker-compose.yml      # Docker 编排 (SQLite3)
│       ├── .env.example            # 环境变量模板
│       ├── init.sql                # SQLite 初始化脚本
│       ├── nginx.conf              # Nginx 配置
│       └── deploy.sh               # 一键部署脚本
├── data/
│   └── warning_rules.json          # 预警规则模板
├── docs/                           # 申报文档占位
├── prompts/                        # Prompt 模板占位
└── README.md                       # 本文件
```

---

## 🔌 API 接口说明

### 1. 健康检查

```http
GET /health
```

**响应示例**:
```json
{"status": "ok"}
```

### 2. 获取学生三维画像

```http
GET /api/profile/{uuid}
```

**响应示例**:
```json
{
  "uuid": "a1b2c3d4e5f6g7h8",
  "knowledge_score": 78.5,
  "skill_score": 72.0,
  "literacy_score": 81.3,
  "week": 12,
  "class": "计算机应用 2201 班",
  "major": "计算机应用"
}
```

### 3. 生成 AI 诊断报告

```http
POST /api/diagnosis
Content-Type: application/json

{
  "knowledge": 78.5,
  "skill": 72.0,
  "literacy": 81.3
}
```

**响应示例**:
```json
{
  "report": "优势：素养维度表现优秀...[AI 辅助生成]",
  "generated_at": "2024-01-15T10:30:00+08:00",
  "model": "文心一言 4.0"
}
```

### 4. 获取预警列表

```http
GET /api/warnings
```

**响应示例**:
```json
{
  "warnings": [
    {
      "rule_name": "技能薄弱预警",
      "priority": "high",
      "trigger_time": "2024-01-15 10:30:00",
      "message": "skill_score < 60 AND debug_attempts > 8"
    }
  ],
  "total": 1
}
```

---

## 🔒 安全与合规

### 数据安全

- ✅ 所有学生标识经 SHA-256 哈希脱敏后存储
- ✅ 敏感配置通过环境变量注入，禁止硬编码
- ✅ `.env` 文件已加入 `.gitignore`

### AI 合规

- ✅ 所有大模型输出强制携带 `[AI 辅助生成]` 标记
- ✅ 符合《生成式人工智能服务管理暂行办法》第 12 条
- ✅ 支持优雅降级（API 不可用时返回友好提示）

### 代码规范

- ✅ PEP 8 代码风格
- ✅ RESTful API 设计
- ✅ 完整中文 Docstring 注释

---

## 📊 核心功能模块

| 模块 | 功能描述 | 申报指标 |
|------|----------|----------|
| **① 多源数据融合** | 自动采集签到/测验/代码提交等数据，计算三维得分 | 有效性/数据分析 |
| **② AI 智能诊断** | 调用文心一言生成≤200 字诊断报告 | AI 赋能/内容生成 |
| **③ 零代码预警** | JSON 配置阈值规则，自动触发分级干预 | 策略辅助/操作简单 |
| **④ 数据可视化** | ECharts 渲染雷达图/折线图/热力图 | 数据可视化/真实落地 |
| **⑤ 干预闭环** | 记录全流程，生成数字成长档案 | 实用性/影响力 |

---

## 🧪 测试验证

```bash
# 查看服务状态
docker compose ps

# 查看后端日志
docker compose logs -f backend

# 测试 API
curl http://localhost/health
curl http://localhost/api/profile/test-uuid-123
curl http://localhost/api/warnings
```

---

## 📝 环境变量配置

| 变量名 | 说明 | 必填 |
|--------|------|------|
| `BAIDU_API_KEY` | 文心一言 API Key | 可选* |
| `BAIDU_SECRET_KEY` | 文心一言 Secret Key | 可选* |
| `FLASK_DEBUG` | Flask 调试模式 (true/false) | ❌ |
| `SECRET_KEY` | Flask 密钥 | ❌ |

*注：不配置 AI 密钥时，诊断接口将返回降级提示，不影响其他功能测试

---

## 🔄 变更说明

### SQLite3 版本更新

- 数据库从 MySQL 8.0 改为 SQLite3，简化部署流程
- 无需额外数据库服务，开箱即用
- 保留完整的数据模型和查询接口
- 适合演示、测试和小规模部署场景

---

## 📄 开源协议

MIT License

---

## 👥 开发团队

慧学通项目组 - 中职教育数字化转型实践

---

## 📞 技术支持

如有问题，请提交 Issue 或联系项目维护者。
