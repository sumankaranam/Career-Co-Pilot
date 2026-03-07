from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=True, index=True)
    file_path = Column(String, nullable=False)
    text_content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    alignment_runs = relationship("AlignmentRun", back_populates="resume")


class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    raw_html = Column(Text, nullable=True)
    jd_text = Column(Text, nullable=False)
    is_international = Column(Boolean, default=False)
    location = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    poster_name = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    alignment_runs = relationship("AlignmentRun", back_populates="job_posting")


class AlignmentRun(Base):
    __tablename__ = "alignment_runs"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_posting_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    aligned_resume_text = Column(Text, nullable=False)
    aligned_resume_file_path = Column(String, nullable=True)
    cover_letter = Column(Text, nullable=True)
    email_template = Column(Text, nullable=True)
    linkedin_dm = Column(Text, nullable=True)
    hidden_matches_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    resume = relationship("Resume", back_populates="alignment_runs")
    job_posting = relationship("JobPosting", back_populates="alignment_runs")

