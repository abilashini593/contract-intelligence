from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from app.models.contract import Contract, ContractVersion
from app.schemas.summary import ReviewedContractSummaryResponse, LEGAL_DISCLAIMER_TEXT
from app.schemas.extraction import (
    PartyResponse,
    ClauseResponse,
    ObligationResponse,
    UnclearTermResponse,
)
from app.schemas.reminder import CalculatedReminderResponse

def generate_reviewed_summary(
    contract: Contract,
    version: ContractVersion,
    db: Session
) -> ReviewedContractSummaryResponse:
    """
    Generates a formal, reviewed contract summary including only approved items,
    deterministic deadlines, flagged ambiguous terms, and explicit information-management disclaimers.
    """
    # 1. Filter approved items
    approved_parties = [
        PartyResponse.model_validate(p) for p in version.parties if p.status in ["APPROVED", "EDITED"]
    ]
    approved_clauses = [
        ClauseResponse.model_validate(c) for c in version.clauses if c.status in ["APPROVED", "EDITED"]
    ]
    approved_obligations = [
        ObligationResponse.model_validate(o) for o in version.obligations if o.status in ["APPROVED", "EDITED"]
    ]
    reminders = [
        CalculatedReminderResponse.model_validate(r) for r in version.reminders if not r.is_dismissed
    ]
    flagged_unclear = [
        UnclearTermResponse.model_validate(u) for u in version.unclear_terms if u.status != "REJECTED"
    ]

    total_approved = len(approved_parties) + len(approved_clauses) + len(approved_obligations)
    total_pending = (
        sum(1 for p in version.parties if p.status == "PENDING") +
        sum(1 for c in version.clauses if c.status == "PENDING") +
        sum(1 for o in version.obligations if o.status == "PENDING") +
        sum(1 for u in version.unclear_terms if u.status == "PENDING")
    )
    total_stale = (
        sum(1 for p in version.parties if p.is_stale) +
        sum(1 for c in version.clauses if c.is_stale) +
        sum(1 for o in version.obligations if o.is_stale)
    )

    # 2. Extract key milestone dates
    effective_date = next((p.effective_date for p in approved_parties if p.effective_date), None)
    if not effective_date:
        effective_date = next((c.effective_date for c in approved_clauses if c.effective_date), None)

    expiry_clause = next((c for c in approved_clauses if c.clause_type in ["EXPIRY", "RENEWAL"] and c.expiry_date), None)
    expiry_date = expiry_clause.expiry_date if expiry_clause else None

    renewal_clause = next((c for c in approved_clauses if c.clause_type == "RENEWAL"), None)
    renewal_summary = f"{renewal_clause.title}: {renewal_clause.summary}" if renewal_clause else "No specific renewal clause approved."

    termination_clause = next((c for c in approved_clauses if c.clause_type == "TERMINATION"), None)
    termination_summary = f"{termination_clause.title}: {termination_clause.summary}" if termination_clause else "Standard termination terms apply."

    # 3. Generate Markdown content
    md_lines = [
        f"# Reviewed Contract Summary: {contract.title}",
        f"**Contract Version:** v{version.version_number} | **Generated On:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "> [!IMPORTANT]",
        f"> **ADMINISTRATIVE INFORMATION MANAGEMENT DISCLAIMER**",
        f"> {LEGAL_DISCLAIMER_TEXT}",
        "",
        "---",
        "",
        "## 1. Key Metadata & Contract Parties",
        f"- **Effective Date:** {effective_date or 'Not formally confirmed'}",
        f"- **Contract Expiry:** {expiry_date or 'Indefinite / Not specified'}",
        f"- **Review Status:** {total_approved} Approved Items | {total_pending} Pending Review | {total_stale} Stale Items",
        "",
        "### Confirmed Parties",
    ]

    if approved_parties:
        for p in approved_parties:
            jur = f" (Jurisdiction: {p.jurisdiction})" if p.jurisdiction else ""
            md_lines.append(f"- **{p.name}** — *Role: {p.role}*{jur} [Citation: {p.source_section or 'Preamble'}]")
    else:
        md_lines.append("- *No parties currently marked as approved.*")

    md_lines.extend([
        "",
        "## 2. Key Approved Clauses",
        f"- **Renewal Window:** {renewal_summary}",
        f"- **Termination Standard:** {termination_summary}",
        "",
    ])

    for c in approved_clauses:
        notice_str = f" | Notice Period: {c.notice_period_days} days" if c.notice_period_days else ""
        md_lines.append(f"### {c.title} ({c.clause_type}{notice_str})")
        md_lines.append(f"{c.summary}")
        if c.source_quote:
            md_lines.append(f"> *Source Citation ({c.source_section or 'Doc'}):* \"{c.source_quote}\"")
        md_lines.append("")

    md_lines.extend([
        "## 3. Approved Key Obligations & Deadlines",
    ])

    if approved_obligations:
        for o in approved_obligations:
            due_str = f" | Due Date: **{o.due_date}**" if o.due_date else (f" | Frequency: **{o.frequency}**" if o.frequency else "")
            md_lines.append(f"- **{o.title}** ({o.responsible_party}){due_str}")
            md_lines.append(f"  - {o.description}")
            if o.consequence_of_breach:
                md_lines.append(f"  - *Breach Consequence:* {o.consequence_of_breach}")
    else:
        md_lines.append("- *No obligations currently marked as approved.*")

    md_lines.extend([
        "",
        "## 4. Deterministic Upcoming Reminders Schedule",
    ])

    if reminders:
        for r in sorted(reminders, key=lambda x: x.reminder_date):
            resp = f" ({r.responsible_party})" if r.responsible_party else ""
            md_lines.append(f"- **[{r.reminder_date}]** ({r.urgency}) {r.title}{resp}: Target {r.target_date}")
    else:
        md_lines.append("- *No active reminders scheduled.*")

    if flagged_unclear:
        md_lines.extend([
            "",
            "## 5. Unclear Terms & Open Clarification Questions",
        ])
        for u in flagged_unclear:
            md_lines.append(f"### [Flagged: {u.issue_type}] {u.term_title}")
            md_lines.append(f"{u.description}")
            if u.clarification_questions:
                for q in u.clarification_questions:
                    ans = f" -> *User Answer: {q.user_answer}*" if q.user_answer else ""
                    md_lines.append(f"  - **Question:** {q.question}{ans}")

    markdown_text = "\n".join(md_lines)

    return ReviewedContractSummaryResponse(
        contract_id=contract.id,
        contract_title=contract.title,
        version_number=version.version_number,
        version_id=version.id,
        effective_date=effective_date,
        expiry_date=expiry_date,
        renewal_summary=renewal_summary,
        termination_summary=termination_summary,
        approved_parties=approved_parties,
        approved_clauses=approved_clauses,
        approved_obligations=approved_obligations,
        calculated_reminders=reminders,
        flagged_unclear_terms=flagged_unclear,
        policy_checks_count=len(contract.policy_documents),
        total_approved_items=total_approved,
        total_pending_items=total_pending,
        total_stale_items=total_stale,
        disclaimer=LEGAL_DISCLAIMER_TEXT,
        generated_at=datetime.utcnow(),
        markdown_content=markdown_text
    )
