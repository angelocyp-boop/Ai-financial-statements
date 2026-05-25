from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ValidationResultResponse(BaseModel):
    id: int
    engagement_id: int
    check_type: str
    severity: str
    message: str
    details: Optional[str]
    is_resolved: bool
    resolved_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class ValidationSummary(BaseModel):
    total: int
    errors: int
    warnings: int
    info: int
    unresolved: int
    results: List[ValidationResultResponse]
