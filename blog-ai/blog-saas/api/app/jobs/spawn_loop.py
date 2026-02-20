import os
import time
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
from app.services.action_spawner import spawn_actions_for_post
from app.services.comment_spawner import spawn_debate_for_post
from app.services.human_reply_spawner import spawn_agent_replies_to_human

SLEEP_SECONDS   = int(os.getenv("SPAWN_LOOP_SECONDS", "60"))
ORG_ID          = int(os.getenv("SPAWN_LOOP_ORG_ID", "1"))
MAX_POSTS       = int(os.getenv("SPAWN_LOOP_MAX_POSTS", "5"))
N               = int(os.getenv("SPAWN_LOOP_N", "3"))
DEBATE_AGENT_IDS = [int(x) for x in os.getenv("DEBATE_AGENT_IDS", "1,3,7").split(",")]
DEBATE_ROUNDS   = int(os.getenv("DEBATE_ROUNDS", "2"))


def main() -> None:
    print(f"[spawn_loop] org_id={ORG_ID} every={SLEEP_SECONDS}s max_posts={MAX_POSTS} n={N}")
    print(f"[debate_loop] agents={DEBATE_AGENT_IDS} rounds={DEBATE_ROUNDS}")

    while True:
        db = SessionLocal()
        try:
            # 1. Spawn actions + debates automáticos
            posts = (
                db.query(Post)
                .filter(Post.org_id == ORG_ID, Post.status == "published")
                .order_by(desc(Post.published_at), desc(Post.created_at))
                .limit(MAX_POSTS)
                .all()
            )
            for p in posts:
                created = spawn_actions_for_post(db, org_id=ORG_ID, post_id=p.id, max_n=N)
                if created:
                    print(f"[spawn_loop] post_id={p.id} actions={[a.id for a in created]}")

                debate_status = getattr(p, "debate_status", "none")
                if debate_status == "none":
                    try:
                        comments = spawn_debate_for_post(
                            db=db,
                            org_id=ORG_ID,
                            post_id=p.id,
                            agent_ids=DEBATE_AGENT_IDS,
                            rounds=DEBATE_ROUNDS,
                            publish=True,
                            source="debate",
                        )
                        if comments:
                            p.debate_status = "open"
                            db.add(p)
                            db.commit()
                            print(f"[debate_loop] post_id={p.id} comments={len(comments)} debate=open")
                    except Exception as de:
                        print(f"[debate_loop] post_id={p.id} error: {repr(de)}")

            # 2. Responder a comentarios humanos recientes (últimos 10 min)
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
                    )
                    .first()
                )
                if not existing_reply:
                    try:
                        replies = spawn_agent_replies_to_human(
                            db=db,
                            org_id=ORG_ID,
                            post_id=hc.post_id,
                            human_comment_id=hc.id,
                            agent_ids=DEBATE_AGENT_IDS,
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
