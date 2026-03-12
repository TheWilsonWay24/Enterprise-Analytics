import streamlit as st
import streamlit_authenticator as stauth

# ── Credentials (hashed passwords) ───────────────────────────────────────────
CREDENTIALS = {
    "usernames": {
        "admin": {
            "name":     "Admin",
            "password": "$2b$12$nGL2PgG0J2TklT8JSD29a.M1rhHi2xjmbETM95KOfshN1sgWGvJ1S",
        },
        "analyst": {
            "name":     "Analyst",
            "password": "$2b$12$7KYhK5xvX9memYNw7LyJde1zgxLJHPrGOLk8tbyXJGFOypOg/phG.",
        },
    }
}

def get_authenticator():
    return stauth.Authenticate(
        CREDENTIALS,
        cookie_name="superstore_auth",
        cookie_key="superstore_secret_key_x9k2",
        cookie_expiry_days=7,
    )

def require_auth():
    """
    Call at the top of every page.
    Shows login form if not authenticated and stops execution.
    Returns (authenticator, username) if authenticated.
    """
    authenticator = get_authenticator()
    authenticator.login(location="main")

    status = st.session_state.get("authentication_status")

    if status is True:
        return authenticator, st.session_state.get("username")

    if status is False:
        st.error("Username or password is incorrect.")

    # Not authenticated — stop rendering the rest of the page
    st.stop()
