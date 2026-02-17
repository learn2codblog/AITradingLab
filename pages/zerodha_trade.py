"""
Zerodha Trade page module for AI Trading Lab PRO+
"""
import streamlit as st
from ui.components import create_section_header


def render_zerodha_trade():
    """Render the Zerodha Trade page content."""
    create_section_header(
        "Zerodha Automated Trading",
        "Execute Trades Through Zerodha Kite",
        "🔁"
    )

    # Log activity
    try:
        from src.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        user_id = st.session_state.get('user_id')
        if user_id and supabase.is_connected():
            supabase.log_activity(
                user_id=user_id,
                activity_type='kite_trade_view',
                description="Opened Zerodha Trade page",
                status='success'
            )
    except Exception:
        pass

    st.info("🚧 Zerodha Trade page is under development. This will enable automated trading through Zerodha.")

    # Placeholder content
    st.markdown("""
    ### Planned Features:
    - **Automated Trading**: Execute AI-generated signals
    - **Order Management**: Place, modify, and cancel orders
    - **Risk Controls**: Position sizing and stop-loss automation
    - **Trade Logging**: Complete trading activity audit trail
    - **Performance Tracking**: Trading strategy performance metrics
    """)