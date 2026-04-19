"""
慧学通 (HuiXueTong) - 数据模型模块
功能：数据库模型定义、ORM 映射
"""

from datetime import datetime


class Student:
    """学生信息模型（预留，待对接 SQLAlchemy）"""
    
    def __init__(self, student_id: str, name: str, class_id: str = None):
        self.student_id = student_id
        self.name = name
        self.class_id = class_id
        self.created_at = datetime.now()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'student_id': self.student_id,
            'name': self.name,
            'class_id': self.class_id,
            'created_at': self.created_at.isoformat()
        }


class BehaviorData:
    """学生行为数据模型（预留）"""
    
    def __init__(self, student_id: str, quiz_avg: float = 0.0, 
                 attendance: float = 0.0, debug_success: float = 0.0,
                 project_score: float = 0.0, pep8_score: float = 0.0):
        self.student_id = student_id
        self.quiz_avg = quiz_avg
        self.attendance = attendance
        self.debug_success = debug_success
        self.project_score = project_score
        self.pep8_score = pep8_score
        self.updated_at = datetime.now()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'student_id': self.student_id,
            'quiz_avg': self.quiz_avg,
            'attendance': self.attendance,
            'debug_success': self.debug_success,
            'project_score': self.project_score,
            'pep8_score': self.pep8_score,
            'updated_at': self.updated_at.isoformat()
        }


class AbilityProfile:
    """学生能力画像模型（预留）"""
    
    def __init__(self, student_uuid: str, knowledge_score: float = 0.0,
                 skill_score: float = 0.0, literacy_score: float = 0.0):
        self.student_uuid = student_uuid
        self.knowledge_score = knowledge_score
        self.skill_score = skill_score
        self.literacy_score = literacy_score
        self.generated_at = datetime.now()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'student_uuid': self.student_uuid,
            'knowledge_score': self.knowledge_score,
            'skill_score': self.skill_score,
            'literacy_score': self.literacy_score,
            'generated_at': self.generated_at.isoformat()
        }


class WarningRecord:
    """预警记录模型（预留）"""
    
    def __init__(self, rule_name: str, priority: str, student_uuid: str,
                 message: str, trigger_time: datetime = None):
        self.rule_name = rule_name
        self.priority = priority
        self.student_uuid = student_uuid
        self.message = message
        self.trigger_time = trigger_time or datetime.now()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'rule_name': self.rule_name,
            'priority': self.priority,
            'student_uuid': self.student_uuid,
            'message': self.message,
            'trigger_time': self.trigger_time.isoformat()
        }
