from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse

router = APIRouter(prefix="/clients", tags=["Clients"])


def _ensure_firm(client: Client, firm_id: int):
    if client.firm_id != firm_id:
        raise HTTPException(403, "Access denied")


@router.get("", response_model=List[ClientResponse])
def list_clients(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    clients = db.query(Client).filter(Client.firm_id == current_user.firm_id, Client.is_active == True).all()
    result = []
    for c in clients:
        r = ClientResponse.model_validate(c)
        r.engagement_count = len(c.engagements)
        result.append(r)
    return result


@router.post("", response_model=ClientResponse, status_code=201)
def create_client(payload: ClientCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    client = Client(**payload.model_dump(), firm_id=current_user.firm_id)
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(404, "Client not found")
    _ensure_firm(client, current_user.firm_id)
    return client


@router.patch("/{client_id}", response_model=ClientResponse)
def update_client(client_id: int, payload: ClientUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(404, "Client not found")
    _ensure_firm(client, current_user.firm_id)
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(client, field, value)
    db.commit()
    db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=204)
def archive_client(client_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(404, "Client not found")
    _ensure_firm(client, current_user.firm_id)
    client.is_active = False
    db.commit()
