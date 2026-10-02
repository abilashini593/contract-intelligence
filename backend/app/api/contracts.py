import os
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.contract import Contract, ContractVersion, PolicyDocument
from app.models.extracted_item import (
    ExtractedParty,
    ExtractedClause,
    ExtractedObligation,
    UnclearTerm,
    ClarificationQuestion,
)
from app.schemas.contract import (
    ContractDetailResponse,
    ContractSummaryItem,
    ContractVersionResponse,
)
from app.parsers import (
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_text_from_raw,
    PDFParsingError,
    DOCXParsingError,
    TextParsingError,
)
from app.services.gemini_service import analyze_contract_with_gemini, GeminiAPIKeyMissingError, GeminiServiceError
from app.services.reminder_service import calculate_reminders_for_version
from app.services.stale_service import detect_stale_items_for_version

router = APIRouter(prefix="/api/contracts", tags=["Contracts"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}

def parse_document_file_or_text(
    file: Optional[UploadFile],
    pasted_text: Optional[str],
    default_filename: str = "Pasted_Contract.txt"
) -> tuple[str, str, str]:
    """
    Validates and extracts plain text from an uploaded file or pasted text.
    Returns (extracted_text, filename, file_type).
    """
    if file and file.filename:
        filename = file.filename
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '{ext}'. Supported formats: PDF (.pdf), DOCX (.docx), and TXT (.txt)."
            )
        
        file_bytes = file.file.read()
        if not file_bytes or len(file_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Uploaded file '{filename}' is empty."
            )

        try:
            if ext == ".pdf":
                text, _ = extract_text_from_pdf(file_bytes)
                return text, filename, "pdf"
            elif ext == ".docx":
                text, _ = extract_text_from_docx(file_bytes)
                return text, filename, "docx"
            elif ext == ".txt":
                raw_str = file_bytes.decode("utf-8", errors="replace")
                text, _ = extract_text_from_raw(raw_str)
                return text, filename, "text"
        except (PDFParsingError, DOCXParsingError, TextParsingError) as parse_err:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(parse_err)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error parsing document: {str(e)}"
            )

    elif pasted_text and pasted_text.strip():
        try:
            text, _ = extract_text_from_raw(pasted_text)
            return text, default_filename, "text"
        except TextParsingError as tpe:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(tpe))

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a contract document by uploading a PDF, DOCX, or TXT file, or by pasting contract text."
        )

def save_extracted_items_to_db(
    version: ContractVersion,
    ai_output,
    db: Session
):
    """Saves Gemini structured AI items into relational database models."""
    for p in ai_output.parties:
        party_obj = ExtractedParty(
            version_id=version.id,
            name=p.name,
            role=p.role,
            effective_date=p.effective_date or ai_output.overall_effective_date,
            jurisdiction=p.jurisdiction,
            source_page=p.source_page,
            source_section=p.source_section,
            source_quote=p.source_quote,
            certainty=p.certainty or "CONFIRMED",
            confidence_score=p.confidence_score or 1.0,
            uncertainty_rationale=p.uncertainty_rationale,
            status="PENDING",
            is_stale=False
        )
        db.add(party_obj)

    for c in ai_output.clauses:
        clause_obj = ExtractedClause(
            version_id=version.id,
            clause_type=c.clause_type,
            title=c.title,
            summary=c.summary,
            effective_date=c.effective_date,
            expiry_date=c.expiry_date,
            renewal_type=c.renewal_type,
            notice_period_days=c.notice_period_days,
            termination_type=c.termination_type,
            source_page=c.source_page,
            source_section=c.source_section,
            source_quote=c.source_quote,
            certainty=c.certainty or "CONFIRMED",
            confidence_score=c.confidence_score or 1.0,
            uncertainty_rationale=c.uncertainty_rationale,
            status="PENDING",
            is_stale=False
        )
        db.add(clause_obj)

    for o in ai_output.obligations:
        obligation_obj = ExtractedObligation(
            version_id=version.id,
            title=o.title,
            description=o.description,
            responsible_party=o.responsible_party,
            due_date=o.due_date,
            frequency=o.frequency,
            consequence_of_breach=o.consequence_of_breach,
            source_page=o.source_page,
            source_section=o.source_section,
            source_quote=o.source_quote,
            certainty=o.certainty or "CONFIRMED",
            confidence_score=o.confidence_score or 1.0,
            uncertainty_rationale=o.uncertainty_rationale,
            status="PENDING",
            is_stale=False
        )
        db.add(obligation_obj)

    for u in ai_output.unclear_terms:
        unclear_obj = UnclearTerm(
            version_id=version.id,
            term_title=u.term_title,
            clause_reference=u.clause_reference,
            issue_type=u.issue_type,
            description=u.description,
            policy_reference=u.policy_reference,
            source_page=u.source_page,
            source_section=u.source_section,
            source_quote=u.source_quote,
            certainty=u.certainty or "UNCERTAIN",
            confidence_score=u.confidence_score or 0.5,
            uncertainty_rationale=u.uncertainty_rationale,
            status="PENDING",
            is_stale=False
        )
        db.add(unclear_obj)
        db.flush() # Populate unclear_obj.id for questions

        for q in u.clarification_questions:
            q_obj = ClarificationQuestion(
                unclear_term_id=unclear_obj.id,
                question=q.question,
                suggested_action=q.suggested_action
            )
            db.add(q_obj)

    db.commit()

