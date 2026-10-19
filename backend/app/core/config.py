"""Application configuration settings using Pydantic Settings."""

from functools import lru_cache
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with safe local defaults and Phase 2 limits."""

    app_name: str = "RepoSense AI Backend"
    app_version: str = "0.3.0"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    cors_origins: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
    ]
    log_level: str = "INFO"
    phase: str = "Phase 3 - Testing, Security & Release"

    # GitHub ingestion & resource limits
    github_token: Union[str, None] = None
    max_tree_entries: int = 5000
    max_file_size_bytes: int = 1_048_576  # 1 MB
    max_total_source_bytes: int = 25_000_000  # 25 MB
    max_files_processed: int = 600
    request_timeout_seconds: float = 30.0

    # AI Provider settings
    ai_provider: str = "none"  # "none", "gemini", "openai", "anthropic", "ollama"
    ai_api_key: Union[str, None] = None
    ai_model: Union[str, None] = None
    ai_api_base: Union[str, None] = None

    # Storage & cache
    sqlite_db_path: str = "reposense_cache.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse comma-separated string into a list of allowed origins."""
        if isinstance(v, str) and not v.startswith("["):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return [str(origin).strip() for origin in v if str(origin).strip()]
        return v


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings instance."""
    return Settings()
