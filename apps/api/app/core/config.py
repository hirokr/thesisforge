from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


PRODUCTION_ENVS = {"production", "staging"}
PRODUCTION_REQUIRED_SETTINGS = (
    "database_url",
    "supabase_jwt_secret",
    "openai_api_key",
)


class Settings(BaseSettings):
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    frontend_origin: str = "http://localhost:3000"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/thesisforge"
    supabase_url: str = ""
    supabase_jwt_secret: str = ""
    supabase_jwt_audience: str = "authenticated"
    upload_storage_dir: str = "storage/uploads"
    openai_api_key: str = ""
    openai_base_url: str = ""
    llm_default_provider: str = "openai"
    llm_default_model: str = "gpt-4.1-mini"
    band_api_base_url: str = "https://app.band.ai/api/v1/agent"
    band_api_key: str = ""
    band_project_id: str = ""
    redis_url: str = "redis://localhost:6379/0"
    analysis_queue_name: str = "thesisforge-analysis"
    analysis_job_timeout_seconds: int = Field(default=1800, ge=1)
    rate_limit_window_seconds: int = Field(default=60, ge=1)
    rate_limit_file_uploads_per_window: int = Field(default=60, ge=1)
    rate_limit_analysis_runs_per_window: int = Field(default=20, ge=1)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("database_url", mode="before")
    @classmethod
    def use_psycopg_driver(cls, value: object) -> object:
        if isinstance(value, str) and value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value


def validate_startup_settings(settings: Settings) -> None:
    missing = required_missing_settings(settings)
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(f"Missing required backend environment variable(s) for {settings.app_env}: {joined}")


def required_missing_settings(settings: Settings) -> list[str]:
    if settings.app_env.lower() not in PRODUCTION_ENVS:
        return []

    missing: list[str] = []
    for setting_name in PRODUCTION_REQUIRED_SETTINGS:
        value = getattr(settings, setting_name)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(setting_name.upper())
    return missing


@lru_cache
def get_settings() -> Settings:
    return Settings()
