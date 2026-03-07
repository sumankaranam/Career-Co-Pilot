from pathlib import Path

from ..models import AlignmentRun, JobPosting
from .llm_client import get_llm_client


PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"
OUTREACH_PROMPT_PATH = PROMPTS_DIR / "outreach_prompt.txt"


def _load_outreach_template() -> str:
    return OUTREACH_PROMPT_PATH.read_text(encoding="utf-8")


def build_outreach_prompt(alignment: AlignmentRun, job: JobPosting) -> str:
    template = _load_outreach_template()
    return template.format(
        job_description=job.jd_text,
        aligned_resume=alignment.aligned_resume_text,
        company_name=job.company_name or "Unknown",
        location=job.location or "Unknown",
        poster_name=job.poster_name or "Unknown",
        contact_email=job.contact_email or "Unknown",
    ).strip()


def generate_outreach(alignment: AlignmentRun, job: JobPosting) -> tuple[str, str, str]:
    llm = get_llm_client()
    prompt = build_outreach_prompt(alignment, job)
    raw = llm.generate_text(prompt, temperature=0.5)

    cover = ""
    subject = ""
    body = ""
    dm = ""

    current = None
    for line in raw.splitlines():
        line = line.rstrip()
        if line.strip() == "=== COVER LETTER ===":
            current = "cover"
            continue
        if line.strip() == "=== EMAIL SUBJECT ===":
            current = "subject"
            continue
        if line.strip() == "=== EMAIL BODY ===":
            current = "body"
            continue
        if line.strip() == "=== LINKEDIN DM ===":
            current = "dm"
            continue

        if current == "cover":
            cover += line + "\n"
        elif current == "subject":
            subject += line + " "
        elif current == "body":
            body += line + "\n"
        elif current == "dm":
            dm += line + "\n"

    email_template = f"Subject: {subject.strip()}\n\n{body.strip()}"
    return cover.strip(), email_template, dm.strip()

