"""
数据库配置和会话管理
使用 SQLAlchemy 作为 ORM
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./travel_gpt.db"
    
    # LLM Configuration (新方式)
    LLM_PROVIDER: str = ""  # "nvidia", "ollama", or "dashscope"
    
    # NVIDIA GLM API Configuration
    NVIDIA_API_KEY: str = ""  # NVIDIA API Key
    NVIDIA_MODEL: str = "z-ai/glm4.7"  # GLM model name
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:8b"
    
    # DashScope Configuration
    DASHSCOPE_API_KEY: str = ""
    
    # LLM Configuration (旧方式，兼容)
    LLM_API_KEY: str = ""
    LLM_OPENAI_BASE: str = ""
    LLM_MODEL_NAME: str = ""
    
    # 图片搜索 API
    UNSPLASH_ACCESS_KEY: str = ""
    PEXELS_API_KEY: str = ""
    
    # 天气 API
    OPENWEATHER_API_KEY: str = ""
    
    # 搜索工具 API
    TAVILY_API_KEY: str = ""
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # Email Configuration
    RESEND_API_KEY: str = ""
    FROM_EMAIL: str = ""
    SMTP_HOST: str = ""
    SMTP_PORT: str = "587"
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    DEFAULT_EMAIL_ACCOUNT: str = ""
    DEFAULT_EMAIL_PASSWORD: str = ""
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-for-jwt-change-this-in-production"
    
    class Config:
        env_file = ".env"
        extra = "allow"  # 允许额外的环境变量


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()

# 依赖注入：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
