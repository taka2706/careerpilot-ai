import streamlit as st

from frontend.api_client import BackendError, request
from frontend.common import configure_page

configure_page("Application Generator", "✍️")
profile_id = st.session_state.get("profile_id")
jobs = st.session_state.get("jobs", [])
if not profile_id or not jobs:
    st.info("Save a profile and search for jobs first.")
else:
    job_by_label = {f"{job['title']} — {job['company']}": job for job in jobs}
    selected = st.selectbox("Job", list(job_by_label))
    if st.button("Generate and verify draft", use_container_width=True):
        try:
            result = request(
                "POST",
                "/applications/generate",
                json={"profile_id": profile_id, "job_id": job_by_label[selected]["id"]},
                timeout=120,
            )
            assert isinstance(result, dict)
            st.session_state.application = result
        except (BackendError, AssertionError) as exc:
            st.error(str(exc))

draft = st.session_state.get("application")
if draft:
    st.success(f"Verification: {draft['verification_status']}")
    st.subheader("Resume summary")
    st.write(draft["resume_summary"])
    st.subheader("Project bullets")
    for bullet in draft["project_bullets"]:
        st.write(f"- {bullet}")
    st.subheader("Cover letter")
    st.text_area("Cover letter draft", draft["cover_letter"], height=240)
    st.subheader("Recruiter message")
    st.write(draft["recruiter_message"])
    st.subheader("LinkedIn message")
    st.write(draft["linkedin_message"])
    st.caption("Review and submit manually. CareerPilot never submits applications.")
