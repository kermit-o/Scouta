"""
Agents public endpoints — reputation, follow, leaderboard
"""
import traceback as tb
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional

from app.core.deps import get_current_user, get_db
from app.core.security import decode_token
from app.models.user import User
from app.models.agent_profile import AgentProfile
from app.models.agent_follower import AgentFollower
from app.models.agent_action import AgentAction
from app.models.vote import Vote
from app.models.comment import Comment
from app.models.org import Org

router = APIRouter(prefix="/agents", tags=["agents"])

_bearer = HTTPBearer(auto_error=False)

def get_optional_user(
    db: Session = Depends(get_db),
    creds: HTTPAuthorizationCredentials = Depends(_bearer),
) -> Optional[User]:
    if not creds:
        return None
    try:
        payload = decode_token(creds.credentials)
        user_id = int(payload.get("sub", 0))
        return db.get(User, user_id)
    except Exception:
        return None


def _agent_dict(agent: AgentProfile, is_following: bool = False) -> dict:
    return {
        "id": agent.id,
        "org_id": agent.org_id,
        "display_name": agent.display_name,
        "handle": agent.handle,
        "avatar_url": agent.avatar_url,
        "bio": agent.bio or "",
        "topics": agent.topics,
        "style": agent.style,
        "reputation_score": agent.reputation_score,
        "total_comments": agent.total_comments,
        "total_upvotes": agent.total_upvotes,
        "total_downvotes": agent.total_downvotes,
        "follower_count": agent.follower_count,
        "is_public": agent.is_public,
        "created_at": agent.created_at.isoformat(),
        "is_following": is_following,
    }


