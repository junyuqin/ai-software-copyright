"""
慧学通 (HuiXueTong) - 学情智能分析信息系统后端主入口
功能：路由定义、CORS 配置、异常处理、健康检查、SQLite3 数据库集成
申报映射：智能信息系统 - 数据分析/策略辅助/内容生成
"""
import os
import json
import sqlite3
import logging
from flask import Flask, request, jsonify, send_from_directory
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
app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
app.config['JSON_AS_ASCII'] = False  # 支持中文 JSON 响应

# 配置 CORS，允许前端跨域访问
CORS(app, origins=os.getenv('CORS_ORIGINS', '*').split(','))

# 数据库路径
DB_PATH = os.getenv('SQLITE_DB_PATH', 'data/huixuetong.db')

# 确保数据目录存在
os.makedirs(os.path.dirname(DB_PATH) if os.path.dirname(DB_PATH) else '.', exist_ok=True)

# 初始化大模型服务
llm_service = LLMService()


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库（如果不存在）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 创建表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            uuid TEXT PRIMARY KEY,
            student_id TEXT,
            name TEXT,
            class TEXT NOT NULL,
            major TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS behavior_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT NOT NULL,
            week INTEGER NOT NULL,
            attendance REAL DEFAULT 0.8,
            quiz_avg REAL DEFAULT 70.0,
            debug_success REAL DEFAULT 0.5,
            project_score REAL DEFAULT 70.0,
            pep8_score REAL DEFAULT 70.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ability_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT NOT NULL,
            week INTEGER NOT NULL,
            knowledge_score REAL DEFAULT 0.0,
            skill_score REAL DEFAULT 0.0,
            literacy_score REAL DEFAULT 0.0,
            diagnosis TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS warning_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT NOT NULL,
            rule_name TEXT NOT NULL,
            priority TEXT DEFAULT 'medium',
            message TEXT,
            status TEXT DEFAULT 'pending',
            triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_uuid_week ON behavior_data(uuid, week)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_profile_uuid_week ON ability_profile(uuid, week)')
    
    conn.commit()
    conn.close()
    logger.info("数据库初始化完成")


@app.route('/')
def index():
    """前端首页"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    用于 Docker 健康检查和系统状态监控
    """
    try:
        # 检查数据库连接
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "ok",
        "database": db_status,
        "version": "1.0.0"
    })


