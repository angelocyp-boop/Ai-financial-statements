from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel


class EngagementCreate(BaseModel):
    client_id: int
    year: int
    period_start: date
    period_end: date
    comparative_year: Optional[int] = None
    reporting_standard: str = "IFRS"
    currency: str = "EUR"
    preparer_id: Optional[int] = None
    reviewer_id: Optional[int] = None
    notes: Optional[str] = None


class EngagementUpdate(BaseModel):
    status: Optional[str] = None
    reporting_standard: Optional[str] = None
    currency: Optional[str] = None
    preparer_id: Optional[int] = None
    reviewer_id: Optional[int] = None
    notes: Optional[str] = None


class EngagementResponse(BaseModel):
    id: int
    client_id: int
    firm_id: int
    year: int
    period_start: date
    period_end: date
    comparative_year: Optional[int]
    status: str
    reporting_standard: str
    currency: str
    preparer_id: Optional[int]
    reviewer_id: Optional[int]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    client_name: Optional[str] = None

    model_config = {"from_attributes": True}
