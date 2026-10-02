from unittest.mock import MagicMock
from app.services.summary_service import generate_reviewed_summary
from app.models.contract import Contract, ContractVersion
from app.models.extracted_item import ExtractedParty, ExtractedClause, ExtractedObligation, UnclearTerm
from app.models.reminder import CalculatedReminder
from app.schemas.summary import LEGAL_DISCLAIMER_TEXT

def test_summary_includes_only_approved_and_edited_items():
    contract = Contract(
        id=1,
        title="Enterprise SaaS Agreement",
        description="Master agreement"
    )
    contract.policy_documents = []

    version = ContractVersion(
        id=1,
        contract_id=1,
        version_number=1,
        filename="saas_contract.pdf",
        file_type="pdf",
        raw_text="Contract content...",
        is_active=True
    )

    # Party 1 approved, Party 2 pending
    p1 = ExtractedParty(
        id=1, version_id=1, name="Cloud Services Corp", role="Vendor",
        status="APPROVED", is_stale=False, certainty="CONFIRMED", confidence_score=1.0,
        source_quote="Cloud Services Corp ('Vendor')"
    )
    p2 = ExtractedParty(
        id=2, version_id=1, name="Undecided Subcontractor", role="Subcontractor",
        status="PENDING", is_stale=False, certainty="UNCERTAIN", confidence_score=0.4,
        source_quote="may engage subcontractors"
    )
    version.parties = [p1, p2]

    # Clause 1 approved, Clause 2 rejected
    c1 = ExtractedClause(
        id=1, version_id=1, clause_type="RENEWAL", title="Annual Renewal",
        summary="Auto-renews unless 30 days notice.",
        notice_period_days=30, expiry_date="2027-01-01",
        status="APPROVED", is_stale=False, certainty="CONFIRMED", confidence_score=1.0,
        source_quote="renews for successive 1-year terms"
    )
    c2 = ExtractedClause(
        id=2, version_id=1, clause_type="OTHER", title="Draft Marketing Clause",
        summary="Vendor may use logo.",
        status="REJECTED", is_stale=False, certainty="CONFIRMED", confidence_score=0.9,
        source_quote="right to display logo"
    )
    version.clauses = [c1, c2]

    # Obligation 1 edited (counts as approved), Obligation 2 pending
    o1 = ExtractedObligation(
        id=1, version_id=1, title="Quarterly Security Reports",
        description="Deliver quarterly compliance reports.",
        responsible_party="Vendor", due_date="2026-06-30",
        status="EDITED", is_stale=False, certainty="CONFIRMED", confidence_score=1.0,
        source_quote="quarterly compliance reporting"
    )
    o2 = ExtractedObligation(
        id=2, version_id=1, title="Pending Duty",
        description="To be reviewed.",
        responsible_party="Client",
        status="PENDING", is_stale=False, certainty="CONFIRMED", confidence_score=1.0,
        source_quote="pending"
    )
    version.obligations = [o1, o2]

    # Unclear term flagged
    u1 = UnclearTerm(
        id=1, version_id=1, term_title="Ambiguous SLA Credits",
        issue_type="AMBIGUITY",
        description="Calculation method for downtime credits is omitted.",
        status="PENDING", is_stale=False, certainty="UNCERTAIN", confidence_score=0.5,
        source_quote="credits as determined by vendor"
    )
    u1.clarification_questions = []
    version.unclear_terms = [u1]

    r1 = CalculatedReminder(
        id=1, version_id=1, title="Renewal Notice Deadline",
        category="RENEWAL_NOTICE", target_date="2026-12-02",
        reminder_date="2026-11-02", days_before=30,
        description="Notice window reminder", urgency="MEDIUM", is_dismissed=False
    )
    version.reminders = [r1]

    mock_db = MagicMock()

    summary = generate_reviewed_summary(contract, version, mock_db)

    # Assertions
    assert summary.contract_title == "Enterprise SaaS Agreement"
    assert summary.version_number == 1
    # Only approved or edited items in approved list
    assert len(summary.approved_parties) == 1
    assert summary.approved_parties[0].name == "Cloud Services Corp"
    assert len(summary.approved_clauses) == 1
    assert summary.approved_clauses[0].title == "Annual Renewal"
    assert len(summary.approved_obligations) == 1
    assert summary.approved_obligations[0].title == "Quarterly Security Reports"

    # Verify counts
    assert summary.total_approved_items == 3
    assert summary.total_pending_items == 3 # p2, o2, u1
    assert summary.total_stale_items == 0

    # Verify legal disclaimer presence
    assert summary.disclaimer == LEGAL_DISCLAIMER_TEXT
    assert "ADMINISTRATIVE INFORMATION MANAGEMENT DISCLAIMER" in summary.markdown_content
    assert "DISCLAIMER: This document is an information-management summary" in summary.markdown_content
