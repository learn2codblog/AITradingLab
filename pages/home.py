"""
Home page module for AI Trading Lab PRO+
"""
import streamlit as st
from ui.components import create_section_header, create_info_card


def render_home_page():
    """Render the Home page content."""
    create_section_header(
        "Welcome to AI Trading Lab PRO+",
        "Your Professional AI-Powered Trading & Analysis Platform",
        "🚀"
    )

    # Welcome Cards
    col1, col2, col3 = st.columns(3)

    with col1:
        create_info_card(
            "Stock Analysis",
            "Perform comprehensive technical and fundamental analysis with AI-powered insights.",
            ""
            "info"
        )

    with col2:
        create_info_card(
            "Smart Screener",
            "Screen stocks by sector with advanced ML models and multi-timeframe analysis.",
            "🎯",
            "success"
        )

    with col3:
        create_info_card(
            "Portfolio Manager",
            "Optimize your portfolio with modern portfolio theory and AI recommendations.",
            "💼",
            "warning"
        )

    st.markdown("### 🌟 Key Features")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        #### 📈 Advanced Analytics
        - **Multi-Timeframe Analysis**: Support & resistance across multiple timeframes
        - **Technical Indicators**: 20+ indicators including RSI, MACD, Bollinger Bands
        - **Price Targets**: AI-powered entry, target, and stop-loss calculations
        - **Risk Management**: Dynamic position sizing and risk assessment
        """)

        st.markdown("""
        #### 🤖 Machine Learning
        - **Random Forest & XGBoost**: Advanced ML models for predictions
        - **Feature Engineering**: 50+ engineered features
        - **Backtesting**: Historical performance validation
        - **Confidence Scoring**: Signal strength assessment
        """)

    with col2:
        st.markdown("""
        #### 💰 Fundamental Analysis
        - **Financial Metrics**: P/E, ROE, Profit Margins, Growth Rates
        - **News Sentiment**: AI-powered sentiment analysis
        - **Analyst Ratings**: Target prices and recommendations
        - **Sector Analysis**: Compare across industry peers
        """)

        st.markdown("""
        #### 🎯 Smart Screener
        - **Sector-wise Screening**: Analyze stocks by sector (beyond Nifty 50)
        - **Universe Size**: Up to 500+ stocks across multiple sectors
        - **Buy/Sell Signals**: AI-generated actionable signals
        - **Batch Analysis**: Screen multiple stocks simultaneously
        """)

    st.markdown("---")

    # Quick Start Guide
    with st.expander("📚 Quick Start Guide", expanded=False):
        st.markdown("""
        ### Getting Started

        1. **Stock Analysis**: Navigate to 'Stock Analysis' to analyze individual stocks
        2. **Smart Screener**: Use 'Smart Screener' to find opportunities across sectors
        3. **Portfolio Manager**: Build and optimize your portfolio

        ### Tips
        - Adjust date ranges in the sidebar for historical analysis
        - Use confidence thresholds to filter signals
        - Compare multiple stocks in Portfolio Manager
        - Check risk metrics before taking positions
        """)
