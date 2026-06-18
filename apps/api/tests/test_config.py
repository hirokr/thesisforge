import pytest
from pydantic import ValidationError

from app.core.config import Settings, required_missing_settings, validate_startup_settings


def test_development_settings_do_not_require_external_secrets() -> None:
    settings = Settings(app_env="development", supabase_jwt_secret="", openai_api_key="")

    assert required_missing_settings(settings) == []
    validate_startup_settings(settings)


def test_production_settings_report_missing_required_variables() -> None:
    settings = Settings(app_env="production", database_url="", supabase_jwt_secret="", openai_api_key="")

    assert required_missing_settings(settings) == ["DATABASE_URL", "SUPABASE_JWT_SECRET", "OPENAI_API_KEY"]
    with pytest.raises(RuntimeError, match="DATABASE_URL, SUPABASE_JWT_SECRET, OPENAI_API_KEY"):
        validate_startup_settings(settings)


def test_rate_limit_settings_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        Settings(rate_limit_window_seconds=0)


def test_plain_postgres_url_uses_installed_psycopg_driver() -> None:
    settings = Settings(database_url="postgresql://user:password@localhost/thesisforge")

    assert settings.database_url == "postgresql+psycopg://user:password@localhost/thesisforge"
