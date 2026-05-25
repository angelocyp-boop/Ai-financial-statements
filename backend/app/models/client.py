from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(Integer, ForeignKey("firms.id"), nullable=False)
    name = Column(String(200), nullable=False)
    legal_name = Column(String(200))
    registration_number = Column(String(50))
    vat_number = Column(String(50))
    industry = Column(String(100))
    year_end_month = Column(Integer, default=12)
    year_end_day = Column(Integer, default=31)
    currency = Column(String(3), default="EUR")
    address = Column(Text)
    contact_name = Column(String(200))
    contact_email = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    firm = relationship("Firm", back_populates="clients")
    engagements = relationship("Engagement", back_populates="client")
