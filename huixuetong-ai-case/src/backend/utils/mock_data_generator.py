"""
慧学通 (HuiXueTong) - 模拟数据生成器
功能：生成学生信息、行为数据、能力画像等测试数据
用途：系统演示、功能测试、开发调试
"""

import sqlite3
import random
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict


# 示例班级和专业
CLASSES = [
    "2023 级计算机应用 1 班",
    "2023 级计算机应用 2 班",
    "2023 级计算机网络 1 班",
    "2023 级软件技术 1 班",
    "2023 级数字媒体 1 班"
]

MAJORS = [
    "计算机应用",
    "计算机网络技术",
    "软件技术",
    "数字媒体技术应用",
    "物联网技术应用"
]

# 常见中文姓名
FIRST_NAMES = ["张", "王", "李", "赵", "刘", "陈", "杨", "黄", "周", "吴", "徐", "孙", "马", "朱", "胡"]
LAST_NAMES = ["伟", "芳", "娜", "敏", "静", "丽", "强", "磊", "军", "洋", "勇", "艳", "杰", "涛", "明"]


def generate_student_id(index: int) -> str:
    """生成学生 ID"""
    return f"STU{20230000 + index:08d}"


def hash_student_id(uid: str) -> str:
    """SHA-256 哈希脱敏"""
    hash_obj = hashlib.sha256(uid.encode('utf-8'))
    return hash_obj.hexdigest()[:16]


def generate_students(count: int = 30) -> List[Dict]:
    """生成学生信息列表"""
    students = []
    for i in range(count):
        student_id = generate_student_id(i)
        uuid = hash_student_id(student_id)
        name = random.choice(FIRST_NAMES) + random.choice(LAST_NAMES)
        cls = random.choice(CLASSES)
        major = random.choice(MAJORS)
        
        students.append({
            "student_id": student_id,
            "uuid": uuid,
            "name": name,
            "class": cls,
            "major": major
        })
    
    return students


def generate_behavior_data(uuid: str, weeks: int = 12) -> List[Dict]:
    """
    生成学生行为数据（多周）
    模拟真实学习场景：成绩有波动，逐步提升或下降
    """
    data_list = []
    
    # 基础水平（每个学生不同）
    base_quiz = random.uniform(60, 90)
    base_attendance = random.uniform(0.7, 1.0)
    base_debug = random.uniform(0.4, 0.9)
    base_project = random.uniform(65, 95)
    base_pep8 = random.uniform(60, 95)
    
    # 趋势（+表示进步，-表示退步）
    trend_quiz = random.uniform(-0.5, 0.8)
    trend_attendance = random.uniform(-0.02, 0.02)
    trend_debug = random.uniform(-0.01, 0.02)
    
    for week in range(1, weeks + 1):
        # 添加随机波动
        quiz_avg = max(0, min(100, base_quiz + trend_quiz * week + random.uniform(-5, 5)))
        attendance = max(0, min(1, base_attendance + trend_attendance * week + random.uniform(-0.05, 0.05)))
        debug_success = max(0, min(1, base_debug + trend_debug * week + random.uniform(-0.05, 0.05)))
        project_score = max(0, min(100, base_project + random.uniform(-3, 3)))
        pep8_score = max(0, min(100, base_pep8 + random.uniform(-2, 2)))
        
        data_list.append({
            "uuid": uuid,
            "week": week,
            "attendance": round(attendance, 2),
            "quiz_avg": round(quiz_avg, 1),
            "debug_success": round(debug_success, 2),
            "project_score": round(project_score, 1),
            "pep8_score": round(pep8_score, 1)
        })
    
    return data_list


def calc_3d_scores(data: Dict) -> tuple:
    """计算三维能力得分"""
    quiz_avg = data.get('quiz_avg', 70.0)
    attendance = data.get('attendance', 0.8)
    debug_success = data.get('debug_success', 0.5)
    project_score = data.get('project_score', 70.0)
    pep8_score = data.get('pep8_score', 70.0)
    
    knowledge = 0.5 * quiz_avg + 0.3 * attendance * 100 + 12
    skill = 0.6 * debug_success * 100 + 0.4 * project_score
    literacy = 0.4 * attendance * 100 + 0.3 * pep8_score * 10 + 15
    
    knowledge = max(0, min(100, knowledge))
    skill = max(0, min(100, skill))
    literacy = max(0, min(100, literacy))
    
    return (round(knowledge, 1), round(skill, 1), round(literacy, 1))


def init_database(db_path: str):
    """初始化 SQLite 数据库"""
    conn = sqlite3.connect(db_path)
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (uuid) REFERENCES students(uuid) ON DELETE CASCADE
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (uuid) REFERENCES students(uuid) ON DELETE CASCADE
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
            triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP,
            FOREIGN KEY (uuid) REFERENCES students(uuid) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS intervention_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            warning_id INTEGER NOT NULL,
            action_type TEXT NOT NULL,
            action_detail TEXT,
            operator TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (warning_id) REFERENCES warning_records(id) ON DELETE CASCADE
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_uuid_week ON behavior_data(uuid, week)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_profile_uuid_week ON ability_profile(uuid, week)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_status_triggered ON warning_records(status, triggered_at)')
    
    conn.commit()
    return conn


