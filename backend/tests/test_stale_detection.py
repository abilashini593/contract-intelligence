from unittest.mock import MagicMock
from app.services.stale_service import detect_stale_items_for_version
from app.models.contract import ContractVersion
from app.models.extracted_item import ExtractedParty, ExtractedClause, ExtractedObligation

def test_detect_stale_clauses_when_notice_changed():
    mock_db = MagicMock()

    # Version 1 with approved renewal clause: 60 days notice
    v1 = MagicMock(spec=ContractVersion)
    v1.version_number = 1
    c1 = ExtractedClause(
        id=1,
        version_id=1,
        clause_type="RENEWAL",
        title="Renewal Clause",
        summary="Auto-renews with 60 days notice prior to Dec 31.",
        notice_period_days=60,
        expiry_date="2026-12-31",
        renewal_type="Auto-renewal",
        status="APPROVED",
        is_stale=False
    )
    v1.clauses = [c1]
    v1.parties = []
    v1.obligations = []

    # Version 2 with modified renewal clause: altered to 30 days notice
    v2 = MagicMock(spec=ContractVersion)
    v2.version_number = 2
    c2 = ExtractedClause(
        id=2,
        version_id=2,
        clause_type="RENEWAL",
        title="Renewal Clause",
        summary="Auto-renews with 30 days notice prior to Dec 31.",
        notice_period_days=30, # altered!
        expiry_date="2026-12-31",
        renewal_type="Auto-renewal",
        status="PENDING",
        is_stale=False
    )
    v2.clauses = [c2]
    v2.parties = []
    v2.obligations = []

    stale_count = detect_stale_items_for_version(v2, v1, mock_db)
    assert stale_count == 1
    assert c2.status == "STALE"
    assert c2.is_stale is True
    assert "notice period altered from 60d to 30d" in c2.stale_reason

def test_detect_stale_obligations_when_deadline_changed():
    mock_db = MagicMock()

    # v1 approved obligation due on 2026-06-30
    v1 = MagicMock(spec=ContractVersion)
    v1.version_number = 1
    ob1 = ExtractedObligation(
        id=10,
        version_id=1,
        title="Final Deliverable Submission",
        description="Submit complete system code.",
        responsible_party="Vendor",
        due_date="2026-06-30",
        status="APPROVED",
        is_stale=False
    )
    v1.parties = []
    v1.clauses = []
    v1.obligations = [ob1]

    # v2 changed deadline to 2026-05-15
    v2 = MagicMock(spec=ContractVersion)
    v2.version_number = 2
    ob2 = ExtractedObligation(
        id=11,
        version_id=2,
        title="Final Deliverable Submission",
        description="Submit complete system code.",
        responsible_party="Vendor",
        due_date="2026-05-15", # altered!
        status="PENDING",
        is_stale=False
    )
    v2.parties = []
    v2.clauses = []
    v2.obligations = [ob2]

    stale_count = detect_stale_items_for_version(v2, v1, mock_db)
    assert stale_count == 1
    assert ob2.status == "STALE"
    assert ob2.is_stale is True
    assert "due date changed from '2026-06-30' to '2026-05-15'" in ob2.stale_reason

def test_unchanged_items_not_marked_stale():
    mock_db = MagicMock()

    v1 = MagicMock(spec=ContractVersion)
    v1.version_number = 1
    ob1 = ExtractedObligation(
        id=20,
        version_id=1,
        title="Quarterly Review",
        description="Conduct quarterly service review.",
        responsible_party="Both Parties",
        due_date=None,
        status="APPROVED",
        is_stale=False
    )
    v1.parties = []
    v1.clauses = []
    v1.obligations = [ob1]

    v2 = MagicMock(spec=ContractVersion)
    v2.version_number = 2
    ob2 = ExtractedObligation(
        id=21,
        version_id=2,
        title="Quarterly Review",
        description="Conduct quarterly service review.",
        responsible_party="Both Parties",
        due_date=None,
        status="PENDING",
        is_stale=False
    )
    v2.parties = []
    v2.clauses = []
    v2.obligations = [ob2]

    stale_count = detect_stale_items_for_version(v2, v1, mock_db)
    assert stale_count == 0
    assert ob2.is_stale is False
    assert ob2.status == "PENDING"
