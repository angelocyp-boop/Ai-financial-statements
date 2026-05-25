from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DisclosureNoteResponse(BaseModel):
    id: int
    engagement_id: int
    note_type: str
    note_number: Optional[int]
    title: str
    content: Optional[str]
    is_ai_generated: bool
    is_approved: bool
    order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DisclosureNoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_approved: Optional[bool] = None
    order: Optional[int] = None


class GenerateDisclosuresRequest(BaseModel):
    engagement_id: int
    note_types: Optional[list[str]] = None  # None = auto-detect from mappings
    regenerate_existing: bool = False
