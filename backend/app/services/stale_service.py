from typing import List, Tuple
from sqlalchemy.orm import Session
from app.models.contract import ContractVersion
from app.models.extracted_item import (
    ExtractedParty,
    ExtractedClause,
    ExtractedObligation,
    UnclearTerm,
)

def normalize_text(text: str) -> str:
    """Normalizes text for robust comparison."""
    if not text:
        return ""
    return " ".join(text.lower().split())

def detect_stale_items_for_version(
    current_version: ContractVersion,
    previous_version: ContractVersion,
    db: Session
) -> int:
    """
    Compares the newly uploaded version items against the previously APPROVED items
    from the preceding contract version. If an item was approved in the previous version
    but has altered terms, dates, or stipulations in the new version, marks the new item
    as STALE (with is_stale=True and a human-readable stale_reason explaining the change).
    
    Returns the total count of items flagged as STALE.
    """
    stale_count = 0

    # 1. Compare Parties
    prev_approved_parties = [p for p in previous_version.parties if p.status == "APPROVED"]
    for prev_party in prev_approved_parties:
        prev_name_norm = normalize_text(prev_party.name)
        # Find match in current version
        match = next(
            (p for p in current_version.parties if normalize_text(p.name) == prev_name_norm),
            None
        )
        if match:
            changes = []
            if normalize_text(match.role) != normalize_text(prev_party.role):
                changes.append(f"role changed from '{prev_party.role}' to '{match.role}'")
            if match.effective_date != prev_party.effective_date:
                changes.append(f"effective date changed from '{prev_party.effective_date}' to '{match.effective_date}'")
            if normalize_text(match.jurisdiction or "") != normalize_text(prev_party.jurisdiction or ""):
                changes.append(f"jurisdiction changed from '{prev_party.jurisdiction}' to '{match.jurisdiction}'")
            
            if changes:
                match.status = "STALE"
                match.is_stale = True
                match.stale_reason = f"Approved in v{previous_version.version_number}, but {', '.join(changes)}."
                stale_count += 1

    # 2. Compare Clauses
    prev_approved_clauses = [c for c in previous_version.clauses if c.status == "APPROVED"]
    for prev_clause in prev_approved_clauses:
        # Match by clause_type or similar title
        match = next(
            (c for c in current_version.clauses if c.clause_type == prev_clause.clause_type),
            None
        )
        if not match:
            # Fallback match by normalized title
            match = next(
                (c for c in current_version.clauses if normalize_text(c.title) == normalize_text(prev_clause.title)),
                None
            )

        if match:
            clause_changes = []
            if match.notice_period_days != prev_clause.notice_period_days:
                clause_changes.append(f"notice period altered from {prev_clause.notice_period_days}d to {match.notice_period_days}d")
            if match.expiry_date != prev_clause.expiry_date:
                clause_changes.append(f"expiry date altered from '{prev_clause.expiry_date}' to '{match.expiry_date}'")
            if normalize_text(match.renewal_type or "") != normalize_text(prev_clause.renewal_type or ""):
                clause_changes.append(f"renewal type altered from '{prev_clause.renewal_type}' to '{match.renewal_type}'")
            if normalize_text(match.summary)[:60] != normalize_text(prev_clause.summary)[:60]:
                clause_changes.append("clause terms or language modified")

            if clause_changes:
                match.status = "STALE"
                match.is_stale = True
                match.stale_reason = f"Previously approved in v{previous_version.version_number}. Differences: {'; '.join(clause_changes)}."
                stale_count += 1

    # 3. Compare Obligations
    prev_approved_obs = [o for o in previous_version.obligations if o.status == "APPROVED"]
    for prev_ob in prev_approved_obs:
        prev_title_norm = normalize_text(prev_ob.title)
        match = next(
            (o for o in current_version.obligations if normalize_text(o.title) == prev_title_norm),
            None
        )
        if not match:
            # Match by responsible party if only 1 obligation for that party
            party_matches = [
                o for o in current_version.obligations 
                if normalize_text(o.responsible_party) == normalize_text(prev_ob.responsible_party)
            ]
            if len(party_matches) == 1:
                match = party_matches[0]

        if match:
            ob_changes = []
            if match.due_date != prev_ob.due_date:
                ob_changes.append(f"due date changed from '{prev_ob.due_date}' to '{match.due_date}'")
            if normalize_text(match.responsible_party) != normalize_text(prev_ob.responsible_party):
                ob_changes.append(f"responsible party changed from '{prev_ob.responsible_party}' to '{match.responsible_party}'")
            if normalize_text(match.description)[:60] != normalize_text(prev_ob.description)[:60]:
                ob_changes.append("obligation scope or terms revised")

            if ob_changes:
                match.status = "STALE"
                match.is_stale = True
                match.stale_reason = f"Previously approved in v{previous_version.version_number}. Changes: {', '.join(ob_changes)}."
                stale_count += 1

    db.commit()
    return stale_count
