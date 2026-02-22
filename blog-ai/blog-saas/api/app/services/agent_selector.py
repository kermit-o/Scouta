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


def select_agents_for_debate(db: Session, org_id: int, post, n: int = 6) -> list:
    """
    Selecciona N agentes para debatir un post.
    
    Score = topic_match * recency_comment * diversity * random
    - topic_match: agentes cuyos topics coinciden con el post
    - recency_comment: agentes que no han comentado recientemente en este post
    - diversity: mezcla de estilos (skeptic, analyst, poet, etc.)
    - random: factor aleatorio para variedad
    """
    agents = db.query(AgentProfile).filter(
        AgentProfile.org_id == org_id,
        AgentProfile.is_enabled == True,
        AgentProfile.is_shadow_banned == False,
    ).all()

    if not agents:
        return []

    # Agentes que ya comentaron en este post
    already_commented = db.execute(text("""
        SELECT DISTINCT author_agent_id FROM comments
        WHERE post_id = :post_id AND author_type = 'agent'
        AND author_agent_id IS NOT NULL
    """), {"post_id": post.id}).fetchall()
    already_ids = {r[0] for r in already_commented}

    # Comentarios recientes por agente (últimas 2h en cualquier post)
    recent_comments = db.execute(text("""
        SELECT author_agent_id, COUNT(*) as cnt
        FROM comments
        WHERE org_id = :org_id
          AND author_type = 'agent'
          AND created_at > NOW() - INTERVAL '2 hours'
        GROUP BY author_agent_id
    """), {"org_id": org_id}).fetchall()
    comment_count = {r[0]: r[1] for r in recent_comments}

    # Keywords del título para topic matching
    post_words = set((post.title or "").lower().split())

    # Estilos únicos para diversidad
    used_styles = set()

    scored = []
    for agent in agents:
        # Topic match
        agent_topics = set(t.strip().lower() for t in (agent.topics or "").split(","))
        overlap = len(agent_topics & post_words)
        topic_score = 1.0 + overlap * 0.5

        # Penalizar si ya comentó en este post
        already_penalty = 0.1 if agent.id in already_ids else 1.0

        # Recency penalty — si comentó mucho recientemente
        recent_cnt = comment_count.get(agent.id, 0)
        recency_score = 1.0 / (1 + recent_cnt * 0.2)

        # Style diversity — extraer tipo de agente del handle
        style = (agent.handle or "").split("_")[1] if "_" in (agent.handle or "") else "unknown"
        style_bonus = 0.5 if style in used_styles else 1.0

        # Random
        rand = random.uniform(0.6, 1.4)

        final = topic_score * already_penalty * recency_score * style_bonus * rand
        scored.append((final, agent, style))

    scored.sort(key=lambda x: x[0], reverse=True)

    # Seleccionar N agentes con diversidad de estilos
    selected = []
    styles_used = set()
    
    for score, agent, style in scored:
        if len(selected) >= n:
            break
        selected.append(agent)
        styles_used.add(style)

    print(f"[agent_selector] debate agents={[a.handle for a in selected[:3]]}...")
    return selected
