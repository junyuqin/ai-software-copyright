-- 慧学通数据库初始化脚本
-- 符合MySQL 8.0规范，支持行为日志与画像存储

CREATE DATABASE IF NOT EXISTS huixuetong CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE huixuetong;

-- 学生信息表
CREATE TABLE IF NOT EXISTS students (
    uuid VARCHAR(64) PRIMARY KEY COMMENT '学生唯一标识（SHA-256脱敏后）',
    class VARCHAR(50) NOT NULL COMMENT '班级',
    major VARCHAR(100) NOT NULL COMMENT '专业',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生基本信息表';

-- 学习行为数据表
CREATE TABLE IF NOT EXISTS behavior_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(64) NOT NULL COMMENT '学生UUID',
    week INT NOT NULL COMMENT '教学周次',
    attendance DECIMAL(3,2) DEFAULT 0.8 COMMENT '出勤率 (0-1)',
    quiz_avg DECIMAL(5,2) DEFAULT 70.0 COMMENT '测验平均分',
    debug_success DECIMAL(3,2) DEFAULT 0.5 COMMENT '调试成功率',
    project_score DECIMAL(5,2) DEFAULT 70.0 COMMENT '项目评分',
    pep8_score DECIMAL(5,2) DEFAULT 70.0 COMMENT 'PEP8规范得分',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间',
    INDEX idx_uuid_week (uuid, week),
    FOREIGN KEY (uuid) REFERENCES students(uuid) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生学习行为数据表';

-- 能力画像表
CREATE TABLE IF NOT EXISTS ability_profile (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(64) NOT NULL COMMENT '学生UUID',
    week INT NOT NULL COMMENT '教学周次',
    knowledge_score DECIMAL(5,1) DEFAULT 0.0 COMMENT '知识维度得分',
    skill_score DECIMAL(5,1) DEFAULT 0.0 COMMENT '技能维度得分',
    literacy_score DECIMAL(5,1) DEFAULT 0.0 COMMENT '素养维度得分',
    diagnosis TEXT COMMENT 'AI诊断报告',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '生成时间',
    INDEX idx_uuid_week (uuid, week),
    FOREIGN KEY (uuid) REFERENCES students(uuid) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生三维能力画像表';

-- 预警记录表
CREATE TABLE IF NOT EXISTS warning_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(64) NOT NULL COMMENT '学生UUID',
    rule_name VARCHAR(100) NOT NULL COMMENT '触发规则名称',
    priority ENUM('low', 'medium', 'high') DEFAULT 'medium' COMMENT '预警优先级',
    message TEXT COMMENT '预警详情',
    status ENUM('pending', 'processed', 'ignored') DEFAULT 'pending' COMMENT '处理状态',
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '触发时间',
    processed_at TIMESTAMP NULL COMMENT '处理时间',
    INDEX idx_status_triggered (status, triggered_at),
    FOREIGN KEY (uuid) REFERENCES students(uuid) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='预警干预记录表';

-- 干预流水表（闭环追踪）
CREATE TABLE IF NOT EXISTS intervention_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    warning_id INT NOT NULL COMMENT '关联预警ID',
    action_type VARCHAR(50) NOT NULL COMMENT '干预类型：resource_push/teacher_notify/retest',
    action_detail TEXT COMMENT '干预详情',
    operator VARCHAR(50) COMMENT '操作人',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    FOREIGN KEY (warning_id) REFERENCES warning_records(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='干预闭环流水表';

-- 插入示例数据（用于测试）
INSERT INTO students (uuid, class, major) VALUES 
('a1b2c3d4e5f6g7h8', '2023级计算机应用1班', '计算机应用'),
('i9j0k1l2m3n4o5p6', '2023级计算机网络2班', '计算机网络技术');

INSERT INTO behavior_data (uuid, week, attendance, quiz_avg, debug_success, project_score, pep8_score) VALUES
('a1b2c3d4e5f6g7h8', 10, 0.95, 82.5, 0.70, 85.0, 88.0),
('i9j0k1l2m3n4o5p6', 10, 0.75, 65.0, 0.45, 60.0, 72.0);
