"""
Zerodha Portfolio page module for AI Trading Lab PRO+
"""
import streamlit as st
from ui.components import create_section_header


def render_zerodha_portfolio():
    """Render the Zerodha Portfolio page content."""
    create_section_header(
        "Zerodha Portfolio",
        "View and Analyze Your Zerodha Portfolio",
        "📊"
    )

    # Log activity
    try:
        from src.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        user_id = st.session_state.get('user_id')
        if user_id and supabase.is_connected():
            supabase.log_activity(
                user_id=user_id,
                activity_type='kite_portfolio_view',
                description="Opened Zerodha Portfolio page",
                status='success'
            )
    except Exception:
        pass

    st.info("🚧 Zerodha Portfolio page is under development. This will integrate with Zerodha Kite API.")

    # Placeholder content
    st.markdown("""
    ### Planned Features:
    - **Portfolio Overview**: Holdings, P&L, and performance
    - **Position Analysis**: Current positions with AI insights
    - **Order History**: Trading history and order management
    - **Margin Information**: Available margin and utilization
    - **Risk Metrics**: Portfolio risk assessment
    """)