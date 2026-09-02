import streamlit as st

from frontend.api_client import BackendError, request
from frontend.common import configure_page

configure_page("Agent Runs", "⚙️")
profile_id = st.session_state.get("profile_id")
default_request = "Find remote AI internships in India suitable for a beginner"
user_request = st.text_area("CareerPilot request", value=default_request)

if not profile_id:
    st.info("Save a profile first.")
elif st.button("Run CareerPilot", type="primary", use_container_width=True):
    try:
        with st.status("Running the agent graph…", expanded=True) as status:
            st.write("Planning, researching, retrieving, ranking, writing, and verifying")
            result = request(
                "POST",
                "/agents/run",
                json={"profile_id": profile_id, "user_request": user_request},
                timeout=180,
            )
            assert isinstance(result, dict)
            st.session_state.last_run = result
            status.update(label=f"Run {result['status']}", state="complete")
    except (BackendError, AssertionError) as exc:
        st.error(str(exc))

run = st.session_state.get("last_run")
if run:
    columns = st.columns(3)
    columns[0].metric("Status", run["status"])
    columns[1].metric("Final step", run["current_step"])
    columns[2].metric("Retries", run["retries"])
    st.write(f"Run ID: `{run['id']}`")
    st.json(run["run_data"], expanded=False)

st.divider()
if st.button("Load recent runs"):
    try:
        history = request("GET", "/runs")
        if isinstance(history, list):
            st.session_state.run_history = history
    except BackendError as exc:
        st.error(str(exc))
if st.session_state.get("run_history"):
    st.dataframe(st.session_state.run_history, use_container_width=True)
