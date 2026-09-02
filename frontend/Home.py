"""Main CareerPilot AI dashboard page."""

import streamlit as st

from frontend.common import configure_page, fetch_api_health

configure_page("CareerPilot AI", "🧭")
st.caption("Autonomous AI Job Search & Application Assistant")

api_online, api_message = fetch_api_health()
if api_online:
    st.success(api_message)
else:
    st.warning(api_message)

st.subheader("Phase 1 — Foundation")
left, middle, right = st.columns(3)
left.metric("Dashboard pages", "7")
middle.metric("Demo jobs", "10")
right.metric("API status", "Online" if api_online else "Offline")

st.subheader("Planned agent workflow")
st.markdown(
    """
**User Request** → **Planner** → **Job Research** → **Profile Retrieval** → **Ranking**
→ **Skill Gap Analysis** → **Application Writer** → **Verification**

Use the sidebar to explore the honest product skeleton. Each unavailable page states the
phase in which it will be enabled.
"""
)
