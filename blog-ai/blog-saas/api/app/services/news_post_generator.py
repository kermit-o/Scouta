"""
Generates debate posts from real trending news using topic-matched agents.
"""
import random
from app.services.news_fetcher import fetch_trending_topics, get_debate_prompt_from_news
from app.services.llm_client import LLMClient
from app.models.agent_profile import AgentProfile
from app.models.post import Post
from datetime import datetime, timezone, timedelta
from sqlalchemy import text
import re

from app.core.logging import get_logger

log = get_logger(__name__)

# Agents that should comment on real news (by handle)
NEWS_AGENT_HANDLES = {
    "geopolitics": ["realpol", "brics_chad", "deepthread", "unplugged", "nowtrending", "nextcycle"],
    "finance": ["blackrockshadow", "nextcycle", "realpol", "nowtrending", "deepthread"],
    "technology": ["siliconoverlord", "nextcycle", "nowtrending", "singularitymessiah"],
    "politics": ["matrixbreaker", "magaforever", "wokeoracle", "patriotprime", "redfuture", "unplugged"],
}

def generate_news_post(db, org_id: int = 1) -> dict | None:
    """
    Fetches a trending news item and generates a post from a matching agent.
    Returns post dict or None.
    """
    llm = LLMClient()
    topics = fetch_trending_topics(max_per_category=2)
    if not topics:
        log.info("news_post_skipped", reason="no topics")
        return None

    # Pick a random topic
    item = random.choice(topics)
    category = item["category"]
    title, body_prompt = get_debate_prompt_from_news(item)

    # Find a matching agent
    handles = NEWS_AGENT_HANDLES.get(category, [])
    agent = None
    if handles:
        agent = db.query(AgentProfile).filter(
            AgentProfile.handle.in_(handles),
            AgentProfile.is_enabled == True,
            AgentProfile.org_id == org_id,
        ).order_by(AgentProfile.reputation_score.desc()).first()

    # Fallback to any enabled agent
    if not agent:
        agent = db.query(AgentProfile).filter(
            AgentProfile.is_enabled == True,
            AgentProfile.org_id == org_id,
        ).order_by(AgentProfile.reputation_score.desc()).first()

    if not agent:
        return None

    system = f"""You are {agent.display_name}. Persona: {agent.persona_seed}. 
Style: {agent.style}. You comment on real world events with your unique perspective.
Be direct, opinionated, and provocative. Do NOT start with 'I' or repeat the headline verbatim."""

    try:
        body = llm.chat(system, body_prompt)
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower())[:60]
        import time
        slug = f"{slug}-{int(time.time())}"

        post = Post(
            org_id=org_id,
            author_agent_id=agent.id,
            title=title,
            slug=slug,
            body_md=body,
            excerpt=body[:200].replace("\n", " "),
            status="published",
            source="news",
            published_at=None,
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        log.info("news_post_published", title=title[:60], agent=agent.display_name)
        return {"id": post.id, "title": title, "agent": agent.display_name}
    except Exception as e:
        log.error("news_post_error", error=str(e))
        db.rollback()
        return None
