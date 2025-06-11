"""Application settings with Railway support"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Railway provides these automatically
    database_url: str = os.getenv("DATABASE_URL", "")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    port: int = int(os.getenv("PORT", "8000"))
    
    # Environment
    environment: str = os.getenv("RAILWAY_ENVIRONMENT", "production")
    
    # Authentication
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-this-in-production")
    jwt_algorithm: str = "HS256"
    access_token_expire_hours: int = 24
    
    # CORS
    allowed_origins: list[str] = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:3000"
    ).split(",")
    
    # LLM APIs
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Vector DB
    pinecone_api_key: Optional[str] = os.getenv("PINECONE_API_KEY")
    pinecone_env: str = os.getenv("PINECONE_ENV", "us-east-1")
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()