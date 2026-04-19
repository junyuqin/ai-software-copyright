"""
慧学通 (HuiXueTong) - 学情智能分析信息系统后端主入口
功能：路由定义、CORS 配置、异常处理、健康检查
申报映射：智能信息系统 - 数据分析/策略辅助/内容生成
"""
import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from services.llm_service import LLMService
from utils.data_fusion import calc_3d_scores, hash_student_id

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化 Flask 应用
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 支持中文 JSON 响应

# 配置 CORS，允许前端跨域访问
CORS(app, origins=os.getenv('CORS_ORIGINS', '*').split(','))

# 初始化大模型服务
llm_service = LLMService()


@app.route('/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    用于 Docker 健康检查和系统状态监控
    """
    return jsonify({"status": "ok"})


@app.route('/api/profile/<uuid>', methods=['GET'])
def get_profile(uuid):
    """
    获取学生三维能力画像
    参数：uuid - 学生唯一标识（已脱敏）
    返回：知识/技能/素养三维得分
    申报映射：多源数据融合与三维画像计算
    """
    try:
        # 模拟从数据库获取学生行为数据
        # 实际场景中应从 SQLite 查询 behavior_data 表
        mock_data = {
            'attendance': 0.95,      # 出勤率
            'quiz_avg': 78.5,        # 测验平均分
            'debug_success': 0.72,   # 调试成功率
            'project_score': 85.0,   # 项目评分
            'pep8_score': 8.5        # PEP8 规范得分 (0-10)
        }
        
        # 计算三维得分
        knowledge, skill, literacy = calc_3d_scores(mock_data)
        
        # 返回脱敏后的画像数据
        return jsonify({
            "uuid": hash_student_id(uuid),
            "knowledge_score": round(knowledge, 1),
            "skill_score": round(skill, 1),
            "literacy_score": round(literacy, 1),
            "week": 12,
            "class": "计算机应用 2201 班",
            "major": "计算机应用"
        })
    
    except Exception as e:
        logger.error(f"获取画像失败：{str(e)}")
        return jsonify({"error": "获取画像失败", "code": 500}), 500


@app.route('/api/diagnosis', methods=['POST'])
def generate_diagnosis():
    """
    生成 AI 智能诊断报告
    参数：knowledge, skill, literacy - 三维得分
    返回：个性化诊断报告（含优势、薄弱点、建议）
    申报映射：AI 智能诊断与报告生成
    合规要求：末尾必须附加 [AI 辅助生成] 标记
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "请求数据为空", "code": 400}), 400
        
        # 验证必要参数
        required_fields = ['knowledge', 'skill', 'literacy']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"缺少必要参数：{field}", "code": 400}), 400
        
        k_score = float(data['knowledge'])
        s_score = float(data['skill'])
        l_score = float(data['literacy'])
        
        # 调用大模型服务生成诊断报告
        report = llm_service.generate_diagnosis(k_score, s_score, l_score)
        
        return jsonify({
            "report": report,
            "generated_at": "2024-01-15T10:30:00+08:00",
            "model": "文心一言 4.0"
        })
    
    except ValueError as e:
        logger.warning(f"参数类型错误：{str(e)}")
        return jsonify({"error": "参数类型错误", "code": 400}), 400
    except Exception as e:
        logger.error(f"生成诊断报告失败：{str(e)}")
        return jsonify({"error": "生成诊断报告失败", "code": 500}), 500


@app.route('/api/warnings', methods=['GET'])
def get_warnings():
    """
    获取预警列表
    返回：当前触发的预警规则及详情
    申报映射：零代码预警规则引擎
    """
    try:
        # 模拟从数据库获取预警记录
        # 实际场景中应读取 warning_rules.json 并匹配学生数据
        mock_warnings = [
            {
                "id": 1,
                "rule_name": "技能薄弱预警",
                "priority": "high",
                "trigger_time": "2024-01-15T09:00:00+08:00",
                "student_uuid": "a1b2c3d4...",
                "message": "技能得分低于 60 且调试尝试次数超过 8 次",
                "intervention": "推送 Python 调试技巧微课"
            },
            {
                "id": 2,
                "rule_name": "出勤率预警",
                "priority": "medium",
                "trigger_time": "2024-01-14T14:30:00+08:00",
                "student_uuid": "e5f6g7h8...",
                "message": "连续 3 周出勤率低于 80%",
                "intervention": "通知班主任跟进"
            }
        ]
        
        return jsonify({
            "warnings": mock_warnings,
            "total": len(mock_warnings)
        })
    
    except Exception as e:
        logger.error(f"获取预警列表失败：{str(e)}")
        return jsonify({"error": "获取预警列表失败", "code": 500}), 500


@app.route('/api/interventions', methods=['POST'])
def record_intervention():
    """
    记录干预流水
    参数：student_uuid, intervention_type, resource_id, teacher_id
    返回：干预记录 ID
    申报映射：干预闭环与成长档案
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "请求数据为空", "code": 400}), 400
        
        required_fields = ['student_uuid', 'intervention_type']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"缺少必要参数：{field}", "code": 400}), 400
        
        # 模拟写入数据库
        intervention_id = 1001  # 实际应为数据库自增 ID
        
        return jsonify({
            "intervention_id": intervention_id,
            "status": "recorded",
            "timestamp": "2024-01-15T11:00:00+08:00"
        })
    
    except Exception as e:
        logger.error(f"记录干预失败：{str(e)}")
        return jsonify({"error": "记录干预失败", "code": 500}), 500


@app.errorhandler(404)
def not_found(error):
    """全局 404 异常处理"""
    return jsonify({"error": "资源未找到", "code": 404}), 404


@app.errorhandler(500)
def internal_error(error):
    """全局 500 异常处理"""
    return jsonify({"error": "服务器内部错误", "code": 500}), 500


@app.errorhandler(Exception)
def handle_exception(error):
    """全局未捕获异常处理"""
    logger.error(f"未捕获异常：{str(error)}")
    return jsonify({"error": "系统异常", "code": 500}), 500


if __name__ == '__main__':
    # 从环境变量获取配置
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    logger.info(f"启动慧学通后端服务：{host}:{port}")
    app.run(host=host, port=port, debug=debug)
