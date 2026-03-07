from ..models import AlignmentRun, JobPosting
from .llm_client import get_llm_client


def build_outreach_prompt(alignment: AlignmentRun, job: JobPosting) -> str:
    return f"""
You are an expert in professional communication.

JOB DESCRIPTION:
{job.jd_text}

ALIGNED RESUME:
{alignment.aligned_resume_text}

JOB METADATA:
- Company: {job.company_name or "Unknown"}
- Location: {job.location or "Unknown"}
- Poster name: {job.poster_name or "Unknown"}
- Contact email: {job.contact_email or "Unknown"}

TASKS:
1. Write a tailored COVER LETTER (3–5 short paragraphs) that references the most relevant experience and skills.
2. Write a concise, professional COLD EMAIL for the hiring contact, with a subject line and email body.
3. Write a short, friendly LINKEDIN DM (InMail style) addressed to the poster by name if available.

OUTPUT FORMAT (plain text):
=== COVER LETTER ===
<cover letter>

=== EMAIL SUBJECT ===
<subject>

=== EMAIL BODY ===
<body>

=== LINKEDIN DM ===
<dm>
""".strip()


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

