import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.trial_balance import TrialBalance, TBLine, TBStatus
from app.models.engagement import Engagement
from app.schemas.trial_balance import TrialBalanceResponse, TBLineResponse, TBLineUpdate
from app.services.tb_parser import parse_trial_balance
from app.services.ai_mapper import run_bulk_mapping
from app.config import settings

router = APIRouter(prefix="/trial-balance", tags=["Trial Balance"])


@router.post("/upload/{eng_id}", response_model=TrialBalanceResponse, status_code=201)
async def upload_trial_balance(
    eng_id: int,
    file: UploadFile = File(...),
    is_comparative: bool = False,
    background_tasks: BackgroundTasks = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    eng = db.query(Engagement).filter(Engagement.id == eng_id, Engagement.firm_id == current_user.firm_id).first()
    if not eng:
        raise HTTPException(404, "Engagement not found")

    allowed = {".xlsx", ".xls", ".csv"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(400, f"Unsupported file type: {ext}. Allowed: {allowed}")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, f"tb_{eng_id}_{file.filename}")
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    tb = TrialBalance(
        engagement_id=eng_id,
        filename=file.filename,
        file_path=file_path,
        is_comparative=is_comparative,
        status=TBStatus.PENDING,
    )
    db.add(tb)
    db.commit()
    db.refresh(tb)

    background_tasks.add_task(_process_tb, tb.id, current_user.firm_id)
    return tb


async def _process_tb(tb_id: int, firm_id: int):
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        tb = db.query(TrialBalance).filter(TrialBalance.id == tb_id).first()
        if not tb:
            return
        tb.status = TBStatus.PROCESSING
        db.commit()
        lines = parse_trial_balance(tb.file_path)
        for line_data in lines:
            line = TBLine(
                trial_balance_id=tb_id,
                account_code=line_data.get("account_code"),
                account_name=line_data["account_name"],
                debit=line_data.get("debit", 0),
                credit=line_data.get("credit", 0),
                balance=line_data.get("balance", 0),
                is_comparative=tb.is_comparative,
            )
            db.add(line)
        db.flush()
        tb.row_count = len(lines)
        db.commit()
        await run_bulk_mapping(tb_id, firm_id, db)
        tb.status = TBStatus.PROCESSED
        from datetime import datetime
        tb.processed_at = datetime.utcnow()
        db.commit()
    except Exception as e:
        tb.status = TBStatus.ERROR
        tb.error_message = str(e)
        db.commit()
    finally:
        db.close()


@router.get("/{tb_id}", response_model=TrialBalanceResponse)
def get_trial_balance(tb_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    tb = db.query(TrialBalance).filter(TrialBalance.id == tb_id).first()
    if not tb:
        raise HTTPException(404, "Trial balance not found")
    eng = db.query(Engagement).filter(Engagement.id == tb.engagement_id, Engagement.firm_id == current_user.firm_id).first()
    if not eng:
        raise HTTPException(403, "Access denied")
    return tb


@router.get("/engagement/{eng_id}", response_model=List[TrialBalanceResponse])
def list_tb_for_engagement(eng_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    eng = db.query(Engagement).filter(Engagement.id == eng_id, Engagement.firm_id == current_user.firm_id).first()
    if not eng:
        raise HTTPException(404, "Engagement not found")
    return db.query(TrialBalance).filter(TrialBalance.engagement_id == eng_id).all()


@router.patch("/line/{line_id}", response_model=TBLineResponse)
def update_tb_line(line_id: int, payload: TBLineUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    line = db.query(TBLine).filter(TBLine.id == line_id).first()
    if not line:
        raise HTTPException(404, "Line not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(line, field, value)
    line.is_manually_mapped = True
    db.commit()
    db.refresh(line)
    tb = db.query(TrialBalance).filter(TrialBalance.id == line.trial_balance_id).first()
    tb.mapped_count = db.query(TBLine).filter(
        TBLine.trial_balance_id == tb.id, TBLine.ifrs_category != None
    ).count()
    db.commit()
    return line
