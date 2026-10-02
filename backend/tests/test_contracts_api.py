from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.models.contract import Contract, ContractVersion
from app.models.extracted_item import ExtractedParty, ExtractedClause, ExtractedObligation, UnclearTerm
from app.schemas.extraction import (
    ContractAnalysisAIOutput,
    AIPartyItem,
    AIClauseItem,
    AIObligationItem,
    AIUnclearTermItem,
    AIClarificationQuestion,
)
from app.schemas.summary import LEGAL_DISCLAIMER_TEXT

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "disclaimer" in data
    assert data["disclaimer"] == LEGAL_DISCLAIMER_TEXT
    assert "Information Management Tool" in data["application_type"]

def test_upload_validation_missing_input():
    response = client.post("/api/contracts/upload", data={})
    assert response.status_code == 400
    assert "Please provide a contract document" in response.json()["detail"]

def test_upload_validation_unsupported_file_extension():
    response = client.post(
        "/api/contracts/upload",
        files={"file": ("contract.exe", b"binary content", "application/octet-stream")}
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]

def test_upload_contract_with_mocked_gemini():
    # Mock AI response
    fake_ai_output = ContractAnalysisAIOutput(
        contract_title="Apex Cloud MSA",
        overall_effective_date="2026-03-01",
        parties=[
            AIPartyItem(
                name="Apex Cloud Solutions Inc.",
                role="Vendor",
                effective_date="2026-03-01",
                jurisdiction="Delaware",
                source_section="Preamble",
                source_quote="Apex Cloud Solutions Inc. ('Vendor')",
                certainty="CONFIRMED",
                confidence_score=1.0
            ),
            AIPartyItem(
                name="Meridian Financial Corp.",
                role="Client",
                effective_date="2026-03-01",
                jurisdiction="New York",
                source_section="Preamble",
                source_quote="Meridian Financial Corp. ('Client')",
                certainty="CONFIRMED",
                confidence_score=1.0
            )
        ],
        clauses=[
            AIClauseItem(
                clause_type="EXPIRY",
                title="Initial Term & Expiration",
                summary="2-year initial term expiring 2028-02-29.",
                expiry_date="2028-02-29",
                source_section="Section 1.1",
                source_quote="terminating on February 29, 2028",
                certainty="CONFIRMED",
                confidence_score=1.0
            ),
            AIClauseItem(
                clause_type="RENEWAL",
                title="Automatic Renewal",
                summary="Auto-renews unless 60 days notice is given.",
                notice_period_days=60,
                expiry_date="2028-02-29",
                renewal_type="Auto-renewal",
                source_section="Section 2.1",
                source_quote="at least sixty (60) days prior to expiration",
                certainty="CONFIRMED",
                confidence_score=1.0
            )
        ],
        obligations=[
            AIObligationItem(
                title="Annual SOC 2 Audit",
                description="Deliver SOC 2 Type II audit report.",
                responsible_party="Vendor",
                due_date="2026-09-30",
                source_section="Section 4.1",
                source_quote="Vendor shall provide Client with an updated SOC 2 report",
                certainty="CONFIRMED",
                confidence_score=1.0
            )
        ],
        unclear_terms=[
            AIUnclearTermItem(
                term_title="Vague Disaster Recovery Standard",
                clause_reference="Section 6.1",
                issue_type="AMBIGUITY",
                description="Refers to industry benchmarks without specific RTO/RPO targets.",
                source_section="Section 6.1",
                source_quote="adhering to commercially standard practices",
                certainty="UNCERTAIN",
                confidence_score=0.5,
                clarification_questions=[
                    AIClarificationQuestion(
                        question="What specific RTO and RPO limits are required for disaster recovery?",
                        suggested_action="Specify RTO <= 4 hours and RPO <= 1 hour."
                    )
                ]
            )
        ]
    )

    # Mock DB session
    mock_db = MagicMock()
    mock_contract = Contract(id=101, title="Apex Cloud MSA", description="Created via TEXT upload")
    mock_contract.versions = []
    mock_contract.policy_documents = []

    def mock_add(obj):
        if isinstance(obj, Contract):
            obj.id = 101
            obj.versions = []
            obj.policy_documents = []
        elif isinstance(obj, ContractVersion):
            obj.id = 201
            obj.parties = []
            obj.clauses = []
            obj.obligations = []
            obj.unclear_terms = []
            obj.reminders = []
            mock_contract.versions.append(obj)

    mock_db.add.side_effect = mock_add
    mock_db.query.return_value.filter.return_value.first.return_value = mock_contract
    mock_db.query.return_value.order_by.return_value.all.return_value = [mock_contract]

    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("app.api.contracts.analyze_contract_with_gemini", return_value=fake_ai_output):
        response = client.post(
            "/api/contracts/upload",
            data={
                "pasted_text": "Sample contract text between Apex Cloud and Meridian Financial...",
                "title": "Apex Cloud MSA"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 101
        assert data["title"] == "Apex Cloud MSA"

    app.dependency_overrides.clear()
