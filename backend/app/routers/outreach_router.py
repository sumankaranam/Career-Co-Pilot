from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services.outreach_service import generate_outreach

router = APIRouter(prefix="/api/outreach", tags=["outreach"])


@router.post("/generate", response_model=schemas.OutreachOut, status_code=status.HTTP_200_OK)
def generate_outreach_templates(
    payload: schemas.OutreachRequest,
    db: Session = Depends(get_db),
) -> schemas.OutreachOut:
    alignment = db.query(models.AlignmentRun).get(payload.alignment_id)
    if not alignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alignment run not found.",
        )

    job = db.query(models.JobPosting).get(alignment.job_posting_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found.",
        )

    cover, email_template, dm = generate_outreach(alignment, job)

    alignment.cover_letter = cover
    alignment.email_template = email_template
    alignment.linkedin_dm = dm
    db.add(alignment)
    db.commit()
    db.refresh(alignment)

    return schemas.OutreachOut(
        cover_letter=cover,
        email_template=email_template,
        linkedin_dm=dm,
    )

