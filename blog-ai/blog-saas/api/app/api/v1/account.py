"""Account self-service endpoints.

Currently: store-compliant account deletion (App Store Guideline 5.1.1(v) and
Google Play require an in-app way for users to delete their account).
"""
from datetime import datetime, timezone
import secrets

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.core.security import hash_password
from app.models.user import User

router = APIRouter(tags=["account"])


@router.delete("/account")
def delete_account(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Soft-delete the authenticated user's account.

    Anonymizes PII in place and stamps deleted_at; the row is kept so
    referential integrity (posts, lives, coin transactions) is preserved.
    A non-null deleted_at blocks all future authentication, which also
    revokes any still-valid JWTs (enforced in deps.get_current_user).
    """
    if getattr(user, "deleted_at", None):
        return {"status": "already_deleted"}

    uid = user.id
    # Scramble the UNIQUE/NOT NULL columns to values that stay unique per id.
    user.email = f"deleted_{uid}_{secrets.token_hex(8)}@deleted.invalid"
    user.username = f"deleted_{uid}"
    user.display_name = "Deleted user"
    user.avatar_url = ""
    user.bio = ""
    user.interests = ""
    user.website = ""
    user.location = ""
    user.verification_token = None
    user.is_verified = False
    # Unusable random password hash so the old credentials can never match.
    user.password_hash = hash_password(secrets.token_urlsafe(32))
    user.deleted_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()

    try:
        from app.services.analytics import track_event
        track_event(db, "account_deleted", user_id=uid, alert=False)
    except Exception:
        pass

    return {"status": "deleted"}
