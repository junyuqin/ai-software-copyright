"""
慧学通 (HuiXueTong) - 配置管理模块
功能：应用配置加载、环境变量管理、配置类定义
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
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # CORS 配置
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # 百度文心一言配置
    BAIDU_API_KEY = os.getenv('BAIDU_API_KEY', '')
    BAIDU_SECRET_KEY = os.getenv('BAIDU_SECRET_KEY', '')
    BAIDU_TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
    BAIDU_CHAT_URL = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions"
    
    # 数据库配置（预留）
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_NAME = os.getenv('DB_NAME', 'huixuetong')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    @classmethod
    def init_app(cls, app):
        """初始化 Flask 应用配置"""
        app.config['DEBUG'] = cls.FLASK_DEBUG
        app.config['SECRET_KEY'] = cls.SECRET_KEY
        app.config['CORS_ORIGINS'] = cls.CORS_ORIGINS
        
        # 数据库配置（预留）
        if cls.DB_PASSWORD:
            app.config['SQLALCHEMY_DATABASE_URI'] = (
                f"mysql+pymysql://{cls.DB_USER}:{cls.DB_PASSWORD}"
                f"@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
            )
            app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


def load_config():
    """加载配置文件"""
    env_file = os.path.join(
        os.path.dirname(__file__), 
        '..', '..', '..', 'deploy', '.env'
    )
    load_dotenv(env_file)
    return Config
