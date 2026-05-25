from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.validation import ValidationResult
from app.models.engagement import Engagement
from app.schemas.validation import ValidationResultResponse, ValidationSummary

router = APIRouter(prefix="/validation", tags=["Validation"])


@router.post("/run/{eng_id}", response_model=ValidationSummary)
def run_validation(eng_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    eng = db.query(Engagement).filter(Engagement.id == eng_id, Engagement.firm_id == current_user.firm_id).first()
    if not eng:
        raise HTTPException(404, "Engagement not found")

    from app.services.validation_engine import run_all_checks
    results = run_all_checks(eng_id, db)

    all_results = db.query(ValidationResult).filter(ValidationResult.engagement_id == eng_id).all()
    return ValidationSummary(
        total=len(all_results),
        errors=sum(1 for r in all_results if r.severity.value == "ERROR"),
        warnings=sum(1 for r in all_results if r.severity.value == "WARNING"),
        info=sum(1 for r in all_results if r.severity.value == "INFO"),
        unresolved=sum(1 for r in all_results if not r.is_resolved),
        results=[ValidationResultResponse.model_validate(r) for r in all_results],
    )


@router.get("/{eng_id}", response_model=ValidationSummary)
def get_validation_results(eng_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    eng = db.query(Engagement).filter(Engagement.id == eng_id, Engagement.firm_id == current_user.firm_id).first()
    if not eng:
        raise HTTPException(404, "Engagement not found")
    all_results = db.query(ValidationResult).filter(ValidationResult.engagement_id == eng_id).all()
    return ValidationSummary(
        total=len(all_results),
        errors=sum(1 for r in all_results if r.severity.value == "ERROR"),
        warnings=sum(1 for r in all_results if r.severity.value == "WARNING"),
        info=sum(1 for r in all_results if r.severity.value == "INFO"),
        unresolved=sum(1 for r in all_results if not r.is_resolved),
        results=[ValidationResultResponse.model_validate(r) for r in all_results],
    )


@router.post("/resolve/{result_id}")
def resolve_validation(result_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    from datetime import datetime
    result = db.query(ValidationResult).filter(ValidationResult.id == result_id).first()
    if not result:
        raise HTTPException(404, "Result not found")
    result.is_resolved = True
    result.resolved_by_id = current_user.id
    result.resolved_at = datetime.utcnow()
    db.commit()
    return {"message": "Resolved"}
