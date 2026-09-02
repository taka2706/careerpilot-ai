"""Safe in-memory text extraction and deterministic resume section parsing."""

import io
import re
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError


class ResumeValidationError(ValueError):
    """Raised when an uploaded resume is unsafe, unsupported, or unreadable."""


SECTION_ALIASES = {
    "education": "education",
    "skills": "skills",
    "technical skills": "skills",
    "projects": "projects",
    "experience": "experience",
    "work experience": "experience",
    "certifications": "certifications",
    "tools": "tools",
    "programming languages": "programming_languages",
    "languages": "programming_languages",
}


def sanitize_filename(filename: str) -> str:
    """Drop path components and replace unsafe display characters."""

    basename = Path(filename).name
    return re.sub(r"[^A-Za-z0-9._-]", "_", basename)[:160]


def extract_resume_text(filename: str, content: bytes, max_size_mb: int) -> str:
    """Extract text without writing or executing the uploaded file."""

    safe_name = sanitize_filename(filename)
    suffix = Path(safe_name).suffix.casefold()
    if suffix not in {".pdf", ".txt", ".md"}:
        raise ResumeValidationError("Only PDF, TXT, and Markdown resumes are supported.")
    if not content:
        raise ResumeValidationError("The uploaded resume is empty.")
    if len(content) > max_size_mb * 1024 * 1024:
        raise ResumeValidationError(f"Resume exceeds the {max_size_mb} MB upload limit.")

    try:
        if suffix == ".pdf":
            reader = PdfReader(io.BytesIO(content))
            if reader.is_encrypted:
                raise ResumeValidationError("Encrypted PDF resumes are not supported.")
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        else:
            text = content.decode("utf-8")
    except (UnicodeDecodeError, OSError, ValueError, PdfReadError) as exc:
        if isinstance(exc, ResumeValidationError):
            raise
        raise ResumeValidationError("The resume could not be read safely.") from exc

    normalized = re.sub(r"\r\n?", "\n", text).strip()
    if not normalized:
        raise ResumeValidationError("No readable text was found in the resume.")
    return normalized


def parse_resume_sections(text: str) -> dict[str, list[str]]:
    """Extract common resume sections with predictable line-based rules."""

    sections: dict[str, list[str]] = {value: [] for value in set(SECTION_ALIASES.values())}
    active_section: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip().strip("#").strip()
        if not line:
            continue
        heading = re.sub(r"[:\s]+$", "", line).casefold()
        if heading in SECTION_ALIASES:
            active_section = SECTION_ALIASES[heading]
            continue
        if active_section:
            items = re.split(r"\s*[•|,;]\s*", line.lstrip("-* "))
            sections[active_section].extend(item.strip() for item in items if item.strip())

    for key, values in sections.items():
        sections[key] = list(dict.fromkeys(values))
    return sections
