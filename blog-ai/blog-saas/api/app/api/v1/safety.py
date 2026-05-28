"""Trust & Safety endpoints: UGC reporting and account-level user blocking.

Required by App Store Guideline 1.2 and Google Play's UGC policy for apps with
user-generated content and live streaming.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, require_superuser
from app.models.user import User
from app.models.report import Report
from app.models.user_block import UserBlock

router = APIRouter(tags=["safety"])

_VALID_TARGETS = {"user", "post", "comment", "live", "message"}


class ReportIn(BaseModel):
    target_type: str
    target_id: str
    reason: str
    details: Optional[str] = None


def get_blocked_user_ids(db: Session, user_id: int) -> set[int]:
    """User ids the given user has blocked. Reusable for content filtering in
    feeds, chat, live, etc."""
    rows = db.query(UserBlock.blocked_user_id).filter(UserBlock.blocker_user_id == user_id).all()
    return {r[0] for r in rows}


@router.post("/report")
def create_report(
    payload: ReportIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    target_type = (payload.target_type or "").strip().lower()
    if target_type not in _VALID_TARGETS:
        raise HTTPException(status_code=400, detail="invalid target_type")
    if not payload.target_id or not (payload.reason or "").strip():
        raise HTTPException(status_code=400, detail="target_id and reason are required")

    # Collapse duplicate open reports from the same user on the same target.
    existing = (
        db.query(Report)
        .filter(
            Report.reporter_user_id == user.id,
            Report.target_type == target_type,
            Report.target_id == str(payload.target_id),
            Report.status == "open",
        )
        .first()
    )
    if existing:
        return {"status": "already_reported", "id": existing.id}

    report = Report(
        reporter_user_id=user.id,
        target_type=target_type,
        target_id=str(payload.target_id),
        reason=payload.reason.strip()[:50],
        details=(payload.details or None),
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    try:
        from app.services.analytics import track_event
        track_event(db, "content_reported", user_id=user.id, alert=True)
    except Exception:
        pass

    return {"status": "reported", "id": report.id}


@router.post("/users/{username}/block")
def block_user(
    username: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    target = db.query(User).filter(User.username == username).one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="user not found")
    if target.id == user.id:
        raise HTTPException(status_code=400, detail="cannot block yourself")

    existing = (
        db.query(UserBlock)
        .filter(UserBlock.blocker_user_id == user.id, UserBlock.blocked_user_id == target.id)
        .first()
    )
    if not existing:
        db.add(UserBlock(blocker_user_id=user.id, blocked_user_id=target.id))
        db.commit()
    return {"status": "blocked", "username": username}


@router.delete("/users/{username}/block")
def unblock_user(
    username: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    target = db.query(User).filter(User.username == username).one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="user not found")
    db.query(UserBlock).filter(
        UserBlock.blocker_user_id == user.id,
        UserBlock.blocked_user_id == target.id,
    ).delete()
    db.commit()
    return {"status": "unblocked", "username": username}


@router.get("/users/blocks")
def list_blocks(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ids = get_blocked_user_ids(db, user.id)
    if not ids:
        return {"blocked": []}
    rows = db.query(User.username, User.display_name).filter(User.id.in_(ids)).all()
    return {"blocked": [{"username": u, "display_name": d} for (u, d) in rows]}


# ── Admin moderation ───────────────────────────────────────
class ResolveIn(BaseModel):
    status: str  # reviewed | actioned | dismissed


@router.get("/admin/reports")
def list_reports(
    status: str = "open",
    limit: int = 50,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_superuser),
):
    q = db.query(Report)
    if status:
        q = q.filter(Report.status == status)
    rows = q.order_by(Report.created_at.desc()).limit(min(limit, 200)).all()
    return {
        "reports": [
            {
                "id": r.id,
                "reporter_user_id": r.reporter_user_id,
                "target_type": r.target_type,
                "target_id": r.target_id,
                "reason": r.reason,
                "details": r.details,
                "status": r.status,
                "created_at": str(r.created_at),
            }
            for r in rows
        ]
    }


@router.post("/admin/reports/{report_id}/resolve")
def resolve_report(
    report_id: int,
    payload: ResolveIn,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_superuser),
):
    if payload.status not in {"reviewed", "actioned", "dismissed", "open"}:
        raise HTTPException(status_code=400, detail="invalid status")
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="report not found")
    report.status = payload.status
    db.add(report)
    db.commit()
    return {"status": "ok", "id": report_id, "new_status": payload.status}
