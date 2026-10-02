from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.extracted_item import (
    ExtractedParty,
    ExtractedClause,
    ExtractedObligation,
    UnclearTerm,
    ClarificationQuestion,
)
from app.schemas.extraction import (
    PartyResponse,
    ClauseResponse,
    ObligationResponse,
    UnclearTermResponse,
    PartyUpdate,
    ClauseUpdate,
    ObligationUpdate,
    UnclearTermUpdate,
    ItemStatusUpdate,
)
from app.services.reminder_service import calculate_reminders_for_version

router = APIRouter(prefix="/api/items", tags=["Extracted Items"])

class BatchStatusUpdate(BaseModel):
    item_type: str # 'party', 'clause', 'obligation', 'unclear_term'
    item_ids: List[int]
    status: str # 'APPROVED', 'REJECTED'

@router.patch("/party/{item_id}", response_model=PartyResponse)
def update_party(item_id: int, payload: PartyUpdate, db: Session = Depends(get_db)):
    """Edits, approves, or rejects an extracted party item."""
    item = db.query(ExtractedParty).filter(ExtractedParty.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Party item not found.")

    for field, val in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, val)

    # If user manually approves or edits a stale item, resolve stale status
    if payload.status in ["APPROVED", "EDITED"]:
        item.is_stale = False

    db.commit()
    db.refresh(item)
    return item

@router.patch("/clause/{item_id}", response_model=ClauseResponse)
def update_clause(item_id: int, payload: ClauseUpdate, db: Session = Depends(get_db)):
    """Edits, approves, or rejects an extracted clause, recalculating deterministic reminder dates."""
    item = db.query(ExtractedClause).filter(ExtractedClause.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clause item not found.")

    for field, val in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, val)

    if payload.status in ["APPROVED", "EDITED"]:
        item.is_stale = False

    db.commit()
    db.refresh(item)

    # Recalculate deterministic reminders since dates or status may have changed
    calculate_reminders_for_version(item.version, db)

    return item

@router.patch("/obligation/{item_id}", response_model=ObligationResponse)
def update_obligation(item_id: int, payload: ObligationUpdate, db: Session = Depends(get_db)):
    """Edits, approves, or rejects an extracted obligation, recalculating deterministic reminder dates."""
    item = db.query(ExtractedObligation).filter(ExtractedObligation.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Obligation item not found.")

    for field, val in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, val)

    if payload.status in ["APPROVED", "EDITED"]:
        item.is_stale = False

    db.commit()
    db.refresh(item)

    # Recalculate deterministic reminders
    calculate_reminders_for_version(item.version, db)

    return item

@router.patch("/unclear-term/{item_id}", response_model=UnclearTermResponse)
def update_unclear_term(item_id: int, payload: UnclearTermUpdate, db: Session = Depends(get_db)):
    """Edits, resolves, or answers clarification questions for an unclear or conflicting term."""
    item = db.query(UnclearTerm).filter(UnclearTerm.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unclear term item not found.")

    for field, val in payload.model_dump(exclude_unset=True).items():
        if field == "user_answer" and val and item.clarification_questions:
            # Set answer on the first question or all questions
            item.clarification_questions[0].user_answer = val
        else:
            setattr(item, field, val)

    if payload.status in ["APPROVED", "EDITED"]:
        item.is_stale = False

    db.commit()
    db.refresh(item)
    return item

@router.post("/batch-status", status_code=status.HTTP_200_OK)
def batch_update_status(payload: BatchStatusUpdate, db: Session = Depends(get_db)):
    """Batch approves or rejects extracted items."""
    target_cls = {
        "party": ExtractedParty,
        "clause": ExtractedClause,
        "obligation": ExtractedObligation,
        "unclear_term": UnclearTerm,
    }.get(payload.item_type)

    if not target_cls:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid item_type '{payload.item_type}'.")

    items = db.query(target_cls).filter(target_cls.id.in_(payload.item_ids)).all()
    version_to_refresh = None
    for item in items:
        item.status = payload.status
        if payload.status in ["APPROVED", "EDITED"]:
            item.is_stale = False
        version_to_refresh = item.version

    db.commit()

    if version_to_refresh and payload.item_type in ["clause", "obligation"]:
        calculate_reminders_for_version(version_to_refresh, db)

    return {"updated_count": len(items), "status": payload.status}
