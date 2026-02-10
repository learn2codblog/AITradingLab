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