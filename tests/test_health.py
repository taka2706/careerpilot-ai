"""API health endpoint tests."""

import httpx
import pytest
from fastapi import FastAPI


@pytest.mark.asyncio
async def test_health_check_returns_service_metadata(api_app: FastAPI) -> None:
    transport = httpx.ASGITransport(app=api_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "CareerPilot AI",
        "version": "0.1.0",
    }


@pytest.mark.asyncio
async def test_unknown_route_returns_structured_error(api_app: FastAPI) -> None:
    transport = httpx.ASGITransport(app=api_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/not-a-real-route")

    assert response.status_code == 404
    assert response.json() == {"error": {"code": "http_error", "message": "Not Found"}}
