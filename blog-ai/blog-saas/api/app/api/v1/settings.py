from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, require_org_role
from app.models.user import User
from app.models.org_settings import OrgSettings
from app.api.v1.schemas.settings import OrgSettingsOut, OrgSettingsPatch

router = APIRouter(tags=["settings"])

def _get_or_create_org_settings(db: Session, org_id: int) -> OrgSettings:
    s = db.query(OrgSettings).filter(OrgSettings.org_id == org_id).one_or_none()
    if s:
        return s
    s = OrgSettings(org_id=org_id)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

@router.get("/orgs/{org_id}/settings", response_model=OrgSettingsOut)
def get_settings(
    org_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> OrgSettingsOut:
    require_org_role(org_id=org_id, allowed_roles={"owner", "admin", "editor", "viewer"}, db=db, user=user)
    s = _get_or_create_org_settings(db, org_id)
    return OrgSettingsOut(
        org_id=s.org_id,
        agents_enabled=s.agents_enabled,
        auto_publish=s.auto_publish,
        max_agents_per_post=s.max_agents_per_post,
        max_actions_per_day=s.max_actions_per_day,
        spawn_probability_base=s.spawn_probability_base,
        locale=s.locale,
    )

@router.patch("/orgs/{org_id}/settings", response_model=OrgSettingsOut)
def patch_settings(
    org_id: int,
    payload: OrgSettingsPatch,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> OrgSettingsOut:
    require_org_role(org_id=org_id, allowed_roles={"owner", "admin"}, db=db, user=user)
    s = _get_or_create_org_settings(db, org_id)

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(s, k, v)

    db.add(s)
    db.commit()
    db.refresh(s)

    return OrgSettingsOut(
        org_id=s.org_id,
        agents_enabled=s.agents_enabled,
        auto_publish=s.auto_publish,
        max_agents_per_post=s.max_agents_per_post,
        max_actions_per_day=s.max_actions_per_day,
        spawn_probability_base=s.spawn_probability_base,
        locale=s.locale,
    )
