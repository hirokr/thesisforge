from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    frontend_origin: str = "http://localhost:3000"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/thesisforge"
    supabase_jwt_secret: str = ""
    supabase_jwt_audience: str = "authenticated"
    upload_storage_dir: str = "storage/uploads"
    openai_api_key: str = ""
    llm_default_provider: str = "openai"
    llm_default_model: str = "gpt-4.1-mini"
    band_api_base_url: str = "https://app.band.ai/api/v1/agent"
    band_api_key: str = ""
    band_project_id: str = ""
    redis_url: str = "redis://localhost:6379/0"
    analysis_queue_name: str = "thesisforge-analysis"
    analysis_job_timeout_seconds: int = 1800

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
