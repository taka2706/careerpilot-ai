import streamlit as st

from frontend.common import configure_page, render_phase_notice

configure_page("Profile", "👤")
st.file_uploader("Upload resume", type=["pdf", "txt", "md"], disabled=True)
render_phase_notice(2, "secure resume upload, extraction, indexing, and profile retrieval.")

