from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.schemas.extraction import (
    PartyResponse,
    ClauseResponse,
    ObligationResponse,
    UnclearTermResponse,
)

class PolicyDocumentResponse(BaseModel):
    id: int
    contract_id: int
    title: str
    filename: str
    file_type: str
    created_at: datetime

    class Config:
        from_attributes = True

class ContractVersionResponse(BaseModel):
    id: int
    contract_id: int
    version_number: int
    filename: str
    file_type: str
    is_active: bool
    created_at: Optional[datetime] = None
    parties: List[PartyResponse] = []
    clauses: List[ClauseResponse] = []
    obligations: List[ObligationResponse] = []
    unclear_terms: List[UnclearTermResponse] = []

    class Config:
        from_attributes = True

class ContractSummaryItem(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    latest_version: int
    parties_count: int
    clauses_count: int
    obligations_count: int
    unclear_terms_count: int
    stale_items_count: int

    class Config:
        from_attributes = True

class ContractDetailResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    versions: List[ContractVersionResponse] = []
    policy_documents: List[PolicyDocumentResponse] = []
    current_version: Optional[ContractVersionResponse] = None

    class Config:
        from_attributes = True
