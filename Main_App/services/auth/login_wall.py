import streamlit as st
from services.persistence.exercise_repository import get_or_create_user


def render_login_wall() -> bool:
    # User already logged in
    if st.session_state.get("user_id"):
        return True

    st.title("🏋️‍♂️ AI Real-time GYM Trainer")
    st.markdown("### Welcome! Please enter a username to start.")

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input(
            "Name (Unique)",
            placeholder="unique name e.g. raunakpratap",
        ).strip()

        submit_button = st.form_submit_button(
            "Start Session",
            width="stretch",
        )

    if submit_button:
        if not username:
            st.error("Username cannot be empty.")
            return False

        if len(username) < 3:
            st.error("Username must be at least 3 characters long.")
            return False

        if len(username) > 30:
            st.error("Username must be less than 30 characters.")
            return False

        try:
            user = get_or_create_user(username)

            if user is None:
                st.error("Unable to create user.")
                return False

            st.session_state["user_id"] = user["id"]
            st.session_state["username"] = user["username"]

            st.rerun()

        except Exception as e:
            st.error(f"Unable to start session.\n\n{e}")

    return False
