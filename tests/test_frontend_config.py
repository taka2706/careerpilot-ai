"""Tests for deployment-aware frontend configuration."""

from frontend.api_client import api_url


def test_api_url_accepts_render_private_host(monkeypatch) -> None:
    monkeypatch.setenv("CAREERPILOT_API_URL", "careerpilot-api:10000")

    assert api_url() == "http://careerpilot-api:10000"


def test_api_url_preserves_explicit_scheme(monkeypatch) -> None:
    monkeypatch.setenv("CAREERPILOT_API_URL", "https://api.example.com/")

    assert api_url() == "https://api.example.com"
