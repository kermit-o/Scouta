
"""
Post Generator Simple - Versión COMPLETA y CORRECTA
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
import json

from app.models.post import Post


class PostGeneratorSimple:
    """Generador simple que crea posts básicos"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_and_save_post(self, org_id: int, agent_id: int) -> Optional[Post]:
        """Versión que SÍ funciona"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Crear post con TODOS los campos requeridos
        post = Post(
            org_id=org_id,
            author_type="agent",
            author_user_id=None,
            author_agent_id=agent_id,
            title=f"Post automático generado {timestamp}",
            slug=f"post-auto-{datetime.now().strftime('%H%M%S')}",
            body_md=f"""# Post generado automáticamente

Generado: {timestamp}

Este es un post de prueba generado por el sistema autónomo.
Está funcionando correctamente con el modelo actual.""",
            excerpt=f"Post automático generado el {timestamp}",
            status="published",
            published_at=datetime.now(),
            post_metadata=json.dumps({
                "generated": True,
                "source": "simple_generator",
                "timestamp": timestamp,
                "agent_id": agent_id
            })
        )
        
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        
        print(f"✓ Post simple creado: {post.title}")
        return post
