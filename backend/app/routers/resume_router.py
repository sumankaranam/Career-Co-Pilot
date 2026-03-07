from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services.docx_service import extract_text_from_docx, save_base_resume

router = APIRouter(prefix="/api/resume", tags=["resume"])


@router.post("/base", response_model=schemas.ResumeOut, status_code=status.HTTP_201_CREATED)
async def upload_base_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> schemas.ResumeOut:
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .docx files are supported for the base resume.",
        )

    contents = await file.read()
    path = save_base_resume(contents, file.filename)
    text = extract_text_from_docx(path)
    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded .docx appears to be empty or unreadable.",
        )

    # For v1, assume a single local user, so we just keep the latest resume.
    resume = models.Resume(
        user_id=None,
        file_path=str(path),
        text_content=text,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("/base/latest", response_model=schemas.ResumeOut)
def get_latest_base_resume(db: Session = Depends(get_db)) -> schemas.ResumeOut:
    resume = (
        db.query(models.Resume)
        .order_by(models.Resume.created_at.desc())
        .first()
    )
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No base resume found. Please upload one first.",
        )
    return resume

