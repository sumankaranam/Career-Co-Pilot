from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services.scraper_service import scrape_linkedin_job

router = APIRouter(prefix="/api/job", tags=["job"])


@router.post("/analyze", response_model=schemas.JobOut, status_code=status.HTTP_201_CREATED)
def analyze_job(
    payload: schemas.JobAnalyzeRequest,
    db: Session = Depends(get_db),
) -> schemas.JobOut:
    try:
        jd_text, raw_html, location, contact_email = scrape_linkedin_job(payload.url)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to scrape job URL: {exc}",
        ) from exc

    # Simple international heuristic: if location does not contain "India"
    is_international = False
    if location and "india" not in location.lower():
        is_international = True

    job = models.JobPosting(
        url=str(payload.url),
        raw_html=raw_html,
        jd_text=jd_text,
        is_international=is_international,
        location=location,
        company_name=None,
        poster_name=None,
        contact_email=contact_email,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

