from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import verify_password, hash_password, create_access_token
from app.models.firm import Firm, FirmUser, UserRole
from app.schemas.auth import TokenResponse, RegisterRequest, LoginRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(FirmUser).filter(FirmUser.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    firm = Firm(name=payload.firm_name)
    db.add(firm)
    db.flush()
    user = FirmUser(
        firm_id=firm.id,
        email=payload.email,
        password_hash=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        role=UserRole.ADMIN,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id), "firm_id": firm.id})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        firm_id=firm.id,
        email=user.email,
        full_name=f"{user.first_name} {user.last_name}",
        role=user.role.value,
    )


@router.post("/token", response_model=TokenResponse)
def login_form(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(FirmUser).filter(FirmUser.email == form.username, FirmUser.is_active == True).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user.last_login = datetime.utcnow()
    db.commit()
    token = create_access_token({"sub": str(user.id), "firm_id": user.firm_id})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        firm_id=user.firm_id,
        email=user.email,
        full_name=f"{user.first_name} {user.last_name}",
        role=user.role.value,
    )


@router.post("/login", response_model=TokenResponse)
def login_json(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(FirmUser).filter(FirmUser.email == payload.email, FirmUser.is_active == True).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user.last_login = datetime.utcnow()
    db.commit()
    token = create_access_token({"sub": str(user.id), "firm_id": user.firm_id})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        firm_id=user.firm_id,
        email=user.email,
        full_name=f"{user.first_name} {user.last_name}",
        role=user.role.value,
    )


@router.get("/me")
def me(current_user=Depends(__import__("app.auth", fromlist=["get_current_user"]).get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "role": current_user.role.value,
        "firm_id": current_user.firm_id,
    }
