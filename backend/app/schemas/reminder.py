from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class CalculatedReminderResponse(BaseModel):
    id: int
    version_id: int
    clause_id: Optional[int] = None
    obligation_id: Optional[int] = None
    title: str
    category: str # RENEWAL_NOTICE, CONTRACT_EXPIRY, OBLIGATION_DEADLINE, RECURRING_OBLIGATION
    target_date: str # YYYY-MM-DD
    reminder_date: str # YYYY-MM-DD
    days_before: int
    responsible_party: Optional[str] = None
    description: str
    urgency: str # OVERDUE, HIGH, MEDIUM, LOW
    is_dismissed: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ReminderUrgencyCounts(BaseModel):
    overdue: int = 0
    next_7_days: int = 0
    next_30_days: int = 0
    next_90_days: int = 0
    total_active: int = 0
