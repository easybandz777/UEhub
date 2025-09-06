"""
Application settings and configuration.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database configuration."""
    
    url: str = Field(..., env="DATABASE_URL")
    echo: bool = Field(False, env="DATABASE_ECHO")
    pool_size: int = Field(10, env="DATABASE_POOL_SIZE")
    max_overflow: int = Field(20, env="DATABASE_MAX_OVERFLOW")
    
    # Neon-specific settings
    neon_api_endpoint: Optional[str] = Field(None, env="NEON_API_ENDPOINT")
    neon_api_key: Optional[str] = Field(None, env="NEON_API_KEY")
    
    class Config:
        env_prefix = "DATABASE_"


class RedisSettings(BaseSettings):
    """Redis configuration."""
    
    url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    db: int = Field(0, env="REDIS_DB")
    max_connections: int = Field(10, env="REDIS_MAX_CONNECTIONS")
    
    class Config:
        env_prefix = "REDIS_"


class AuthSettings(BaseSettings):
    """Authentication configuration."""
    
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    @validator("secret_key")
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    class Config:
        env_prefix = "AUTH_"


class StorageSettings(BaseSettings):
    """Storage configuration."""
    
    backend: str = Field("local", env="STORAGE_BACKEND")
    local_path: str = Field("./uploads", env="STORAGE_LOCAL_PATH")
    
    # S3 settings
    s3_bucket: Optional[str] = Field(None, env="S3_BUCKET")
    s3_region: Optional[str] = Field(None, env="S3_REGION")
    s3_access_key: Optional[str] = Field(None, env="S3_ACCESS_KEY")
    s3_secret_key: Optional[str] = Field(None, env="S3_SECRET_KEY")
    s3_endpoint_url: Optional[str] = Field(None, env="S3_ENDPOINT_URL")
    
    @validator("backend")
    def validate_backend(cls, v):
        if v not in ["local", "s3"]:
            raise ValueError("STORAGE_BACKEND must be 'local' or 's3'")
        return v
    
    class Config:
        env_prefix = "STORAGE_"


class MailSettings(BaseSettings):
    """Email configuration."""
    
    backend: str = Field("console", env="MAIL_BACKEND")
    from_email: str = Field("noreply@uehub.com", env="MAIL_FROM_EMAIL")
    from_name: str = Field("UE Hub", env="MAIL_FROM_NAME")
    
    # Resend settings
    resend_api_key: Optional[str] = Field(None, env="RESEND_API_KEY")
    
    @validator("backend")
    def validate_backend(cls, v):
        if v not in ["console", "resend"]:
            raise ValueError("MAIL_BACKEND must be 'console' or 'resend'")
        return v
    
    class Config:
        env_prefix = "MAIL_"


class AppSettings(BaseSettings):
    """Main application settings."""
    
    # App info
    name: str = Field("UE Hub", env="APP_NAME")
    version: str = Field("1.0.0", env="APP_VERSION")
    description: str = Field("Upper Echelon Hub - Inventory and Training System")
    
    # Environment
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(False, env="DEBUG")
    
    # API settings
    api_prefix: str = Field("/v1", env="API_PREFIX")
    cors_origins: List[str] = Field(
        ["http://localhost:3000"], 
        env="CORS_ORIGINS"
    )
    
    # Security
    allowed_hosts: List[str] = Field(["*"], env="ALLOWED_HOSTS")
    
    # Observability
    sentry_dsn: Optional[str] = Field(None, env="SENTRY_DSN")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # Feature flags
    enable_docs: bool = Field(True, env="ENABLE_DOCS")
    enable_metrics: bool = Field(True, env="ENABLE_METRICS")
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("allowed_hosts", pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("environment")
    def validate_environment(cls, v):
        if v not in ["development", "staging", "production"]:
            raise ValueError("ENVIRONMENT must be 'development', 'staging', or 'production'")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        if v.upper() not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError("LOG_LEVEL must be a valid logging level")
        return v.upper()


class Settings(BaseSettings):
    """Combined application settings."""
    
    app: AppSettings = AppSettings()
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    auth: AuthSettings = AuthSettings()
    storage: StorageSettings = StorageSettings()
    mail: MailSettings = MailSettings()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
