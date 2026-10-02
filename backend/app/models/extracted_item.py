from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from app.database import Base

class ExtractedParty(Base):
    __tablename__ = "extracted_parties"

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("contract_versions.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False) # e.g. 'Vendor', 'Client', 'Disclosing Party'
    effective_date = Column(String(100), nullable=True) # ISO or raw format e.g. '2026-01-01'
    jurisdiction = Column(String(150), nullable=True)

    # Status & Audit
    status = Column(String(50), default="PENDING", nullable=False) # PENDING, APPROVED, REJECTED, EDITED, STALE
    user_correction_notes = Column(Text, nullable=True)
    is_stale = Column(Boolean, default=False, nullable=False)
    stale_reason = Column(Text, nullable=True)

    # Citation & Certainty
    source_page = Column(Integer, nullable=True)
    source_section = Column(String(255), nullable=True)
    source_quote = Column(Text, nullable=True)
    certainty = Column(String(50), default="CONFIRMED", nullable=False) # CONFIRMED, UNCERTAIN
    confidence_score = Column(Float, default=1.0, nullable=False)
    uncertainty_rationale = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    version = relationship("ContractVersion", back_populates="parties")

class ExtractedClause(Base):
    __tablename__ = "extracted_clauses"

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("contract_versions.id", ondelete="CASCADE"), nullable=False)
    clause_type = Column(String(50), nullable=False) # EXPIRY, RENEWAL, TERMINATION, NOTICE, OTHER
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    effective_date = Column(String(100), nullable=True)
    expiry_date = Column(String(100), nullable=True)
    renewal_type = Column(String(100), nullable=True) # Auto-renewal, Manual, None
    notice_period_days = Column(Integer, nullable=True)
    termination_type = Column(String(100), nullable=True) # For Cause, For Convenience, Both

    # Status & Audit
    status = Column(String(50), default="PENDING", nullable=False)
    user_correction_notes = Column(Text, nullable=True)
    is_stale = Column(Boolean, default=False, nullable=False)
    stale_reason = Column(Text, nullable=True)

    # Citation & Certainty
    source_page = Column(Integer, nullable=True)
    source_section = Column(String(255), nullable=True)
    source_quote = Column(Text, nullable=True)
    certainty = Column(String(50), default="CONFIRMED", nullable=False)
    confidence_score = Column(Float, default=1.0, nullable=False)
    uncertainty_rationale = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    version = relationship("ContractVersion", back_populates="clauses")
    reminders = relationship("CalculatedReminder", back_populates="clause", cascade="all, delete-orphan")

class ExtractedObligation(Base):
    __tablename__ = "extracted_obligations"

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("contract_versions.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    responsible_party = Column(String(255), nullable=False)
    due_date = Column(String(100), nullable=True) # ISO e.g. '2026-06-30'
    frequency = Column(String(100), nullable=True) # One-time, Monthly, Quarterly, Annual
    consequence_of_breach = Column(Text, nullable=True)

    # Status & Audit
    status = Column(String(50), default="PENDING", nullable=False)
    user_correction_notes = Column(Text, nullable=True)
    is_stale = Column(Boolean, default=False, nullable=False)
    stale_reason = Column(Text, nullable=True)

    # Citation & Certainty
    source_page = Column(Integer, nullable=True)
    source_section = Column(String(255), nullable=True)
    source_quote = Column(Text, nullable=True)
    certainty = Column(String(50), default="CONFIRMED", nullable=False)
    confidence_score = Column(Float, default=1.0, nullable=False)
    uncertainty_rationale = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    version = relationship("ContractVersion", back_populates="obligations")
    reminders = relationship("CalculatedReminder", back_populates="obligation", cascade="all, delete-orphan")

class UnclearTerm(Base):
    __tablename__ = "unclear_terms"

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("contract_versions.id", ondelete="CASCADE"), nullable=False)
    term_title = Column(String(255), nullable=False)
    clause_reference = Column(String(255), nullable=True)
    issue_type = Column(String(100), nullable=False) # AMBIGUITY, CONFLICTING_TERMS, POLICY_CONFLICT, UNDEFINED_STANDARD
    description = Column(Text, nullable=False)
    policy_reference = Column(String(255), nullable=True) # If conflict with organizational policy doc

    # Status & Audit
    status = Column(String(50), default="PENDING", nullable=False)
    user_correction_notes = Column(Text, nullable=True)
    is_stale = Column(Boolean, default=False, nullable=False)
    stale_reason = Column(Text, nullable=True)

    # Citation & Certainty
    source_page = Column(Integer, nullable=True)
    source_section = Column(String(255), nullable=True)
    source_quote = Column(Text, nullable=True)
    certainty = Column(String(50), default="UNCERTAIN", nullable=False)
    confidence_score = Column(Float, default=0.5, nullable=False)
    uncertainty_rationale = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    version = relationship("ContractVersion", back_populates="unclear_terms")
    clarification_questions = relationship("ClarificationQuestion", back_populates="unclear_term", cascade="all, delete-orphan")

class ClarificationQuestion(Base):
    __tablename__ = "clarification_questions"

    id = Column(Integer, primary_key=True, index=True)
    unclear_term_id = Column(Integer, ForeignKey("unclear_terms.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    suggested_action = Column(Text, nullable=True)
    user_answer = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    unclear_term = relationship("UnclearTerm", back_populates="clarification_questions")
