from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class ClientBase(BaseModel):
    name: str
    legal_name: Optional[str] = None
    registration_number: Optional[str] = None
    vat_number: Optional[str] = None
    industry: Optional[str] = None
    year_end_month: int = 12
    year_end_day: int = 31
    currency: str = "EUR"
    address: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    legal_name: Optional[str] = None
    registration_number: Optional[str] = None
    vat_number: Optional[str] = None
    industry: Optional[str] = None
    currency: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class ClientResponse(ClientBase):
    id: int
    firm_id: int
    is_active: bool
    created_at: datetime
    engagement_count: Optional[int] = 0

    model_config = {"from_attributes": True}
