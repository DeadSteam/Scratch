import json
from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Application
    APP_NAME: str = "Experiment Management API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = Field(..., description="Main database URL")
    USERS_DATABASE_URL: str = Field(..., description="Users database URL")
    KNOWLEDGE_DATABASE_URL: str | None = Field(
        default=None, description="Knowledge base database URL"
    )
    DB_POOL_SIZE: int = Field(default=5, description="Database pool size")
    DB_MAX_OVERFLOW: int = Field(default=10, description="Database max overflow")
    DB_ECHO: bool = Field(default=False, description="Database echo SQL queries")

    # Redis
    REDIS_URL: str = Field(..., description="Redis connection URL")
    REDIS_DEFAULT_TIMEOUT: int = Field(
        default=3600, description="Default Redis key timeout in seconds"
    )

    # Security
    SECRET_KEY: str = Field(..., description="Secret key for JWT tokens")
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, description="Access token expiration in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, description="Refresh token expiration in days"
    )

    # Default Admin User
    ADMIN_USERNAME: str = Field(default="admin", description="Default admin username")
    ADMIN_EMAIL: str = Field(default="admin@example.com", description="Default admin email")
    ADMIN_PASSWORD: str = Field(default="Akrawer1", description="Default admin password")

    # CORS
    CORS_ORIGINS: list[str] = Field(default=["*"], description="CORS allowed origins")
    CORS_CREDENTIALS: bool = Field(default=True, description="CORS allow credentials")
    CORS_METHODS: list[str] = Field(default=["*"], description="CORS allowed methods")
    CORS_HEADERS: list[str] = Field(default=["*"], description="CORS allowed headers")

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS_ORIGINS from JSON string or list."""
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v if isinstance(v, list) else []

    @field_validator("CORS_METHODS", mode="before")
    @classmethod
    def parse_cors_methods(cls, v: Any) -> list[str]:
        """Parse CORS_METHODS from JSON string or list."""
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                return [method.strip() for method in v.split(",") if method.strip()]
        return v if isinstance(v, list) else []

    @field_validator("CORS_HEADERS", mode="before")
    @classmethod
    def parse_cors_headers(cls, v: Any) -> list[str]:
        """Parse CORS_HEADERS from JSON string or list."""
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                return [header.strip() for header in v.split(",") if header.strip()]
        return v if isinstance(v, list) else []

    # File Upload
    MAX_FILE_SIZE: int = Field(
        default=10 * 1024 * 1024, description="Max file size in bytes (10MB)"
    )
    ALLOWED_IMAGE_TYPES: list[str] = Field(
        default=["image/jpeg", "image/png", "image/webp"], description="Allowed image MIME types"
    )

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="Log format"
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance. Loads from env via pydantic-settings."""
    return Settings()  # type: ignore[call-arg]


# Global settings instance
settings = get_settings()
