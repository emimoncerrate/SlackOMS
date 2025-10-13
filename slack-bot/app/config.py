"""
Configuration management for Slack Bot
Loads and validates environment variables
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Slack Configuration
    slack_bot_token: str
    slack_signing_secret: str
    
    # OMS API Configuration
    oms_api_url: str
    oms_api_key: str
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 3000
    environment: str = "development"
    
    # Application
    app_name: str = "Paper Trading Slack Bot"
    version: str = "1.0.0"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