@router.post("/upload", response_model=ContractDetailResponse, status_code=status.HTTP_201_CREATED)
def upload_contract(
    file: Optional[UploadFile] = File(None),
    pasted_text: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    policy_file: Optional[UploadFile] = File(None),
    policy_pasted_text: Optional[str] = Form(None),
    policy_title: Optional[str] = Form(None),
    x_gemini_api_key: Optional[str] = Header(None, alias="X-Gemini-API-Key"),
    db: Session = Depends(get_db)
):
    """
    Uploads a new contract (PDF, DOCX, or text) and optional organizational policy document.
    Parses documents, performs Gemini AI structured extraction, and calculates deterministic reminder dates.
    """
    # 1. Parse Contract Text
    contract_text, filename, file_type = parse_document_file_or_text(file, pasted_text, "Uploaded_Contract.txt")

    # 2. Parse Optional Policy Document
    policy_text = None
    policy_filename = None
    policy_ftype = None
    if (policy_file and policy_file.filename) or (policy_pasted_text and policy_pasted_text.strip()):
        policy_text, policy_filename, policy_ftype = parse_document_file_or_text(
            policy_file, policy_pasted_text, "Organizational_Policy.txt"
        )

    # 3. Analyze with Gemini API
    try:
        ai_output = analyze_contract_with_gemini(
            contract_text=contract_text,
            policy_text=policy_text,
            api_key=x_gemini_api_key
        )
    except GeminiAPIKeyMissingError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except GeminiServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

    # 4. Create Contract & Version 1 in DB
    contract_title = title.strip() if title and title.strip() else ai_output.contract_title or filename
    contract = Contract(
        title=contract_title,
        description=f"Created via {file_type.upper()} upload ({filename})."
    )
    db.add(contract)
    db.flush()

    # Optional Policy Document record
    if policy_text:
        policy_doc = PolicyDocument(
            contract_id=contract.id,
            title=policy_title or "Organizational Policy",
            filename=policy_filename or "policy.txt",
            file_type=policy_ftype or "text",
            raw_text=policy_text
        )
        db.add(policy_doc)

    # Version 1
    version1 = ContractVersion(
        contract_id=contract.id,
        version_number=1,
        filename=filename,
        file_type=file_type,
        raw_text=contract_text,
        is_active=True
    )
    db.add(version1)
    db.flush()

    # 5. Save Extracted Items
    save_extracted_items_to_db(version1, ai_output, db)

    # 6. Calculate Deterministic Reminders
    calculate_reminders_for_version(version1, db)

    # Refresh and return
    db.refresh(contract)
    return contract

