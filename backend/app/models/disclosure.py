import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import relationship
from app.database import Base


class DisclosureType(str, enum.Enum):
    ACCOUNTING_POLICIES = "ACCOUNTING_POLICIES"
    PPE = "PPE"
    INTANGIBLES = "INTANGIBLES"
    REVENUE = "REVENUE"
    TAXATION = "TAXATION"
    RELATED_PARTIES = "RELATED_PARTIES"
    SHARE_CAPITAL = "SHARE_CAPITAL"
    BORROWINGS = "BORROWINGS"
    COMMITMENTS = "COMMITMENTS"
    EVENTS_AFTER_REPORTING = "EVENTS_AFTER_REPORTING"
    GOING_CONCERN = "GOING_CONCERN"
    LEASES = "LEASES"
    FINANCIAL_INSTRUMENTS = "FINANCIAL_INSTRUMENTS"
    SEGMENT_INFORMATION = "SEGMENT_INFORMATION"
    CUSTOM = "CUSTOM"


class DisclosureNote(Base):
    __tablename__ = "disclosure_notes"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    note_type = Column(SAEnum(DisclosureType), nullable=False)
    note_number = Column(Integer)
    title = Column(String(300), nullable=False)
    content = Column(Text)
    is_ai_generated = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    engagement = relationship("Engagement", back_populates="disclosures")
