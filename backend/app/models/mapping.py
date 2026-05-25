import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class IFRSCategory(str, enum.Enum):
    # Non-current assets
    PPE = "PPE"
    RIGHT_OF_USE = "RIGHT_OF_USE"
    INTANGIBLES = "INTANGIBLES"
    GOODWILL = "GOODWILL"
    INVESTMENTS_ASSOCIATES = "INVESTMENTS_ASSOCIATES"
    FINANCIAL_ASSETS_NC = "FINANCIAL_ASSETS_NC"
    DEFERRED_TAX_ASSET = "DEFERRED_TAX_ASSET"
    OTHER_NC_ASSETS = "OTHER_NC_ASSETS"
    # Current assets
    INVENTORIES = "INVENTORIES"
    TRADE_RECEIVABLES = "TRADE_RECEIVABLES"
    PREPAYMENTS = "PREPAYMENTS"
    FINANCIAL_ASSETS_C = "FINANCIAL_ASSETS_C"
    CASH = "CASH"
    OTHER_C_ASSETS = "OTHER_C_ASSETS"
    # Non-current liabilities
    BORROWINGS_NC = "BORROWINGS_NC"
    LEASE_LIABILITIES_NC = "LEASE_LIABILITIES_NC"
    DEFERRED_TAX_LIABILITY = "DEFERRED_TAX_LIABILITY"
    EMPLOYEE_OBLIGATIONS = "EMPLOYEE_OBLIGATIONS"
    OTHER_NC_LIABILITIES = "OTHER_NC_LIABILITIES"
    # Current liabilities
    TRADE_PAYABLES = "TRADE_PAYABLES"
    BORROWINGS_C = "BORROWINGS_C"
    LEASE_LIABILITIES_C = "LEASE_LIABILITIES_C"
    TAX_PAYABLE = "TAX_PAYABLE"
    ACCRUALS = "ACCRUALS"
    OTHER_C_LIABILITIES = "OTHER_C_LIABILITIES"
    # Equity
    SHARE_CAPITAL = "SHARE_CAPITAL"
    SHARE_PREMIUM = "SHARE_PREMIUM"
    RETAINED_EARNINGS = "RETAINED_EARNINGS"
    OTHER_RESERVES = "OTHER_RESERVES"
    # P&L
    REVENUE = "REVENUE"
    COST_OF_SALES = "COST_OF_SALES"
    OTHER_INCOME = "OTHER_INCOME"
    DISTRIBUTION_COSTS = "DISTRIBUTION_COSTS"
    ADMIN_EXPENSES = "ADMIN_EXPENSES"
    OTHER_OP_EXPENSES = "OTHER_OP_EXPENSES"
    FINANCE_INCOME = "FINANCE_INCOME"
    FINANCE_COSTS = "FINANCE_COSTS"
    INCOME_TAX = "INCOME_TAX"
    OCI = "OCI"


class MappingLibrary(Base):
    """Firm-level learned mapping patterns, improving over time."""
    __tablename__ = "mapping_library"

    id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(Integer, ForeignKey("firms.id"), nullable=False)
    account_code_pattern = Column(String(100))
    account_name_keywords = Column(JSON)
    ifrs_category = Column(SAEnum(IFRSCategory), nullable=False)
    normal_balance = Column(String(10), default="DR")
    usage_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    firm = relationship("Firm", back_populates="mapping_library")
