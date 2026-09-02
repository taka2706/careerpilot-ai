"""Main CareerPilot AI dashboard page."""

import streamlit as st

from frontend.common import configure_page, fetch_api_health

configure_page("CareerPilot AI", "🧭")
st.caption("An agentic job-search and application assistant")

api_online, api_message = fetch_api_health()
if api_online:
    st.success(api_message)
else:
    st.warning(api_message)

st.subheader("Phase 1 foundation")
left, middle, right = st.columns(3)
left.metric("Dashboard pages", "7")
middle.metric("Demo jobs", "3")
right.metric("API status", "Online" if api_online else "Offline")

st.markdown(
    """
Use the sidebar to explore the product skeleton. The later phases will progressively
activate resume ingestion, retrieval, deterministic ranking, LangGraph orchestration,
application writing, verification, and evaluation.
"""
)

