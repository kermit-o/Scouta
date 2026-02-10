from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, require_org_role
from app.models.org import Org
from app.models.org_member import OrgMember
from app.models.user import User
from app.api.v1.schemas.orgs import OrgCreateIn, OrgOut

router = APIRouter(tags=["orgs"])

@router.post("/orgs", response_model=OrgOut)
def create_org(
    payload: OrgCreateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> OrgOut:
    existing = db.query(Org).filter(Org.slug == payload.slug).one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Slug already in use")

    org = Org(name=payload.name, slug=payload.slug)
    db.add(org)
    db.commit()
    db.refresh(org)

    # creator becomes owner
    m = OrgMember(org_id=org.id, user_id=user.id, role="owner")
    db.add(m)
    db.commit()

    return OrgOut(id=org.id, name=org.name, slug=org.slug)

@router.get("/orgs/me", response_model=list[OrgOut])
def list_my_orgs(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[OrgOut]:
    rows = (
        db.query(Org)
        .join(OrgMember, OrgMember.org_id == Org.id)
        .filter(OrgMember.user_id == user.id)
        .all()
    )
    return [OrgOut(id=o.id, name=o.name, slug=o.slug) for o in rows]

@router.get("/orgs/{org_id}", response_model=OrgOut)
def get_org(
    org_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> OrgOut:
    require_org_role(org_id=org_id, allowed_roles={"owner", "admin", "editor", "viewer"}, db=db, user=user)
    org = db.get(Org, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Org not found")
    return OrgOut(id=org.id, name=org.name, slug=org.slug)
