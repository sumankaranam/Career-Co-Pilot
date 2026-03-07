from textwrap import shorten
from typing import Dict, Tuple

from ..models import JobPosting, Resume
from .llm_client import get_llm_client


def build_alignment_prompt(resume: Resume, job: JobPosting) -> str:
    international_hint = (
        "The job is OUTSIDE India. If the candidate has any onsite or international experience, "
        "move it toward the top of the resume and explicitly mention relocation and visa willingness."
        if job.is_international
        else "The job is in India or local; no special relocation messaging is required."
    )

    return f"""
You are an expert resume writer.

JOB DESCRIPTION:
{job.jd_text}

BASE RESUME:
{resume.text_content}

TASKS:
1. Identify must-have skills and responsibilities from the job description.
2. Identify "hidden matches" where the candidate has similar skills or experience that is not phrased exactly like the JD.
3. Rewrite the resume so that:
   - The most relevant experience and skills are emphasized and appear early.
   - Hidden matches are made explicit where appropriate.
   - The structure remains ATS-friendly (concise bullet points, clear section headings).
4. {international_hint}

OUTPUT FORMAT:
- First, provide a short "Hidden Matches Summary" paragraph.
- Then, output the FULL aligned resume in plain text, organized into sections (e.g., SUMMARY, EXPERIENCE, SKILLS, EDUCATION).
""".strip()


def parse_alignment_output(output: str) -> Tuple[str, Dict[str, str]]:
    """
    Very lightweight parser that:
    - Extracts the hidden matches summary from the first paragraph.
    - Treats subsequent ALL-CAPS lines as section headings.
    """
    lines = [line.rstrip() for line in output.splitlines()]
    lines = [ln for ln in lines if ln.strip()]

    if not lines:
        return "", {"ALIGNED RESUME": ""}

    # Hidden matches summary: first non-empty paragraph
    hidden_summary = lines[0]

    sections: Dict[str, str] = {}
    current_section = "ALIGNED RESUME"
    buffer: list[str] = []

    for line in lines[1:]:
        if line.isupper() and len(line.split()) <= 5:
            # Flush previous section
            if buffer:
                sections[current_section] = "\n".join(buffer).strip()
                buffer = []
            current_section = line.strip()
        else:
            buffer.append(line)

    if buffer and current_section not in sections:
        sections[current_section] = "\n".join(buffer).strip()

    if not sections:
        sections["ALIGNED RESUME"] = "\n".join(lines[1:]).strip()

    return hidden_summary, sections


def align_resume(resume: Resume, job: JobPosting) -> Tuple[str, Dict[str, str]]:
    llm = get_llm_client()
    prompt = build_alignment_prompt(resume, job)
    raw_output = llm.generate_text(prompt)
    hidden_summary, sections = parse_alignment_output(raw_output)
    if not hidden_summary:
        hidden_summary = "Hidden matches could not be extracted; please review the aligned resume manually."
    return hidden_summary, sections


def build_preview_from_sections(sections: Dict[str, str], max_chars: int = 400) -> str:
    full_text = "\n\n".join(
        f"{name}\n{content}" for name, content in sections.items() if content.strip()
    )
    return shorten(full_text, width=max_chars, placeholder="...")

