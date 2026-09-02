import streamlit as st

from frontend.common import configure_page, render_phase_notice

configure_page("Agent Runs", "⚙️")
st.status("No workflow is running", state="complete")
render_phase_notice(4, "LangGraph progress, conditional routing, failures, and bounded retries.")

