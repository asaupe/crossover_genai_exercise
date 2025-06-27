"""
Configuration settings for the GenAI Email Processing System.
"""

from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import Field, model_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application Configuration
    APP_NAME: str = Field(default="GenAI Email Processor", env="APP_NAME")
    APP_VERSION: str = Field(default="1.0.0", env="APP_VERSION")
    DEBUG: bool = Field(default=False, env="DEBUG")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-3.5-turbo", env="OPENAI_MODEL")
    OPENAI_MAX_TOKENS: int = Field(default=1000, env="OPENAI_MAX_TOKENS")
    TEMPERATURE: float = Field(default=0.7, env="TEMPERATURE")
    TOP_P: float = Field(default=1.0, env="TOP_P")
    FREQUENCY_PENALTY: float = Field(default=0.0, env="FREQUENCY_PENALTY")
    PRESENCE_PENALTY: float = Field(default=0.0, env="PRESENCE_PENALTY")
    
    # Database Configuration
    DATABASE_URL: str = Field(default="sqlite:///./emails.db", env="DATABASE_URL")
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    
    # Vector Database Configuration
    CHROMA_PERSIST_DIRECTORY: str = Field(default="./chroma_db", env="CHROMA_PERSIST_DIRECTORY")
    EMBEDDING_MODEL: str = Field(default="text-embedding-ada-002", env="EMBEDDING_MODEL")
    
    # Email Processing Configuration
    MAX_EMAIL_LENGTH: int = Field(default=10000, env="MAX_EMAIL_LENGTH")
    MAX_RESPONSE_LENGTH: int = Field(default=2000, env="MAX_RESPONSE_LENGTH")
    SUPPORTED_LANGUAGES: Union[List[str], str] = Field(default=["en", "es", "fr", "de"], env="SUPPORTED_LANGUAGES")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=3600, env="RATE_LIMIT_WINDOW")
    
    # Security
    SECRET_KEY: str = Field(default="your_secret_key_here", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    @model_validator(mode='after')
    def parse_supported_languages(self):
        """Parse comma-separated string into list of strings."""
        if isinstance(self.SUPPORTED_LANGUAGES, str):
            self.SUPPORTED_LANGUAGES = [lang.strip() for lang in self.SUPPORTED_LANGUAGES.split(',') if lang.strip()]
        return self
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
