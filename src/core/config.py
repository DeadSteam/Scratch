import json
from functools import lru_cache
from typing import Any, Self

from pydantic import Field, field_validator, model_validator
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
    AUTO_SEED_REFERENCE_DATA: bool = Field(
        default=True,
        description=(
            "If true, seed demo films, equipment configs, and knowledge "
            "when those tables are empty"
        ),
    )

    # Redis
    REDIS_URL: str = Field(..., description="Redis connection URL")
    REDIS_DEFAULT_TIMEOUT: int = Field(
        default=3600, description="Default Redis key timeout in seconds"
    )

    # Security
    SECRET_KEY: str = Field(..., description="Secret key for JWT tokens")
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if v.startswith("generate-") or len(v) < 32:
            raise ValueError(
                "SECRET_KEY must be a random string of at least 32 characters. "
                'Generate: python -c "import secrets; print(secrets.token_urlsafe(32))"'
            )
        return v

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, description="Access token expiration in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, description="Refresh token expiration in days"
    )

    # Default Admin User
    ADMIN_USERNAME: str = Field(default="admin", description="Default admin username")
    ADMIN_EMAIL: str = Field(
        default="admin@example.com", description="Default admin email"
    )
    ADMIN_PASSWORD: str = Field(
        ..., description="Admin password (required, set via ADMIN_PASSWORD env var)"
    )

    # Metrics (Prometheus scrape endpoint)
    METRICS_USERNAME: str | None = Field(
        default=None,
        description="Basic auth username for /metrics (required in production)",
    )
    METRICS_PASSWORD: str | None = Field(
        default=None,
        description="Basic auth password for /metrics (required in production)",
    )

    # Public registration (disable in production)
    ALLOW_PUBLIC_REGISTRATION: bool = Field(
        default=True,
        description="Allow unauthenticated POST /auth/register",
    )

    # CORS
    CORS_ORIGINS: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8080",
        ],
        description="CORS allowed origins",
    )
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
        default=["image/jpeg", "image/png", "image/webp"],
        description="Allowed image MIME types",
    )

    # Celery / RabbitMQ
    CELERY_BROKER_URL: str = Field(
        default="amqp://guest:guest@rabbitmq:5672//",
        description="Celery broker URL (RabbitMQ)",
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://redis:6379/1",
        description="Celery result backend URL",
    )

    # Logging & Observability
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format",
    )
    OTLP_ENDPOINT: str = Field(
        default="http://tempo:4317",
        description="OTLP collector endpoint",
    )

    @model_validator(mode="after")
    def validate_production_security(self) -> Self:
        """Enforce safe defaults in production."""
        if self.ENVIRONMENT == "production":
            if "*" in self.CORS_ORIGINS:
                raise ValueError(
                    "CORS_ORIGINS must not contain '*' when ENVIRONMENT=production"
                )
            if self.CORS_CREDENTIALS and not self.CORS_ORIGINS:
                raise ValueError(
                    "CORS_ORIGINS must be a non-empty whitelist in production"
                )
            if not self.METRICS_USERNAME or not self.METRICS_PASSWORD:
                raise ValueError(
                    "METRICS_USERNAME and METRICS_PASSWORD are required in production"
                )
        if self.CORS_CREDENTIALS and "*" in self.CORS_ORIGINS:
            raise ValueError(
                "CORS_ORIGINS cannot be '*' when CORS_CREDENTIALS is enabled"
            )
        return self

    def is_cors_origin_allowed(self, origin: str | None) -> bool:
        """Return True if the request Origin is allowed."""
        if not origin:
            return False
        if "*" in self.CORS_ORIGINS:
            return True
        return origin in self.CORS_ORIGINS


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance. Loads from env via pydantic-settings."""
    return Settings()


# Global settings instance
settings = get_settings()
