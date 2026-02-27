"""
Post Generator — usa generate_post_for_agent con LLMClient (Qwen + DeepSeek fallback)
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.post import Post
from app.models.agent_profile import AgentProfile


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
            print(f"❌ PostGenerator.generate_and_save_post error: {e}")
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
                print(f"✅ Post generado: #{post.id} '{post.title[:60]}' status={post.status}")
        return posts
