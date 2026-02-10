import random
import re
from sqlalchemy.orm import Session

from app.models.agent_profile import AgentProfile

ARCHETYPES = [
    {"display_name": "The Skeptic", "style": "concise", "topics": "ai,product,truth", "risk_level": 1, "persona_seed": "Sharp, rational, challenges assumptions."},
    {"display_name": "The Builder", "style": "structured", "topics": "engineering,systems", "risk_level": 1, "persona_seed": "Pragmatic, solution-first, clear steps."},
    {"display_name": "The Poet", "style": "evocative", "topics": "culture,meaning", "risk_level": 1, "persona_seed": "Symbolic, aesthetic, metaphor-rich."},
    {"display_name": "The Contrarian", "style": "provocative", "topics": "debate,angles", "risk_level": 2, "persona_seed": "Pushes opposing viewpoints, tests ideas."},
    {"display_name": "The Analyst", "style": "technical", "topics": "data,logic", "risk_level": 1, "persona_seed": "Quant-minded, precise, evidence-based."},
]

def _slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "agent"

def _next_unique_handle(existing: set[str], base: str) -> str:
    base = _slugify(base)
    for i in range(1, 10000):
        h = f"{base}_{i:02d}"
        if h not in existing:
            existing.add(h)
            return h
    raise RuntimeError("Could not generate unique handle (exhausted)")

def create_random_agents(db: Session, org_id: int, n: int) -> list[AgentProfile]:
    # preload existing handles for org (single query)
    rows = db.query(AgentProfile.handle).filter(AgentProfile.org_id == org_id).all()
    existing_handles: set[str] = {r[0] for r in rows}

    created: list[AgentProfile] = []
    picks = [random.choice(ARCHETYPES) for _ in range(n)]

    for p in picks:
        handle = _next_unique_handle(existing_handles, p["display_name"])
        a = AgentProfile(
            org_id=org_id,
            display_name=p["display_name"],
            handle=handle,
            avatar_url="",
            persona_seed=p["persona_seed"],
            topics=p["topics"],
            style=p["style"],
            risk_level=p["risk_level"],
            is_enabled=True,
        )
        db.add(a)
        created.append(a)

    db.commit()
    for a in created:
        db.refresh(a)
    return created
