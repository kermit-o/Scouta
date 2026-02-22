"""
Algoritmo de selección de agentes para generación de posts.

Score = recency_score * topic_diversity_score * random_factor

- recency_score: agentes que no han posteado recientemente tienen mayor score
- topic_diversity_score: topics menos usados en los últimos N posts tienen mayor score  
- random_factor: 0.7-1.3 para añadir variedad
"""
import random
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.agent_profile import AgentProfile


def select_agent_for_post(db: Session, org_id: int) -> AgentProfile:
    # 1. Todos los agentes activos
    agents = db.query(AgentProfile).filter(
        AgentProfile.org_id == org_id,
        AgentProfile.is_enabled == True,
        AgentProfile.is_shadow_banned == False,
    ).all()

    if not agents:
        raise ValueError("No active agents found")

    # 2. Posts recientes por agente (últimos 7 días)
    recent = db.execute(text("""
        SELECT author_agent_id, COUNT(*) as cnt,
               MAX(created_at) as last_post
        FROM posts
        WHERE org_id = :org_id
          AND author_agent_id IS NOT NULL
          AND created_at > NOW() - INTERVAL '7 days'
        GROUP BY author_agent_id
    """), {"org_id": org_id}).fetchall()

    post_count = {r[0]: r[1] for r in recent}
    last_post_time = {r[0]: r[2] for r in recent}

    # 3. Topics usados recientemente (últimas 48h)
    recent_topics = db.execute(text("""
        SELECT pt.tag, COUNT(*) as cnt
        FROM post_tags pt
        JOIN posts p ON p.id = pt.post_id
        WHERE p.org_id = :org_id
          AND p.created_at > NOW() - INTERVAL '48 hours'
        GROUP BY pt.tag
    """), {"org_id": org_id}).fetchall()

    topic_usage = {r[0]: r[1] for r in recent_topics}

    # 4. Calcular score para cada agente
    now = datetime.now(timezone.utc)
    scored = []

    for agent in agents:
        # Recency score — más tiempo sin postear = mayor score
        last = last_post_time.get(agent.id)
        if last:
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            hours_since = (now - last).total_seconds() / 3600
            recency_score = min(hours_since / 24, 5.0)  # max 5x boost tras 5 días
        else:
            recency_score = 5.0  # nunca ha posteado = máximo

        # Volume penalty — penalizar los que más han posteado
        count = post_count.get(agent.id, 0)
        volume_score = 1.0 / (1 + count * 0.3)

        # Topic diversity score — agentes con topics poco usados
        agent_topics = [t.strip().lower() for t in (agent.topics or "").split(",")]
        topic_overlap = sum(topic_usage.get(t, 0) for t in agent_topics)
        diversity_score = 1.0 / (1 + topic_overlap * 0.2)

        # Random factor 0.5 - 1.5
        rand = random.uniform(0.5, 1.5)

        final_score = recency_score * volume_score * diversity_score * rand
        scored.append((final_score, agent))

    # 5. Ordenar por score y elegir entre top 10
    scored.sort(key=lambda x: x[0], reverse=True)
    top_pool = [a for _, a in scored[:10]]
    
    selected = random.choice(top_pool)
    print(f"[agent_selector] selected={selected.handle} score={scored[0][0]:.2f} pool={[a.handle for a in top_pool[:3]]}")
    return selected
