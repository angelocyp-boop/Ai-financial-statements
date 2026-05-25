import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import relationship
from app.database import Base


class TBStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    ERROR = "ERROR"


class TrialBalance(Base):
    __tablename__ = "trial_balances"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500))
    is_comparative = Column(Boolean, default=False)
    status = Column(SAEnum(TBStatus), default=TBStatus.PENDING)
    error_message = Column(Text)
    row_count = Column(Integer, default=0)
    mapped_count = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)

    engagement = relationship("Engagement", back_populates="trial_balances")
    lines = relationship("TBLine", back_populates="trial_balance", cascade="all, delete-orphan")


class TBLine(Base):
    __tablename__ = "tb_lines"

    id = Column(Integer, primary_key=True, index=True)
    trial_balance_id = Column(Integer, ForeignKey("trial_balances.id"), nullable=False)
    account_code = Column(String(50))
    account_name = Column(String(300), nullable=False)
    debit = Column(Numeric(18, 2), default=0)
    credit = Column(Numeric(18, 2), default=0)
    balance = Column(Numeric(18, 2), default=0)
    is_comparative = Column(Boolean, default=False)

    # IFRS mapping
    ifrs_category = Column(String(100))
    ifrs_subcategory = Column(String(200))
    normal_balance = Column(String(10))  # DR or CR
    mapping_confidence = Column(Numeric(5, 4), default=0)
    mapping_explanation = Column(Text)
    is_manually_mapped = Column(Boolean, default=False)
    is_excluded = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trial_balance = relationship("TrialBalance", back_populates="lines")
