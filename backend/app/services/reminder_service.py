from datetime import datetime, date, timedelta
from typing import List, Optional
from dateutil import parser as date_parser
from sqlalchemy.orm import Session
from app.models.contract import ContractVersion
from app.models.extracted_item import ExtractedClause, ExtractedObligation
from app.models.reminder import CalculatedReminder

def parse_iso_or_text_date(date_str: Optional[str]) -> Optional[date]:
    """
    Deterministically parses a date string into a Python datetime.date object.
    Supports ISO formats ('YYYY-MM-DD') and common text formats.
    """
    if not date_str or not date_str.strip():
        return None
    try:
        # First try strict ISO
        return datetime.strptime(date_str.strip()[:10], "%Y-%m-%d").date()
    except ValueError:
        pass

    try:
        dt = date_parser.parse(date_str.strip(), fuzzy=True)
        return dt.date()
    except (ValueError, TypeError, OverflowError):
        return None

def compute_urgency(target_date: date, ref_date: Optional[date] = None) -> str:
    """
    Computes deterministic urgency based on days remaining until the target date.
    """
    today = ref_date or date.today()
    delta = (target_date - today).days

    if delta < 0:
        return "OVERDUE"
    elif delta <= 7:
        return "HIGH"
    elif delta <= 30:
        return "MEDIUM"
    else:
        return "LOW"

def calculate_reminders_for_version(
    version: ContractVersion,
    db: Session,
    ref_date: Optional[date] = None
) -> List[CalculatedReminder]:
    """
    Deterministically computes all reminder dates for a contract version's
    clauses and obligations using pure Python date arithmetic (zero AI).
    Removes previous calculated reminders and inserts the fresh deterministic schedule.
    """
    today = ref_date or date.today()
    created_reminders: List[CalculatedReminder] = []

    # 1. Process Clauses (Expiry, Renewal, Notice)
    for clause in version.clauses:
        # Skip rejected items
        if clause.status == "REJECTED":
            continue

        expiry_d = parse_iso_or_text_date(clause.expiry_date)

        # A) Expiry Date Reminders
        if expiry_d:
            expiry_offsets = [90, 60, 30, 14, 7]
            for offset in expiry_offsets:
                remind_d = expiry_d - timedelta(days=offset)
                urgency = compute_urgency(expiry_d, today)
                desc = f"Contract expiry in {offset} days for '{clause.title}'. Target expiry date: {expiry_d.isoformat()}."
                
                reminder = CalculatedReminder(
                    version_id=version.id,
                    clause_id=clause.id,
                    title=f"Contract Expiry ({offset}d): {clause.title}",
                    category="CONTRACT_EXPIRY",
                    target_date=expiry_d.isoformat(),
                    reminder_date=remind_d.isoformat(),
                    days_before=offset,
                    description=desc,
                    urgency=urgency,
                    is_dismissed=False
                )
                created_reminders.append(reminder)

        # B) Renewal / Notice Cutoff Reminders
        notice_days = clause.notice_period_days
        if expiry_d and notice_days and notice_days > 0:
            notice_cutoff_d = expiry_d - timedelta(days=notice_days)
            notice_offsets = [30, 14, 7, 0]
            
            for offset in notice_offsets:
                remind_d = notice_cutoff_d - timedelta(days=offset)
                urgency = compute_urgency(notice_cutoff_d, today)
                desc = (
                    f"Notice deadline approaching ({offset} days prior to notice cutoff). "
                    f"Requires {notice_days} days notice before expiry on {expiry_d.isoformat()}. "
                    f"Notice deadline date: {notice_cutoff_d.isoformat()}."
                )
                label = f"Notice Cutoff ({offset}d prior)" if offset > 0 else "Notice Cutoff Date"
                reminder = CalculatedReminder(
                    version_id=version.id,
                    clause_id=clause.id,
                    title=f"{label}: {clause.title}",
                    category="RENEWAL_NOTICE",
                    target_date=notice_cutoff_d.isoformat(),
                    reminder_date=remind_d.isoformat(),
                    days_before=offset,
                    description=desc,
                    urgency=urgency,
                    is_dismissed=False
                )
                created_reminders.append(reminder)

    # 2. Process Obligations
    for obligation in version.obligations:
        if obligation.status == "REJECTED":
            continue

        due_d = parse_iso_or_text_date(obligation.due_date)

        # Fixed deadline obligation
        if due_d:
            offsets = [30, 14, 7, 1]
            for offset in offsets:
                # Only schedule if target is sufficiently far or for record
                remind_d = due_d - timedelta(days=offset)
                urgency = compute_urgency(due_d, today)
                desc = (
                    f"Obligation deadline for '{obligation.title}' ({obligation.responsible_party}) "
                    f"is due in {offset} days on {due_d.isoformat()}."
                )
                reminder = CalculatedReminder(
                    version_id=version.id,
                    obligation_id=obligation.id,
                    title=f"Obligation Due ({offset}d): {obligation.title}",
                    category="OBLIGATION_DEADLINE",
                    target_date=due_d.isoformat(),
                    reminder_date=remind_d.isoformat(),
                    days_before=offset,
                    responsible_party=obligation.responsible_party,
                    description=desc,
                    urgency=urgency,
                    is_dismissed=False
                )
                created_reminders.append(reminder)

        # Recurring obligation calculation (Monthly, Quarterly, Annual)
        elif obligation.frequency and obligation.frequency.lower() in ["monthly", "quarterly", "annual"]:
            freq = obligation.frequency.lower()
            interval_days = 30 if freq == "monthly" else 90 if freq == "quarterly" else 365
            # Project next upcoming recurrence date deterministically
            next_target = today + timedelta(days=interval_days)
            remind_d = next_target - timedelta(days=7)
            desc = (
                f"Recurring ({obligation.frequency}) obligation '{obligation.title}' "
                f"assigned to {obligation.responsible_party}. Next projected cycle deadline: {next_target.isoformat()}."
            )
            reminder = CalculatedReminder(
                version_id=version.id,
                obligation_id=obligation.id,
                title=f"Recurring Obligation: {obligation.title}",
                category="RECURRING_OBLIGATION",
                target_date=next_target.isoformat(),
                reminder_date=remind_d.isoformat(),
                days_before=7,
                responsible_party=obligation.responsible_party,
                description=desc,
                urgency="MEDIUM",
                is_dismissed=False
            )
            created_reminders.append(reminder)

    # Clean existing reminders for this version in database
    db.query(CalculatedReminder).filter(CalculatedReminder.version_id == version.id).delete()

    for r in created_reminders:
        db.add(r)
    db.commit()

    return created_reminders
