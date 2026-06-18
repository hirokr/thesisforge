from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_compose_builds_demo_assets_and_runs_analysis_worker() -> None:
    compose = yaml.safe_load((REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
    services = compose["services"]

    assert services["api"]["build"] == {"context": ".", "dockerfile": "apps/api/Dockerfile"}
    assert services["worker"]["build"] == services["api"]["build"]
    assert services["worker"]["command"] == [
        "rq",
        "worker",
        "thesisforge-analysis",
        "--url",
        "redis://redis:6379/0",
    ]


def test_rls_migration_supports_standalone_postgres() -> None:
    migration = (REPO_ROOT / "apps/api/alembic/versions/20260617_0002_rls_policies.py").read_text(encoding="utf-8")

    assert "CREATE SCHEMA IF NOT EXISTS auth" in migration
    assert "CREATE OR REPLACE FUNCTION auth.uid()" in migration
