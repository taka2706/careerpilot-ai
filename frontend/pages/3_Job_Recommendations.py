import streamlit as st

from frontend.api_client import BackendError, request
from frontend.common import configure_page

configure_page("Job Recommendations", "🎯")
profile_id = st.session_state.get("profile_id")
jobs = st.session_state.get("jobs", [])

if not profile_id or not jobs:
    st.info("Save a profile and search for jobs first.")
elif st.button("Calculate deterministic rankings", use_container_width=True):
    rankings = []
    try:
        for job in jobs:
            result = request(
                "POST",
                f"/jobs/{job['id']}/analyze",
                json={
                    "profile_id": profile_id,
                    "preferences": st.session_state.get("preferences", {}),
                },
            )
            assert isinstance(result, dict)
            rankings.append({"job": job, "ranking": result})
        st.session_state.rankings = sorted(
            rankings, key=lambda item: item["ranking"]["overall_score"], reverse=True
        )
    except (BackendError, AssertionError) as exc:
        st.error(str(exc))

for item in st.session_state.get("rankings", []):
    job, ranking = item["job"], item["ranking"]
    st.subheader(f"{ranking['overall_score']:.1f}% · {job['title']}")
    columns = st.columns(4)
    columns[0].metric("Skills", f"{ranking['skills_score']:.0f}%")
    columns[1].metric("Experience", f"{ranking['experience_score']:.0f}%")
    columns[2].metric("Education", f"{ranking['education_score']:.0f}%")
    columns[3].metric("Location", f"{ranking['location_score']:.0f}%")
    st.write(ranking["explanation"])
    missing = ranking.get("missing_requirements", [])
    st.warning(
        f"Missing required skills: {', '.join(missing)}"
        if missing
        else "No required skills missing."
    )
