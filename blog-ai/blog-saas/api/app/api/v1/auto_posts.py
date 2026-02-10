"""
Endpoints para generación automática de posts
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.services.post_generator_simple import PostGeneratorSimple as PostGenerator
from app.models.agent_profile import AgentProfile

router = APIRouter()

@router.post("/orgs/{org_id}/generate-post")
def generate_post_from_trends(
    org_id: int,
    agent_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Genera un post automáticamente desde tendencias
    """
    # Si no se especifica agente, usar uno aleatorio
    if not agent_id:
        agent = db.query(AgentProfile).filter(
            AgentProfile.org_id == org_id,
            AgentProfile.is_enabled == True
        ).first()
        
        if not agent:
            raise HTTPException(404, "No hay agentes activos en esta organización")
        
        agent_id = agent.id
    
    # Generar post
    generator = PostGenerator(db)
    post = generator.generate_and_save_post(org_id, agent_id)
    
    if not post:
        raise HTTPException(500, "No se pudo generar el post")
    
    return {
        "success": True,
        "post": {
            "id": post.id,
            "title": post.title,
            "excerpt": post.excerpt,
            "status": post.status
        }
    }

@router.post("/orgs/{org_id}/generate-multiple")
def generate_multiple_posts(
    org_id: int,
    count: int = 3,
    db: Session = Depends(get_db)
):
    """
    Genera múltiples posts automáticamente
    """
    # Obtener agentes activos
    agents = db.query(AgentProfile).filter(
        AgentProfile.org_id == org_id,
        AgentProfile.is_enabled == True
    ).all()
    
    if not agents:
        raise HTTPException(404, "No hay agentes activos en esta organización")
    
    agent_ids = [agent.id for agent in agents]
    
    # Generar posts
    generator = PostGenerator(db)
    posts = generator.generate_multiple_posts(org_id, agent_ids, count)
    
    return {
        "success": True,
        "generated": len(posts),
        "posts": [
            {
                "id": p.id,
                "title": p.title,
                "agent_id": p.author_agent_id
            }
            for p in posts
        ]
    }

@router.get("/trends/current")
def get_current_trends():
    """
    Obtiene tendencias actuales (sin guardar posts)
    """
    from app.services.trend_scanner import TrendScanner
    
    scanner = TrendScanner()
    trends = scanner.get_current_trends()
    
    return {
        "trends": trends,
        "count": len(trends)
    }
