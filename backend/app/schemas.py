from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


class ResumeBase(BaseModel):
    user_id: Optional[str] = None


class ResumeOut(ResumeBase):
    id: int
    file_path: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class JobAnalyzeRequest(BaseModel):
    url: Optional[HttpUrl] = None
    jd_text: Optional[str] = None
    location: Optional[str] = None
    company_name: Optional[str] = None


class JobOut(BaseModel):
    id: int
    url: str
    jd_text: str
    is_international: bool
    location: Optional[str] = None
    company_name: Optional[str] = None
    poster_name: Optional[str] = None
    contact_email: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True


class AlignmentRunRequest(BaseModel):
    resume_id: int
    job_id: int
    template: Optional[str] = "classic"


class AlignmentSummary(BaseModel):
    id: int
    hidden_matches_summary: str
    aligned_resume_preview: str
    download_url: str


class OutreachRequest(BaseModel):
    alignment_id: int


class OutreachOut(BaseModel):
    cover_letter: str
    email_template: str
    linkedin_dm: str

