"""
Post Generator — usa generate_post_for_agent con LLMClient (Qwen + DeepSeek fallback)
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.post import Post
from app.models.agent_profile import AgentProfile

from app.core.logging import get_logger

log = get_logger(__name__)


class PostGenerator:
    def __init__(self, db: Session):
        self.db = db

    def generate_and_save_post(self, org_id: int, agent_id: int) -> Optional[Post]:
        from app.services.agent_post_generator import generate_post_for_agent
        try:
            post = generate_post_for_agent(
                db=self.db,
                org_id=org_id,
                agent_id=agent_id,
                publish=True,
            )
            return post
        except Exception as e:
            log.error("post_generate_failed", error=str(e))
            return None

    def generate_multiple_posts(self, org_id: int, agent_ids: List[int], num_posts: int) -> List[Post]:
        import random
        posts = []
        agents = list(agent_ids)
        random.shuffle(agents)
        for agent_id in agents[:num_posts]:
            post = self.generate_and_save_post(org_id, agent_id)
            if post:
                posts.append(post)
                log.info("post_generated", post_id=post.id, title=post.title[:60], status=post.status)
        return posts
