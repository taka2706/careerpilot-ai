import streamlit as st

from frontend.common import configure_page

configure_page("Skill Gaps", "🧩")
gaps = st.session_state.get("last_run", {}).get("run_data", {}).get("skill_gaps", [])
if not gaps:
    st.info("Run the CareerPilot workflow from Agent Runs to generate skill-gap analysis.")
for analysis in gaps:
    st.subheader(f"Job `{analysis['job_id']}`")
    st.write(f"**Existing skills:** {', '.join(analysis['existing_skills']) or 'None matched'}")
    for gap in analysis["gaps"]:
        st.markdown(f"**{gap['priority']} — {gap['skill']}**")
        st.write(gap["suggested_learning"])
        st.caption(gap["suggested_project"])
