from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user, hash_password
from app.models.firm import Firm, FirmUser, UserRole
from app.schemas.firm import FirmResponse, FirmUpdate, UserResponse, InviteUserRequest

router = APIRouter(prefix="/firms", tags=["Firms"])


@router.get("/me", response_model=FirmResponse)
def get_my_firm(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    firm = db.query(Firm).filter(Firm.id == current_user.firm_id).first()
    if not firm:
        raise HTTPException(404, "Firm not found")
    return firm


@router.patch("/me", response_model=FirmResponse)
def update_firm(payload: FirmUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(403, "Admin only")
    firm = db.query(Firm).filter(Firm.id == current_user.firm_id).first()
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(firm, field, value)
    db.commit()
    db.refresh(firm)
    return firm


@router.get("/me/users", response_model=List[UserResponse])
def list_users(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(FirmUser).filter(FirmUser.firm_id == current_user.firm_id).all()


@router.post("/me/users", response_model=UserResponse, status_code=201)
def invite_user(payload: InviteUserRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(403, "Admin only")
    if db.query(FirmUser).filter(FirmUser.email == payload.email).first():
        raise HTTPException(400, "Email already registered")
    user = FirmUser(
        firm_id=current_user.firm_id,
        email=payload.email,
        password_hash=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        role=UserRole(payload.role),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
