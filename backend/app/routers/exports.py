import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.engagement import Engagement
from app.config import settings

router = APIRouter(prefix="/exports", tags=["Exports"])


@router.post("/word/{eng_id}")
async def export_word(eng_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    eng = db.query(Engagement).filter(Engagement.id == eng_id, Engagement.firm_id == current_user.firm_id).first()
    if not eng:
        raise HTTPException(404, "Engagement not found")

    from app.services.word_exporter import generate_word_report
    file_path = generate_word_report(eng_id, db)
    return FileResponse(
        path=file_path,
        filename=f"financial_statements_{eng.client.name}_{eng.year}.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@router.post("/pdf/{eng_id}")
async def export_pdf(eng_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    eng = db.query(Engagement).filter(Engagement.id == eng_id, Engagement.firm_id == current_user.firm_id).first()
    if not eng:
        raise HTTPException(404, "Engagement not found")

    from app.services.word_exporter import generate_word_report
    from app.services.pdf_exporter import generate_pdf_report
    file_path = generate_pdf_report(eng_id, db)
    return FileResponse(
        path=file_path,
        filename=f"financial_statements_{eng.client.name}_{eng.year}.pdf",
        media_type="application/pdf",
    )
