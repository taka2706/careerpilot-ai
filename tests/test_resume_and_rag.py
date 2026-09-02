"""Resume safety, extraction, and retrieval tests."""

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.schemas.profile import ProfileCreate
from app.services.profile_service import ProfileService
from app.services.resume_parser import ResumeValidationError, extract_resume_text


def test_markdown_resume_is_structured_and_retrievable(
    db_session: Session, test_settings: Settings
) -> None:
    content = b"# Skills\nPython, FastAPI, Git\n# Projects\nBuilt a FastAPI recommendation API"
    service = ProfileService(db_session, test_settings)

    profile = service.ingest_resume("Ada", None, "../unsafe resume.md", content)
    results = service.retrieve(profile.id, "FastAPI project")

    assert profile.skills == ["Python", "FastAPI", "Git"]
    assert profile.projects == ["Built a FastAPI recommendation API"]
    assert results
    assert any("FastAPI" in result.text for result in results)


def test_manual_profile_does_not_require_resume(
    db_session: Session, test_settings: Settings
) -> None:
    profile = ProfileService(db_session, test_settings).create(ProfileCreate(name="Grace"))
    assert profile.name == "Grace"
    assert profile.skills == []


def test_resume_rejects_unsupported_extension() -> None:
    try:
        extract_resume_text("resume.exe", b"not executable", 5)
    except ResumeValidationError as exc:
        assert "Only PDF" in str(exc)
    else:
        raise AssertionError("Unsupported resume extension was accepted")
