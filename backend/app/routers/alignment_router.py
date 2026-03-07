from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services.alignment_service import (
    align_resume,
    build_preview_from_sections,
)
from ..services.docx_service import generate_aligned_resume_docx

router = APIRouter(prefix="/api/alignment", tags=["alignment"])


@router.post("/run", response_model=schemas.AlignmentSummary, status_code=status.HTTP_201_CREATED)
def run_alignment(
    payload: schemas.AlignmentRunRequest,
    db: Session = Depends(get_db),
) -> schemas.AlignmentSummary:
    resume = db.query(models.Resume).get(payload.resume_id)
    job = db.query(models.JobPosting).get(payload.job_id)
    if not resume or not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume or job not found.",
        )

    hidden_summary, sections = align_resume(resume, job)
    docx_path = generate_aligned_resume_docx(
        sections,
        filename=f"aligned_resume_{resume.id}_{job.id}.docx",
        template=payload.template or "classic",
    )

    aligned_text = "\n\n".join(
        f"{name}\n{content}" for name, content in sections.items()
    )

    alignment = models.AlignmentRun(
        resume_id=resume.id,
        job_posting_id=job.id,
        aligned_resume_text=aligned_text,
        aligned_resume_file_path=str(docx_path),
        hidden_matches_summary=hidden_summary,
    )
    db.add(alignment)
    db.commit()
    db.refresh(alignment)

    download_url = f"/api/alignment/{alignment.id}/download"
    preview = build_preview_from_sections(sections)

    return schemas.AlignmentSummary(
        id=alignment.id,
        hidden_matches_summary=hidden_summary,
        aligned_resume_preview=preview,
        download_url=download_url,
    )


@router.get("/{alignment_id}/download")
def download_aligned_resume(
    alignment_id: int,
    db: Session = Depends(get_db),
) -> FileResponse:
    alignment = db.query(models.AlignmentRun).get(alignment_id)
    if not alignment or not alignment.aligned_resume_file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aligned resume not found.",
        )
    return FileResponse(
        alignment.aligned_resume_file_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="aligned_resume.docx",
    )

