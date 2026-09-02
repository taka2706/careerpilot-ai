import streamlit as st

from frontend.common import configure_page, render_phase_notice

configure_page("Job Recommendations", "🎯")
st.metric("Top match", "—", help="A deterministic score will appear after analysis.")
render_phase_notice(3, "ranked jobs, score breakdowns, and missing requirements.")

