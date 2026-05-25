import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import relationship
from app.database import Base


class StatementType(str, enum.Enum):
    SFP = "SFP"          # Statement of Financial Position
    PL = "PL"            # Profit & Loss / Income Statement
    CASH_FLOW = "CASH_FLOW"
    EQUITY = "EQUITY"    # Statement of Changes in Equity


class FinancialStatement(Base):
    __tablename__ = "financial_statements"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    statement_type = Column(SAEnum(StatementType), nullable=False)
    version = Column(Integer, default=1)
    is_approved = Column(Boolean, default=False)
    approved_by_id = Column(Integer, ForeignKey("firm_users.id"))
    approved_at = Column(DateTime)
    generated_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    engagement = relationship("Engagement", back_populates="statements")
    lines = relationship(
        "StatementLine", back_populates="statement",
        cascade="all, delete-orphan", order_by="StatementLine.order"
    )


class StatementLine(Base):
    __tablename__ = "statement_lines"

    id = Column(Integer, primary_key=True, index=True)
    statement_id = Column(Integer, ForeignKey("financial_statements.id"), nullable=False)
    section = Column(String(200))
    subsection = Column(String(200))
    label = Column(String(300), nullable=False)
    current_amount = Column(Numeric(18, 2))
    comparative_amount = Column(Numeric(18, 2))
    note_reference = Column(String(20))
    indent_level = Column(Integer, default=0)
    is_header = Column(Boolean, default=False)
    is_subtotal = Column(Boolean, default=False)
    is_total = Column(Boolean, default=False)
    is_bold = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    tb_line_ids = Column(Text)  # comma-separated TBLine IDs contributing to this line

    statement = relationship("FinancialStatement", back_populates="lines")
