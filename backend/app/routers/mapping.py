from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.trial_balance import TrialBalance, TBLine
from app.models.engagement import Engagement
from app.schemas.mapping import MappingLibraryEntry, BulkMappingRequest

router = APIRouter(prefix="/mapping", tags=["Mapping"])


@router.post("/run")
async def run_mapping(
    payload: BulkMappingRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tb = db.query(TrialBalance).filter(TrialBalance.id == payload.trial_balance_id).first()
    if not tb:
        raise HTTPException(404, "Trial balance not found")
    eng = db.query(Engagement).filter(Engagement.id == tb.engagement_id, Engagement.firm_id == current_user.firm_id).first()
    if not eng:
        raise HTTPException(403, "Access denied")
    from app.services.ai_mapper import run_bulk_mapping
    background_tasks.add_task(run_bulk_mapping, tb.id, current_user.firm_id, None)
    return {"message": "Mapping started", "trial_balance_id": tb.id}


@router.get("/library", response_model=List[MappingLibraryEntry])
def get_mapping_library(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    from app.models.mapping import MappingLibrary
    return db.query(MappingLibrary).filter(MappingLibrary.firm_id == current_user.firm_id).order_by(MappingLibrary.usage_count.desc()).all()
