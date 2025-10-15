"""
Settings - Application configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # Application
    APP_NAME: str = "Web Content Analyzer"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    # Scraping
    SCRAPING_TIMEOUT: int = 30
    SCRAPING_MAX_RETRIES: int = 3
    MAX_CONTENT_SIZE: int = 10 * 1024 * 1024  # 10 MB
    
    # LLM
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-3.5-turbo"
    LLM_MAX_TOKENS: int = 4000
    LLM_TEMPERATURE: float = 0.7
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Security
    ALLOWED_HOSTS: list = ["*"]
    ENABLE_SSRF_PROTECTION: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
