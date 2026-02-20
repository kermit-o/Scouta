import os
import time
from sqlalchemy import desc

from app.core.db import SessionLocal
from app.models.post import Post
from app.services.action_spawner import spawn_actions_for_post

SLEEP_SECONDS = int(os.getenv("SPAWN_LOOP_SECONDS", "30"))
ORG_ID = int(os.getenv("SPAWN_LOOP_ORG_ID", "1"))
MAX_POSTS = int(os.getenv("SPAWN_LOOP_MAX_POSTS", "5"))
N = int(os.getenv("SPAWN_LOOP_N", "3"))

def main() -> None:
    print(f"[spawn_loop] org_id={ORG_ID} every={SLEEP_SECONDS}s max_posts={MAX_POSTS} n={N}")
    while True:
        db = SessionLocal()
        try:
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
                    print(f"[spawn_loop] post_id={p.id} created_actions={[a.id for a in created]}")
        except Exception as e:
            print("[spawn_loop] error:", repr(e))
        finally:
            db.close()

        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    main()
