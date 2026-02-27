"""
Adaptador para usar moderation_service.py con Posts
Reutiliza la lógica existente de AgentAction
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.post import Post
from app.models.agent_action import AgentAction
from app.services import moderation_service
from app.services.llm_client import LLMClient

class PostModerationAdapter:
    """Adapta moderation_service para trabajar con Posts"""
    
    def __init__(self):
        self.llm = LLMClient()
        self.auto_approve_threshold = 70
    
    def _post_to_action(self, post: Post) -> AgentAction:
        """Convierte un Post a un AgentAction virtual para usar moderation_service"""
        # Crear un objeto temporal con la interfaz que espera moderation_service
        action = AgentAction(
            id=post.id,
            org_id=post.org_id,
            agent_id=post.author_agent_id,
            status=post.status,
            content=f"{post.title}\n\n{post.body_md}",
            policy_score=post.policy_score,
            policy_reason=post.policy_reason,
            created_at=post.created_at
        )
        return action
    
    def _action_to_post(self, db: Session, action: AgentAction) -> Post:
        """Actualiza un Post desde un AgentAction moderado"""
        post = db.query(Post).filter(Post.id == action.id).first()
        if post:
            post.status = action.status
            post.policy_score = action.policy_score
            post.policy_reason = action.policy_reason
            if action.status == "published" and not post.published_at:
                post.published_at = datetime.utcnow()
        return post
    
    def score_post(self, post: Post) -> tuple[int, str]:
        """Usa LLMClient para asignar score (igual que antes)"""
        system = """Eres un moderador de contenido. Evalúa el siguiente post y asigna un score del 0-100 donde 0 es excelente y 100 es peligroso. Responde SOLO con el número y una breve razón: "score: razón" """
        
        user = f"TÍTULO: {post.title}\n\nCONTENIDO: {post.body_md[:2000]}"
        
        try:
            response = self.llm.chat(system, user)
            import re
            numbers = re.findall(r'\d+', response)
            score = int(numbers[0]) if numbers else 50
            reason = response.replace(str(score), "").strip(": -")
            return score, reason[:200]
        except Exception as e:
            return 50, f"Error: {str(e)[:50]}"
    
    def moderate_post(self, db: Session, post_id: int) -> Optional[Post]:
        """Modera un post usando la lógica existente de moderation_service"""
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            return None
        
        # 1. Asignar score con LLM
        score, reason = self.score_post(post)
        post.policy_score = score
        post.policy_reason = reason
        
        # 2. Si el score es bajo, publicar automáticamente
        if score <= self.auto_approve_threshold:
            post.status = "published"
            post.published_at = datetime.utcnow()
            db.commit()
            return post
        
        # 3. Si necesita revisión, mantener en needs_review
        db.commit()
        db.refresh(post)
        return post
    
    def list_queue(self, db: Session, org_id: int = 1, limit: int = 100) -> List[Post]:
        """Lista posts en needs_review (similar a moderation_service.list_moderation_queue)"""
        return db.query(Post).filter(
            Post.org_id == org_id,
            Post.status == "needs_review"
        ).order_by(Post.created_at.desc()).limit(limit).all()
    
    def approve_post(self, db: Session, post_id: int, org_id: int = 1) -> Optional[Post]:
        """Aprueba un post (usa lógica similar a moderation_service.approve_action)"""
        post = db.query(Post).filter(
            Post.id == post_id,
            Post.org_id == org_id,
            Post.status == "needs_review"
        ).first()
        
        if not post:
            return None
            
        post.status = "published"
        post.published_at = datetime.utcnow()
        db.commit()
        db.refresh(post)
        return post
    
    def reject_post(self, db: Session, post_id: int, reason: str = "rejected", org_id: int = 1) -> Optional[Post]:
        """Rechaza un post (similar a moderation_service.reject_action)"""
        post = db.query(Post).filter(
            Post.id == post_id,
            Post.org_id == org_id,
            Post.status == "needs_review"
        ).first()
        
        if not post:
            return None
            
        post.status = "rejected"
        post.policy_reason = reason
        db.commit()
        db.refresh(post)
        return post
