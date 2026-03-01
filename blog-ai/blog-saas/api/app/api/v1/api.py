
"""
API Router principal - Combina todos los routers
"""
from fastapi import APIRouter

from app.api.v1 import auth, posts, orgs, auto_posts, debate, comments, notifications, profile, agents, billing
from app.api.v1.debates import router as debates_router

api_router = APIRouter()

# Incluir todos los routers
api_router.include_router(auth.router, prefix="", tags=["auth"])
api_router.include_router(orgs.router, prefix="", tags=["orgs"])
api_router.include_router(posts.router, prefix="", tags=["posts"])
api_router.include_router(debate.router)
api_router.include_router(auto_posts.router, prefix="/auto-posts", tags=["auto-posts"])

api_router.include_router(comments.router)
api_router.include_router(notifications.router)
api_router.include_router(profile.router)
api_router.include_router(agents.router)
api_router.include_router(billing.router)
api_router.include_router(debates_router)
