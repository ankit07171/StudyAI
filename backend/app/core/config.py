"""
Application configuration settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Union
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Use model_config instead of nested Config class
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields in .env
    )
    
    # Application
    APP_NAME: str = "AI Study Assistant"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database - MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017/studyai"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Google OAuth (OPTIONAL)
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    
    # LLM APIs
    GOOGLE_API_KEY: str  # Required - Google Gemini for AI generation
    OPENAI_API_KEY: Optional[str] = None  # Optional
    ANTHROPIC_API_KEY: Optional[str] = None  # Optional
    
    # Vector Database (Pinecone v5 with Serverless)
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = "us-east-1"  # AWS region for serverless
    PINECONE_INDEX_NAME: str = "studyai-embeddings"
    
    # Redis (OPTIONAL - for caching)
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: Optional[int] = None
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB
    ALLOWED_EXTENSIONS: str = "pdf"  # Changed to string, will split in code
    MAX_FILES_PER_SUBJECT: int = 10
    UPLOAD_DIR: str = "./uploads"
    
    # Embeddings
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIMENSION: int = 384
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # LLM
    DEFAULT_LLM: str = "gemini-3.1-flash-lite"
    DEFAULT_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 4096
    
    # Email (for password reset)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""  # For Gmail, use App Password (16 chars)
    EMAIL_FROM: str = ""
    EMAIL_FROM_NAME: str = "AI Study Assistant"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"  # Changed to string, will split in code
    
    # Celery (OPTIONAL - requires Redis)
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    # Sentry (OPTIONAL - for error tracking)
    SENTRY_DSN: Optional[str] = None
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Convert ALLOWED_EXTENSIONS string to list"""
        if isinstance(self.ALLOWED_EXTENSIONS, str):
            return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]
        return self.ALLOWED_EXTENSIONS
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
