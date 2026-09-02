"""Environment-based application configuration.

Secrets are represented with ``SecretStr`` so accidental logging or printing masks them.
Phase 1 does not require an API key.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated settings loaded from environment variables or a local .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "CareerPilot AI"
    app_env: str = "development"
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = Field(default=8000, ge=1, le=65535)
    database_url: str = "sqlite:///./careerpilot.db"
    openai_api_key: SecretStr | None = None
    openai_base_url: str | None = None
    openai_model: str | None = None
    max_agent_retries: int = Field(default=2, ge=0, le=10)
    llm_timeout_seconds: float = Field(default=60.0, gt=0, le=300)
    log_level: str = "INFO"
    max_upload_size_mb: int = Field(default=5, ge=1, le=50)
    rag_storage_path: Path = Path("data/rag")
    embedding_dimensions: int = Field(default=384, ge=64, le=2_048)
    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:8501"])

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        """Accept only standard Python logging levels."""

        normalized = value.upper()
        allowed_levels = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}
        if normalized not in allowed_levels:
            raise ValueError(f"LOG_LEVEL must be one of {sorted(allowed_levels)}")
        return normalized


@lru_cache
def get_settings() -> Settings:
    """Return one cached settings instance for the process."""

    return Settings()
