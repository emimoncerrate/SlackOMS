"""
Configuration management for OMS API
Loads and validates environment variables
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Security
    oms_api_key: str
    
    # Database
    database_url: str
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    environment: str = "development"
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    # Application
    app_name: str = "SlackOMS API"
    version: str = "1.0.0"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

