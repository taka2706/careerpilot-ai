import streamlit as st

from frontend.common import configure_page, render_phase_notice

configure_page("Application Generator", "✍️")
st.button("Generate verified drafts", disabled=True, use_container_width=True)
render_phase_notice(5, "grounded resume text, cover letters, and outreach messages.")

