import streamlit as st

from frontend.common import configure_page, render_phase_notice

configure_page("Job Search", "🔎")
st.text_input("What role are you looking for?", placeholder="Remote AI internships in India")
st.button("Search jobs", disabled=True, use_container_width=True)
render_phase_notice(3, "provider-based job search with the bundled demo provider.")

