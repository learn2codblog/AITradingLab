"""
Account Settings page module for AI Trading Lab PRO+
"""
import streamlit as st
from ui.components import create_section_header


def render_account_settings():
    """Render the Account Settings page content."""
    create_section_header(
        "Account Settings",
        "Configure Your Account Preferences",
        "⚙️"
    )

    # Log activity
    try:
        from src.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        user_id = st.session_state.get('user_id')
        if user_id and supabase.is_connected():
            supabase.log_activity(
                user_id=user_id,
                activity_type='account_settings_view',
                description="Opened Account Settings",
                status='success'
            )
    except Exception:
        pass

    st.info("🚧 Account Settings page is under development. This will include account configuration options.")

    # Placeholder content
    st.markdown("""
    ### Planned Features:
    - **Display Preferences**: Theme, layout, and UI customization
    - **Data Preferences**: Default timeframes and data sources
    - **Notification Settings**: Email and in-app notifications
    - **Export Settings**: Data export preferences
    - **Integration Settings**: Third-party service connections
    """)