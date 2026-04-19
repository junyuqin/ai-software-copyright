-- 慧学通数据库初始化脚本 (SQLite3 版本)
-- 支持行为日志与画像存储，简化部署流程

-- 学生信息表
CREATE TABLE IF NOT EXISTS students (
    uuid TEXT PRIMARY KEY,
    class TEXT NOT NULL,
    major TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 学习行为数据表
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
);

CREATE INDEX IF NOT EXISTS idx_uuid_week ON behavior_data(uuid, week);

-- 能力画像表
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
);

CREATE INDEX IF NOT EXISTS idx_profile_uuid_week ON ability_profile(uuid, week);

-- 预警记录表
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
);

CREATE INDEX IF NOT EXISTS idx_status_triggered ON warning_records(status, triggered_at);

-- 干预流水表（闭环追踪）
CREATE TABLE IF NOT EXISTS intervention_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    warning_id INTEGER NOT NULL,
    action_type TEXT NOT NULL,
    action_detail TEXT,
    operator TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (warning_id) REFERENCES warning_records(id) ON DELETE CASCADE
);

-- 插入示例数据（用于测试）
INSERT OR IGNORE INTO students (uuid, class, major) VALUES
('a1b2c3d4e5f6g7h8', '2023 级计算机应用 1 班', '计算机应用'),
('i9j0k1l2m3n4o5p6', '2023 级计算机网络 2 班', '计算机网络技术');

INSERT INTO behavior_data (uuid, week, attendance, quiz_avg, debug_success, project_score, pep8_score) VALUES
('a1b2c3d4e5f6g7h8', 10, 0.95, 82.5, 0.70, 85.0, 88.0),
('i9j0k1l2m3n4o5p6', 10, 0.75, 65.0, 0.45, 60.0, 72.0);