@app.route('/api/profile/<uuid>', methods=['GET'])
def get_profile(uuid):
    """
    获取学生三维能力画像
    参数：uuid - 学生唯一标识（已脱敏）
    返回：知识/技能/素养三维得分及详细信息
    申报映射：多源数据融合与三维画像计算
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询最新一周的行为数据
        cursor.execute('''
            SELECT uuid, week, attendance, quiz_avg, debug_success, project_score, pep8_score
            FROM behavior_data
            WHERE uuid = ?
            ORDER BY week DESC
            LIMIT 1
        ''', (uuid,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # 从数据库获取真实数据
            mock_data = {
                'attendance': float(row['attendance']),
                'quiz_avg': float(row['quiz_avg']),
                'debug_success': float(row['debug_success']),
                'project_score': float(row['project_score']),
                'pep8_score': float(row['pep8_score'])
            }
            week = row['week']
        else:
            # 如果没有数据，使用模拟数据
            mock_data = {
                'attendance': 0.95,
                'quiz_avg': 78.5,
                'debug_success': 0.72,
                'project_score': 85.0,
                'pep8_score': 8.5
            }
            week = 12
        
        # 计算三维得分
        knowledge, skill, literacy = calc_3d_scores(mock_data)
        
        # 返回脱敏后的画像数据
        return jsonify({
            "uuid": hash_student_id(uuid),
            "knowledge_score": round(knowledge, 1),
            "skill_score": round(skill, 1),
            "literacy_score": round(literacy, 1),
            "week": week,
            "class": "计算机应用 2201 班",
            "major": "计算机应用"
        })
    
    except Exception as e:
        logger.error(f"获取画像失败：{str(e)}")
        return jsonify({"error": "获取画像失败", "code": 500}), 500


@app.route('/api/profiles', methods=['GET'])
def get_all_profiles():
    """
    获取所有学生的三维能力画像列表
    返回：班级所有学生的画像摘要
    申报映射：数据可视化/学情看板
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询所有学生的最新画像
        cursor.execute('''
            SELECT ap.uuid, ap.week, ap.knowledge_score, ap.skill_score, ap.literacy_score,
                   s.name, s.class, s.major
            FROM ability_profile ap
            LEFT JOIN students s ON ap.uuid = s.uuid
            WHERE ap.week = (SELECT MAX(week) FROM ability_profile)
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        profiles = []
        for row in rows:
            profiles.append({
                "uuid": row['uuid'],
                "name": row['name'] or '未知',
                "class": row['class'] or '未知班级',
                "major": row['major'] or '未知专业',
                "knowledge_score": round(row['knowledge_score'], 1),
                "skill_score": round(row['skill_score'], 1),
                "literacy_score": round(row['literacy_score'], 1)
            })
        
        return jsonify({
            "profiles": profiles,
            "total": len(profiles)
        })
    
    except Exception as e:
        logger.error(f"获取画像列表失败：{str(e)}")
        return jsonify({"error": "获取画像列表失败", "code": 500}), 500


@app.route('/api/growth/<uuid>', methods=['GET'])
def get_growth_history(uuid):
    """
    获取学生成长轨迹（历史数据）
    参数：uuid - 学生唯一标识
    返回：多周的能力得分变化趋势
    申报映射：数据可视化/成长档案
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询历史画像数据
        cursor.execute('''
            SELECT week, knowledge_score, skill_score, literacy_score
            FROM ability_profile
            WHERE uuid = ?
            ORDER BY week ASC
        ''', (uuid,))
        
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                "week": row['week'],
                "knowledge_score": round(row['knowledge_score'], 1),
                "skill_score": round(row['skill_score'], 1),
                "literacy_score": round(row['literacy_score'], 1)
            })
        
        return jsonify({
            "uuid": hash_student_id(uuid),
            "history": history,
            "total_weeks": len(history)
        })
    
    except Exception as e:
        logger.error(f"获取成长轨迹失败：{str(e)}")
        return jsonify({"error": "获取成长轨迹失败", "code": 500}), 500


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
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询所有预警记录
        cursor.execute('''
            SELECT id, uuid, rule_name, priority, message, status, triggered_at
            FROM warning_records
            ORDER BY 
                CASE priority 
                    WHEN 'high' THEN 1 
                    WHEN 'medium' THEN 2 
                    WHEN 'low' THEN 3 
                    ELSE 4 
                END,
                triggered_at DESC
            LIMIT 50
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        warnings = []
        for row in rows:
            intervention_map = {
                "技能薄弱预警": "推送调试技巧微课",
                "出勤率预警": "通知班主任跟进",
                "知识掌握不足": "推送基础知识点复习材料",
                "素养待提升": "通知任课教师关注学习态度",
                "综合优秀表彰": "推送进阶挑战任务"
            }
            
            warnings.append({
                "id": row['id'],
                "rule_name": row['rule_name'],
                "priority": row['priority'],
                "trigger_time": row['triggered_at'],
                "student_uuid": hash_student_id(row['uuid']),
                "message": row['message'] or f"{row['rule_name']}触发条件满足",
                "intervention": intervention_map.get(row['rule_name'], "人工评估后处理"),
                "status": row['status']
            })
        
        return jsonify({
            "warnings": warnings,
            "total": len(warnings)
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
        
        required_fields = ['warning_id', 'action_type']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"缺少必要参数：{field}", "code": 400}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 插入干预记录
        cursor.execute('''
            INSERT INTO intervention_log (warning_id, action_type, action_detail, operator)
            VALUES (?, ?, ?, ?)
        ''', (
            data['warning_id'],
            data['action_type'],
            data.get('action_detail', ''),
            data.get('operator', 'system')
        ))
        
        # 更新预警状态
        cursor.execute('''
            UPDATE warning_records 
            SET status = 'processed', processed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (data['warning_id'],))
        
        intervention_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            "intervention_id": intervention_id,
            "status": "recorded",
            "timestamp": "2024-01-15T11:00:00+08:00"
        })
    
    except Exception as e:
        logger.error(f"记录干预失败：{str(e)}")
        return jsonify({"error": "记录干预失败", "code": 500}), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    文件上传接口（代码提交、作业上传）
    支持 .py, .js, .html, .css, .json 等文件
    申报映射：多源数据采集
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "未找到上传文件", "code": 400}), 400
        
        file = request.files['file']
        student_uuid = request.form.get('uuid', 'unknown')
        assignment_id = request.form.get('assignment_id', '')
        
        if file.filename == '':
            return jsonify({"error": "文件名为空", "code": 400}), 400
        
        # 检查文件扩展名
        allowed_extensions = {'py', 'js', 'html', 'css', 'json', 'txt', 'md'}
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        
        if ext not in allowed_extensions:
            return jsonify({"error": f"不支持的文件类型：.{ext}", "code": 400}), 400
        
        # 保存文件（实际项目中应保存到对象存储或专门目录）
        upload_dir = os.path.join(os.path.dirname(DB_PATH), 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        safe_filename = f"{hash_student_id(student_uuid)}_{assignment_id}_{file.filename}"
        file_path = os.path.join(upload_dir, safe_filename)
        file.save(file_path)
        
        logger.info(f"文件上传成功：{safe_filename}")
        
        return jsonify({
            "success": True,
            "filename": safe_filename,
            "size": os.path.getsize(file_path),
            "upload_time": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"文件上传失败：{str(e)}")
        return jsonify({"error": "文件上传失败", "code": 500}), 500


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


# 导入 datetime 用于文件上传时间戳
from datetime import datetime

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    
    # 从环境变量获取配置
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    logger.info(f"启动慧学通后端服务：{host}:{port}")
    app.run(host=host, port=port, debug=debug)
