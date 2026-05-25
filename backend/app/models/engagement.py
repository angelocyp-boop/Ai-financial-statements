import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import relationship
from app.database import Base


class EngagementStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    REVIEW = "REVIEW"
    COMPLETE = "COMPLETE"


class ReportingStandard(str, enum.Enum):
    IFRS = "IFRS"
    IFRS_SME = "IFRS_SME"


class Engagement(Base):
    __tablename__ = "engagements"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    firm_id = Column(Integer, ForeignKey("firms.id"), nullable=False)
    year = Column(Integer, nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    comparative_year = Column(Integer)
    status = Column(SAEnum(EngagementStatus), default=EngagementStatus.DRAFT)
    reporting_standard = Column(SAEnum(ReportingStandard), default=ReportingStandard.IFRS)
    currency = Column(String(3), default="EUR")
    preparer_id = Column(Integer, ForeignKey("firm_users.id"))
    reviewer_id = Column(Integer, ForeignKey("firm_users.id"))
    notes = Column(Text)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = relationship("Client", back_populates="engagements")
    trial_balances = relationship("TrialBalance", back_populates="engagement")
    statements = relationship("FinancialStatement", back_populates="engagement")
    disclosures = relationship("DisclosureNote", back_populates="engagement", order_by="DisclosureNote.order")
    validations = relationship("ValidationResult", back_populates="engagement")
