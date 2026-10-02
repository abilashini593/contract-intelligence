from typing import List, Optional
from pydantic import BaseModel, Field

# --- Citation & Certainty Base ---
class SourceCitation(BaseModel):
    source_page: Optional[int] = Field(None, description="Page number where the information was found (1-indexed), or null if not applicable.")
    source_section: Optional[str] = Field(None, description="Section heading or clause identifier, e.g. 'Section 4.1' or 'Recital B'.")
    source_quote: str = Field(..., description="Exact verbatim excerpt from the document supporting this extracted item.")

class CertaintyInfo(BaseModel):
    certainty: str = Field("CONFIRMED", description="'CONFIRMED' for explicitly defined facts; 'UNCERTAIN' for ambiguous, implied, or contested terms.")
    confidence_score: float = Field(1.0, ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0.")
    uncertainty_rationale: Optional[str] = Field(None, description="Detailed explanation if certainty is UNCERTAIN.")

# --- AI Extraction Models (Output Schema) ---
class AIPartyItem(BaseModel):
    name: str = Field(..., description="Legal name of the entity or individual.")
    role: str = Field(..., description="Contract role (e.g. 'Vendor', 'Client', 'Disclosing Party', 'Service Provider').")
    effective_date: Optional[str] = Field(None, description="Effective date in YYYY-MM-DD format if stated in relation to parties.")
    jurisdiction: Optional[str] = Field(None, description="Governing law jurisdiction or formation state if mentioned.")
    source_page: Optional[int] = None
    source_section: Optional[str] = None
    source_quote: str
    certainty: str = "CONFIRMED"
    confidence_score: float = 1.0
    uncertainty_rationale: Optional[str] = None

class AIClauseItem(BaseModel):
    clause_type: str = Field(..., description="'EXPIRY', 'RENEWAL', 'TERMINATION', 'NOTICE', or 'OTHER'.")
    title: str = Field(..., description="Concise title for the clause.")
    summary: str = Field(..., description="Clear, plain-language summary of what this clause stipulates.")
    effective_date: Optional[str] = Field(None, description="Effective date in YYYY-MM-DD if specified.")
    expiry_date: Optional[str] = Field(None, description="Expiry date in YYYY-MM-DD if explicitly stated or calculable.")
    renewal_type: Optional[str] = Field(None, description="'Auto-renewal', 'Manual renewal', 'Mutual consent', or 'None'.")
    notice_period_days: Optional[int] = Field(None, description="Notice period required in days (e.g. 30, 60, 90).")
    termination_type: Optional[str] = Field(None, description="'For Cause', 'For Convenience', 'Both', or 'Mutual'.")
    source_page: Optional[int] = None
    source_section: Optional[str] = None
    source_quote: str
    certainty: str = "CONFIRMED"
    confidence_score: float = 1.0
    uncertainty_rationale: Optional[str] = None

class AIObligationItem(BaseModel):
    title: str = Field(..., description="Actionable title for the obligation.")
    description: str = Field(..., description="Specific operational or legal duty required.")
    responsible_party: str = Field(..., description="Party responsible for performing the obligation.")
    due_date: Optional[str] = Field(None, description="Specific deadline date in YYYY-MM-DD if fixed.")
    frequency: Optional[str] = Field(None, description="'One-time', 'Monthly', 'Quarterly', 'Annual', or 'As needed'.")
    consequence_of_breach: Optional[str] = Field(None, description="Stipulated remedy, penalty, or default consequence if breached.")
    source_page: Optional[int] = None
    source_section: Optional[str] = None
    source_quote: str
    certainty: str = "CONFIRMED"
    confidence_score: float = 1.0
    uncertainty_rationale: Optional[str] = None

class AIClarificationQuestion(BaseModel):
    question: str = Field(..., description="Targeted question to ask the user or legal counsel to clarify this ambiguous clause.")
    suggested_action: Optional[str] = Field(None, description="Recommended next step or document clarification.")

class AIUnclearTermItem(BaseModel):
    term_title: str = Field(..., description="Title of the ambiguous or conflicting term.")
    clause_reference: Optional[str] = Field(None, description="Clause number or section where ambiguity occurs.")
    issue_type: str = Field(..., description="'AMBIGUITY', 'CONFLICTING_TERMS', 'POLICY_CONFLICT', or 'UNDEFINED_STANDARD'.")
    description: str = Field(..., description="Explanation of why this term is unclear, contradictory, or conflicts with organizational policy.")
    policy_reference: Optional[str] = Field(None, description="Section of the organizational policy that conflicts, if applicable.")
    source_page: Optional[int] = None
    source_section: Optional[str] = None
    source_quote: str
    certainty: str = "UNCERTAIN"
    confidence_score: float = 0.5
    uncertainty_rationale: Optional[str] = None
    clarification_questions: List[AIClarificationQuestion] = []

class ContractAnalysisAIOutput(BaseModel):
    contract_title: str = Field(..., description="Identified formal title of the contract.")
    overall_effective_date: Optional[str] = Field(None, description="Global contract effective date in YYYY-MM-DD.")
    parties: List[AIPartyItem] = []
    clauses: List[AIClauseItem] = []
    obligations: List[AIObligationItem] = []
    unclear_terms: List[AIUnclearTermItem] = []

# --- API Request / Response Schemas ---
class ItemStatusUpdate(BaseModel):
    status: str = Field(..., description="'APPROVED', 'REJECTED', 'PENDING', 'EDITED'")
    user_correction_notes: Optional[str] = None

class PartyUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    effective_date: Optional[str] = None
    jurisdiction: Optional[str] = None
    status: Optional[str] = None
    user_correction_notes: Optional[str] = None
    certainty: Optional[str] = None

class ClauseUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    clause_type: Optional[str] = None
    effective_date: Optional[str] = None
    expiry_date: Optional[str] = None
    renewal_type: Optional[str] = None
    notice_period_days: Optional[int] = None
    termination_type: Optional[str] = None
    status: Optional[str] = None
    user_correction_notes: Optional[str] = None
    certainty: Optional[str] = None

class ObligationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    responsible_party: Optional[str] = None
    due_date: Optional[str] = None
    frequency: Optional[str] = None
    consequence_of_breach: Optional[str] = None
    status: Optional[str] = None
    user_correction_notes: Optional[str] = None
    certainty: Optional[str] = None

class UnclearTermUpdate(BaseModel):
    term_title: Optional[str] = None
    description: Optional[str] = None
    issue_type: Optional[str] = None
    status: Optional[str] = None
    user_correction_notes: Optional[str] = None
    user_answer: Optional[str] = None

class PartyResponse(BaseModel):
    id: int
    version_id: int
    name: str
    role: str
    effective_date: Optional[str] = None
    jurisdiction: Optional[str] = None
    status: str
    user_correction_notes: Optional[str] = None
    is_stale: bool
    stale_reason: Optional[str] = None
    source_page: Optional[int] = None
    source_section: Optional[str] = None
    source_quote: Optional[str] = None
    certainty: str
    confidence_score: float
    uncertainty_rationale: Optional[str] = None

    class Config:
        from_attributes = True

class ClauseResponse(BaseModel):
    id: int
    version_id: int
    clause_type: str
    title: str
    summary: str
    effective_date: Optional[str] = None
    expiry_date: Optional[str] = None
    renewal_type: Optional[str] = None
    notice_period_days: Optional[int] = None
    termination_type: Optional[str] = None
    status: str
    user_correction_notes: Optional[str] = None
    is_stale: bool
    stale_reason: Optional[str] = None
    source_page: Optional[int] = None
    source_section: Optional[str] = None
    source_quote: Optional[str] = None
    certainty: str
    confidence_score: float
    uncertainty_rationale: Optional[str] = None

    class Config:
        from_attributes = True

class ObligationResponse(BaseModel):
    id: int
    version_id: int
    title: str
    description: str
    responsible_party: str
    due_date: Optional[str] = None
    frequency: Optional[str] = None
    consequence_of_breach: Optional[str] = None
    status: str
    user_correction_notes: Optional[str] = None
    is_stale: bool
    stale_reason: Optional[str] = None
    source_page: Optional[int] = None
    source_section: Optional[str] = None
    source_quote: Optional[str] = None
    certainty: str
    confidence_score: float
    uncertainty_rationale: Optional[str] = None

    class Config:
        from_attributes = True

class ClarificationQuestionResponse(BaseModel):
    id: int
    question: str
    suggested_action: Optional[str] = None
    user_answer: Optional[str] = None

    class Config:
        from_attributes = True

class UnclearTermResponse(BaseModel):
    id: int
    version_id: int
    term_title: str
    clause_reference: Optional[str] = None
    issue_type: str
    description: str
    policy_reference: Optional[str] = None
    status: str
    user_correction_notes: Optional[str] = None
    is_stale: bool
    stale_reason: Optional[str] = None
    source_page: Optional[int] = None
    source_section: Optional[str] = None
    source_quote: Optional[str] = None
    certainty: str
    confidence_score: float
    uncertainty_rationale: Optional[str] = None
    clarification_questions: List[ClarificationQuestionResponse] = []

    class Config:
        from_attributes = True
