import streamlit as st

from frontend.api_client import BackendError, request
from frontend.common import configure_page

configure_page("Evaluations", "📊")
if st.button("Run 10 offline scenarios", use_container_width=True):
    try:
        result = request("POST", "/evaluations/run", timeout=120)
        assert isinstance(result, dict)
        st.session_state.evaluations = result
    except (BackendError, AssertionError) as exc:
        st.error(str(exc))
elif "evaluations" not in st.session_state:
    try:
        result = request("GET", "/evaluations")
        if isinstance(result, dict):
            st.session_state.evaluations = result
    except BackendError:
        pass

report = st.session_state.get("evaluations")
if report:
    columns = st.columns(4)
    columns[0].metric("Scenarios", report["total_scenarios"])
    columns[1].metric("Success", f"{report['task_success_rate'] * 100:.0f}%")
    columns[2].metric("Tool success", f"{report['average_tool_success_rate'] * 100:.0f}%")
    columns[3].metric("Unsupported claims", f"{report['unsupported_claim_rate'] * 100:.1f}%")
    st.dataframe(report["results"], use_container_width=True)
else:
    st.info("Run the offline evaluation suite to populate metrics.")
