"""Configuration settings for the Question Answer Generator."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False
    
    # File Storage
    upload_dir: str = "./uploads"
    output_dir: str = "./outputs"
    max_file_size_mb: int = 50
    
    # LLM API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    perplexity_api_key: str = ""
    
    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # Celery Configuration
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # Vector Database Configuration
    vector_db_path: str = "./data/chromadb"
    
    # Supported Languages
    supported_languages: List[str] = [
        "en", "es", "fr", "de", "zh", 
        "ja", "hi", "ar", "pt", "ru"
    ]
    
    # PDF Configuration
    pdf_retention_days: int = 7
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    # Security Configuration
    enforce_https: bool = False  # Set to True in production
    secret_key: str = ""  # Used for JWT token generation
    encryption_key: str = ""  # Used for API key encryption
    rate_limit_enabled: bool = True
    
    # Database Configuration
    data_dir: str = "./data"
    
    # Content Security Policy
    csp_enabled: bool = True
    csp_directives: str = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"


# Global settings instance
settings = Settings()
