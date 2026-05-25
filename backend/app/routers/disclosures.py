from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.disclosure import DisclosureNote, DisclosureType
from app.models.engagement import Engagement
from app.schemas.disclosure import DisclosureNoteResponse, DisclosureNoteUpdate, GenerateDisclosuresRequest

router = APIRouter(prefix="/disclosures", tags=["Disclosures"])


@router.post("/generate", response_model=List[DisclosureNoteResponse])
async def generate_disclosures(
    payload: GenerateDisclosuresRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    eng = db.query(Engagement).filter(Engagement.id == payload.engagement_id, Engagement.firm_id == current_user.firm_id).first()
    if not eng:
        raise HTTPException(404, "Engagement not found")

    from app.services.disclosure_generator import generate_disclosure_notes
    notes = await generate_disclosure_notes(eng.id, payload.note_types, payload.regenerate_existing, db)
    return notes


@router.get("/engagement/{eng_id}", response_model=List[DisclosureNoteResponse])
def list_disclosures(eng_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    eng = db.query(Engagement).filter(Engagement.id == eng_id, Engagement.firm_id == current_user.firm_id).first()
    if not eng:
        raise HTTPException(404, "Engagement not found")
    return db.query(DisclosureNote).filter(DisclosureNote.engagement_id == eng_id).order_by(DisclosureNote.order).all()


@router.get("/{note_id}", response_model=DisclosureNoteResponse)
def get_disclosure(note_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    note = db.query(DisclosureNote).filter(DisclosureNote.id == note_id).first()
    if not note:
        raise HTTPException(404, "Disclosure not found")
    return note


@router.patch("/{note_id}", response_model=DisclosureNoteResponse)
def update_disclosure(note_id: int, payload: DisclosureNoteUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    note = db.query(DisclosureNote).filter(DisclosureNote.id == note_id).first()
    if not note:
        raise HTTPException(404, "Disclosure not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(note, field, value)
    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=204)
def delete_disclosure(note_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    note = db.query(DisclosureNote).filter(DisclosureNote.id == note_id).first()
    if not note:
        raise HTTPException(404, "Disclosure not found")
    db.delete(note)
    db.commit()
