from datetime import date, timedelta
from unittest.mock import MagicMock
from app.services.reminder_service import (
    parse_iso_or_text_date,
    compute_urgency,
    calculate_reminders_for_version,
)
from app.models.contract import ContractVersion
from app.models.extracted_item import ExtractedClause, ExtractedObligation

def test_parse_iso_or_text_date():
    assert parse_iso_or_text_date("2026-12-31") == date(2026, 12, 31)
    assert parse_iso_or_text_date("2026-05-15T00:00:00") == date(2026, 5, 15)
    assert parse_iso_or_text_date("October 25, 2026") == date(2026, 10, 25)
    assert parse_iso_or_text_date("invalid date") is None
    assert parse_iso_or_text_date(None) is None

def test_compute_urgency():
    today = date(2026, 6, 1)
    
    # Overdue
    assert compute_urgency(date(2026, 5, 30), today) == "OVERDUE"
    # High (within 7 days)
    assert compute_urgency(date(2026, 6, 5), today) == "HIGH"
    # Medium (within 30 days)
    assert compute_urgency(date(2026, 6, 20), today) == "MEDIUM"
    # Low (> 30 days)
    assert compute_urgency(date(2026, 8, 1), today) == "LOW"

def test_deterministic_expiry_and_renewal_reminders():
    # Setup mock version with clauses
    version = MagicMock(spec=ContractVersion)
    version.id = 1

    clause_expiry = ExtractedClause(
        id=10,
        version_id=1,
        clause_type="EXPIRY",
        title="Initial Term & Expiration",
        summary="Agreement expires on 2026-12-31.",
        expiry_date="2026-12-31",
        notice_period_days=None,
        status="APPROVED"
    )

    clause_renewal = ExtractedClause(
        id=11,
        version_id=1,
        clause_type="RENEWAL",
        title="Automatic Renewal Notice",
        summary="Renews automatically unless 60 days notice is given before 2026-12-31.",
        expiry_date="2026-12-31",
        notice_period_days=60,
        status="APPROVED"
    )

    version.clauses = [clause_expiry, clause_renewal]
    version.obligations = []

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.delete.return_value = None

    ref_date = date(2026, 6, 1)
    reminders = calculate_reminders_for_version(version, mock_db, ref_date=ref_date)

    # Verify Expiry reminders (90, 60, 30, 14, 7 days before 2026-12-31)
    expiry_reminders = [r for r in reminders if r.category == "CONTRACT_EXPIRY"]
    assert len(expiry_reminders) >= 5
    reminder_dates = [r.reminder_date for r in expiry_reminders]
    assert "2026-10-02" in reminder_dates # 90 days before Dec 31
    assert "2026-11-01" in reminder_dates # 60 days before Dec 31
    assert "2026-12-01" in reminder_dates # 30 days before Dec 31

    # Verify Renewal Notice Cutoff reminders:
    # Notice Cutoff = Dec 31, 2026 - 60 days = Nov 1, 2026
    renewal_reminders = [r for r in reminders if r.category == "RENEWAL_NOTICE"]
    assert len(renewal_reminders) == 4
    for r in renewal_reminders:
        assert r.target_date == "2026-11-01"

def test_deterministic_obligation_reminders():
    version = MagicMock(spec=ContractVersion)
    version.id = 2
    version.clauses = []

    ob_fixed = ExtractedObligation(
        id=20,
        version_id=2,
        title="Deliver Annual Security Audit",
        description="Provide SOC2 Type II report.",
        responsible_party="Vendor",
        due_date="2026-09-30",
        frequency="One-time",
        status="APPROVED"
    )

    ob_rejected = ExtractedObligation(
        id=21,
        version_id=2,
        title="Unwanted Draft Duty",
        description="Disregarded duty.",
        responsible_party="Client",
        due_date="2026-08-15",
        status="REJECTED"
    )

    version.obligations = [ob_fixed, ob_rejected]

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.delete.return_value = None

    reminders = calculate_reminders_for_version(version, mock_db, ref_date=date(2026, 6, 1))

    # Rejected obligation must have zero reminders
    rejected_rems = [r for r in reminders if r.obligation_id == 21]
    assert len(rejected_rems) == 0

    # Fixed obligation has reminders (30, 14, 7, 1 days before Sept 30, 2026)
    fixed_rems = [r for r in reminders if r.obligation_id == 20]
    assert len(fixed_rems) == 4
    dates = [r.reminder_date for r in fixed_rems]
    assert "2026-08-31" in dates # 30d before
    assert "2026-09-16" in dates # 14d before
    assert "2026-09-23" in dates # 7d before
    assert "2026-09-29" in dates # 1d before
