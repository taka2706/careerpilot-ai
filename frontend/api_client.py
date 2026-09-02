"""Small timeout-aware HTTP client shared by Streamlit pages."""

import os
from typing import Any

import httpx


class BackendError(RuntimeError):
    """A user-displayable backend communication error."""


def api_url() -> str:
    configured_url = os.getenv("CAREERPILOT_API_URL", "http://localhost:8000").rstrip("/")
    if "://" not in configured_url:
        configured_url = f"http://{configured_url}"
    return configured_url


def request(
    method: str, path: str, *, timeout: float = 20.0, **kwargs: Any
) -> dict[str, Any] | list[dict[str, Any]]:
    """Call the backend and convert transport/API failures into friendly errors."""

    try:
        response = httpx.request(method, f"{api_url()}{path}", timeout=timeout, **kwargs)
        if response.is_error:
            payload = response.json()
            message = payload.get("error", {}).get("message", response.text)
            raise BackendError(message)
        result: dict[str, Any] | list[dict[str, Any]] = response.json()
        return result
    except httpx.HTTPError as exc:
        raise BackendError(f"Cannot reach the CareerPilot API at {api_url()}.") from exc
    except ValueError as exc:
        raise BackendError("The backend returned an unreadable response.") from exc
