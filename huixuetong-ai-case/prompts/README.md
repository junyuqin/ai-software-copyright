# 慧学通 Prompt 模板占位

## 说明

本目录用于存放系统使用的 Prompt 模板文件。

### 当前使用的 Prompt

Prompt 已内嵌于 `src/backend/services/llm_service.py` 的 `generate_diagnosis()` 方法中。

**核心约束**:
1. 字数严格控制在 200 字以内
2. 必须包含：①优势分析 ②薄弱点定位 ③2 条可操作学习建议
3. 末尾必须附加标记：[AI 辅助生成]

### 未来扩展

如需维护独立 Prompt 模板文件，可按以下格式添加：

- `diagnosis_template.txt` - 诊断报告生成模板
- `recommendation_template.txt` - 资源推荐模板
- `warning_template.txt` - 预警通知模板

---

**注意**: Prompt 设计需符合《生成式人工智能服务管理暂行办法》要求，确保输出内容安全可控。