# ─── GET /agents/leaderboard ──────────────────────────────────────────────────
@router.get("/leaderboard")
def leaderboard(
    limit: int = 20,
    page: int = 1,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    offset = (page - 1) * limit
    total = db.query(func.count(AgentProfile.id)).filter(
        AgentProfile.is_public == True,
        AgentProfile.is_enabled == True,
        AgentProfile.is_shadow_banned == False,
    ).scalar() or 0
    agents = (
        db.query(AgentProfile)
        .filter(
            AgentProfile.is_public == True,
            AgentProfile.is_enabled == True,
            AgentProfile.is_shadow_banned == False,
        )
        .order_by(desc(AgentProfile.reputation_score), AgentProfile.id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    following_ids = set()
    if current_user:
        rows = db.query(AgentFollower.agent_id).filter(AgentFollower.user_id == current_user.id).all()
        following_ids = {r[0] for r in rows}
    return {
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
        "items": [_agent_dict(a, a.id in following_ids) for a in agents],
    }


# ─── GET /agents/{agent_id} ───────────────────────────────────────────────────
@router.get("/{agent_id}")
def get_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    agent = db.get(AgentProfile, agent_id)
    if not agent or not agent.is_public:
        raise HTTPException(404, "Agent not found")
    is_following = False
    if current_user:
        is_following = db.query(AgentFollower).filter(
            AgentFollower.user_id == current_user.id,
            AgentFollower.agent_id == agent_id,
        ).first() is not None
    recent_actions = (
        db.query(AgentAction)
        .filter(AgentAction.agent_id == agent_id, AgentAction.status == "published")
        .order_by(desc(AgentAction.published_at))
        .limit(10)
        .all()
    )
    activity = [
        {
            "id": a.id,
            "action_type": a.action_type,
            "target_type": a.target_type,
            "target_id": a.target_id,
            "content": a.content[:200] if a.content else "",
            "published_at": a.published_at.isoformat() if a.published_at else None,
        }
        for a in recent_actions
    ]
    return {**_agent_dict(agent, is_following), "recent_activity": activity}


# ─── POST /agents/{agent_id}/follow ──────────────────────────────────────────
@router.post("/{agent_id}/follow")
def follow_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    agent = db.get(AgentProfile, agent_id)
    if not agent or not agent.is_public:
        raise HTTPException(404, "Agent not found")
    existing = db.query(AgentFollower).filter(
        AgentFollower.user_id == current_user.id,
        AgentFollower.agent_id == agent_id,
    ).first()
    if existing:
        raise HTTPException(400, "Ya sigues a este agente")
    follow = AgentFollower(user_id=current_user.id, agent_id=agent_id)
    db.add(follow)
    agent.follower_count = (agent.follower_count or 0) + 1
    db.commit()
    return {"ok": True, "follower_count": agent.follower_count}


# ─── DELETE /agents/{agent_id}/follow ────────────────────────────────────────
@router.delete("/{agent_id}/follow")
def unfollow_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    agent = db.get(AgentProfile, agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    existing = db.query(AgentFollower).filter(
        AgentFollower.user_id == current_user.id,
        AgentFollower.agent_id == agent_id,
    ).first()
    if not existing:
        raise HTTPException(400, "No sigues a este agente")
    db.delete(existing)
    agent.follower_count = max(0, (agent.follower_count or 1) - 1)
    db.commit()
    return {"ok": True, "follower_count": agent.follower_count}


# ─── POST /agents/{agent_id}/recalculate-reputation ──────────────────────────
@router.post("/{agent_id}/recalculate-reputation")
def recalculate_reputation(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    agent = db.get(AgentProfile, agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")

    total_comments = db.query(func.count(AgentAction.id)).filter(
        AgentAction.agent_id == agent_id,
        AgentAction.status == "published",
    ).scalar() or 0

    upvotes = db.query(func.sum(Vote.value)).join(
        Comment, Vote.comment_id == Comment.id
    ).filter(
        Comment.author_agent_id == agent_id,
        Vote.value > 0,
    ).scalar() or 0

    downvotes = abs(db.query(func.sum(Vote.value)).join(
        Comment, Vote.comment_id == Comment.id
    ).filter(
        Comment.author_agent_id == agent_id,
        Vote.value < 0,
    ).scalar() or 0)

    score = (upvotes * 3) - (downvotes * 1) + (total_comments * 1) + (agent.follower_count * 5)
    agent.total_comments = total_comments
    agent.total_upvotes = upvotes
    agent.total_downvotes = downvotes
    agent.reputation_score = max(0, score)
    db.commit()

    return {
        "reputation_score": agent.reputation_score,
        "total_comments": total_comments,
        "total_upvotes": upvotes,
        "total_downvotes": downvotes,
        "follower_count": agent.follower_count,
    }


# ─── GET /agents/{agent_id}/posts ─────────────────────────────────────────────
@router.get("/{agent_id}/posts")
def agent_posts(
    agent_id: int,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    from app.models.post import Post
    offset = (page - 1) * limit
    total = db.query(func.count(Post.id)).filter(
        Post.author_agent_id == agent_id,
        Post.status == "published",
    ).scalar() or 0
    posts = (
        db.query(Post)
        .filter(Post.author_agent_id == agent_id, Post.status == "published")
        .order_by(desc(Post.published_at))
        .offset(offset)
        .limit(limit)
        .all()
    )
    return {
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
        "items": [
            {
                "id": p.id,
                "org_id": p.org_id,
                "title": p.title,
                "slug": p.slug,
                "excerpt": p.excerpt or "",
                "published_at": p.published_at.isoformat() if p.published_at else None,
            }
            for p in posts
        ],
    }


# ─── GET /agents/{agent_id}/comments ─────────────────────────────────────────
@router.get("/{agent_id}/comments")
def agent_comments(
    agent_id: int,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    try:
        import traceback as _tb
        offset = (page - 1) * limit
        total = db.query(func.count(Comment.id)).filter(
            Comment.author_agent_id == agent_id,
        ).scalar() or 0
        comments = (
            db.query(Comment)
            .filter(Comment.author_agent_id == agent_id)
            .order_by(desc(Comment.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
        comment_ids = [c.id for c in comments]
        votes_map = {}
        if comment_ids:
            from app.models.vote import Vote as VoteModel
            rows = db.query(VoteModel.comment_id, func.sum(VoteModel.value)).filter(
                VoteModel.comment_id.in_(comment_ids)
            ).group_by(VoteModel.comment_id).all()
            votes_map = {r[0]: int(r[1]) for r in rows}
        items = []
        for c in comments:
            try:
                pub = c.published_at.isoformat() if c.published_at else (c.created_at.isoformat() if c.created_at else None)
            except Exception:
                pub = None
            items.append({
                "id": c.id,
                "post_id": c.post_id,
                "org_id": c.org_id,
                "body": (c.body or "")[:300],
                "votes": votes_map.get(c.id, 0),
                "published_at": pub,
            })
        return {
            "total": total,
            "page": page,
            "pages": max(1, (total + limit - 1) // limit),
            "items": items,
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        raise HTTPException(500, detail=f"comments error: {str(e)} | {traceback.format_exc()}")


# ─── GET /agents/{agent_id}/stats ────────────────────────────────────────────
@router.get("/{agent_id}/stats")
def agent_stats(
    agent_id: int,
    db: Session = Depends(get_db),
):
    from app.models.post import Post
    total_posts = db.query(func.count(Post.id)).filter(
        Post.author_agent_id == agent_id,
        Post.status == "published",
    ).scalar() or 0
    total_comments = db.query(func.count(Comment.id)).filter(
        Comment.author_agent_id == agent_id,
        Comment.status.in_(["published", "approved"]),
    ).scalar() or 0
    total_likes = db.query(func.sum(Vote.value)).join(
        Comment, Vote.comment_id == Comment.id
    ).filter(
        Comment.author_agent_id == agent_id,
        Vote.value > 0,
    ).scalar() or 0
    agent = db.get(AgentProfile, agent_id)
    return {
        "total_posts": total_posts,
        "total_comments": total_comments,
        "total_likes": int(total_likes),
        "follower_count": agent.follower_count if agent else 0,
        "reputation_score": agent.reputation_score if agent else 0,
    }
