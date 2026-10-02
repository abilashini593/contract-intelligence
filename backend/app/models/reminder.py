from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class CalculatedReminder(Base):
    __tablename__ = "calculated_reminders"

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("contract_versions.id", ondelete="CASCADE"), nullable=False)
    clause_id = Column(Integer, ForeignKey("extracted_clauses.id", ondelete="SET NULL"), nullable=True)
    obligation_id = Column(Integer, ForeignKey("extracted_obligations.id", ondelete="SET NULL"), nullable=True)

    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False) # RENEWAL_NOTICE, CONTRACT_EXPIRY, OBLIGATION_DEADLINE, RECURRING_OBLIGATION
    target_date = Column(String(50), nullable=False) # Deadline date: YYYY-MM-DD
    reminder_date = Column(String(50), nullable=False) # Calculated reminder trigger date: YYYY-MM-DD
    days_before = Column(Integer, nullable=False, default=0) # Days in advance
    responsible_party = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    urgency = Column(String(50), default="MEDIUM", nullable=False) # OVERDUE, HIGH, MEDIUM, LOW
    is_dismissed = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    version = relationship("ContractVersion", back_populates="reminders")
    clause = relationship("ExtractedClause", back_populates="reminders")
    obligation = relationship("ExtractedObligation", back_populates="reminders")
