from pathlib import Path
from typing import Dict

from docx import Document

from ..database import STORAGE_DIR


def save_base_resume(file_bytes: bytes, filename: str) -> Path:
    resumes_dir = STORAGE_DIR / "resumes"
    resumes_dir.mkdir(parents=True, exist_ok=True)
    path = resumes_dir / filename
    path.write_bytes(file_bytes)
    return path


def extract_text_from_docx(path: Path) -> str:
    document = Document(str(path))
    parts = [para.text for para in document.paragraphs if para.text.strip()]
    return "\n".join(parts)


def generate_aligned_resume_docx(
    sections: Dict[str, str], filename: str = "aligned_resume.docx"
) -> Path:
    generated_dir = STORAGE_DIR / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)

    doc = Document()
    for section, content in sections.items():
        doc.add_heading(section, level=1)
        for line in content.split("\n"):
            if line.strip():
                doc.add_paragraph(line)

    out_path = generated_dir / filename
    doc.save(str(out_path))
    return out_path

