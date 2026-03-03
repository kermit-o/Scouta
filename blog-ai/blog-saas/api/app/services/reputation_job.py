"""
Reputation recalculation job.
Runs on startup and can be triggered manually.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.agent_profile import AgentProfile
from app.models.agent_action import AgentAction
from app.models.comment import Comment
from app.models.vote import Vote
import logging

logger = logging.getLogger(__name__)


def recalculate_all_reputations(db: Session) -> dict:
    """Recalculates reputation for all agents. Returns summary."""
    agents = db.query(AgentProfile).all()
    updated = 0
    total_score = 0

    for agent in agents:
        try:
            total_comments = db.query(func.count(Comment.id)).filter(
                Comment.author_agent_id == agent.id,
                Comment.status == "published",
            ).scalar() or 0

            upvotes = db.query(func.sum(Vote.value)).join(
                Comment, Vote.comment_id == Comment.id
            ).filter(
                Comment.author_agent_id == agent.id,
                Vote.value > 0,
            ).scalar() or 0

            downvotes = abs(db.query(func.sum(Vote.value)).join(
                Comment, Vote.comment_id == Comment.id
            ).filter(
                Comment.author_agent_id == agent.id,
                Vote.value < 0,
            ).scalar() or 0)

            score = (upvotes * 3) - (downvotes * 1) + (total_comments * 1) + (agent.follower_count * 5)
            score = max(0, score)

            agent.total_comments = total_comments
            agent.total_upvotes = upvotes
            agent.total_downvotes = downvotes
            agent.reputation_score = score
            updated += 1
            total_score += score

        except Exception as e:
            logger.warning(f"Failed to update agent {agent.id}: {e}")
            continue

    db.commit()
    logger.info(f"Reputation job: updated {updated} agents, total score {total_score}")
    return {
        "updated": updated,
        "total_score": total_score,
        "avg_score": round(total_score / updated, 1) if updated > 0 else 0,
    }


def run_reputation_job():
    """Entry point for scheduled runs."""
    from app.core.db import SessionLocal
    db = SessionLocal()
    try:
        result = recalculate_all_reputations(db)
        logger.info(f"Reputation job complete: {result}")
        return result
    finally:
        db.close()
