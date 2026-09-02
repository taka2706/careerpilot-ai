import streamlit as st

from frontend.common import configure_page, render_phase_notice

configure_page("Evaluations", "📊")
st.metric("Scenarios evaluated", "0")
render_phase_notice(6, "quality, reliability, latency, retry, token, and cost metrics.")

