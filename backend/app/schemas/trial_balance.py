from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel


class TBLineResponse(BaseModel):
    id: int
    account_code: Optional[str]
    account_name: str
    debit: Decimal
    credit: Decimal
    balance: Decimal
    is_comparative: bool
    ifrs_category: Optional[str]
    ifrs_subcategory: Optional[str]
    normal_balance: Optional[str]
    mapping_confidence: Optional[Decimal]
    mapping_explanation: Optional[str]
    is_manually_mapped: bool
    is_excluded: bool

    model_config = {"from_attributes": True}


class TBLineUpdate(BaseModel):
    ifrs_category: Optional[str] = None
    ifrs_subcategory: Optional[str] = None
    normal_balance: Optional[str] = None
    is_manually_mapped: bool = True
    is_excluded: Optional[bool] = None


class TrialBalanceResponse(BaseModel):
    id: int
    engagement_id: int
    filename: str
    is_comparative: bool
    status: str
    row_count: int
    mapped_count: int
    uploaded_at: datetime
    processed_at: Optional[datetime]
    error_message: Optional[str]
    lines: List[TBLineResponse] = []

    model_config = {"from_attributes": True}
