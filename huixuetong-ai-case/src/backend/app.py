"""
慧学通 (HuiXueTong) - 学情智能分析信息系统后端主入口
功能：路由定义、CORS配置、全局异常处理、健康检查
申报映射：智能信息系统 - 数据分析/策略辅助/内容生成
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from services.llm_service import LLMService
from utils.data_fusion import calc_3d_scores, hash_student_id

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'deploy', '.env'))

app = Flask(__name__)

# 配置CORS，允许前端跨域访问
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 初始化大模型服务
llm_service = LLMService()


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口，用于Docker健康检测"""
    return jsonify({"status": "ok"})


@app.route('/api/profile/<uuid>', methods=['GET'])
def get_profile(uuid):
    """
    获取学生三维能力画像
    输入：学生UUID（已脱敏）
    输出：知识/技能/素养三维得分
    申报映射：多源数据融合与三维画像计算
    """
    try:
        # 模拟从数据库获取行为数据（实际应从behavior_data表查询）
        mock_data = {
            "quiz_avg": 75.0,
            "attendance": 0.9,
            "debug_success": 0.65,
            "project_score": 80.0,
            "pep8_score": 85.0
        }
        
        # 计算三维得分
        knowledge, skill, literacy = calc_3d_scores(mock_data)
        
        return jsonify({
            "uuid": uuid,
            "knowledge_score": round(knowledge, 1),
            "skill_score": round(skill, 1),
            "literacy_score": round(literacy, 1)
        })
    except Exception as e:
        app.logger.error(f"获取画像失败: {str(e)}")
        return jsonify({"error": "画像计算失败", "code": 500}), 500


@app.route('/api/diagnosis', methods=['POST'])
def generate_diagnosis():
    """
    生成AI诊断报告
    输入：{knowledge_score, skill_score, literacy_score}
    输出：≤200字个性化诊断报告（含[AI辅助生成]标记）
    申报映射：AI智能诊断与报告生成
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "请求数据为空", "code": 400}), 400
        
        k_score = data.get('knowledge_score', 0)
        s_score = data.get('skill_score', 0)
        l_score = data.get('literacy_score', 0)
        
        # 调用大模型服务生成诊断报告
        report = llm_service.generate_diagnosis(k_score, s_score, l_score)
        
        return jsonify({
            "diagnosis": report,
            "ai_marked": True
        })
    except Exception as e:
        app.logger.error(f"生成诊断报告失败: {str(e)}")
        return jsonify({"error": "诊断报告生成失败", "code": 500}), 500


@app.route('/api/warnings', methods=['GET'])
def get_warnings():
    """
    获取预警列表
    输出：模拟预警记录（规则名、优先级、触发时间）
    申报映射：零代码预警规则引擎
    """
    try:
        # 模拟预警数据（实际应从预警记录表查询）
        warnings = [
            {
                "rule_name": "技能薄弱预警",
                "priority": "high",
                "trigger_time": "2025-01-15 10:30:00",
                "student_uuid": "a1b2c3d4...",
                "message": "skill_score < 60 AND debug_attempts > 8"
            },
            {
                "rule_name": "素养待提升",
                "priority": "medium",
                "trigger_time": "2025-01-15 09:15:00",
                "student_uuid": "e5f6g7h8...",
                "message": "literacy_score < 65"
            }
        ]
        return jsonify({"warnings": warnings})
    except Exception as e:
        app.logger.error(f"获取预警列表失败: {str(e)}")
        return jsonify({"error": "预警列表获取失败", "code": 500}), 500


@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({"error": "资源未找到", "code": 404}), 404


@app.errorhandler(500)
def internal_error(error):
    """500错误处理，禁止裸奔"""
    return jsonify({"error": "服务器内部错误", "code": 500}), 500


if __name__ == '__main__':
    # 从环境变量获取端口，默认5000
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