@router.post("/{contract_id}/upload-version", response_model=ContractDetailResponse, status_code=status.HTTP_201_CREATED)
def upload_contract_version(
    contract_id: int,
    file: Optional[UploadFile] = File(None),
    pasted_text: Optional[str] = Form(None),
    x_gemini_api_key: Optional[str] = Header(None, alias="X-Gemini-API-Key"),
    db: Session = Depends(get_db)
):
    """
    Uploads a new version (e.g. v2) for an existing contract.
    Extracts structured items, flags stale items comparing against approved items from previous version,
    and recalculates deterministic reminder dates.
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contract {contract_id} not found.")

    previous_active_version = next((v for v in contract.versions if v.is_active), None)
    if not previous_active_version:
        previous_active_version = contract.versions[-1] if contract.versions else None

    # Parse document
    new_ver_num = len(contract.versions) + 1
    contract_text, filename, file_type = parse_document_file_or_text(
        file, pasted_text, f"Contract_v{new_ver_num}.txt"
    )

    # Check policy doc if exists for contract
    policy_text = contract.policy_documents[0].raw_text if contract.policy_documents else None

    # Analyze with Gemini
    try:
        ai_output = analyze_contract_with_gemini(
            contract_text=contract_text,
            policy_text=policy_text,
            api_key=x_gemini_api_key
        )
    except GeminiAPIKeyMissingError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except GeminiServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

    # Mark previous versions inactive
    for v in contract.versions:
        v.is_active = False

    # Create new version
    new_version = ContractVersion(
        contract_id=contract.id,
        version_number=new_ver_num,
        filename=filename,
        file_type=file_type,
        raw_text=contract_text,
        is_active=True
    )
    db.add(new_version)
    db.flush()

    # Save extracted items
    save_extracted_items_to_db(new_version, ai_output, db)

    # Detect stale items if we have a previous version
    if previous_active_version:
        detect_stale_items_for_version(new_version, previous_active_version, db)

    # Deterministic reminder calculation
    calculate_reminders_for_version(new_version, db)

    db.refresh(contract)
    return contract

@router.get("", response_model=List[ContractSummaryItem])
def list_contracts(db: Session = Depends(get_db)):
    """Lists all contracts with high-level statistics."""
    contracts = db.query(Contract).order_by(Contract.updated_at.desc()).all()
    results = []
    for c in contracts:
        latest_ver = max([v.version_number for v in c.versions], default=1)
        active_ver = next((v for v in c.versions if v.is_active), (c.versions[-1] if c.versions else None))
        
        parties_c = len(active_ver.parties) if active_ver else 0
        clauses_c = len(active_ver.clauses) if active_ver else 0
        obs_c = len(active_ver.obligations) if active_ver else 0
        unclear_c = len(active_ver.unclear_terms) if active_ver else 0
        stale_c = sum(1 for item in (
            (active_ver.parties if active_ver else []) +
            (active_ver.clauses if active_ver else []) +
            (active_ver.obligations if active_ver else [])
        ) if item.is_stale)

        results.append(ContractSummaryItem(
            id=c.id,
            title=c.title,
            description=c.description,
            created_at=c.created_at,
            updated_at=c.updated_at,
            latest_version=latest_ver,
            parties_count=parties_c,
            clauses_count=clauses_c,
            obligations_count=obs_c,
            unclear_terms_count=unclear_c,
            stale_items_count=stale_c
        ))
    return results

@router.get("/{contract_id}", response_model=ContractDetailResponse)
def get_contract(contract_id: int, db: Session = Depends(get_db)):
    """Retrieves full contract details including all versions and active items."""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contract {contract_id} not found.")
    
    # Identify current version
    current_ver = next((v for v in contract.versions if v.is_active), None)
    if not current_ver and contract.versions:
        current_ver = contract.versions[-1]

    # Convert to schema
    resp = ContractDetailResponse.model_validate(contract)
    if current_ver:
        resp.current_version = ContractVersionResponse.model_validate(current_ver)
    return resp

@router.get("/{contract_id}/versions/{version_id}", response_model=ContractVersionResponse)
def get_contract_version(contract_id: int, version_id: int, db: Session = Depends(get_db)):
    """Retrieves a specific historical version of a contract."""
    version = db.query(ContractVersion).filter(
        ContractVersion.id == version_id,
        ContractVersion.contract_id == contract_id
    ).first()
    if not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract version not found.")
    return version

@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract(contract_id: int, db: Session = Depends(get_db)):
    """Deletes a contract and all associated versions, items, and reminders."""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contract {contract_id} not found.")
    db.delete(contract)
    db.commit()
    return None
