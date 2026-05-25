from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.statement import FinancialStatement, StatementType
from app.models.engagement import Engagement
from app.schemas.statement import FinancialStatementResponse, StatementLineUpdate, GenerateStatementsRequest

router = APIRouter(prefix="/statements", tags=["Statements"])


@router.post("/generate", response_model=List[FinancialStatementResponse])
async def generate_statements(
    payload: GenerateStatementsRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    eng = db.query(Engagement).filter(Engagement.id == payload.engagement_id, Engagement.firm_id == current_user.firm_id).first()
    if not eng:
        raise HTTPException(404, "Engagement not found")

    from app.services.statement_builder import build_statements
    statements = build_statements(eng.id, payload.statement_types, db)
    return statements


@router.get("/engagement/{eng_id}", response_model=List[FinancialStatementResponse])
def list_statements(eng_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    eng = db.query(Engagement).filter(Engagement.id == eng_id, Engagement.firm_id == current_user.firm_id).first()
    if not eng:
        raise HTTPException(404, "Engagement not found")
    return db.query(FinancialStatement).filter(FinancialStatement.engagement_id == eng_id).all()


@router.get("/{stmt_id}", response_model=FinancialStatementResponse)
def get_statement(stmt_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = db.query(FinancialStatement).filter(FinancialStatement.id == stmt_id).first()
    if not stmt:
        raise HTTPException(404, "Statement not found")
    eng = db.query(Engagement).filter(Engagement.id == stmt.engagement_id, Engagement.firm_id == current_user.firm_id).first()
    if not eng:
        raise HTTPException(403, "Access denied")
    return stmt


@router.patch("/line/{line_id}")
def update_statement_line(line_id: int, payload: StatementLineUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    from app.models.statement import StatementLine
    line = db.query(StatementLine).filter(StatementLine.id == line_id).first()
    if not line:
        raise HTTPException(404, "Line not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(line, field, value)
    db.commit()
    db.refresh(line)
    return line


@router.post("/{stmt_id}/approve")
def approve_statement(stmt_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    from datetime import datetime
    stmt = db.query(FinancialStatement).filter(FinancialStatement.id == stmt_id).first()
    if not stmt:
        raise HTTPException(404, "Statement not found")
    eng = db.query(Engagement).filter(Engagement.id == stmt.engagement_id, Engagement.firm_id == current_user.firm_id).first()
    if not eng:
        raise HTTPException(403, "Access denied")
    stmt.is_approved = True
    stmt.approved_by_id = current_user.id
    stmt.approved_at = datetime.utcnow()
    db.commit()
    return {"message": "Statement approved"}
