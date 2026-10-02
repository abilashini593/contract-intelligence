from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.contract import Contract, ContractVersion
from app.schemas.summary import ReviewedContractSummaryResponse
from app.services.summary_service import generate_reviewed_summary

router = APIRouter(prefix="/api/contracts", tags=["Reviewed Summary"])

@router.get("/{contract_id}/summary", response_model=ReviewedContractSummaryResponse)
def get_reviewed_contract_summary(
    contract_id: int,
    version_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Generates and returns the reviewed contract summary.
    Includes only approved items, upcoming deadlines, clarification questions,
    and prominent administrative information-management disclaimers.
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contract {contract_id} not found.")

    if version_id:
        version = db.query(ContractVersion).filter(
            ContractVersion.id == version_id,
            ContractVersion.contract_id == contract_id
        ).first()
        if not version:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specified version not found.")
    else:
        version = next((v for v in contract.versions if v.is_active), None)
        if not version and contract.versions:
            version = contract.versions[-1]

    if not version:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No contract versions available.")

    summary = generate_reviewed_summary(contract, version, db)
    return summary

@router.get("/{contract_id}/summary/markdown", response_class=Response)
def export_summary_markdown(
    contract_id: int,
    version_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Exports the reviewed contract summary as a downloadable Markdown document.
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found.")

    version = db.query(ContractVersion).filter(
        ContractVersion.id == version_id if version_id else ContractVersion.contract_id == contract_id
    ).order_by(ContractVersion.version_number.desc()).first()

    if not version:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No contract versions available.")

    summary = generate_reviewed_summary(contract, version, db)
    filename = f"reviewed_summary_{contract.title.replace(' ', '_')}_v{version.version_number}.md"

    return Response(
        content=summary.markdown_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
