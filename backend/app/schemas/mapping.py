from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class MappingSuggestion(BaseModel):
    account_code: Optional[str]
    account_name: str
    ifrs_category: str
    ifrs_subcategory: Optional[str]
    normal_balance: str
    confidence: float
    explanation: str


class BulkMappingRequest(BaseModel):
    trial_balance_id: int
    use_ai: bool = True
    use_library: bool = True


class MappingLibraryEntry(BaseModel):
    id: int
    account_code_pattern: Optional[str]
    account_name_keywords: Optional[List[str]]
    ifrs_category: str
    normal_balance: str
    usage_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
