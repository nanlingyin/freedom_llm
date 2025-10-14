"""
核心配置模块
从环境变量加载所有配置项
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
import json


class Settings(BaseSettings):
    """应用配置类"""
    
    # ==================== LLM配置 ====================
    llm_provider: str = Field(default="openai", alias="LLM_PROVIDER")
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_base_url: Optional[str] = Field(default=None, alias="LLM_BASE_URL")
    llm_model: str = Field(default="gpt-3.5-turbo", alias="LLM_MODEL")
    llm_temperature: float = Field(default=0.7, alias="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=2000, alias="LLM_MAX_TOKENS")
    
    # ==================== 数据库配置 ====================
    database_url: str = Field(default="sqlite:///./freedom_ai.db", alias="DATABASE_URL")
    vector_db_path: str = Field(default="./chroma_db", alias="VECTOR_DB_PATH")
    
    # ==================== 服务器配置 ====================
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        alias="CORS_ORIGINS"
    )
    
    # ==================== AI人格配置 ====================
    ai_name: str = Field(default="小艾", alias="AI_NAME")
    ai_personality: str = Field(
        default="你是一个友好、幽默、善解人意的AI助手。",
        alias="AI_PERSONALITY"
    )
    ai_gender: str = Field(default="female", alias="AI_GENDER")
    ai_age: int = Field(default=25, alias="AI_AGE")
    
    # ==================== 主动对话配置 ====================
    proactive_chat_enabled: bool = Field(default=True, alias="PROACTIVE_CHAT_ENABLED")
    proactive_chat_min_interval: int = Field(default=1800, alias="PROACTIVE_CHAT_MIN_INTERVAL")
    proactive_chat_max_interval: int = Field(default=7200, alias="PROACTIVE_CHAT_MAX_INTERVAL")
    user_active_hours: List[int] = Field(
        default=[9,10,11,12,13,14,15,16,17,18,19,20,21,22],
        alias="USER_ACTIVE_HOURS"
    )
    
    # ==================== 记忆系统配置 ====================
    short_term_memory_size: int = Field(default=20, alias="SHORT_TERM_MEMORY_SIZE")
    long_term_memory_retrieve_size: int = Field(default=5, alias="LONG_TERM_MEMORY_RETRIEVE_SIZE")
    memory_importance_threshold: float = Field(default=0.6, alias="MEMORY_IMPORTANCE_THRESHOLD")
    
    # ==================== 日程系统配置 ====================
    schedule_remind_advance_minutes: int = Field(default=15, alias="SCHEDULE_REMIND_ADVANCE_MINUTES")
    schedule_smart_suggest: bool = Field(default=True, alias="SCHEDULE_SMART_SUGGEST")
    
    # ==================== 安全配置 ====================
    secret_key: str = Field(default="change-this-secret-key", alias="SECRET_KEY")
    access_token_expire_days: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_DAYS")
    
    # ==================== 日志配置 ====================
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="./logs/app.log", alias="LOG_FILE")
    
    # ==================== 功能开关 ====================
    enable_emotion_analysis: bool = Field(default=True, alias="ENABLE_EMOTION_ANALYSIS")
    enable_voice: bool = Field(default=False, alias="ENABLE_VOICE")
    enable_image_understanding: bool = Field(default=False, alias="ENABLE_IMAGE_UNDERSTANDING")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            """自定义环境变量解析"""
            if field_name in ["cors_origins", "user_active_hours"]:
                try:
                    return json.loads(raw_val)
                except json.JSONDecodeError:
                    # 如果不是JSON，尝试逗号分隔
                    if "," in raw_val:
                        values = [v.strip() for v in raw_val.split(",")]
                        if field_name == "user_active_hours":
                            return [int(v) for v in values if v.isdigit()]
                        return values
            return raw_val


# 创建全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings
