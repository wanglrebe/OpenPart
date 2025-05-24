# backend/app/core/config.py (更新版本)
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 数据库配置
    database_url: str = "postgresql://openpart_user:your_password@localhost:5432/openpart"
    debug: bool = True
    
    # JWT 配置
    secret_key: str = "your-super-secret-key-change-in-production-please"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        extra = "allow"  # 允许额外字段

settings = Settings()