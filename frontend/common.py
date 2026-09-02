"""Shared Streamlit UI helpers."""

import httpx
import streamlit as st

from frontend.api_client import api_url


def configure_page(title: str, icon: str = "🧭") -> None:
    """Apply consistent page metadata and heading."""

    st.set_page_config(page_title=f"{title} | CareerPilot AI", page_icon=icon, layout="wide")
    st.title(title)


def render_phase_notice(phase: int, description: str) -> None:
    """Explain when a placeholder feature is scheduled."""

    st.info(f"Planned for Phase {phase}: {description}")


def fetch_api_health() -> tuple[bool, str]:
    """Check API health without allowing a network error to crash the dashboard."""

    backend_url = api_url()
    try:
        response = httpx.get(f"{backend_url}/health", timeout=2.0)
        response.raise_for_status()
        payload = response.json()
        return True, f"{payload['service']} API {payload['version']} is online"
    except (httpx.HTTPError, KeyError, ValueError):
        return False, f"API unavailable at {backend_url}. Start it with the command in README.md."
