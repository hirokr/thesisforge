from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models import Agent
from app.seeds.agents import DEFAULT_AGENTS, seed_default_agents


def test_seed_default_agents_is_idempotent() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        first_count = seed_default_agents(db)
        second_count = seed_default_agents(db)
        agents = db.scalars(select(Agent)).all()

    assert first_count == len(DEFAULT_AGENTS)
    assert second_count == 0
    assert len(agents) == len(DEFAULT_AGENTS)
    assert {agent.slug for agent in agents} == {agent.slug for agent in DEFAULT_AGENTS}