def populate_mock_data(db_path: str, student_count: int = 30, weeks: int = 12):
    """填充模拟数据到数据库"""
    print(f"正在初始化数据库：{db_path}")
    
    conn = init_database(db_path)
    cursor = conn.cursor()
    
    # 检查是否已有数据
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] > 0:
        print("数据库中已有数据，跳过初始化")
        conn.close()
        return
    
    # 生成学生
    students = generate_students(student_count)
    print(f"生成 {len(students)} 名学生信息...")
    
    for student in students:
        cursor.execute('''
            INSERT INTO students (uuid, student_id, name, class, major)
            VALUES (?, ?, ?, ?, ?)
        ''', (student['uuid'], student['student_id'], student['name'], 
              student['class'], student['major']))
    
    # 生成行为数据
    print(f"生成 {weeks} 周的行为数据...")
    total_records = 0
    for student in students:
        behavior_data = generate_behavior_data(student['uuid'], weeks)
        for record in behavior_data:
            cursor.execute('''
                INSERT INTO behavior_data (uuid, week, attendance, quiz_avg, 
                                          debug_success, project_score, pep8_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (record['uuid'], record['week'], record['attendance'],
                  record['quiz_avg'], record['debug_success'], 
                  record['project_score'], record['pep8_score']))
            total_records += 1
        
        # 计算最新一周的能力画像
        latest_data = behavior_data[-1]
        k, s, l = calc_3d_scores(latest_data)
        
        # 生成模拟诊断
        diagnosis = generate_mock_diagnosis(k, s, l)
        
        cursor.execute('''
            INSERT INTO ability_profile (uuid, week, knowledge_score, 
                                        skill_score, literacy_score, diagnosis)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (student['uuid'], weeks, k, s, l, diagnosis))
    
    # 生成一些预警记录
    print("生成预警记录...")
    generate_mock_warnings(cursor, students)
    
    conn.commit()
    conn.close()
    
    print(f"✅ 数据初始化完成！")
    print(f"   - 学生数：{student_count}")
    print(f"   - 行为记录：{total_records}")
    print(f"   - 能力画像：{student_count}")


def generate_mock_diagnosis(k: float, s: float, l: float) -> str:
    """生成模拟诊断报告（用于无 AI 时的降级）"""
    advantages = []
    weaknesses = []
    suggestions = []
    
    if k >= 80:
        advantages.append("知识掌握扎实")
    elif k >= 60:
        advantages.append("基础知识基本掌握")
    else:
        weaknesses.append("理论知识需加强")
        suggestions.append("建议每周复习课堂笔记 2 小时")
    
    if s >= 80:
        advantages.append("动手能力强")
    elif s >= 60:
        advantages.append("实践技能良好")
    else:
        weaknesses.append("代码调试能力待提升")
        suggestions.append("多做编程练习，善用调试工具")
    
    if l >= 80:
        advantages.append("学习态度认真")
    elif l >= 60:
        advantages.append("学习习惯较好")
    else:
        weaknesses.append("学习规范性需改进")
        suggestions.append("注意代码规范，按时完成任务")
    
    report = f"优势：{'、'.join(advantages)}。"
    if weaknesses:
        report += f"薄弱点：{'、'.join(weaknesses)}。"
    if suggestions:
        report += f"建议：{'；'.join(suggestions[:2])}。"
    report += " [AI 辅助生成]"
    
    return report


def generate_mock_warnings(cursor, students: List[Dict]):
    """生成模拟预警记录"""
    warnings = []
    
    for student in students:
        # 随机触发不同类型的预警
        rand = random.random()
        
        if rand < 0.15:  # 15% 概率技能薄弱
            warnings.append((
                student['uuid'],
                "技能薄弱预警",
                "high",
                f"skill_score < 60 AND debug_attempts > 8"
            ))
        elif rand < 0.25:  # 10% 概率出勤率预警
            warnings.append((
                student['uuid'],
                "出勤率预警",
                "high",
                f"attendance < 0.8 连续 3 周"
            ))
        elif rand < 0.35:  # 10% 概率知识不足
            warnings.append((
                student['uuid'],
                "知识掌握不足",
                "medium",
                f"knowledge_score < 65"
            ))
    
    for w in warnings:
        cursor.execute('''
            INSERT INTO warning_records (uuid, rule_name, priority, message)
            VALUES (?, ?, ?, ?)
        ''', w)


if __name__ == '__main__':
    import os
    
    # 默认数据库路径
    db_path = os.getenv('SQLITE_DB_PATH', '/app/data/huixuetong.db')
    
    # 如果是本地开发，使用相对路径
    if not os.path.exists(os.path.dirname(db_path)):
        db_path = 'data/huixuetong.db'
        os.makedirs('data', exist_ok=True)
    
    populate_mock_data(db_path, student_count=30, weeks=12)
