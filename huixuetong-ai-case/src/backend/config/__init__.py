"""
慧学通 (HuiXueTong) - 配置管理模块
功能：应用配置加载、环境变量管理、配置类定义 (支持 SQLite3)
申报映射：操作简单易用/环境隔离
"""

import os
from dotenv import load_dotenv


class Config:
    """应用配置类，支持多环境配置"""

    # 基础配置
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Flask 配置
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # CORS 配置
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

    # 百度文心一言配置
    BAIDU_API_KEY = os.getenv('BAIDU_API_KEY', '')
    BAIDU_SECRET_KEY = os.getenv('BAIDU_SECRET_KEY', '')
    BAIDU_TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
    BAIDU_CHAT_URL = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions"

    # SQLite3 数据库配置 (替代 MySQL，简化部署)
    SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', '/app/data/huixuetong.db')

    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # 预警规则配置
    WARNING_RULES_PATH = os.getenv('WARNING_RULES_PATH', '/app/data/warning_rules.json')

    @classmethod
    def init_app(cls, app):
        """初始化 Flask 应用配置"""
        app.config['DEBUG'] = cls.FLASK_DEBUG
        app.config['SECRET_KEY'] = cls.SECRET_KEY
        app.config['CORS_ORIGINS'] = cls.CORS_ORIGINS

        # SQLite3 数据库配置 (无需额外服务，开箱即用)
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{cls.SQLITE_DB_PATH}"
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


def load_config():
    """加载配置文件"""
    # 尝试从 deploy/.env 加载
    env_file = os.path.join(
        os.path.dirname(__file__),
        '..', '..', '..', 'deploy', '.env'
    )
    if os.path.exists(env_file):
        load_dotenv(env_file)
    else:
        # 尝试从当前目录加载
        load_dotenv()
    return Config
