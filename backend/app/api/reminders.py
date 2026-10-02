from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.contract import Contract, ContractVersion
from app.models.reminder import CalculatedReminder
from app.schemas.reminder import CalculatedReminderResponse, ReminderUrgencyCounts
from app.services.reminder_service import compute_urgency, parse_iso_or_text_date

router = APIRouter(prefix="/api/contracts", tags=["Reminders & Deadlines"])

class RemindersListResponse(BaseModel):
    contract_id: int
    version_id: int
    reminders: List[CalculatedReminderResponse]
    urgency_counts: ReminderUrgencyCounts

@router.get("/{contract_id}/reminders", response_model=RemindersListResponse)
def get_contract_reminders(
    contract_id: int,
    version_id: Optional[int] = Query(None),
    urgency: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    include_dismissed: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Retrieves deterministic reminders and deadlines for upcoming obligations and renewal notices.
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contract {contract_id} not found.")

    if version_id:
        target_version = db.query(ContractVersion).filter(
            ContractVersion.id == version_id,
            ContractVersion.contract_id == contract_id
        ).first()
        if not target_version:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specified version not found.")
    else:
        target_version = next((v for v in contract.versions if v.is_active), None)
        if not target_version and contract.versions:
            target_version = contract.versions[-1]

    if not target_version:
        return RemindersListResponse(
            contract_id=contract_id,
            version_id=0,
            reminders=[],
            urgency_counts=ReminderUrgencyCounts()
        )

    query = db.query(CalculatedReminder).filter(CalculatedReminder.version_id == target_version.id)

    if not include_dismissed:
        query = query.filter(CalculatedReminder.is_dismissed == False)

    if urgency:
        query = query.filter(CalculatedReminder.urgency == urgency.upper())

    if category:
        query = query.filter(CalculatedReminder.category == category.upper())

    all_reminders = query.order_by(CalculatedReminder.reminder_date.asc()).all()

    # Re-evaluate live urgency against today
    today = date.today()
    for r in all_reminders:
        target_d = parse_iso_or_text_date(r.target_date)
        if target_d:
            r.urgency = compute_urgency(target_d, today)

    # Compute urgency metrics
    counts = ReminderUrgencyCounts()
    for r in all_reminders:
        target_d = parse_iso_or_text_date(r.target_date)
        if not target_d:
            continue
        days = (target_d - today).days
        if days < 0:
            counts.overdue += 1
        elif days <= 7:
            counts.next_7_days += 1
        elif days <= 30:
            counts.next_30_days += 1
        elif days <= 90:
            counts.next_90_days += 1
    counts.total_active = len(all_reminders)

    return RemindersListResponse(
        contract_id=contract_id,
        version_id=target_version.id,
        reminders=[CalculatedReminderResponse.model_validate(r) for r in all_reminders],
        urgency_counts=counts
    )

@router.patch("/reminders/{reminder_id}/toggle-dismiss", response_model=CalculatedReminderResponse)
def toggle_dismiss_reminder(reminder_id: int, db: Session = Depends(get_db)):
    """Toggles the dismissed status of a calculated reminder."""
    reminder = db.query(CalculatedReminder).filter(CalculatedReminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found.")

    reminder.is_dismissed = not reminder.is_dismissed
    db.commit()
    db.refresh(reminder)
    return reminder
