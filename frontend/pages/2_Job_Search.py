import streamlit as st

from frontend.api_client import BackendError, request
from frontend.common import configure_page

configure_page("Job Search", "🔎")
st.caption("Searches 10 fictional demo jobs through the provider interface.")

with st.form("job_search"):
    query = st.text_input("Role", value="AI", placeholder="Generative AI")
    location = st.text_input("Location", value="India")
    remote_only = st.checkbox("Remote only", value=True)
    beginner = st.checkbox("Beginner friendly", value=True)
    limit = st.slider("Maximum results", 1, 50, 10)
    submitted = st.form_submit_button("Search jobs", use_container_width=True)

if submitted:
    preferences = {
        "query": query,
        "location": location or None,
        "remote_only": remote_only,
        "beginner_friendly": beginner,
        "limit": limit,
    }
    try:
        result = request("POST", "/jobs/search", json=preferences)
        assert isinstance(result, list)
        st.session_state.jobs = result
        st.session_state.preferences = preferences
        st.success(f"Found {len(result)} matching demo job(s).")
    except (BackendError, AssertionError) as exc:
        st.error(str(exc))

for job in st.session_state.get("jobs", []):
    with st.expander(f"{job['title']} — {job['company']}"):
        st.write(f"**Location:** {job['location']} · **Policy:** {job['remote_status']}")
        st.write(job["description"])
        st.write(f"**Required:** {', '.join(job['required_skills'])}")
        st.write(f"**Preferred:** {', '.join(job['preferred_skills'])}")
        st.caption("Fictional demo listing — not an active opening")
