from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    versions = relationship("ContractVersion", back_populates="contract", cascade="all, delete-orphan", order_by="ContractVersion.version_number")
    policy_documents = relationship("PolicyDocument", back_populates="contract", cascade="all, delete-orphan")

class ContractVersion(Base):
    __tablename__ = "contract_versions"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False, default=1)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False) # 'pdf', 'docx', 'text'
    raw_text = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    contract = relationship("Contract", back_populates="versions")
    parties = relationship("ExtractedParty", back_populates="version", cascade="all, delete-orphan")
    clauses = relationship("ExtractedClause", back_populates="version", cascade="all, delete-orphan")
    obligations = relationship("ExtractedObligation", back_populates="version", cascade="all, delete-orphan")
    unclear_terms = relationship("UnclearTerm", back_populates="version", cascade="all, delete-orphan")
    reminders = relationship("CalculatedReminder", back_populates="version", cascade="all, delete-orphan")

class PolicyDocument(Base):
    __tablename__ = "policy_documents"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    raw_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    contract = relationship("Contract", back_populates="policy_documents")
