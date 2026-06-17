from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Agent


@dataclass(frozen=True)
class DefaultAgent:
    name: str
    slug: str
    description: str
    system_prompt: str
    default_model_provider: str = "openai"
    default_model_name: str = "gpt-4.1-mini"
    temperature: float = 0.2
    is_active: bool = True


DEFAULT_AGENTS: tuple[DefaultAgent, ...] = (
    DefaultAgent(
        name="Literature Review Agent",
        slug="literature-review",
        description="Reviews literature coverage, source quality, and positioning against related work.",
        system_prompt="You evaluate thesis literature reviews for coverage, recency, relevance, synthesis quality, and missing scholarly context.",
    ),
    DefaultAgent(
        name="Research Gap Agent",
        slug="research-gap",
        description="Finds weak, broad, unsupported, or poorly differentiated research gap statements.",
        system_prompt="You inspect thesis drafts for precise research gaps, novelty claims, and alignment between problem framing and contribution.",
    ),
    DefaultAgent(
        name="Citation Agent",
        slug="citation",
        description="Checks whether claims are supported by appropriate references and flags citation issues.",
        system_prompt="You verify citation coverage, citation relevance, claim support, and possible unsupported assertions in academic writing.",
    ),
    DefaultAgent(
        name="Methodology Consistency Agent",
        slug="methodology-consistency",
        description="Reviews method choices, data flow, evaluation design, and consistency with research questions.",
        system_prompt="You evaluate whether methodology sections are coherent, reproducible, and aligned with objectives and expected evidence.",
    ),
    DefaultAgent(
        name="Results Interpretation Agent",
        slug="results-interpretation",
        description="Assesses whether results are interpreted accurately and connected to the research questions.",
        system_prompt="You review results and discussion sections for overclaiming, missing comparisons, weak interpretation, and unsupported conclusions.",
    ),
    DefaultAgent(
        name="Defense Preparation Agent",
        slug="defense-preparation",
        description="Prepares likely defense questions, risks, and concise answer guidance.",
        system_prompt="You generate defense preparation notes by identifying methodological risks, likely examiner questions, and evidence-backed responses.",
    ),
    DefaultAgent(
        name="Report Generator Agent",
        slug="report-generator",
        description="Compiles findings into structured thesis quality reports and action plans.",
        system_prompt="You synthesize multi-agent findings into clear review reports with priorities, evidence, and actionable revision tasks.",
    ),
)


def seed_default_agents(db: Session) -> int:
    existing_slugs = set(db.scalars(select(Agent.slug)).all())
    inserted_count = 0

    for default_agent in DEFAULT_AGENTS:
        if default_agent.slug in existing_slugs:
            continue

        db.add(
            Agent(
                name=default_agent.name,
                slug=default_agent.slug,
                description=default_agent.description,
                system_prompt=default_agent.system_prompt,
                default_model_provider=default_agent.default_model_provider,
                default_model_name=default_agent.default_model_name,
                temperature=default_agent.temperature,
                is_active=default_agent.is_active,
            )
        )
        inserted_count += 1

    db.commit()
    return inserted_count
