from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel


class StatementLineResponse(BaseModel):
    id: int
    section: Optional[str]
    subsection: Optional[str]
    label: str
    current_amount: Optional[Decimal]
    comparative_amount: Optional[Decimal]
    note_reference: Optional[str]
    indent_level: int
    is_header: bool
    is_subtotal: bool
    is_total: bool
    is_bold: bool
    order: int

    model_config = {"from_attributes": True}


class StatementLineUpdate(BaseModel):
    label: Optional[str] = None
    current_amount: Optional[Decimal] = None
    comparative_amount: Optional[Decimal] = None
    note_reference: Optional[str] = None


class FinancialStatementResponse(BaseModel):
    id: int
    engagement_id: int
    statement_type: str
    version: int
    is_approved: bool
    approved_at: Optional[datetime]
    generated_at: datetime
    lines: List[StatementLineResponse] = []

    model_config = {"from_attributes": True}


class GenerateStatementsRequest(BaseModel):
    engagement_id: int
    statement_types: List[str] = ["SFP", "PL", "CASH_FLOW", "EQUITY"]
    include_comparative: bool = True
