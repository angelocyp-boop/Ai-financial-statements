import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import relationship
from app.database import Base


class ValidationSeverity(str, enum.Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class ValidationResult(Base):
    __tablename__ = "validation_results"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    check_type = Column(String(100), nullable=False)
    severity = Column(SAEnum(ValidationSeverity), nullable=False)
    message = Column(String(500), nullable=False)
    details = Column(Text)
    is_resolved = Column(Boolean, default=False)
    resolved_by_id = Column(Integer, ForeignKey("firm_users.id"))
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    engagement = relationship("Engagement", back_populates="validations")
