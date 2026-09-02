"""Public API integration test for the main user journey."""

import httpx
import pytest
from fastapi import FastAPI
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db


@pytest.mark.asyncio
async def test_api_user_journey(
    api_app: FastAPI, db_session: Session, test_settings: Settings
) -> None:
    def override_db():  # type: ignore[no-untyped-def]
        yield db_session

    api_app.dependency_overrides[get_db] = override_db
    api_app.dependency_overrides[get_settings] = lambda: test_settings
    transport = httpx.ASGITransport(app=api_app)
    try:
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            upload = await client.post(
                "/profiles/upload",
                data={"name": "API Candidate"},
                files={
                    "resume": (
                        "resume.md",
                        b"# Skills\nPython, Git, REST APIs\n# Projects\nBuilt a Python API",
                        "text/markdown",
                    )
                },
            )
            assert upload.status_code == 201, upload.text
            profile_id = upload.json()["id"]

            search = await client.post(
                "/jobs/search",
                json={
                    "query": "AI",
                    "location": "India",
                    "remote_only": True,
                    "beginner_friendly": True,
                    "limit": 10,
                },
            )
            assert search.status_code == 200, search.text
            jobs = search.json()
            assert jobs

            analysis = await client.post(
                f"/jobs/{jobs[0]['id']}/analyze",
                json={"profile_id": profile_id, "preferences": {"remote_only": True}},
            )
            assert analysis.status_code == 200, analysis.text
            assert 0 <= analysis.json()["overall_score"] <= 100

            workflow = await client.post(
                "/agents/run",
                json={
                    "profile_id": profile_id,
                    "user_request": "Find remote AI internships in India for a beginner",
                },
            )
            assert workflow.status_code == 201, workflow.text
            assert workflow.json()["status"] == "completed"

            run_status = await client.get(f"/runs/{workflow.json()['id']}")
            assert run_status.status_code == 200

            application = await client.post(
                "/applications/generate",
                json={"profile_id": profile_id, "job_id": jobs[0]["id"]},
            )
            assert application.status_code == 201, application.text
            assert application.json()["verification_status"] == "verified"

            evaluation = await client.post("/evaluations/run")
            assert evaluation.status_code == 200
            assert evaluation.json()["total_scenarios"] == 10
    finally:
        api_app.dependency_overrides.clear()
