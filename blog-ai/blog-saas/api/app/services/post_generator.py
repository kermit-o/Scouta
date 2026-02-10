
"""
Post Generator ULTRA SIMPLE - Versión que SEGURO funciona
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
import json

from app.models.post import Post


class PostGenerator:
    """Genera posts simples que SEGURO funcionan"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_and_save_post(self, org_id: int, agent_id: int) -> Optional[Post]:
        """
        Genera un post ULTRA simple que funciona
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        # Crear post CORRECTAMENTE según el modelo Post actual
        post = Post(
            org_id=org_id,
            author_type="agent",
            author_user_id=None,
            author_agent_id=agent_id,
            title=f"Post auto generado {timestamp}",
            slug=f"post-auto-{datetime.utcnow().strftime('%H%M%S')}",
            body_md=f"""# Post generado automáticamente

Generado el: {timestamp}

Este post fue creado automáticamente por el sistema.
Funciona correctamente con el modelo actual de Post.

## Detalles:
- Org ID: {org_id}
- Agent ID: {agent_id}
- Timestamp: {timestamp}""",
            excerpt=f"Post automático generado el {timestamp}",
            status="published",
            published_at=datetime.utcnow(),
            post_metadata=json.dumps({
                "generated": True,
                "source": "ultra_simple_generator",
                "timestamp": timestamp,
                "org_id": org_id,
                "agent_id": agent_id
            })
        )
        
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        
        print(f"✓ Post ULTRA simple generado: {post.title}")
        return post
