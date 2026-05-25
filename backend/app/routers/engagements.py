from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.engagement import Engagement, EngagementStatus
from app.models.client import Client
from app.schemas.engagement import EngagementCreate, EngagementUpdate, EngagementResponse

router = APIRouter(prefix="/engagements", tags=["Engagements"])


def _ensure_access(eng: Engagement, firm_id: int):
    if eng.firm_id != firm_id:
        raise HTTPException(403, "Access denied")


@router.get("", response_model=List[EngagementResponse])
def list_engagements(
    client_id: int = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Engagement).filter(Engagement.firm_id == current_user.firm_id)
    if client_id:
        q = q.filter(Engagement.client_id == client_id)
    engs = q.order_by(Engagement.year.desc()).all()
    result = []
    for e in engs:
        r = EngagementResponse.model_validate(e)
        if e.client:
            r.client_name = e.client.name
        result.append(r)
    return result


@router.post("", response_model=EngagementResponse, status_code=201)
def create_engagement(payload: EngagementCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == payload.client_id, Client.firm_id == current_user.firm_id).first()
    if not client:
        raise HTTPException(404, "Client not found")
    eng = Engagement(**payload.model_dump(), firm_id=current_user.firm_id)
    db.add(eng)
    db.commit()
    db.refresh(eng)
    r = EngagementResponse.model_validate(eng)
    r.client_name = client.name
    return r


@router.get("/{eng_id}", response_model=EngagementResponse)
def get_engagement(eng_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    eng = db.query(Engagement).filter(Engagement.id == eng_id).first()
    if not eng:
        raise HTTPException(404, "Engagement not found")
    _ensure_access(eng, current_user.firm_id)
    r = EngagementResponse.model_validate(eng)
    if eng.client:
        r.client_name = eng.client.name
    return r


@router.patch("/{eng_id}", response_model=EngagementResponse)
def update_engagement(eng_id: int, payload: EngagementUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    eng = db.query(Engagement).filter(Engagement.id == eng_id).first()
    if not eng:
        raise HTTPException(404, "Engagement not found")
    _ensure_access(eng, current_user.firm_id)
    for field, value in payload.model_dump(exclude_none=True).items():
        if field == "status":
            setattr(eng, field, EngagementStatus(value))
        else:
            setattr(eng, field, value)
    db.commit()
    db.refresh(eng)
    return eng
