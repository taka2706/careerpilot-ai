import streamlit as st

from frontend.api_client import BackendError, request
from frontend.common import configure_page

configure_page("Profile", "👤")
st.write("Create a basic profile or upload a PDF, TXT, or Markdown resume (maximum 5 MB).")

with st.form("profile_form"):
    name = st.text_input("Name")
    email = st.text_input("Email (optional)")
    resume = st.file_uploader("Resume (optional)", type=["pdf", "txt", "md"])
    submitted = st.form_submit_button("Save profile", use_container_width=True)

if submitted:
    try:
        if resume:
            form_data = {"name": name}
            if email:
                form_data["email"] = email
            result = request(
                "POST",
                "/profiles/upload",
                data=form_data,
                files={"resume": (resume.name, resume.getvalue(), resume.type)},
            )
        else:
            result = request("POST", "/profiles", json={"name": name, "email": email or None})
        assert isinstance(result, dict)
        st.session_state.profile = result
        st.session_state.profile_id = result["id"]
        st.success("Profile saved and resume indexed." if resume else "Basic profile saved.")
    except (BackendError, AssertionError) as exc:
        st.error(str(exc))

if st.session_state.get("profile"):
    profile = st.session_state.profile
    st.subheader("Active profile")
    st.write(f"**{profile['name']}** · ID: `{profile['id']}`")
    for label, key in (
        ("Skills", "skills"),
        ("Projects", "projects"),
        ("Experience", "experience"),
        ("Education", "education"),
        ("Tools", "tools"),
    ):
        values = profile.get(key, [])
        if values:
            st.write(f"**{label}:** {', '.join(values)}")
