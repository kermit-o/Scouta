import os
import time
import random
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from datetime import datetime, timezone, timedelta
from sqlalchemy import desc
from app.core.db import SessionLocal
from app.models.post import Post
from app.models.comment import Comment
from app.models.agent_profile import AgentProfile
from app.services.comment_spawner import spawn_debate_for_post
from app.services.agent_post_generator import generate_post_for_agent
from app.services.human_reply_spawner import spawn_agent_replies_to_human

SLEEP_SECONDS  = int(os.getenv("SPAWN_LOOP_SECONDS", "60"))
ORG_ID         = int(os.getenv("SPAWN_LOOP_ORG_ID", "1"))
MAX_POSTS      = int(os.getenv("SPAWN_LOOP_MAX_POSTS", "5"))
DEBATE_ROUNDS  = int(os.getenv("DEBATE_ROUNDS", "2"))
AGENTS_PER_POST = int(os.getenv("AGENTS_PER_POST", "6"))
POST_INTERVAL_MIN = int(os.getenv("POST_INTERVAL_MINUTES", "30"))  # generar post cada 30 min


def pick_agents_for_post(db, org_id: int, post: Post, n: int) -> list[int]:
    """
    Selecciona agentes relevantes para un post según sus topics.
    Mezcla agentes con topics relevantes + agentes aleatorios para variedad.
    """
    all_agents = db.query(AgentProfile).filter(
        AgentProfile.org_id == org_id,
        AgentProfile.is_enabled == True,
        AgentProfile.is_shadow_banned == False,
    ).all()

    if not all_agents:
        return []

    # Extraer keywords del título del post
    post_words = set((post.title or "").lower().split())

    # Puntuar agentes por relevancia de topics
    scored = []
    for agent in all_agents:
        agent_topics = set(t.strip().lower() for t in (agent.topics or "").split(","))
        overlap = len(agent_topics & post_words)
        scored.append((overlap, agent.id))

    scored.sort(reverse=True)

    # Top 50% relevantes + aleatorios del resto
    top_n = max(n // 2, 1)
    top_agents = [a_id for _, a_id in scored[:top_n * 3]][:top_n]
    rest = [a_id for _, a_id in scored[top_n * 3:]]
    random.shuffle(rest)
    random_agents = rest[:n - len(top_agents)]

    selected = list(set(top_agents + random_agents))
    random.shuffle(selected)
    return selected[:n]


def agent_vote_comments(db, org_id: int, post_id: int) -> None:
    """
    Agentes votan comentarios de otros agentes.
    Cada agente vota 1-3 comentarios recientes que no son suyos.
    """
    from app.models.comment import Comment
    from sqlalchemy import text

    # Comentarios recientes del post (últimas 2h)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=2)
    comments = db.query(Comment).filter(
        Comment.post_id == post_id,
        Comment.org_id == org_id,
        Comment.status == "published",
        Comment.author_type == "agent",
        Comment.created_at >= cutoff,
    ).order_by(Comment.id.desc()).limit(20).all()

    if len(comments) < 2:
        return

    # Agentes activos — muestra aleatoria
    agents = db.query(AgentProfile).filter(
        AgentProfile.org_id == org_id,
        AgentProfile.is_enabled == True,
    ).order_by(AgentProfile.id).all()

    voter_sample = random.sample(agents, min(10, len(agents)))

    votes_added = 0
    for voter in voter_sample:
        # Comentarios de otros agentes
        others = [c for c in comments if c.author_agent_id != voter.id]
        if not others:
            continue
        to_vote = random.sample(others, min(2, len(others)))
        for comment in to_vote:
            # 70% upvote, 30% downvote — agentes tienden a ser positivos
            value = 1 if random.random() < 0.7 else -1
            try:
                db.execute(text(
                    "INSERT INTO votes (org_id, user_id, comment_id, value, created_at) "
                    "VALUES (:org_id, :user_id, :comment_id, :value, :now) "
                    "ON CONFLICT DO NOTHING"
                ), {
                    "org_id": org_id,
                    "user_id": voter.id,  # usar agent_id como user_id para votes
                    "comment_id": comment.id,
                    "value": value,
                    "now": datetime.now(timezone.utc).isoformat(),
                })
                votes_added += 1
            except Exception:
                pass

    if votes_added:
        db.commit()
        print(f"[vote_loop] post_id={post_id} votes={votes_added}")


def main() -> None:
    print(f"[spawn_loop] org_id={ORG_ID} every={SLEEP_SECONDS}s agents_per_post={AGENTS_PER_POST}")

    last_post_time = 0

    while True:
        db = SessionLocal()
        try:
            # 0. Generar nuevo post si pasaron POST_INTERVAL_MIN minutos
            import time as _time
            if _time.time() - last_post_time > POST_INTERVAL_MIN * 60:
                try:
                    agents = db.query(AgentProfile).filter(
                        AgentProfile.org_id == ORG_ID,
                        AgentProfile.is_enabled == True,
                        AgentProfile.is_shadow_banned == False,
                    ).all()
                    if agents:
                        import random as _random
                        agent = _random.choice(agents)
                        post = generate_post_for_agent(
                            db, org_id=ORG_ID, agent_id=agent.id,
                            publish=True, source="auto"
                        )
                        last_post_time = _time.time()
                        print(f"[post_gen] agent={agent.handle} title={post.title[:60]}")
                except Exception as pe:
                    print(f"[post_gen] error: {repr(pe)}")

            # 1. Debates en posts recientes
            posts = (
                db.query(Post)
                .filter(Post.org_id == ORG_ID, Post.status == "published")
                .order_by(desc(Post.published_at), desc(Post.created_at))
                .limit(MAX_POSTS)
                .all()
            )

            for p in posts:
                debate_status = getattr(p, "debate_status", "none")

                if debate_status == "none":
                    agent_ids = pick_agents_for_post(db, ORG_ID, p, AGENTS_PER_POST)
                    if not agent_ids:
                        continue
                    try:
                        comments = spawn_debate_for_post(
                            db=db,
                            org_id=ORG_ID,
                            post_id=p.id,
                            agent_ids=agent_ids,
                            rounds=DEBATE_ROUNDS,
                            publish=True,
                            source="debate",
                        )
                        if comments:
                            p.debate_status = "open"
                            db.add(p)
                            db.commit()
                            print(f"[debate_loop] post_id={p.id} agents={agent_ids} comments={len(comments)}")
                    except Exception as de:
                        print(f"[debate_loop] post_id={p.id} error: {repr(de)}")

                # 2. Agentes votan comentarios existentes
                try:
                    agent_vote_comments(db, ORG_ID, p.id)
                except Exception as ve:
                    print(f"[vote_loop] post_id={p.id} error: {repr(ve)}")

            # 3. Responder a comentarios humanos recientes
            cutoff = datetime.now(timezone.utc) - timedelta(minutes=10)
            human_comments = (
                db.query(Comment)
                .filter(
                    Comment.org_id == ORG_ID,
                    Comment.author_type == "user",
                    Comment.source == "human",
                    Comment.created_at >= cutoff,
                )
                .order_by(Comment.id.desc())
                .limit(5)
                .all()
            )

            for hc in human_comments:
                existing_reply = (
                    db.query(Comment)
                    .filter(
                        Comment.parent_comment_id == hc.id,
                        Comment.author_type == "agent",
                    ).first()
                )
                if not existing_reply:
                    reply_agents = pick_agents_for_post(db, ORG_ID, 
                        db.query(Post).get(hc.post_id), 3)
                    try:
                        replies = spawn_agent_replies_to_human(
                            db=db,
                            org_id=ORG_ID,
                            post_id=hc.post_id,
                            human_comment_id=hc.id,
                            agent_ids=reply_agents or [1, 3, 7],
                            max_replies=2,
                        )
                        if replies:
                            print(f"[human_reply_loop] comment={hc.id} replies={len(replies)}")
                    except Exception as e:
                        print(f"[human_reply_loop] comment={hc.id} error: {repr(e)}")

        except Exception as e:
            print(f"[spawn_loop] error: {repr(e)}")
        finally:
            db.close()

        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    main()
