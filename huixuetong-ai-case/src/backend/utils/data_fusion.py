"""
慧学通 (HuiXueTong) - 数据融合工具模块
功能：三维能力得分计算、数据清洗、SHA-256脱敏
申报映射：多源数据融合与三维画像计算/有效性/数据分析
"""

import hashlib
from typing import Dict, Tuple, Any


# 三维得分计算权重配置（可外部调整）
WEIGHTS = {
    'knowledge': {
        'quiz_avg': 0.5,
        'attendance': 0.3,
        'base': 12
    },
    'skill': {
        'debug_success': 0.6,
        'project_score': 0.4
    },
    'literacy': {
        'attendance': 0.4,
        'pep8_score': 0.3,
        'base': 15
    }
}


def calc_3d_scores(data: Dict[str, Any], weights: Dict = None) -> Tuple[float, float, float]:
    """
    计算学生知识-技能-素养三维能力得分
    
    计算公式（符合中职教育评价标准）：
    - knowledge = 0.5*quiz_avg + 0.3*attendance*100 + 12
    - skill = 0.6*debug_success*100 + 0.4*project_score
    - literacy = 0.4*attendance*100 + 0.3*pep8_score*10 + 15
    
    参数：
        data: 包含以下键的字典（支持缺失默认值）：
            - quiz_avg: 测验平均分 (0-100)
            - attendance: 出勤率 (0-1)
            - debug_success: 调试成功率 (0-1)
            - project_score: 项目评分 (0-100)
            - pep8_score: PEP8规范得分 (0-100)
    
    返回：
        (knowledge, skill, literacy) 三元组，保留1位小数
    """
    # 使用默认权重或传入的权重
    if weights is None:
        weights = WEIGHTS
    
    # 类型检查与默认值容错
    quiz_avg = float(data.get('quiz_avg', 70.0))
    attendance = float(data.get('attendance', 0.8))
    debug_success = float(data.get('debug_success', 0.5))
    project_score = float(data.get('project_score', 70.0))
    pep8_score = float(data.get('pep8_score', 70.0))
    
    # 边界值保护（防止异常数据）
    quiz_avg = max(0, min(100, quiz_avg))
    attendance = max(0, min(1, attendance))
    debug_success = max(0, min(1, debug_success))
    project_score = max(0, min(100, project_score))
    pep8_score = max(0, min(100, pep8_score))
    
    # 按配置的权重计算三维得分
    knowledge = (
        weights['knowledge']['quiz_avg'] * quiz_avg +
        weights['knowledge']['attendance'] * attendance * 100 +
        weights['knowledge'].get('base', 12)
    )
    skill = (
        weights['skill']['debug_success'] * debug_success * 100 +
        weights['skill']['project_score'] * project_score
    )
    literacy = (
        weights['literacy']['attendance'] * attendance * 100 +
        weights['literacy']['pep8_score'] * pep8_score * 10 +
        weights['literacy'].get('base', 15)
    )
    
    # 边界保护（确保得分在合理范围）
    knowledge = max(0, min(100, knowledge))
    skill = max(0, min(100, skill))
    literacy = max(0, min(100, literacy))
    
    return (round(knowledge, 1), round(skill, 1), round(literacy, 1))


def hash_student_id(uid: str) -> str:
    """
    对学生标识进行SHA-256哈希脱敏
    符合《个人信息保护法》与教育数据安全规范
    
    参数：
        uid: 原始学生ID（学号/用户ID）
    
    返回：
        SHA-256哈希值（16进制字符串，前8位用于展示）
    """
    if not uid:
        return ""
    
    # SHA-256哈希
    hash_obj = hashlib.sha256(uid.encode('utf-8'))
    full_hash = hash_obj.hexdigest()
    
    # 返回前16位用于系统内部标识（兼顾安全性与可读性）
    return full_hash[:16]


def sanitize_data(data: Dict[str, Any], sensitive_fields: list = None) -> Dict[str, Any]:
    """
    数据脱敏工具函数
    对敏感字段进行哈希处理
    
    参数：
        data: 原始数据字典
        sensitive_fields: 需要脱敏的字段列表，默认['student_id', 'uuid']
    
    返回：
        脱敏后的数据字典
    """
    if sensitive_fields is None:
        sensitive_fields = ['student_id', 'uuid']
    
    sanitized = data.copy()
    for field in sensitive_fields:
        if field in sanitized and sanitized[field]:
            sanitized[field] = hash_student_id(str(sanitized[field]))
    
    return sanitized


def validate_behavior_data(data: Dict[str, Any]) -> bool:
    """
    验证行为数据的有效性
    确保关键字段存在且类型正确
    
    参数：
        data: 待验证的行为数据字典
    
    返回：
        True表示数据有效，False表示数据无效
    """
    required_fields = {
        'quiz_avg': (int, float),
        'attendance': (int, float),
        'debug_success': (int, float),
        'project_score': (int, float),
        'pep8_score': (int, float)
    }
    
    for field, expected_types in required_fields.items():
        if field not in data:
            return False
        if not isinstance(data[field], expected_types):
            return False
    
    return True
