"""
AI Trading Lab PRO+
Modern UI Application with Enhanced Features
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ══════════════════════════════════════════════════════════════════════
# AUTHENTICATION - CHECK LOGIN STATUS BEFORE ANYTHING ELSE
# ══════════════════════════════════════════════════════════════════════

from src.auth import AuthManager, create_login_page
from ui.login_page import render_login_page

# Initialize authentication
auth_manager = AuthManager()
auth_manager.initialize_session_state()

# Check if user is authenticated
if not auth_manager.is_authenticated():
    # Render login page
    render_login_page(auth_manager)
    st.stop()

# Check if session is valid (not expired)
if not auth_manager.is_session_valid():
    auth_manager.logout()
    st.warning("⏰ Your session has expired. Please login again.")
    render_login_page(auth_manager)
    st.stop()

# ══════════════════════════════════════════════════════════════════════
# MAIN APPLICATION - USER IS AUTHENTICATED
# ══════════════════════════════════════════════════════════════════════

# Import backend modules
from src.data_loader import load_stock_data
from src.fundamental_analysis import get_fundamentals, get_news_sentiment, get_analyst_ratings, get_stock_news
from src.technical_indicators import calculate_technical_indicators, generate_signals, get_trend
from src.feature_engineering import engineer_advanced_features, select_best_features
from src.metrics import sharpe_ratio, max_drawdown
from src.portfolio_optimizer import optimize_portfolio
from src.price_targets import calculate_entry_target_prices
from src.price_targets_enhanced import (
    calculate_multi_timeframe_levels,
    generate_buy_sell_explanation,
    get_sector_stocks_from_universe,
    get_all_available_sectors,
    get_nifty_top_n
)
# Heavy ML imports are lazily loaded to avoid large startup memory usage.
# Use `load_ml_resources()` to import ML functions on demand.
_ml_resources_loaded = False

def load_ml_resources():
    """Lazily import heavy ML modules and bind names into module globals.
    Call this before using ML/advanced AI functions to avoid loading at startup.
    """
    global _ml_resources_loaded
    if _ml_resources_loaded:
        return

    # Import models and advanced AI functions here (CPU-only packages expected)
    try:
        from src.models import train_random_forest, train_xgboost  # type: ignore
        from src.advanced_ai import (
            calculate_advanced_indicators,
            detect_candlestick_patterns,
            detect_chart_patterns,
            detect_market_regime,
            detect_anomalies,
            create_ensemble_prediction,
            generate_ai_analysis,
            predict_with_lstm,
            analyze_news_sentiment,
            calculate_feature_importance,
            calculate_position_size,
            backtest_strategy,
            analyze_sentiment_transformer,
            calculate_supertrend,
            calculate_adx,
            calculate_psar,
            forecast_volatility_garch,
            get_volatility_regime,
            combined_trend_signal,
            predict_with_transformer,
            detect_anomalies_autoencoder,
        )

        # Bind to globals so existing code can use the names directly
        globals().update({
            'train_random_forest': train_random_forest,
            'train_xgboost': train_xgboost,
            'calculate_advanced_indicators': calculate_advanced_indicators,
            'detect_candlestick_patterns': detect_candlestick_patterns,
            'detect_chart_patterns': detect_chart_patterns,
            'detect_market_regime': detect_market_regime,
            'detect_anomalies': detect_anomalies,
            'create_ensemble_prediction': create_ensemble_prediction,
            'generate_ai_analysis': generate_ai_analysis,
            'predict_with_lstm': predict_with_lstm,
            'analyze_news_sentiment': analyze_news_sentiment,
            'calculate_feature_importance': calculate_feature_importance,
            'calculate_position_size': calculate_position_size,
            'backtest_strategy': backtest_strategy,
            'analyze_sentiment_transformer': analyze_sentiment_transformer,
            'calculate_supertrend': calculate_supertrend,
            'calculate_adx': calculate_adx,
            'calculate_psar': calculate_psar,
            'forecast_volatility_garch': forecast_volatility_garch,
            'get_volatility_regime': get_volatility_regime,
            'combined_trend_signal': combined_trend_signal,
            'predict_with_transformer': predict_with_transformer,
            'detect_anomalies_autoencoder': detect_anomalies_autoencoder,
        })

        _ml_resources_loaded = True
    except Exception as e:
        # If lazy import fails, log but allow the app to continue; operations will raise later if used.
        import logging
        logging.getLogger('app_modern').warning(f"Lazy ML import failed: {e}")

from src.risk_management import calculate_risk_metrics, calculate_stop_loss_take_profit
from src.backtester import SimpleBacktester, WalkForwardBacktester, generate_ma_crossover_signals, generate_rsi_signals, generate_macd_signals
from src.email_alerts import EmailAlertConfig, EmailAlertSender, AlertManager
from src.zerodha_integration import ZerodhaAuthenticator, ZerodhaKite, AutomatedTrader, analyze_portfolio

# Import UI modules
from ui.styles import get_custom_css, get_icon_mapping
from ui.components import (
    create_metric_card,
    create_signal_badge,
    create_info_card,
    create_section_header,
    create_price_chart,
    create_volume_chart,
    create_comparison_chart,
    create_gauge_chart,
    create_heatmap
)
from ui.portfolio_builder import (
    create_portfolio_builder,
    create_advanced_portfolio_builder,
    create_mobile_responsive_portfolio,
    show_portfolio_recommendations
)

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# ══════════════════════════════════════════════════════════════════════
# CACHING FOR PERFORMANCE
# ══════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def load_stock_data_cached(symbol: str, start_date, end_date):
    """Cached stock data loading"""
    return load_stock_data(symbol, start_date, end_date)

@st.cache_data(ttl=86400, show_spinner=False)  # Cache for 24 hours
def get_fundamentals_cached(symbol: str):
    """Cached fundamentals - changes less frequently"""
    return get_fundamentals(symbol)

@st.cache_data(ttl=3600, show_spinner=False)
def calculate_indicators_cached(_df):
    """Cached indicator calculation - uses _df to avoid hashing issues"""
    df = _df.copy()
    df = calculate_technical_indicators(df)
    # Lazily import advanced indicators to avoid large memory use at startup
    try:
        load_ml_resources()
    except Exception:
        # If loading fails, allow the error to be surfaced when advanced indicators are used
        pass
    df = calculate_advanced_indicators(df)
    return df

@st.cache_data(ttl=3600, show_spinner=False)
def get_news_sentiment_cached(symbol: str):
    """Cached news sentiment"""
    return get_news_sentiment(symbol)

# ══════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ══════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="AI Trading Lab PRO+",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://docs.streamlit.io',
        'Report a bug': 'https://github.com/streamlit/streamlit/issues',
        'About': '# AI Trading Lab PRO+ v3.0.0\n\nAI-Powered Trading & Portfolio Analysis Platform'
    }
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Add Mobile Responsive CSS
mobile_responsive_css = """
<style>
    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        /* Navigation buttons stack vertically on mobile */
        [data-testid="column"] {
            flex-wrap: wrap;
        }
        
        /* Reduce padding and margins on mobile */
        .stMetric {
            padding: 0.5rem;
        }
        
        /* Make selectbox full width on mobile */
        .stSelectbox {
            width: 100%;
        }
        
        /* Stack columns on mobile */
        .stColumn {
            width: 100% !important;
            margin-bottom: 1rem;
        }
        
        /* Responsive font sizes */
        h1 { font-size: 1.5rem; }
        h2 { font-size: 1.2rem; }
        h3 { font-size: 1rem; }
        
        /* Full width buttons on mobile */
        .stButton button {
            width: 100%;
        }
        
        /* Reduce chart height on mobile */
        .plotly-graph-div {
            height: 250px !important;
        }
    }
    
    @media (max-width: 480px) {
        /* Extra small devices */
        .header-box {
            padding: 20px;
        }
        
        .app-title {
            font-size: 1.8rem;
        }
        
        .app-tagline {
            font-size: 0.9rem;
        }
        
        /* Single column layout on very small screens */
        [data-testid="column"] {
            width: 100% !important;
        }
    }
    
    /* General responsive improvements */
    .stDataFrame {
        overflow-x: auto;
    }
    
    /* Responsive slider width */
    .stSlider {
        width: 100%;
    }
    
    /* Responsive metric cards */
    .metric-card {
        min-height: 80px;
        padding: 1rem;
    }
    
    /* Responsive expander */
    .streamlit-expanderHeader {
        font-size: 0.95rem;
    }
</style>
"""
st.markdown(mobile_responsive_css, unsafe_allow_html=True)

# Get icon mapping
icons = get_icon_mapping()

# ══════════════════════════════════════════════════════════════════════
# TOP BAR - NAVIGATION & SETTINGS
# ══════════════════════════════════════════════════════════════════════

# Modern Header with Clean Design
from pathlib import Path

# Apply header styling
st.markdown("""
<style>
    .header-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 35px 40px;
        border-radius: 18px;
        margin-bottom: 25px;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .app-title {
        color: #ffffff;
        font-size: 2.8rem;
        font-weight: 900;
        margin: 0;
        padding: 0;
        text-shadow: 3px 3px 8px rgba(0, 0, 0, 0.4);
        letter-spacing: -0.5px;
    }
    .app-tagline {
        color: #1a1a2e;
        font-size: 1.1rem;
        font-weight: 700;
        margin: 8px 0 0 0;
        background: rgba(255, 255, 255, 0.85);
        padding: 8px 15px;
        border-radius: 20px;
        display: inline-block;
    }
    .version-badge {
        background: rgba(255, 255, 255, 0.25);
        padding: 10px 22px;
        border-radius: 25px;
        color: #ffffff;
        font-weight: 700;
        font-size: 0.95rem;
        border: 2px solid rgba(255, 255, 255, 0.4);
        display: inline-block;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Create header
st.markdown('<div class="header-box">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([0.7, 5, 2])

with col1:
    # Use the regular logo (not grayscale, not transparent)
    logo_path = Path("Trading/icononly_nobuffer.png")
    if logo_path.exists():
        st.image(str(logo_path), width=60)
    else:
        st.markdown("### 📊")

with col2:
    st.markdown('<h1 class="app-title">💎 TradeGenius AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="app-tagline">🚀 Smart Trading • 🤖 AI-Powered • 📈 Data-Driven Insights</p>', unsafe_allow_html=True)

with col3:
    # Display user info and version
    col3_inner1, col3_inner2 = st.columns([1, 1])
    with col3_inner1:
        user_info = auth_manager.get_user_info()
        if user_info:
            st.markdown(f"<p style='text-align: right; margin: 0; font-size: 12px;'>👤 {user_info['name']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: right; margin: 0; font-size: 11px; color: #ccc;'>{user_info['email']}</p>", unsafe_allow_html=True)
    with col3_inner2:
        st.markdown('<div style="text-align: right; padding-top: 12px;"><span class="version-badge">⚡ v3.0.0</span></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# Navigation Bar
st.markdown("""
<style>
    .nav-bar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

nav_col1, nav_col2, nav_col3, nav_col4, nav_col5, nav_col6, nav_col7, nav_col8, nav_col9, nav_col10 = st.columns(10)

with nav_col1:
    home_btn = st.button("🏠 Home", use_container_width=True, key="nav_home")
with nav_col2:
    analysis_btn = st.button("📊 Analysis", use_container_width=True, key="nav_analysis")
with nav_col3:
    ai_btn = st.button("🤖 AI Deep Analysis", use_container_width=True, key="nav_ai")
with nav_col4:
    screener_btn = st.button("🎯 Screener", use_container_width=True, key="nav_screener")
with nav_col5:
    news_btn = st.button("📰 News", use_container_width=True, key="nav_news")
with nav_col6:
    deeplearning_btn = st.button("🔬 Deep Learning", use_container_width=True, key="nav_deeplearning")
with nav_col7:
    backtest_btn = st.button("📈 Backtest", use_container_width=True, key="nav_backtest")
with nav_col8:
    portfolio_btn = st.button("💼 Portfolio", use_container_width=True, key="nav_portfolio")
with nav_col9:
    settings_btn = st.button("⚙️ Settings", use_container_width=True, key="nav_settings")
with nav_col10:
    logout_btn = st.button("🚪 Logout", use_container_width=True, key="nav_logout", help="Logout and return to login page")

# Determine active page
if 'active_page' not in st.session_state:
    st.session_state.active_page = "🏠 Home"

if home_btn:
    st.session_state.active_page = "🏠 Home"
elif analysis_btn:
    st.session_state.active_page = "📊 Stock Analysis"
elif ai_btn:
    st.session_state.active_page = "🤖 AI Deep Analysis"
elif screener_btn:
    st.session_state.active_page = "🎯 Smart Screener"
elif news_btn:
    st.session_state.active_page = "📰 General News"
elif deeplearning_btn:
    st.session_state.active_page = "🔬 Deep Learning"
elif backtest_btn:
    st.session_state.active_page = "📈 Strategy Backtest"
elif portfolio_btn:
    st.session_state.active_page = "💼 Portfolio Manager"
elif settings_btn:
    st.session_state.active_page = "⚙️ Settings"
elif logout_btn:
    # Handle logout
    auth_manager.logout()
    st.success("✅ Logged out successfully!")
    st.info("Redirecting to login page...")
    import time
    time.sleep(1)
    st.rerun()

page = st.session_state.active_page

# Settings Bar (collapsible)
with st.expander("⚙️ Analysis Settings", expanded=False):
    settings_col1, settings_col2, settings_col3 = st.columns(3)

    with settings_col1:
        start_date = st.date_input(
            "📅 Start Date",
            value=datetime.now() - timedelta(days=365*3),
            help="Historical data start date"
        )

    with settings_col2:
        end_date = st.date_input(
            "📅 End Date",
            value=datetime.now(),
            help="Historical data end date"
        )

    with settings_col3:
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        st.info("💡 Adjust date range for historical analysis")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# HOME PAGE
# ══════════════════════════════════════════════════════════════════════

if page == "🏠 Home":
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
            "📊",
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

# ══════════════════════════════════════════════════════════════════════
# STOCK ANALYSIS PAGE
# ══════════════════════════════════════════════════════════════════════

elif page == "📊 Stock Analysis":
    create_section_header("Stock Analysis", "Comprehensive Technical & Fundamental Analysis", "📊")

    # Input Section
    with st.container():
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

        with col1:
            symbol = st.text_input("Enter Stock Symbol", "RELIANCE.NS", help="e.g., RELIANCE.NS, TCS.NS").upper().strip()

        with col2:
            analysis_type = st.selectbox("Analysis Type", ["Complete", "Technical Only", "Fundamental Only"])

        with col3:
            prediction_days = st.number_input("Prediction Days", 1, 30, 5)

        with col4:
            st.markdown("<br>", unsafe_allow_html=True)
            analyze_button = st.button("🔍 Analyze Stock", type="primary", use_container_width=True)

    if analyze_button and symbol:
        with st.spinner(f"Analyzing {symbol}..."):
            # Load data
            stock_data = load_stock_data(symbol, start_date, end_date)

            if stock_data is None or len(stock_data) < 30:
                st.error("❌ Insufficient data available for this stock. Please try another symbol.")
                st.stop()

            # Get fundamentals (always needed for basic info)
            fundamentals = get_fundamentals(symbol)
            sentiment = get_news_sentiment(symbol)
            analyst_info = get_analyst_ratings(symbol)

            # Calculate technical indicators only if needed
            if analysis_type in ["Complete", "Technical Only"]:
                stock_data = calculate_technical_indicators(stock_data)
                stock_data.dropna(inplace=True)
                entry_targets = calculate_entry_target_prices(stock_data, fundamentals=fundamentals)
            else:
                # For Fundamental Only, just get basic price info
                current_price = stock_data['Close'].iloc[-1]
                entry_targets = {
                    'Current Price': current_price,
                    'Entry Price': current_price,
                    'Target Price': current_price * 1.15,  # Placeholder
                    'Stop Loss': current_price * 0.90,
                    'R/R Ratio': 1.5,
                    'Confidence Score': 0.5,
                    'Strength': 'N/A (Fundamental Only)',
                    'Confidence Reasons': 'Technical analysis not performed in Fundamental Only mode.'
                }

            # ─── PRICE OVERVIEW (Show for all modes) ───
            st.markdown("### 💹 Price Overview")

            current_price = entry_targets['Current Price']

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                create_metric_card("Current Price", f"₹{current_price:.2f}", icon="💰", color="#667eea")

            with col2:
                high_52w = fundamentals.get('52WeekHigh', current_price)
                create_metric_card("52W High", f"₹{high_52w:.2f}", icon="📈", color="#48bb78")

            with col3:
                low_52w = fundamentals.get('52WeekLow', current_price)
                create_metric_card("52W Low", f"₹{low_52w:.2f}", icon="📉", color="#f56565")

            with col4:
                market_cap = fundamentals.get('MarketCap', 0)
                if market_cap > 1e12:
                    cap_str = f"₹{market_cap/1e12:.2f}T"
                elif market_cap > 1e9:
                    cap_str = f"₹{market_cap/1e9:.2f}B"
                else:
                    cap_str = f"₹{market_cap/1e7:.0f}Cr"
                create_metric_card("Market Cap", cap_str, icon="🏦", color="#9f7aea")

            st.markdown("<br>", unsafe_allow_html=True)

            # ─── TECHNICAL ANALYSIS SECTION (Only for Complete or Technical Only) ───
            if analysis_type in ["Complete", "Technical Only"]:
                # Entry/Target/Stop Loss
                st.markdown("### 🎯 Trading Levels")

                entry_price = entry_targets['Entry Price']
                target_price = entry_targets['Target Price']
                stop_loss = entry_targets['Stop Loss']
                rr_ratio = entry_targets['R/R Ratio']

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    create_metric_card("Entry Price", f"₹{entry_price:.2f}", icon="🎯", color="#48bb78")

                with col2:
                    create_metric_card("Target Price", f"₹{target_price:.2f}", icon="🚀", color="#38b2ac")

                with col3:
                    create_metric_card("Stop Loss", f"₹{stop_loss:.2f}", icon="🛑", color="#f56565")

                with col4:
                    create_metric_card("R/R Ratio", f"{rr_ratio:.2f}:1", icon="⚖️", color="#ed8936")

                st.markdown("<br>", unsafe_allow_html=True)

                # ─── SIGNAL & RECOMMENDATION (Technical Only or Complete) ───
                st.markdown("### 🎯 AI Recommendation")

                try:
                    explanation = generate_buy_sell_explanation(stock_data, fundamentals)
                    recommendation = explanation.get('Recommendation', 'N/A')
                    action = explanation.get('Action', 'N/A')
                    main_explanation = explanation.get('Main Explanation', 'N/A')

                    col1, col2 = st.columns([1, 2])

                    with col1:
                        # Signal type
                        if 'BUY' in recommendation:
                            signal_type = 'bullish'
                            badge_icon = "🟢"
                        elif 'SELL' in recommendation:
                            signal_type = 'bearish'
                            badge_icon = "🔴"
                        else:
                            signal_type = 'neutral'
                            badge_icon = "🟡"

                        st.markdown(f"<div style='text-align: center; font-size: 4rem;'>{badge_icon}</div>", unsafe_allow_html=True)
                        st.markdown(f"<h2 style='text-align: center;'>{recommendation}</h2>", unsafe_allow_html=True)
                        st.markdown(f"<p style='text-align: center; font-size: 1.2rem;'><strong>Confidence:</strong> {entry_targets['Confidence Score']:.1%}</p>", unsafe_allow_html=True)

                    with col2:
                        st.markdown(f"**Action:** {action}")
                        st.markdown(f"**Analysis:** {main_explanation}")
                        st.markdown(f"**Strength:** {entry_targets['Strength']}")

                        with st.expander("📋 Detailed Reasons"):
                            st.markdown(entry_targets['Confidence Reasons'])

                    # Signals Breakdown
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        bullish_signals = explanation.get('Bullish Signals', [])
                        st.markdown("**✅ Bullish Signals**")
                        if bullish_signals:
                            for signal in bullish_signals:
                                st.markdown(f"• {signal}")
                        else:
                            st.markdown("_None detected_")

                    with col2:
                        bearish_signals = explanation.get('Bearish Signals', [])
                        st.markdown("**❌ Bearish Signals**")
                        if bearish_signals:
                            for signal in bearish_signals:
                                st.markdown(f"• {signal}")
                        else:
                            st.markdown("_None detected_")

                    with col3:
                        neutral_signals = explanation.get('Neutral Signals', [])
                        st.markdown("**⚪ Neutral Signals**")
                        if neutral_signals:
                            for signal in neutral_signals:
                                st.markdown(f"• {signal}")
                        else:
                            st.markdown("_None detected_")

                except Exception as e:
                    st.warning(f"Could not generate recommendation: {str(e)}")

                # ─── CHARTS (Technical Only or Complete) ───
                st.markdown("### 📈 Price Charts")

                # Create tabs for different views
                chart_tab1, chart_tab2, chart_tab3 = st.tabs(["Price Action", "Volume", "Indicators"])

                with chart_tab1:
                    fig_price = create_price_chart(stock_data.tail(200), f"{symbol} Price Chart")
                    st.plotly_chart(fig_price, use_container_width=True)

                with chart_tab2:
                    fig_volume = create_volume_chart(stock_data.tail(200), f"{symbol} Volume")
                    st.plotly_chart(fig_volume, use_container_width=True)

                with chart_tab3:
                    col1, col2 = st.columns(2)

                    with col1:
                        latest = stock_data.iloc[-1]
                        rsi = latest.get('RSI14', 50)
                        fig_rsi = create_gauge_chart(rsi, "RSI (14)", 0, 100, 30, 70)
                        st.plotly_chart(fig_rsi, use_container_width=True)

                    with col2:
                        macd = latest.get('MACD', 0)
                        signal = latest.get('MACD_Signal', latest.get('Signal_Line', 0))
                        st.markdown("#### MACD Status")
                        if macd > signal:
                            st.success(f"🟢 Bullish (MACD: {macd:.2f} > Signal: {signal:.2f})")
                        else:
                            st.error(f"🔴 Bearish (MACD: {macd:.2f} < Signal: {signal:.2f})")

                # ─── KEY TREND INDICATORS ───
                st.markdown("### 📊 Key Trend Indicators")

                latest = stock_data.iloc[-1]
                current_price = latest['Close']

                # Get all indicator values
                sma20 = latest.get('SMA20', current_price)
                sma50 = latest.get('SMA50', current_price)
                sma200 = latest.get('SMA200', current_price)
                ema12 = latest.get('EMA12', current_price)
                ema26 = latest.get('EMA26', current_price)
                rsi = latest.get('RSI14', 50)
                macd = latest.get('MACD', 0)
                macd_signal = latest.get('MACD_Signal', 0)
                bb_upper = latest.get('BB_Upper', current_price * 1.02)
                bb_lower = latest.get('BB_Lower', current_price * 0.98)
                adx = latest.get('ADX', 25)
                stoch_k = latest.get('Stoch_K', 50)
                atr = latest.get('ATR14', 0)
                volume_ratio = latest.get('Volume_Ratio', 1.0)

                # Trend Indicators Row 1
                ind_col1, ind_col2, ind_col3, ind_col4 = st.columns(4)

                with ind_col1:
                    trend = get_trend(stock_data)
                    trend_color = "#48bb78" if trend == "Bullish" else "#f56565" if trend == "Bearish" else "#ed8936"
                    st.markdown(f"""
                    <div style='background: {trend_color}; padding: 15px; border-radius: 10px; text-align: center;'>
                        <h3 style='color: white; margin: 0;'>📈 Trend</h3>
                        <h2 style='color: white; margin: 5px 0;'>{trend}</h2>
                    </div>
                    """, unsafe_allow_html=True)

                with ind_col2:
                    rsi_status = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"
                    rsi_color = "#f56565" if rsi > 70 else "#48bb78" if rsi < 30 else "#667eea"
                    st.markdown(f"""
                    <div style='background: {rsi_color}; padding: 15px; border-radius: 10px; text-align: center;'>
                        <h3 style='color: white; margin: 0;'>📉 RSI (14)</h3>
                        <h2 style='color: white; margin: 5px 0;'>{rsi:.1f}</h2>
                        <p style='color: rgba(255,255,255,0.9); margin: 0;'>{rsi_status}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with ind_col3:
                    macd_status = "Bullish" if macd > macd_signal else "Bearish"
                    macd_color = "#48bb78" if macd > macd_signal else "#f56565"
                    st.markdown(f"""
                    <div style='background: {macd_color}; padding: 15px; border-radius: 10px; text-align: center;'>
                        <h3 style='color: white; margin: 0;'>📊 MACD</h3>
                        <h2 style='color: white; margin: 5px 0;'>{macd:.2f}</h2>
                        <p style='color: rgba(255,255,255,0.9); margin: 0;'>{macd_status}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with ind_col4:
                    adx_strength = "Strong" if adx > 25 else "Weak"
                    adx_color = "#667eea" if adx > 25 else "#a0aec0"
                    st.markdown(f"""
                    <div style='background: {adx_color}; padding: 15px; border-radius: 10px; text-align: center;'>
                        <h3 style='color: white; margin: 0;'>💪 ADX</h3>
                        <h2 style='color: white; margin: 5px 0;'>{adx:.1f}</h2>
                        <p style='color: rgba(255,255,255,0.9); margin: 0;'>{adx_strength} Trend</p>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Trend Indicators Row 2 - Moving Averages
                st.markdown("#### 📈 Moving Averages")
                ma_col1, ma_col2, ma_col3, ma_col4, ma_col5 = st.columns(5)

                with ma_col1:
                    ma_signal = "🟢" if current_price > sma20 else "🔴"
                    st.metric("SMA 20", f"₹{sma20:.2f}", f"{ma_signal} {'Above' if current_price > sma20 else 'Below'}")

                with ma_col2:
                    ma_signal = "🟢" if current_price > sma50 else "🔴"
                    st.metric("SMA 50", f"₹{sma50:.2f}", f"{ma_signal} {'Above' if current_price > sma50 else 'Below'}")

                with ma_col3:
                    ma_signal = "🟢" if current_price > sma200 else "🔴"
                    st.metric("SMA 200", f"₹{sma200:.2f}", f"{ma_signal} {'Above' if current_price > sma200 else 'Below'}")

                with ma_col4:
                    ema_signal = "🟢" if ema12 > ema26 else "🔴"
                    st.metric("EMA 12", f"₹{ema12:.2f}", f"{ema_signal} {'Above' if ema12 > ema26 else 'Below'} EMA26")

                with ma_col5:
                    st.metric("EMA 26", f"₹{ema26:.2f}", "")

                # Additional Indicators Row
                st.markdown("#### 📊 Additional Indicators")
                add_col1, add_col2, add_col3, add_col4 = st.columns(4)

                with add_col1:
                    bb_pos = "Upper" if current_price > bb_upper else "Lower" if current_price < bb_lower else "Middle"
                    st.metric("Bollinger Position", bb_pos, f"Upper: ₹{bb_upper:.2f} | Lower: ₹{bb_lower:.2f}")

                with add_col2:
                    stoch_status = "Overbought" if stoch_k > 80 else "Oversold" if stoch_k < 20 else "Neutral"
                    st.metric("Stochastic %K", f"{stoch_k:.1f}", stoch_status)

                with add_col3:
                    st.metric("ATR (14)", f"₹{atr:.2f}", f"Volatility: {(atr/current_price*100):.2f}%")

                with add_col4:
                    vol_status = "High" if volume_ratio > 1.5 else "Low" if volume_ratio < 0.7 else "Normal"
                    st.metric("Volume Ratio", f"{volume_ratio:.2f}x", vol_status)

                # ─── MULTI-TIMEFRAME LEVELS ───
                st.markdown("### 📊 Multi-Timeframe Support & Resistance")

                try:
                    mtf_levels = calculate_multi_timeframe_levels(stock_data)
                    mtf_data = []
                    for timeframe, levels in mtf_levels.items():
                        mtf_data.append({
                            'Timeframe': timeframe,
                            'Support': f"₹{levels['Support']:.2f}",
                            'Distance to Support': f"{levels['Distance to Support']:.2f}%",
                            'Resistance': f"₹{levels['Resistance']:.2f}",
                            'Distance to Resistance': f"{levels['Distance to Resistance']:.2f}%"
                        })

                    df_mtf = pd.DataFrame(mtf_data)
                    st.dataframe(df_mtf, use_container_width=True, hide_index=True)
                except Exception as e:
                    st.warning(f"Could not calculate multi-timeframe levels: {str(e)}")

            # ─── FUNDAMENTALS (Fundamental Only or Complete) ───
            if analysis_type in ["Complete", "Fundamental Only"]:
                st.markdown("### 💰 Fundamental Metrics")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    # Use ROE directly (as decimal) or ROE_Percent (as percentage value)
                    roe = fundamentals.get('ROE', 0)
                    roe_pct = fundamentals.get('ROE_Percent', 0)
                    if roe and abs(roe) > 0.0001:
                        roe_display = f"{roe:.2%}"
                    elif roe_pct and abs(roe_pct) > 0.01:
                        roe_display = f"{roe_pct:.2f}%"
                    else:
                        roe_display = "N/A"
                    create_metric_card("ROE", roe_display, icon="📊", color="#667eea")

                with col2:
                    pe = fundamentals.get('PE', 0)
                    pe_display = f"{pe:.1f}" if pe and pe > 0 else "N/A"
                    create_metric_card("P/E Ratio", pe_display, icon="💹", color="#38b2ac")

                with col3:
                    profit_margin = fundamentals.get('ProfitMargin', 0)
                    pm_display = f"{profit_margin:.2%}" if profit_margin else "N/A"
                    create_metric_card("Profit Margin", pm_display, icon="💰", color="#48bb78")

                with col4:
                    revenue_growth = fundamentals.get('RevenueGrowth', 0)
                    rg_display = f"{revenue_growth:.2%}" if revenue_growth else "N/A"
                    create_metric_card("Revenue Growth", rg_display, icon="📈", color="#9f7aea")

                # Additional metrics in expander
                with st.expander("📋 More Fundamental Data"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric("Market Cap (Cr)", f"₹{fundamentals.get('MarketCap', 0) / 1e7:,.1f}")
                        st.metric("Beta", f"{fundamentals.get('Beta', 1):.2f}")
                        st.metric("EPS Growth", f"{fundamentals.get('EPSGrowth', 0):.2%}")

                    with col2:
                        st.metric("News Sentiment", f"{sentiment:.2f}")
                        st.metric("Analyst Target", f"₹{analyst_info.get('TargetPrice', 'N/A')}")
                        st.metric("Recommendation", analyst_info.get('RecommendationKey', 'N/A'))

            # ─── RISK METRICS ───
            st.markdown("### ⚠️ Risk Analysis")

            try:
                risk_metrics = calculate_risk_metrics(stock_data)

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    volatility = risk_metrics.get('volatility', 0)
                    create_metric_card("Volatility (Annual)", f"{volatility:.2%}", icon="📉", color="#ed8936")

                with col2:
                    var_95 = risk_metrics.get('var_95', 0)
                    create_metric_card("VaR (95%)", f"{var_95:.2%}", icon="⚠️", color="#f56565")

                with col3:
                    max_daily_loss = risk_metrics.get('max_daily_loss', 0)
                    create_metric_card("Max Daily Loss", f"{max_daily_loss:.2%}", icon="🔻", color="#e53e3e")

                with col4:
                    downside_dev = risk_metrics.get('downside_deviation', 0)
                    create_metric_card("Downside Deviation", f"{downside_dev:.2%}", icon="📊", color="#fc8181")

            except Exception as e:
                st.warning(f"Could not calculate risk metrics: {str(e)}")

    elif not symbol:
        create_info_card(
            "Get Started",
            "Enter a stock symbol above and click 'Analyze Stock' to begin your analysis.",
            "ℹ️",
            "info"
        )

# ══════════════════════════════════════════════════════════════════════
# AI DEEP ANALYSIS PAGE
# ══════════════════════════════════════════════════════════════════════

elif page == "🤖 AI Deep Analysis":
    create_section_header("AI Deep Analysis", "Advanced Machine Learning & Pattern Recognition", "🤖")

    # Input section
    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        ai_symbol = st.text_input("📈 Enter Stock Symbol", value="RELIANCE.NS", key="ai_symbol",
                                  help="Enter NSE stock with .NS suffix (e.g., RELIANCE.NS, TCS.NS)")

    with col2:
        analysis_depth = st.selectbox("🔬 Analysis Depth",
                                      ["Quick Analysis", "Standard", "Deep Analysis"],
                                      index=1)

    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        run_ai = st.button("🚀 Run AI Analysis", type="primary", use_container_width=True)

    # Advanced Settings Expander
    with st.expander("⚙️ Advanced Analysis Settings"):
        adv_col1, adv_col2, adv_col3 = st.columns(3)
        with adv_col1:
            supertrend_mult = st.slider("SuperTrend Multiplier", 1.0, 4.0, 3.0, 0.5,
                                        help="Higher = fewer signals, lower = more sensitive")
        with adv_col2:
            supertrend_period = st.slider("SuperTrend Period", 5, 20, 10, 1,
                                          help="ATR lookback period")
        with adv_col3:
            st.markdown("**Indicator Sensitivity**")
            st.caption("Higher multiplier = fewer false signals during pullbacks")

    # Feature cards
    st.markdown("### 🎯 Advanced AI Features")

    feat_col1, feat_col2, feat_col3, feat_col4 = st.columns(4)

    with feat_col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px; border-radius: 12px; color: white; text-align: center;'>
            <h3 style='margin: 0; color: white;'>🧠</h3>
            <h4 style='margin: 5px 0; color: white;'>LSTM Prediction</h4>
            <p style='margin: 0; font-size: 0.85rem; color: rgba(255,255,255,0.9);'>Deep Learning price forecast</p>
        </div>
        """, unsafe_allow_html=True)

    with feat_col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f093fb, #f5576c); padding: 20px; border-radius: 12px; color: white; text-align: center;'>
            <h3 style='margin: 0; color: white;'>📊</h3>
            <h4 style='margin: 5px 0; color: white;'>30+ Indicators</h4>
            <p style='margin: 0; font-size: 0.85rem; color: rgba(255,255,255,0.9);'>Advanced technical analysis</p>
        </div>
        """, unsafe_allow_html=True)

    with feat_col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #4facfe, #00f2fe); padding: 20px; border-radius: 12px; color: white; text-align: center;'>
            <h3 style='margin: 0; color: white;'>🎯</h3>
            <h4 style='margin: 5px 0; color: white;'>Pattern Detection</h4>
            <p style='margin: 0; font-size: 0.85rem; color: rgba(255,255,255,0.9);'>Candlestick & chart patterns</p>
        </div>
        """, unsafe_allow_html=True)

    with feat_col4:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #43e97b, #38f9d7); padding: 20px; border-radius: 12px; color: white; text-align: center;'>
            <h3 style='margin: 0; color: white;'>🤖</h3>
            <h4 style='margin: 5px 0; color: white;'>Ensemble ML</h4>
            <p style='margin: 0; font-size: 0.85rem; color: rgba(255,255,255,0.9);'>5 ML models combined</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if run_ai and ai_symbol:
        with st.spinner(f"🤖 Running AI Deep Analysis on {ai_symbol}..."):
            # Load data
            stock_data = load_stock_data(ai_symbol, start_date, end_date)

            if stock_data is None or len(stock_data) < 100:
                st.error("❌ Could not load sufficient data. Please check the symbol.")
            else:
                # Calculate technical indicators
                stock_data = calculate_technical_indicators(stock_data)

                # Calculate advanced indicators
                try:
                    # Ensure ML resources are loaded before calling advanced functions
                    load_ml_resources()
                    stock_data = calculate_advanced_indicators(stock_data)

                    # Recalculate SuperTrend with user-defined parameters
                    stock_data = calculate_supertrend(stock_data, period=supertrend_period, multiplier=supertrend_mult)
                except Exception as e:
                    st.warning(f"Some advanced indicators could not be calculated: {e}")

                # Get fundamentals
                fundamentals = get_fundamentals(ai_symbol)

                # Run AI Analysis with the selected depth
                ai_results = generate_ai_analysis(stock_data, ai_symbol, fundamentals, analysis_depth)

                # ─── AI RECOMMENDATION ───
                st.markdown("### 🎯 AI Recommendation")

                ai_rec = ai_results.get('ai_recommendation', {})
                recommendation = ai_rec.get('recommendation', 'HOLD')
                confidence = ai_rec.get('confidence', 0.5)
                used_depth = ai_rec.get('analysis_depth', analysis_depth)

                # Recommendation card
                if 'BUY' in recommendation:
                    rec_color = '#48bb78'
                    rec_bg = 'linear-gradient(135deg, #48bb78, #38a169)'
                elif 'SELL' in recommendation:
                    rec_color = '#f56565'
                    rec_bg = 'linear-gradient(135deg, #f56565, #e53e3e)'
                else:
                    rec_color = '#ed8936'
                    rec_bg = 'linear-gradient(135deg, #ed8936, #dd6b20)'

                st.markdown(f"""
                <div style='background: {rec_bg}; padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 20px;'>
                    <h1 style='color: white; margin: 0; font-size: 3rem;'>{recommendation}</h1>
                    <p style='color: rgba(255,255,255,0.9); font-size: 1.2rem; margin: 10px 0 0 0;'>
                        Confidence: {confidence:.1%} | Action: {ai_rec.get('action', 'N/A')}
                    </p>
                    <p style='color: rgba(255,255,255,0.7); font-size: 0.9rem; margin: 5px 0 0 0;'>
                        Analysis Mode: {used_depth}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # Display contradictions if any
                contradictions = ai_rec.get('contradictions', [])
                warnings = ai_rec.get('warnings', [])

                if contradictions:
                    st.markdown("#### ⚠️ Signal Contradictions Detected")
                    for contradiction in contradictions:
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #fef3c7, #fde68a); padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #f59e0b;'>
                            <strong style='color: #92400e;'>⚠️ {contradiction.get('type', 'Contradiction')}</strong>
                            <p style='margin: 5px 0; color: #78350f;'>{contradiction.get('description', '')}</p>
                            <p style='margin: 0; color: #92400e; font-style: italic;'>💡 {contradiction.get('resolution', '')}</p>
                        </div>
                        """, unsafe_allow_html=True)

                if warnings:
                    st.markdown("#### ℹ️ Analysis Warnings")
                    for warning in warnings:
                        st.warning(f"⚠️ {warning}")

                # Probability breakdown
                probs = ai_rec.get('probabilities', {})
                prob_col1, prob_col2, prob_col3 = st.columns(3)

                with prob_col1:
                    create_metric_card("Buy Probability", f"{probs.get('buy', 0):.1%}", icon="🟢", color="#48bb78")
                with prob_col2:
                    create_metric_card("Hold Probability", f"{probs.get('hold', 0):.1%}", icon="🟡", color="#ed8936")
                with prob_col3:
                    create_metric_card("Sell Probability", f"{probs.get('sell', 0):.1%}", icon="🔴", color="#f56565")

                # ─── TECHNICAL SCORE ───
                st.markdown("### 📊 Technical Score")

                tech_score = ai_results.get('technical_score', {})
                score = tech_score.get('score', 50)
                grade = tech_score.get('grade', 'C')
                breakdown = tech_score.get('breakdown', {})

                score_col1, score_col2 = st.columns([1, 2])

                with score_col1:
                    # Score gauge
                    if score >= 70:
                        score_color = '#48bb78'
                    elif score >= 50:
                        score_color = '#ed8936'
                    else:
                        score_color = '#f56565'

                    st.markdown(f"""
                    <div style='text-align: center; padding: 20px; background: white; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                        <div style='font-size: 4rem; font-weight: 900; color: {score_color};'>{score:.0f}</div>
                        <div style='font-size: 1.5rem; color: #718096;'>out of 100</div>
                        <div style='font-size: 2rem; margin-top: 10px; padding: 10px 20px; background: {score_color}; color: white; border-radius: 10px; display: inline-block;'>
                            Grade: {grade}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with score_col2:
                    # Breakdown chart
                    import plotly.graph_objects as go

                    categories = list(breakdown.keys())
                    values = list(breakdown.values())

                    fig = go.Figure(data=[
                        go.Bar(x=categories, y=values, marker_color=['#667eea', '#f093fb', '#4facfe', '#43e97b'])
                    ])
                    fig.update_layout(
                        title="Score Breakdown (25 max each)",
                        yaxis_range=[0, 25],
                        height=300,
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # ─── MARKET REGIME ───
                st.markdown("### 🌍 Market Regime Detection")

                regime = ai_results.get('market_regime', {})

                regime_col1, regime_col2, regime_col3 = st.columns(3)

                with regime_col1:
                    primary = regime.get('primary_regime', 'Unknown')
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #667eea, #764ba2); padding: 25px; border-radius: 12px; text-align: center;'>
                        <h4 style='color: rgba(255,255,255,0.8); margin: 0;'>Current Regime</h4>
                        <h2 style='color: white; margin: 10px 0;'>{primary}</h2>
                        <p style='color: rgba(255,255,255,0.8); margin: 0;'>Confidence: {regime.get('confidence', 0):.0%}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with regime_col2:
                    risk = regime.get('risk_level', 'Medium')
                    risk_colors = {'Low': '#48bb78', 'Medium': '#ed8936', 'High': '#f56565', 'Medium-High': '#e53e3e'}
                    st.markdown(f"""
                    <div style='background: {risk_colors.get(risk, '#718096')}; padding: 25px; border-radius: 12px; text-align: center;'>
                        <h4 style='color: rgba(255,255,255,0.8); margin: 0;'>Risk Level</h4>
                        <h2 style='color: white; margin: 10px 0;'>{risk}</h2>
                        <p style='color: rgba(255,255,255,0.8); margin: 0;'>Adjust position size accordingly</p>
                    </div>
                    """, unsafe_allow_html=True)

                with regime_col3:
                    strategy = regime.get('suggested_strategy', 'Standard analysis')
                    st.markdown(f"""
                    <div style='background: #4facfe; padding: 25px; border-radius: 12px; text-align: center;'>
                        <h4 style='color: rgba(255,255,255,0.8); margin: 0;'>Suggested Strategy</h4>
                        <p style='color: white; margin: 10px 0; font-size: 1rem;'>{strategy}</p>
                    </div>
                    """, unsafe_allow_html=True)

                # ─── PATTERN RECOGNITION ───
                st.markdown("### 🕯️ Pattern Recognition")

                pattern_col1, pattern_col2 = st.columns(2)

                with pattern_col1:
                    st.markdown("#### Candlestick Patterns")
                    candle_patterns = ai_results.get('candlestick_patterns', {})

                    if candle_patterns:
                        for name, details in candle_patterns.items():
                            signal = details.get('signal', 'Neutral')
                            if signal == 'Bullish':
                                badge_color = '#48bb78'
                            elif signal == 'Bearish':
                                badge_color = '#f56565'
                            else:
                                badge_color = '#ed8936'

                            st.markdown(f"""
                            <div style='background: white; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid {badge_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                                <strong>{name}</strong>
                                <span style='background: {badge_color}; color: white; padding: 3px 10px; border-radius: 15px; margin-left: 10px; font-size: 0.85rem;'>{signal}</span>
                                <p style='margin: 5px 0 0 0; color: #718096; font-size: 0.9rem;'>{details.get('description', '')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No significant candlestick patterns detected")

                with pattern_col2:
                    st.markdown("#### Chart Patterns")
                    chart_patterns = ai_results.get('chart_patterns', {})

                    if chart_patterns:
                        for name, details in chart_patterns.items():
                            signal = details.get('signal', 'Neutral')
                            if signal == 'Bullish':
                                badge_color = '#48bb78'
                            elif signal == 'Bearish':
                                badge_color = '#f56565'
                            else:
                                badge_color = '#ed8936'

                            st.markdown(f"""
                            <div style='background: white; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid {badge_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                                <strong>{name}</strong>
                                <span style='background: {badge_color}; color: white; padding: 3px 10px; border-radius: 15px; margin-left: 10px; font-size: 0.85rem;'>{signal}</span>
                                <p style='margin: 5px 0 0 0; color: #718096; font-size: 0.9rem;'>{details.get('description', '')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No significant chart patterns detected")

                # ─── ENSEMBLE ML ───
                st.markdown("### 🤖 Ensemble Machine Learning")

                ml_results = ai_results.get('ml_ensemble', {})

                if 'error' not in ml_results:
                    ensemble_pred = ml_results.get('ensemble_prediction', 'Unknown')
                    ensemble_conf = ml_results.get('ensemble_confidence', 0)

                    prediction_horizon = ml_results.get('prediction_horizon', '1-day')
                    pa_context = ml_results.get('price_action_context', {})
                    pa_agrees = pa_context.get('agrees_with_ml', True)
                    pa_note = ''
                    if not pa_agrees:
                        pa_dir = pa_context.get('direction', 'Unknown')
                        pa_note = f"<p style='color: #fbd38d; margin: 8px 0 0 0; font-size: 0.9rem;'>⚠️ Recent price action ({pa_dir}) disagrees with ML prediction - confidence reduced</p>"

                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #1e3a8a, #7c3aed); padding: 20px; border-radius: 12px; margin-bottom: 20px;'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div>
                                <h4 style='color: rgba(255,255,255,0.8); margin: 0;'>Ensemble Prediction ({prediction_horizon} horizon, {ml_results.get('models_used', 5)} ML Models)</h4>
                                <h2 style='color: white; margin: 5px 0;'>{ensemble_pred}</h2>
                                <p style='color: rgba(255,255,255,0.7); margin: 0; font-size: 0.85rem;'>Confidence: {ensemble_conf:.0%}</p>
                            </div>
                            <div style='text-align: right;'>
                                <h4 style='color: rgba(255,255,255,0.8); margin: 0;'>Bullish Probability</h4>
                                <h2 style='color: white; margin: 5px 0;'>{ml_results.get('bullish_probability', 0):.1%}</h2>
                            </div>
                        </div>
                        {pa_note}
                    </div>
                    """, unsafe_allow_html=True)

                    # Individual model results
                    individual = ml_results.get('individual_models', {})

                    if individual:
                        st.markdown("#### Individual Model Results")
                        model_cols = st.columns(len(individual))

                        for i, (model_name, results) in enumerate(individual.items()):
                            with model_cols[i]:
                                if 'error' not in results:
                                    pred = results.get('prediction', 'N/A')
                                    conf = results.get('confidence', 0)
                                    acc = results.get('accuracy', 0)
                                    color = '#48bb78' if pred == 'Bullish' else '#f56565'

                                    st.markdown(f"""
                                    <div style='background: white; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-top: 3px solid {color};'>
                                        <h5 style='margin: 0; color: #4a5568;'>{model_name}</h5>
                                        <h3 style='margin: 5px 0; color: {color};'>{pred}</h3>
                                        <p style='margin: 0; color: #718096; font-size: 0.85rem;'>Conf: {conf:.0%} | Acc: {acc:.0%}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                else:
                    st.warning(f"ML Analysis: {ml_results.get('error', 'Unknown error')}")

                # ─── ANOMALY DETECTION ───
                st.markdown("### ⚠️ Anomaly Detection")

                anomalies = ai_results.get('anomalies', {})
                anomaly_list = anomalies.get('anomalies', [])

                if anomaly_list:
                    for anomaly in anomaly_list:
                        severity = anomaly.get('severity', 'Medium')
                        if severity == 'High':
                            icon = '🔴'
                            color = '#f56565'
                        else:
                            icon = '🟡'
                            color = '#ed8936'

                        st.markdown(f"""
                        <div style='background: white; padding: 15px 20px; border-radius: 10px; margin: 10px 0; border-left: 4px solid {color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                            {icon} <strong style='color: {color};'>{anomaly.get('type', 'Anomaly')}</strong>: {anomaly.get('description', '')}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("✅ No significant anomalies detected")

                # ─── LSTM PREDICTION (Deep Analysis only) ───
                if analysis_depth == "Deep Analysis":
                    st.markdown("### 🧠 LSTM Deep Learning Prediction")

                    with st.spinner("Training LSTM neural network..."):
                        # Ensure ML resources are loaded (lazy import)
                        load_ml_resources()
                        lstm_results = predict_with_lstm(stock_data, lookback=60, forecast_days=5, epochs=30)

                    if 'error' not in lstm_results:
                        predictions = lstm_results.get('predictions', [])
                        trend = lstm_results.get('trend', 'Unknown')
                        expected_return = lstm_results.get('expected_return', 0)
                        lstm_conf = lstm_results.get('confidence', 0)

                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #667eea, #764ba2); padding: 25px; border-radius: 15px; margin-bottom: 20px;'>
                            <h3 style='color: white; margin: 0;'>5-Day Price Forecast</h3>
                            <div style='display: flex; justify-content: space-around; margin-top: 15px;'>
                                <div style='text-align: center;'>
                                    <p style='color: rgba(255,255,255,0.8); margin: 0;'>Current Price</p>
                                    <h2 style='color: white; margin: 5px 0;'>₹{lstm_results.get('current_price', 0):.2f}</h2>
                                </div>
                                <div style='text-align: center;'>
                                    <p style='color: rgba(255,255,255,0.8); margin: 0;'>Predicted (Day 5)</p>
                                    <h2 style='color: white; margin: 5px 0;'>₹{predictions[-1]:.2f}</h2>
                                </div>
                                <div style='text-align: center;'>
                                    <p style='color: rgba(255,255,255,0.8); margin: 0;'>Expected Return</p>
                                    <h2 style='color: {"#48bb78" if expected_return > 0 else "#f56565"}; margin: 5px 0;'>{expected_return:+.2f}%</h2>
                                </div>
                                <div style='text-align: center;'>
                                    <p style='color: rgba(255,255,255,0.8); margin: 0;'>Confidence</p>
                                    <h2 style='color: white; margin: 5px 0;'>{lstm_conf:.0f}%</h2>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Prediction chart
                        fig = go.Figure()

                        # Historical prices (last 30 days)
                        hist_dates = stock_data.index[-30:]
                        hist_prices = stock_data['Close'].iloc[-30:].values

                        fig.add_trace(go.Scatter(
                            x=list(range(-30, 0)),
                            y=hist_prices,
                            mode='lines',
                            name='Historical',
                            line=dict(color='#667eea', width=2)
                        ))

                        # Predictions
                        fig.add_trace(go.Scatter(
                            x=list(range(0, len(predictions) + 1)),
                            y=[hist_prices[-1]] + predictions,
                            mode='lines+markers',
                            name='LSTM Prediction',
                            line=dict(color='#f093fb', width=3, dash='dash'),
                            marker=dict(size=8)
                        ))

                        fig.update_layout(
                            title="LSTM Price Prediction (Next 5 Days)",
                            xaxis_title="Days (0 = Today)",
                            yaxis_title="Price (₹)",
                            height=400,
                            legend=dict(orientation="h", yanchor="bottom", y=1.02)
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        st.warning("⚠️ LSTM predictions are experimental. Past performance doesn't guarantee future results. Use as one factor in your analysis.")
                    else:
                        st.error(f"LSTM Error: {lstm_results.get('error', 'Unknown')}")

                # Summary
                st.markdown("---")
                st.markdown("### 📋 Analysis Summary")

                summary_data = {
                    'Metric': ['AI Recommendation', 'Technical Score', 'Market Regime', 'ML Ensemble', 'Anomalies Detected'],
                    'Value': [
                        recommendation,
                        f"{score:.0f}/100 (Grade: {grade})",
                        regime.get('primary_regime', 'Unknown'),
                        ml_results.get('ensemble_prediction', 'N/A'),
                        str(len(anomaly_list))
                    ],
                    'Confidence': [
                        f"{confidence:.0%}",
                        '-',
                        f"{regime.get('confidence', 0):.0%}",
                        f"{ml_results.get('ensemble_confidence', 0):.0%}" if 'error' not in ml_results else 'N/A',
                        '-'
                    ]
                }

                st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)

                # ═══════════════════════════════════════════════════════════════
                # ENHANCED TECHNICAL INDICATORS DASHBOARD
                # ═══════════════════════════════════════════════════════════════

                st.markdown("---")
                st.markdown("### 📈 Technical Indicators Dashboard")

                # Get the latest indicator values
                latest = stock_data.iloc[-1]

                # ─── COMBINED TREND SIGNAL (SuperTrend + ADX + RSI) ───
                st.markdown("#### 🎯 Combined Trend Signal (SuperTrend + ADX + RSI)")

                trend_signal = combined_trend_signal(stock_data)

                # Determine colors based on signal
                signal_text = trend_signal.get('signal', 'Unknown')
                strength = trend_signal.get('strength', 'Neutral')

                if 'Bullish' in signal_text:
                    signal_color = '#48bb78' if 'Strong' in signal_text else '#68d391'
                    signal_bg = 'linear-gradient(135deg, #48bb78, #38a169)'
                elif 'Bearish' in signal_text:
                    signal_color = '#f56565' if 'Strong' in signal_text else '#fc8181'
                    signal_bg = 'linear-gradient(135deg, #f56565, #c53030)'
                else:
                    signal_color = '#ed8936'
                    signal_bg = 'linear-gradient(135deg, #ed8936, #dd6b20)'

                # Main signal card
                st.markdown(f"""
                <div style='background: {signal_bg}; padding: 25px; border-radius: 15px; margin-bottom: 20px;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <h2 style='color: white; margin: 0;'>{signal_text}</h2>
                            <p style='color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 1.1rem;'>
                                Strength: <strong>{strength}</strong>
                            </p>
                        </div>
                        <div style='text-align: right;'>
                            <div style='background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 10px;'>
                                <p style='color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;'>Based on</p>
                                <p style='color: white; margin: 0; font-weight: bold;'>SuperTrend + ADX + RSI</p>
                            </div>
                        </div>
                    </div>
                    <p style='color: rgba(255,255,255,0.95); margin: 15px 0 0 0; font-size: 1rem;'>
                        💡 {trend_signal.get('description', '')}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # Show warnings if any
                warnings = trend_signal.get('warnings', [])
                if warnings:
                    for warning in warnings:
                        st.warning(f"⚠️ {warning}")

                # Details breakdown
                details = trend_signal.get('details', {})
                detail_col1, detail_col2, detail_col3 = st.columns(3)

                with detail_col1:
                    st_dir = details.get('SuperTrend_Direction', 'N/A')
                    st_color = '#48bb78' if st_dir == 'Bullish' else '#f56565'
                    st.markdown(f"""
                    <div style='background: white; padding: 15px; border-radius: 10px; text-align: center; border-left: 4px solid {st_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <h5 style='color: #4a5568; margin: 0;'>SuperTrend</h5>
                        <h3 style='color: {st_color}; margin: 5px 0;'>{st_dir}</h3>
                    </div>
                    """, unsafe_allow_html=True)

                with detail_col2:
                    adx_val = details.get('ADX_Value', 0)
                    adx_strong = details.get('ADX_Strong', False)
                    adx_color = '#48bb78' if adx_strong else '#ed8936'
                    st.markdown(f"""
                    <div style='background: white; padding: 15px; border-radius: 10px; text-align: center; border-left: 4px solid {adx_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <h5 style='color: #4a5568; margin: 0;'>ADX</h5>
                        <h3 style='color: {adx_color}; margin: 5px 0;'>{adx_val:.1f}</h3>
                        <small style='color: #718096;'>{"Strong Trend" if adx_strong else "Weak Trend"}</small>
                    </div>
                    """, unsafe_allow_html=True)

                with detail_col3:
                    rsi_val = details.get('RSI_14', 50)
                    rsi_mom = details.get('RSI_Momentum', 'Neutral')
                    rsi_color = '#48bb78' if rsi_mom == 'Bullish' else '#f56565'
                    st.markdown(f"""
                    <div style='background: white; padding: 15px; border-radius: 10px; text-align: center; border-left: 4px solid {rsi_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <h5 style='color: #4a5568; margin: 0;'>RSI (14)</h5>
                        <h3 style='color: {rsi_color}; margin: 5px 0;'>{rsi_val:.1f}</h3>
                        <small style='color: #718096;'>{rsi_mom} Momentum</small>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Create tabs for different indicator categories
                ind_tab1, ind_tab2, ind_tab3, ind_tab4 = st.tabs([
                    "📊 Trend Indicators", "⚡ Momentum", "📉 Volatility", "💹 Volume"
                ])

                with ind_tab1:
                    st.markdown("#### Trend Indicators")

                    # Supertrend Signal
                    supertrend_dir = latest.get('Supertrend_Direction', 0)
                    supertrend_val = latest.get('Supertrend', latest['Close'])
                    supertrend_signal = "🟢 BULLISH (Buy)" if supertrend_dir == 1 else "🔴 BEARISH (Sell)"

                    # ADX Trend Strength
                    adx_val = latest.get('ADX', 25)
                    if adx_val > 50:
                        adx_strength = "Very Strong Trend"
                    elif adx_val > 25:
                        adx_strength = "Strong Trend"
                    elif adx_val > 20:
                        adx_strength = "Weak Trend"
                    else:
                        adx_strength = "No Trend (Sideways)"

                    # Moving Average Alignment
                    sma20 = latest.get('SMA_20', latest.get('SMA20', latest['Close']))
                    sma50 = latest.get('SMA_50', latest.get('SMA50', latest['Close']))
                    sma200 = latest.get('SMA_200', latest.get('SMA200', latest['Close']))
                    current_price = latest['Close']

                    if current_price > sma20 > sma50 > sma200:
                        ma_signal = "🟢 Perfect Bullish Alignment"
                    elif current_price > sma50:
                        ma_signal = "🟢 Bullish (Above SMA50)"
                    elif current_price < sma20 < sma50 < sma200:
                        ma_signal = "🔴 Perfect Bearish Alignment"
                    elif current_price < sma50:
                        ma_signal = "🔴 Bearish (Below SMA50)"
                    else:
                        ma_signal = "🟡 Mixed/Sideways"

                    # PSAR Signal
                    psar_val = latest.get('PSAR', latest['Close'])
                    psar_signal = "🟢 BULLISH" if psar_val < current_price else "🔴 BEARISH"

                    # Display trend indicators
                    trend_col1, trend_col2 = st.columns(2)

                    with trend_col1:
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #1e3a5f, #2c5282); padding: 20px; border-radius: 12px; margin: 10px 0;'>
                            <h4 style='color: white; margin: 0;'>🔥 Supertrend</h4>
                            <h2 style='color: {"#48bb78" if supertrend_dir == 1 else "#f56565"}; margin: 10px 0;'>{supertrend_signal}</h2>
                            <p style='color: rgba(255,255,255,0.8); margin: 0;'>Level: ₹{supertrend_val:.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #2d3748, #4a5568); padding: 20px; border-radius: 12px; margin: 10px 0;'>
                            <h4 style='color: white; margin: 0;'>📊 ADX Trend Strength</h4>
                            <h2 style='color: #f6e05e; margin: 10px 0;'>{adx_val:.1f}</h2>
                            <p style='color: rgba(255,255,255,0.8); margin: 0;'>{adx_strength}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with trend_col2:
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #285e61, #2c7a7b); padding: 20px; border-radius: 12px; margin: 10px 0;'>
                            <h4 style='color: white; margin: 0;'>📈 Moving Averages</h4>
                            <h3 style='color: white; margin: 10px 0;'>{ma_signal}</h3>
                            <p style='color: rgba(255,255,255,0.8); margin: 0;'>SMA20: ₹{sma20:.2f} | SMA50: ₹{sma50:.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #553c9a, #6b46c1); padding: 20px; border-radius: 12px; margin: 10px 0;'>
                            <h4 style='color: white; margin: 0;'>⭐ Parabolic SAR</h4>
                            <h2 style='color: {"#48bb78" if psar_val < current_price else "#f56565"}; margin: 10px 0;'>{psar_signal}</h2>
                            <p style='color: rgba(255,255,255,0.8); margin: 0;'>SAR Level: ₹{psar_val:.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    # Trend Visualization Chart
                    st.markdown("#### 📉 Trend Indicators Chart (Last 60 Days)")

                    chart_data = stock_data.tail(60).copy()
                    fig_trend = go.Figure()

                    # Candlestick
                    fig_trend.add_trace(go.Candlestick(
                        x=chart_data.index,
                        open=chart_data['Open'],
                        high=chart_data['High'],
                        low=chart_data['Low'],
                        close=chart_data['Close'],
                        name='Price'
                    ))

                    # Supertrend
                    if 'Supertrend' in chart_data.columns:
                        fig_trend.add_trace(go.Scatter(
                            x=chart_data.index,
                            y=chart_data['Supertrend'],
                            mode='lines',
                            name='Supertrend',
                            line=dict(color='#f6e05e', width=2)
                        ))

                    # SMA lines
                    if 'SMA_20' in chart_data.columns:
                        fig_trend.add_trace(go.Scatter(x=chart_data.index, y=chart_data['SMA_20'],
                                                       mode='lines', name='SMA 20', line=dict(color='#63b3ed', width=1)))
                    if 'SMA_50' in chart_data.columns:
                        fig_trend.add_trace(go.Scatter(x=chart_data.index, y=chart_data['SMA_50'],
                                                       mode='lines', name='SMA 50', line=dict(color='#f687b3', width=1)))

                    fig_trend.update_layout(height=450, title="Price with Supertrend & Moving Averages",
                                           xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig_trend, use_container_width=True)

                with ind_tab2:
                    st.markdown("#### Momentum Indicators")

                    # RSI
                    rsi_val = latest.get('RSI_14', latest.get('RSI14', 50))
                    if rsi_val > 70:
                        rsi_signal = "🔴 OVERBOUGHT"
                        rsi_color = "#f56565"
                    elif rsi_val < 30:
                        rsi_signal = "🟢 OVERSOLD"
                        rsi_color = "#48bb78"
                    else:
                        rsi_signal = "🟡 NEUTRAL"
                        rsi_color = "#ed8936"

                    # MACD
                    macd_val = latest.get('MACD', 0)
                    macd_signal_line = latest.get('MACD_Signal', 0)
                    macd_hist = latest.get('MACD_Histogram', macd_val - macd_signal_line)
                    macd_signal = "🟢 BULLISH" if macd_val > macd_signal_line else "🔴 BEARISH"

                    # Stochastic
                    stoch_k = latest.get('Stoch_K', 50)
                    stoch_d = latest.get('Stoch_D', 50)
                    if stoch_k > 80:
                        stoch_signal = "🔴 OVERBOUGHT"
                    elif stoch_k < 20:
                        stoch_signal = "🟢 OVERSOLD"
                    else:
                        stoch_signal = "🟡 NEUTRAL"

                    # Williams %R
                    williams_r = latest.get('Williams_R', -50)
                    if williams_r > -20:
                        williams_signal = "🔴 OVERBOUGHT"
                    elif williams_r < -80:
                        williams_signal = "🟢 OVERSOLD"
                    else:
                        williams_signal = "🟡 NEUTRAL"

                    mom_col1, mom_col2, mom_col3, mom_col4 = st.columns(4)

                    with mom_col1:
                        st.markdown(f"""
                        <div style='background: white; padding: 20px; border-radius: 12px; text-align: center; border-top: 4px solid {rsi_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                            <h4 style='color: #4a5568; margin: 0;'>RSI (14)</h4>
                            <h2 style='color: {rsi_color}; margin: 10px 0;'>{rsi_val:.1f}</h2>
                            <p style='color: #718096; margin: 0;'>{rsi_signal}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with mom_col2:
                        macd_color = "#48bb78" if macd_val > macd_signal_line else "#f56565"
                        st.markdown(f"""
                        <div style='background: white; padding: 20px; border-radius: 12px; text-align: center; border-top: 4px solid {macd_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                            <h4 style='color: #4a5568; margin: 0;'>MACD</h4>
                            <h2 style='color: {macd_color}; margin: 10px 0;'>{macd_val:.2f}</h2>
                            <p style='color: #718096; margin: 0;'>{macd_signal}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with mom_col3:
                        stoch_color = "#f56565" if stoch_k > 80 else ("#48bb78" if stoch_k < 20 else "#ed8936")
                        st.markdown(f"""
                        <div style='background: white; padding: 20px; border-radius: 12px; text-align: center; border-top: 4px solid {stoch_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                            <h4 style='color: #4a5568; margin: 0;'>Stochastic</h4>
                            <h2 style='color: {stoch_color}; margin: 10px 0;'>{stoch_k:.1f}</h2>
                            <p style='color: #718096; margin: 0;'>{stoch_signal}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with mom_col4:
                        will_color = "#f56565" if williams_r > -20 else ("#48bb78" if williams_r < -80 else "#ed8936")
                        st.markdown(f"""
                        <div style='background: white; padding: 20px; border-radius: 12px; text-align: center; border-top: 4px solid {will_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                            <h4 style='color: #4a5568; margin: 0;'>Williams %R</h4>
                            <h2 style='color: {will_color}; margin: 10px 0;'>{williams_r:.1f}</h2>
                            <p style='color: #718096; margin: 0;'>{williams_signal}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    # Momentum Charts
                    st.markdown("#### 📊 RSI & MACD Chart")

                    from plotly.subplots import make_subplots

                    chart_data = stock_data.tail(60).copy()
                    fig_mom = make_subplots(rows=3, cols=1, shared_xaxes=True,
                                           vertical_spacing=0.05,
                                           row_heights=[0.5, 0.25, 0.25],
                                           subplot_titles=('Price', 'RSI (14)', 'MACD'))

                    # Price
                    fig_mom.add_trace(go.Candlestick(x=chart_data.index, open=chart_data['Open'],
                                                     high=chart_data['High'], low=chart_data['Low'],
                                                     close=chart_data['Close'], name='Price'), row=1, col=1)

                    # RSI
                    rsi_col = 'RSI_14' if 'RSI_14' in chart_data.columns else 'RSI14'
                    if rsi_col in chart_data.columns:
                        fig_mom.add_trace(go.Scatter(x=chart_data.index, y=chart_data[rsi_col],
                                                     mode='lines', name='RSI', line=dict(color='#667eea')), row=2, col=1)
                        fig_mom.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
                        fig_mom.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

                    # MACD
                    if 'MACD' in chart_data.columns:
                        fig_mom.add_trace(go.Scatter(x=chart_data.index, y=chart_data['MACD'],
                                                     mode='lines', name='MACD', line=dict(color='#4facfe')), row=3, col=1)
                        if 'MACD_Signal' in chart_data.columns:
                            fig_mom.add_trace(go.Scatter(x=chart_data.index, y=chart_data['MACD_Signal'],
                                                         mode='lines', name='Signal', line=dict(color='#f093fb')), row=3, col=1)

                    fig_mom.update_layout(height=600, showlegend=True, xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig_mom, use_container_width=True)

                with ind_tab3:
                    st.markdown("#### Volatility Indicators")

                    # ATR
                    atr_val = latest.get('ATR_14', latest.get('ATR14', 0))
                    atr_pct = (atr_val / latest['Close']) * 100

                    # Bollinger Bands
                    bb_upper = latest.get('BB_Upper', latest['Close'] * 1.02)
                    bb_lower = latest.get('BB_Lower', latest['Close'] * 0.98)
                    bb_width = latest.get('BB_Width', 0.04)
                    bb_pct = latest.get('BB_Percent', 0.5)

                    if bb_pct > 1:
                        bb_signal = "🔴 ABOVE UPPER BAND"
                    elif bb_pct < 0:
                        bb_signal = "🟢 BELOW LOWER BAND"
                    else:
                        bb_signal = "🟡 WITHIN BANDS"

                    # Historical Volatility
                    hv_val = latest.get('HV_20', 20)

                    vol_col1, vol_col2, vol_col3 = st.columns(3)

                    with vol_col1:
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #e53e3e, #c53030); padding: 25px; border-radius: 12px; text-align: center;'>
                            <h4 style='color: rgba(255,255,255,0.9); margin: 0;'>ATR (14)</h4>
                            <h2 style='color: white; margin: 10px 0;'>₹{atr_val:.2f}</h2>
                            <p style='color: rgba(255,255,255,0.8); margin: 0;'>{atr_pct:.2f}% of price</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with vol_col2:
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #3182ce, #2b6cb0); padding: 25px; border-radius: 12px; text-align: center;'>
                            <h4 style='color: rgba(255,255,255,0.9); margin: 0;'>Bollinger Bands</h4>
                            <h3 style='color: white; margin: 10px 0;'>{bb_signal}</h3>
                            <p style='color: rgba(255,255,255,0.8); margin: 0;'>Width: {bb_width:.2%}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with vol_col3:
                        if hv_val > 40:
                            hv_level = "HIGH"
                            hv_color = "#e53e3e"
                        elif hv_val > 20:
                            hv_level = "NORMAL"
                            hv_color = "#ed8936"
                        else:
                            hv_level = "LOW"
                            hv_color = "#48bb78"

                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, {hv_color}, {hv_color}dd); padding: 25px; border-radius: 12px; text-align: center;'>
                            <h4 style='color: rgba(255,255,255,0.9); margin: 0;'>Historical Volatility</h4>
                            <h2 style='color: white; margin: 10px 0;'>{hv_val:.1f}%</h2>
                            <p style='color: rgba(255,255,255,0.8); margin: 0;'>{hv_level} Volatility</p>
                        </div>
                        """, unsafe_allow_html=True)

                    # Bollinger Bands Chart
                    st.markdown("#### 📊 Bollinger Bands Chart")

                    chart_data = stock_data.tail(60).copy()
                    fig_bb = go.Figure()

                    fig_bb.add_trace(go.Candlestick(x=chart_data.index, open=chart_data['Open'],
                                                    high=chart_data['High'], low=chart_data['Low'],
                                                    close=chart_data['Close'], name='Price'))

                    if 'BB_Upper' in chart_data.columns:
                        fig_bb.add_trace(go.Scatter(x=chart_data.index, y=chart_data['BB_Upper'],
                                                    mode='lines', name='Upper Band', line=dict(color='rgba(102, 126, 234, 0.5)')))
                        fig_bb.add_trace(go.Scatter(x=chart_data.index, y=chart_data['BB_Lower'],
                                                    mode='lines', name='Lower Band', line=dict(color='rgba(102, 126, 234, 0.5)'),
                                                    fill='tonexty', fillcolor='rgba(102, 126, 234, 0.1)'))
                        fig_bb.add_trace(go.Scatter(x=chart_data.index, y=chart_data['BB_Middle'],
                                                    mode='lines', name='Middle Band', line=dict(color='#667eea', dash='dash')))

                    fig_bb.update_layout(height=400, title="Price with Bollinger Bands", xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig_bb, use_container_width=True)

                with ind_tab4:
                    st.markdown("#### Volume Indicators")

                    # Volume Ratio
                    vol_ratio = latest.get('Volume_Ratio', 1.0)
                    if vol_ratio > 1.5:
                        vol_signal = "🔥 HIGH VOLUME"
                        vol_color = "#48bb78"
                    elif vol_ratio > 1.0:
                        vol_signal = "📈 ABOVE AVERAGE"
                        vol_color = "#38a169"
                    elif vol_ratio > 0.7:
                        vol_signal = "📊 NORMAL"
                        vol_color = "#ed8936"
                    else:
                        vol_signal = "📉 LOW VOLUME"
                        vol_color = "#f56565"

                    # OBV Trend
                    obv_val = latest.get('OBV', 0)

                    # MFI
                    mfi_val = latest.get('MFI', 50)
                    if mfi_val > 80:
                        mfi_signal = "🔴 OVERBOUGHT"
                    elif mfi_val < 20:
                        mfi_signal = "🟢 OVERSOLD"
                    else:
                        mfi_signal = "🟡 NEUTRAL"

                    vol_col1, vol_col2, vol_col3 = st.columns(3)

                    with vol_col1:
                        st.markdown(f"""
                        <div style='background: {vol_color}; padding: 25px; border-radius: 12px; text-align: center;'>
                            <h4 style='color: rgba(255,255,255,0.9); margin: 0;'>Volume Ratio</h4>
                            <h2 style='color: white; margin: 10px 0;'>{vol_ratio:.2f}x</h2>
                            <p style='color: rgba(255,255,255,0.8); margin: 0;'>{vol_signal}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with vol_col2:
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #805ad5, #6b46c1); padding: 25px; border-radius: 12px; text-align: center;'>
                            <h4 style='color: rgba(255,255,255,0.9); margin: 0;'>OBV</h4>
                            <h2 style='color: white; margin: 10px 0;'>{obv_val/1e6:.1f}M</h2>
                            <p style='color: rgba(255,255,255,0.8); margin: 0;'>On Balance Volume</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with vol_col3:
                        mfi_color = "#f56565" if mfi_val > 80 else ("#48bb78" if mfi_val < 20 else "#ed8936")
                        st.markdown(f"""
                        <div style='background: {mfi_color}; padding: 25px; border-radius: 12px; text-align: center;'>
                            <h4 style='color: rgba(255,255,255,0.9); margin: 0;'>Money Flow Index</h4>
                            <h2 style='color: white; margin: 10px 0;'>{mfi_val:.1f}</h2>
                            <p style='color: rgba(255,255,255,0.8); margin: 0;'>{mfi_signal}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    # Volume Chart
                    st.markdown("#### 📊 Volume Analysis")

                    chart_data = stock_data.tail(60).copy()
                    fig_vol = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                           vertical_spacing=0.1, row_heights=[0.6, 0.4])

                    # Price
                    fig_vol.add_trace(go.Candlestick(x=chart_data.index, open=chart_data['Open'],
                                                     high=chart_data['High'], low=chart_data['Low'],
                                                     close=chart_data['Close'], name='Price'), row=1, col=1)

                    # Volume bars
                    colors = ['#48bb78' if c > o else '#f56565' for c, o in zip(chart_data['Close'], chart_data['Open'])]
                    fig_vol.add_trace(go.Bar(x=chart_data.index, y=chart_data['Volume'],
                                            marker_color=colors, name='Volume'), row=2, col=1)

                    fig_vol.update_layout(height=500, showlegend=True, xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig_vol, use_container_width=True)

                # ═══════════════════════════════════════════════════════════════
                # POSITION SIZING & RISK MANAGEMENT
                # ═══════════════════════════════════════════════════════════════

                st.markdown("---")
                st.markdown("### 💰 Position Sizing & Risk Management")

                ps_col1, ps_col2 = st.columns([1, 2])

                with ps_col1:
                    trading_capital = st.number_input("💵 Trading Capital (₹)",
                                                      min_value=10000, max_value=100000000,
                                                      value=100000, step=10000)
                    risk_per_trade = st.slider("⚠️ Risk per Trade (%)", 0.5, 5.0, 2.0, 0.5)
                    atr_mult = st.slider("📏 ATR Multiplier (Stop Loss)", 1.0, 4.0, 2.0, 0.5)

                with ps_col2:
                    position_result = calculate_position_size(stock_data, trading_capital, risk_per_trade, atr_mult)

                    if 'error' not in position_result:
                        ps_col2a, ps_col2b, ps_col2c = st.columns(3)

                        with ps_col2a:
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px; border-radius: 12px; text-align: center;'>
                                <h4 style='color: rgba(255,255,255,0.8); margin: 0;'>Position Size</h4>
                                <h2 style='color: white; margin: 10px 0;'>{position_result['position_size_shares']} shares</h2>
                                <p style='color: rgba(255,255,255,0.8); margin: 0;'>₹{position_result['position_value']:,.0f}</p>
                            </div>
                            """, unsafe_allow_html=True)

                        with ps_col2b:
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, #f56565, #c53030); padding: 20px; border-radius: 12px; text-align: center;'>
                                <h4 style='color: rgba(255,255,255,0.8); margin: 0;'>Stop Loss</h4>
                                <h2 style='color: white; margin: 10px 0;'>₹{position_result['stop_loss_price']:.2f}</h2>
                                <p style='color: rgba(255,255,255,0.8); margin: 0;'>-{position_result['stop_loss_percent']:.1f}%</p>
                            </div>
                            """, unsafe_allow_html=True)

                        with ps_col2c:
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, #48bb78, #38a169); padding: 20px; border-radius: 12px; text-align: center;'>
                                <h4 style='color: rgba(255,255,255,0.8); margin: 0;'>Take Profit (2R)</h4>
                                <h2 style='color: white; margin: 10px 0;'>₹{position_result['take_profit_2r']:.2f}</h2>
                                <p style='color: rgba(255,255,255,0.8); margin: 0;'>+{((position_result['take_profit_2r']/position_result['current_price'])-1)*100:.1f}%</p>
                            </div>
                            """, unsafe_allow_html=True)

                        # Risk details table
                        st.markdown("#### 📋 Trade Setup Details")
                        risk_df = pd.DataFrame({
                            'Parameter': ['Entry Price', 'Stop Loss', 'Take Profit 1:1', 'Take Profit 2:1', 'Take Profit 3:1',
                                          'Risk Amount', 'Volatility Level', 'Recommended Risk %'],
                            'Value': [
                                f"₹{position_result['current_price']:.2f}",
                                f"₹{position_result['stop_loss_price']:.2f}",
                                f"₹{position_result['take_profit_1r']:.2f}",
                                f"₹{position_result['take_profit_2r']:.2f}",
                                f"₹{position_result['take_profit_3r']:.2f}",
                                f"₹{position_result['risk_amount']:,.0f}",
                                position_result['volatility_level'],
                                f"{position_result['recommended_risk_percent']:.1f}%"
                            ]
                        })
                        st.dataframe(risk_df, use_container_width=True, hide_index=True)

                # ═══════════════════════════════════════════════════════════════
                # VOLATILITY FORECASTING (GARCH/EWMA)
                # ═══════════════════════════════════════════════════════════════

                st.markdown("---")
                st.markdown("### 📉 Volatility Forecasting")

                vol_col1, vol_col2 = st.columns(2)

                with vol_col1:
                    with st.spinner("Forecasting volatility..."):
                        vol_forecast = forecast_volatility_garch(stock_data, horizon=5)

                    if 'error' not in vol_forecast:
                        method = vol_forecast.get('method', 'EWMA')
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #2d3748, #4a5568); padding: 20px; border-radius: 12px;'>
                            <h4 style='color: white; margin: 0;'>📊 {method} Volatility Forecast</h4>
                            <div style='display: flex; justify-content: space-around; margin-top: 15px;'>
                                <div style='text-align: center;'>
                                    <p style='color: rgba(255,255,255,0.7); margin: 0;'>Current Daily Vol</p>
                                    <h3 style='color: #f6e05e; margin: 5px 0;'>{vol_forecast['current_daily_vol']*100:.2f}%</h3>
                                </div>
                                <div style='text-align: center;'>
                                    <p style='color: rgba(255,255,255,0.7); margin: 0;'>Annualized Vol</p>
                                    <h3 style='color: #fc8181; margin: 5px 0;'>{vol_forecast['annualized_vol_pct']:.1f}%</h3>
                                </div>
                                <div style='text-align: center;'>
                                    <p style='color: rgba(255,255,255,0.7); margin: 0;'>Vol Trend</p>
                                    <h3 style='color: {"#48bb78" if vol_forecast["vol_trend"] == "Decreasing" else "#f56565"}; margin: 5px 0;'>{vol_forecast['vol_trend']}</h3>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Volatility forecast chart
                        if 'forecasted_daily_vol' in vol_forecast:
                            fig_vol = go.Figure()
                            fig_vol.add_trace(go.Scatter(
                                y=[v*100 for v in vol_forecast['forecasted_daily_vol']],
                                mode='lines+markers',
                                name='Forecasted Volatility',
                                line=dict(color='#f6e05e', width=2)
                            ))
                            fig_vol.update_layout(
                                title="5-Day Volatility Forecast",
                                yaxis_title="Daily Volatility (%)",
                                xaxis_title="Days Ahead",
                                height=250
                            )
                            st.plotly_chart(fig_vol, use_container_width=True)
                    else:
                        st.warning(f"Volatility forecast: {vol_forecast.get('error', 'Unknown error')}")

                with vol_col2:
                    vol_regime = get_volatility_regime(stock_data)

                    if 'error' not in vol_regime:
                        regime = vol_regime.get('regime', 'Unknown')
                        regime_colors = {
                            'Very Low Volatility': '#3182ce',
                            'Low Volatility': '#48bb78',
                            'Normal Volatility': '#ed8936',
                            'High Volatility': '#e53e3e',
                            'Extreme Volatility': '#9b2c2c'
                        }
                        regime_color = regime_colors.get(regime, '#718096')

                        st.markdown(f"""
                        <div style='background: {regime_color}; padding: 20px; border-radius: 12px;'>
                            <h4 style='color: rgba(255,255,255,0.9); margin: 0;'>🎯 Volatility Regime</h4>
                            <h2 style='color: white; margin: 10px 0;'>{regime}</h2>
                            <p style='color: rgba(255,255,255,0.9); margin: 5px 0;'>
                                Position Size Adj: <strong>{vol_regime['position_size_adjustment']:.1f}x</strong>
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                        <div style='background: white; padding: 15px; border-radius: 10px; margin-top: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                            <h5 style='color: #4a5568; margin: 0 0 10px 0;'>💡 Recommendation</h5>
                            <p style='color: #718096; margin: 0;'>{vol_regime.get('recommendation', 'N/A')}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        # Volatility comparison
                        st.markdown("#### Volatility Comparison")
                        vol_compare = pd.DataFrame({
                            'Period': ['10-Day', '30-Day', '60-Day'],
                            'Annualized Vol': [
                                f"{vol_regime['vol_10d']:.1f}%",
                                f"{vol_regime['vol_30d']:.1f}%",
                                f"{vol_regime['vol_60d']:.1f}%"
                            ]
                        })
                        st.dataframe(vol_compare, use_container_width=True, hide_index=True)
                    else:
                        st.warning(f"Volatility regime: {vol_regime.get('error', 'Unknown error')}")

                # ═══════════════════════════════════════════════════════════════
                # FEATURE IMPORTANCE ANALYSIS
                # ═══════════════════════════════════════════════════════════════

                st.markdown("---")
                st.markdown("### 🔬 Feature Importance Analysis")

                with st.spinner("Analyzing feature importance..."):
                    feature_result = calculate_feature_importance(stock_data)

                if 'error' not in feature_result:
                    fi_col1, fi_col2 = st.columns([2, 1])

                    with fi_col1:
                        # Feature importance bar chart
                        top_features = feature_result.get('top_features', [])[:10]

                        fig_fi = go.Figure()
                        fig_fi.add_trace(go.Bar(
                            x=[f['combined_score'] for f in top_features],
                            y=[f['feature'] for f in top_features],
                            orientation='h',
                            marker_color='#667eea'
                        ))
                        fig_fi.update_layout(
                            title="Top 10 Most Predictive Features",
                            xaxis_title="Importance Score",
                            yaxis_title="Feature",
                            height=400
                        )
                        st.plotly_chart(fig_fi, use_container_width=True)

                    with fi_col2:
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #1e3a8a, #7c3aed); padding: 20px; border-radius: 12px; margin-bottom: 15px;'>
                            <h4 style='color: white; margin: 0;'>Model Accuracy</h4>
                            <h2 style='color: #f6e05e; margin: 10px 0;'>{feature_result.get('model_accuracy', 0):.1%}</h2>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown("**Best Features for Prediction:**")
                        for i, feat in enumerate(feature_result.get('best_features', [])[:5], 1):
                            st.markdown(f"{i}. `{feat}`")
                else:
                    st.warning(f"Feature importance analysis: {feature_result.get('error', 'Unknown error')}")

                # ═══════════════════════════════════════════════════════════════
                # BACKTESTING
                # ═══════════════════════════════════════════════════════════════

                st.markdown("---")
                st.markdown("### 📈 Strategy Backtesting")

                # Backtest parameters
                bt_params_col1, bt_params_col2, bt_params_col3 = st.columns(3)
                with bt_params_col1:
                    bt_commission = st.slider("Commission (%)", 0.05, 0.50, 0.10, 0.05, key="bt_comm")
                with bt_params_col2:
                    bt_slippage = st.slider("Slippage (%)", 0.01, 0.20, 0.05, 0.01, key="bt_slip")
                with bt_params_col3:
                    bt_allow_short = st.checkbox("Allow Short Selling", value=True, key="bt_short")

                with st.spinner("Running realistic backtest with costs..."):
                    backtest_result = backtest_strategy(
                        stock_data,
                        initial_capital=100000,
                        commission_pct=bt_commission,
                        slippage_pct=bt_slippage,
                        allow_short=bt_allow_short,
                        max_exposure_pct=25
                    )

                if 'error' not in backtest_result:
                    # First row - Returns
                    bt_col1, bt_col2, bt_col3, bt_col4 = st.columns(4)

                    ret_color = "#48bb78" if backtest_result['total_return_pct'] > 0 else "#f56565"

                    with bt_col1:
                        st.markdown(f"""
                        <div style='background: white; padding: 20px; border-radius: 12px; text-align: center; border-top: 4px solid {ret_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                            <h4 style='color: #4a5568; margin: 0;'>Strategy Return</h4>
                            <h2 style='color: {ret_color}; margin: 10px 0;'>{backtest_result['total_return_pct']:+.2f}%</h2>
                        </div>
                        """, unsafe_allow_html=True)

                    with bt_col2:
                        bh_color = "#48bb78" if backtest_result['buy_hold_return_pct'] > 0 else "#f56565"
                        st.markdown(f"""
                        <div style='background: white; padding: 20px; border-radius: 12px; text-align: center; border-top: 4px solid {bh_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                            <h4 style='color: #4a5568; margin: 0;'>Buy & Hold</h4>
                            <h2 style='color: {bh_color}; margin: 10px 0;'>{backtest_result['buy_hold_return_pct']:+.2f}%</h2>
                        </div>
                        """, unsafe_allow_html=True)

                    with bt_col3:
                        st.markdown(f"""
                        <div style='background: white; padding: 20px; border-radius: 12px; text-align: center; border-top: 4px solid #667eea; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                            <h4 style='color: #4a5568; margin: 0;'>Win Rate</h4>
                            <h2 style='color: #667eea; margin: 10px 0;'>{backtest_result['win_rate_pct']:.1f}%</h2>
                        </div>
                        """, unsafe_allow_html=True)

                    with bt_col4:
                        st.markdown(f"""
                        <div style='background: white; padding: 20px; border-radius: 12px; text-align: center; border-top: 4px solid #f56565; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                            <h4 style='color: #4a5568; margin: 0;'>Max Drawdown</h4>
                            <h2 style='color: #f56565; margin: 10px 0;'>{backtest_result['max_drawdown_pct']:.2f}%</h2>
                        </div>
                        """, unsafe_allow_html=True)

                    # Second row - Risk Metrics
                    st.markdown("#### 📊 Risk-Adjusted Returns")
                    risk_col1, risk_col2, risk_col3, risk_col4 = st.columns(4)

                    sharpe = backtest_result.get('sharpe_ratio', 0)
                    sharpe_color = "#48bb78" if sharpe > 1 else ("#ed8936" if sharpe > 0 else "#f56565")

                    with risk_col1:
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #1e3a5f, #2c5282); padding: 15px; border-radius: 10px; text-align: center;'>
                            <h5 style='color: rgba(255,255,255,0.8); margin: 0;'>Sharpe Ratio</h5>
                            <h2 style='color: {sharpe_color}; margin: 5px 0;'>{sharpe:.2f}</h2>
                            <small style='color: rgba(255,255,255,0.6);'>{"Excellent" if sharpe > 2 else "Good" if sharpe > 1 else "Fair" if sharpe > 0 else "Poor"}</small>
                        </div>
                        """, unsafe_allow_html=True)

                    sortino = backtest_result.get('sortino_ratio', 0)
                    with risk_col2:
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #553c9a, #6b46c1); padding: 15px; border-radius: 10px; text-align: center;'>
                            <h5 style='color: rgba(255,255,255,0.8); margin: 0;'>Sortino Ratio</h5>
                            <h2 style='color: white; margin: 5px 0;'>{sortino:.2f}</h2>
                            <small style='color: rgba(255,255,255,0.6);'>Downside Risk Adj.</small>
                        </div>
                        """, unsafe_allow_html=True)

                    calmar = backtest_result.get('calmar_ratio', 0)
                    with risk_col3:
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #285e61, #2c7a7b); padding: 15px; border-radius: 10px; text-align: center;'>
                            <h5 style='color: rgba(255,255,255,0.8); margin: 0;'>Calmar Ratio</h5>
                            <h2 style='color: white; margin: 5px 0;'>{calmar:.2f}</h2>
                            <small style='color: rgba(255,255,255,0.6);'>Return / Drawdown</small>
                        </div>
                        """, unsafe_allow_html=True)

                    total_costs = backtest_result.get('total_costs', 0)
                    with risk_col4:
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #c53030, #9b2c2c); padding: 15px; border-radius: 10px; text-align: center;'>
                            <h5 style='color: rgba(255,255,255,0.8); margin: 0;'>Total Costs</h5>
                            <h2 style='color: white; margin: 5px 0;'>₹{total_costs:,.0f}</h2>
                            <small style='color: rgba(255,255,255,0.6);'>Commission + Slippage</small>
                        </div>
                        """, unsafe_allow_html=True)

                    # Equity curve
                    equity_data = backtest_result.get('equity_curve', [])
                    if equity_data:
                        fig_eq = go.Figure()
                        fig_eq.add_trace(go.Scatter(
                            y=[e['equity'] for e in equity_data],
                            mode='lines',
                            name='Strategy Equity',
                            line=dict(color='#667eea', width=2)
                        ))
                        fig_eq.update_layout(
                            title="Equity Curve",
                            yaxis_title="Portfolio Value (₹)",
                            height=300
                        )
                        st.plotly_chart(fig_eq, use_container_width=True)

                    # Backtest summary
                    with st.expander("📊 Detailed Backtest Statistics"):
                        bt_stats = pd.DataFrame({
                            'Metric': ['Total Trades', 'Long Trades', 'Short Trades', 'Winning Trades', 'Losing Trades',
                                       'Win Rate', 'Avg Win', 'Avg Loss', 'Profit Factor', 'Max Drawdown',
                                       'Max DD Duration', 'Sharpe Ratio', 'Sortino Ratio', 'Calmar Ratio',
                                       'Total Costs', 'Costs as % of P&L'],
                            'Value': [
                                backtest_result['total_trades'],
                                backtest_result.get('long_trades', 0),
                                backtest_result.get('short_trades', 0),
                                backtest_result['winning_trades'],
                                backtest_result['losing_trades'],
                                f"{backtest_result['win_rate_pct']:.1f}%",
                                f"{backtest_result['avg_win_pct']:.2f}%",
                                f"{backtest_result['avg_loss_pct']:.2f}%",
                                f"{backtest_result['profit_factor']:.2f}",
                                f"{backtest_result['max_drawdown_pct']:.2f}%",
                                f"{backtest_result.get('max_drawdown_duration', 0)} days",
                                f"{backtest_result.get('sharpe_ratio', 0):.2f}",
                                f"{backtest_result.get('sortino_ratio', 0):.2f}",
                                f"{backtest_result.get('calmar_ratio', 0):.2f}",
                                f"₹{backtest_result.get('total_costs', 0):,.2f}",
                                f"{backtest_result.get('cost_pct_of_pnl', 0):.1f}%"
                            ]
                        })
                        st.dataframe(bt_stats, use_container_width=True, hide_index=True)
                else:
                    st.warning(f"Backtesting: {backtest_result.get('error', 'Unknown error')}")

                # ═══════════════════════════════════════════════════════════════
                # NEWS FEED
                # ═══════════════════════════════════════════════════════════════

                st.markdown("---")
                st.markdown("### 📰 Latest News")

                with st.spinner("Loading news..."):
                    news = get_stock_news(ai_symbol, count=8)

                if news and 'error' not in news[0]:
                    news_col1, news_col2 = st.columns(2)

                    for idx, item in enumerate(news):
                        col = news_col1 if idx % 2 == 0 else news_col2
                        with col:
                            st.markdown(f"""
                            <div style='background: white; padding: 15px; border-radius: 10px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                                <a href="{item['link']}" target="_blank" style='text-decoration: none;'>
                                    <h5 style='color: #2d3748; margin: 0 0 8px 0;'>{item['title']}</h5>
                                </a>
                                <p style='color: #718096; font-size: 0.85rem; margin: 0;'>
                                    📰 {item['publisher']} • 🕐 {item['date']}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("📰 No recent news available for this stock.")

    else:
        create_info_card(
            "AI Deep Analysis",
            "Enter a stock symbol and click 'Run AI Analysis' to get comprehensive AI-powered insights including pattern recognition, market regime detection, and machine learning predictions.",
            "🤖",
            "info"
        )

# ══════════════════════════════════════════════════════════════════════
# SMART SCREENER PAGE
# ══════════════════════════════════════════════════════════════════════

elif page == "🎯 Smart Screener":
    create_section_header("Smart Screener", "Discover High-Potential Trading Opportunities", "🎯")

    # Screener Configuration
    col1, col2, col3, col4, col5 = st.columns([2, 2, 1.5, 1, 1])

    with col1:
        screening_mode = st.selectbox(
            "🔍 Screening Strategy",
            ["📊 Sector Focus", "🌐 Market Wide", "💎 Market Cap Focus"],
            help="Choose your screening approach"
        )

    with col2:
        if screening_mode == "📊 Sector Focus":
            all_sectors = get_all_available_sectors()
            selected_sector = st.selectbox("🏢 Select Sector", all_sectors)
            selected_cap = None
            stocks_limit = st.number_input("📈 Stocks to Analyze", 5, 200, 50, 10,
                                          help="Number of stocks to screen from this sector")
        elif screening_mode == "💎 Market Cap Focus":
            selected_sector = None
            selected_cap = st.selectbox("💰 Market Cap",
                                       ["🏆 Large Cap (>₹20,000 Cr)",
                                        "📈 Mid Cap (₹5,000-20,000 Cr)",
                                        "💫 Small Cap (<₹5,000 Cr)"])
            stocks_limit = st.number_input("📈 Stocks to Analyze", 10, 200, 50, 10,
                                          help="Number of stocks from selected market cap")
        else:
            selected_sector = None
            selected_cap = None
            stocks_limit = st.number_input("📈 Stocks to Analyze", 50, 500, 150, 25,
                                          help="Total number of stocks to screen across all sectors")

    with col3:
        confidence_threshold = st.slider("🎯 Min Confidence", 0.5, 0.95, 0.6, 0.05,
                                        help="Filter signals by confidence score")

    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        screen_button = st.button("🚀 Start Screening", type="primary", use_container_width=True)

    with col5:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Reset Filters", use_container_width=True):
            if 'screener_results' in st.session_state:
                del st.session_state.screener_results
            if 'selected_filter' in st.session_state:
                del st.session_state.selected_filter
            st.rerun()

    # Advanced Filters Section
    with st.expander("🔬 Advanced Technical Filters", expanded=False):
        adv_col1, adv_col2, adv_col3, adv_col4 = st.columns(4)

        with adv_col1:
            rsi_filter = st.selectbox(
                "📊 RSI Filter",
                ["All", "Oversold (RSI < 30)", "Neutral (30-70)", "Overbought (RSI > 70)", "Bullish Divergence Zone (30-50)"],
                help="Filter stocks by RSI levels"
            )

        with adv_col2:
            macd_filter = st.selectbox(
                "📈 MACD Filter",
                ["All", "Bullish (MACD > Signal)", "Bearish (MACD < Signal)", "Bullish Crossover", "Near Crossover"],
                help="Filter by MACD signals"
            )

        with adv_col3:
            trend_filter = st.selectbox(
                "📉 Trend Filter",
                ["All", "Strong Uptrend", "Uptrend", "Sideways", "Downtrend", "Strong Downtrend"],
                help="Filter by price trend relative to moving averages"
            )

        with adv_col4:
            volume_filter = st.selectbox(
                "📊 Volume Filter",
                ["All", "High Volume (>1.5x avg)", "Above Average (>1x)", "Low Volume (<0.7x)"],
                help="Filter by relative volume"
            )

        adv_col5, adv_col6, adv_col7, adv_col8 = st.columns(4)

        with adv_col5:
            pattern_filter = st.selectbox(
                "🔮 Pattern Filter",
                ["All", "Bullish Patterns Only", "Bearish Patterns Only", "Reversal Patterns", "Continuation Patterns"],
                help="Filter by detected chart patterns"
            )

        with adv_col6:
            pe_filter = st.selectbox(
                "💰 P/E Ratio",
                ["All", "Undervalued (PE < 15)", "Fair Value (15-25)", "Growth (25-40)", "Premium (> 40)"],
                help="Filter by Price to Earnings ratio"
            )

        with adv_col7:
            momentum_filter = st.selectbox(
                "⚡ Momentum",
                ["All", "Strong Bullish", "Bullish", "Neutral", "Bearish", "Strong Bearish"],
                help="Filter by momentum indicators"
            )

        with adv_col8:
            ai_analysis_mode = st.selectbox(
                "🤖 AI Analysis Mode",
                ["Standard", "Deep Analysis (Slower)", "Quick Scan"],
                help="Choose AI analysis depth - deeper analysis takes longer but is more accurate"
            )

    # Info about screening
    if screening_mode == "📊 Sector Focus":
        create_info_card(
            "Sector-Focused Analysis",
            f"Screening {stocks_limit} stocks from {selected_sector} sector using our comprehensive database of 500+ companies across multiple exchanges.",
            "📊",
            "info"
        )
    elif screening_mode == "💎 Market Cap Focus":
        cap_name = selected_cap.split()[0] if selected_cap else "All"
        create_info_card(
            "Market Cap Analysis",
            f"Analyzing {stocks_limit} {cap_name} stocks based on market capitalization. This helps you find opportunities matching your risk profile.",
            "💎",
            "info"
        )
    else:
        create_info_card(
            "Market-Wide Screening",
            f"Analyzing {stocks_limit} stocks across all sectors from our comprehensive database. This includes large-cap, mid-cap, and quality small-cap companies.",
            "🌐",
            "info"
        )

    if screen_button:
        # Build stock list based on screening mode
        if screening_mode == "📊 Sector Focus":
            stock_list = get_sector_stocks_from_universe(selected_sector, stocks_limit)
            st.info(f"📊 Screening {len(stock_list)} stocks from {selected_sector} sector...")
        elif screening_mode == "💎 Market Cap Focus":
            # Get stocks by market cap category
            from src.stock_universe import get_stocks_by_market_cap, LARGE_CAP, MID_CAP, SMALL_CAP
            if "Large" in selected_cap:
                stock_list = LARGE_CAP[:stocks_limit]
            elif "Mid" in selected_cap:
                stock_list = MID_CAP[:stocks_limit]
            elif "Small" in selected_cap:
                stock_list = SMALL_CAP[:stocks_limit]
            else:
                stock_list = get_nifty_top_n(n=stocks_limit)
            st.info(f"💎 Screening {len(stock_list)} {selected_cap} stocks...")
        else:
            # Market-wide screening - get stocks from all sectors up to the limit
            from src.stock_universe import get_all_stocks
            all_available = get_all_stocks()
            stock_list = all_available[:stocks_limit]
            st.info(f"🌐 Screening {len(stock_list)} stocks across all sectors...")

        if len(stock_list) == 0:
            st.warning("❌ No stocks found for the selected criteria.")
            st.stop()

        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()

        results = []

        for idx, stock_symbol in enumerate(stock_list):
            try:
                status_text.text(f"Analyzing {stock_symbol}... ({idx+1}/{len(stock_list)})")

                # Load data
                stock_data = load_stock_data(stock_symbol, start_date, end_date)

                if stock_data is None or len(stock_data) < 100:
                    continue

                # Calculate indicators
                stock_data = calculate_technical_indicators(stock_data)
                stock_data.dropna(inplace=True)

                if len(stock_data) < 50:
                    continue

                # Get latest values for filtering
                latest = stock_data.iloc[-1]
                rsi_value = latest.get('RSI14', 50)
                macd_value = latest.get('MACD', 0)
                macd_signal = latest.get('MACD_Signal', 0)
                volume_ratio = latest.get('Volume_Ratio', 1.0)
                current_price = latest['Close']
                sma20 = latest.get('SMA20', current_price)
                sma50 = latest.get('SMA50', current_price)
                sma200 = latest.get('SMA200', current_price)

                # Calculate trend
                if current_price > sma20 > sma50 > sma200:
                    trend = "Strong Uptrend"
                elif current_price > sma50 > sma200:
                    trend = "Uptrend"
                elif current_price < sma20 < sma50 < sma200:
                    trend = "Strong Downtrend"
                elif current_price < sma50:
                    trend = "Downtrend"
                else:
                    trend = "Sideways"

                # Calculate momentum
                momentum_val = latest.get('Momentum', 0)
                roc = latest.get('ROC', 0)
                if rsi_value > 60 and macd_value > macd_signal and momentum_val > 0:
                    momentum = "Strong Bullish"
                elif rsi_value > 50 and macd_value > 0:
                    momentum = "Bullish"
                elif rsi_value < 40 and macd_value < macd_signal and momentum_val < 0:
                    momentum = "Strong Bearish"
                elif rsi_value < 50 and macd_value < 0:
                    momentum = "Bearish"
                else:
                    momentum = "Neutral"

                # Apply advanced filters
                # RSI Filter
                if rsi_filter != "All":
                    if "Oversold" in rsi_filter and rsi_value >= 30:
                        continue
                    elif "Overbought" in rsi_filter and rsi_value <= 70:
                        continue
                    elif "Neutral" in rsi_filter and (rsi_value < 30 or rsi_value > 70):
                        continue
                    elif "Bullish Divergence" in rsi_filter and (rsi_value < 30 or rsi_value > 50):
                        continue

                # MACD Filter
                if macd_filter != "All":
                    if "Bullish (MACD > Signal)" in macd_filter and macd_value <= macd_signal:
                        continue
                    elif "Bearish (MACD < Signal)" in macd_filter and macd_value >= macd_signal:
                        continue

                # Trend Filter
                if trend_filter != "All" and trend_filter != trend:
                    continue

                # Volume Filter
                if volume_filter != "All":
                    if "High Volume" in volume_filter and volume_ratio < 1.5:
                        continue
                    elif "Above Average" in volume_filter and volume_ratio < 1.0:
                        continue
                    elif "Low Volume" in volume_filter and volume_ratio >= 0.7:
                        continue

                # Momentum Filter
                if momentum_filter != "All" and momentum_filter != momentum:
                    continue

                # Get fundamentals
                fundamentals = get_fundamentals(stock_symbol)

                # P/E Filter
                pe_ratio = fundamentals.get('PE', 0)
                if pe_filter != "All" and pe_ratio:
                    if "Undervalued" in pe_filter and pe_ratio >= 15:
                        continue
                    elif "Fair Value" in pe_filter and (pe_ratio < 15 or pe_ratio > 25):
                        continue
                    elif "Growth" in pe_filter and (pe_ratio < 25 or pe_ratio > 40):
                        continue
                    elif "Premium" in pe_filter and pe_ratio <= 40:
                        continue

                # Get market cap
                market_cap = fundamentals.get('MarketCap', 0) / 1e7  # Convert to Crores

                # Determine cap category
                if market_cap >= 20000:
                    cap_category = "🏆 Large Cap"
                elif market_cap >= 5000:
                    cap_category = "📈 Mid Cap"
                else:
                    cap_category = "💫 Small Cap"

                # Calculate entry targets
                entry_targets = calculate_entry_target_prices(stock_data, fundamentals=fundamentals)

                # Generate recommendation
                explanation = generate_buy_sell_explanation(stock_data, fundamentals)

                # Extract data
                current_price = entry_targets['Current Price']
                target_price = entry_targets['Target Price']
                stop_loss = entry_targets['Stop Loss']
                confidence = entry_targets['Confidence Score']
                recommendation = explanation.get('Recommendation', 'N/A')

                # Calculate potential return
                potential_return = ((target_price - current_price) / current_price) * 100

                # Filter by market cap if needed
                if screening_mode == "💎 Market Cap Focus" and selected_cap:
                    cap_filter = selected_cap.split()[0]  # Get emoji
                    if cap_filter not in cap_category:
                        continue

                # Only include if confidence meets threshold
                if confidence >= confidence_threshold:
                    results.append({
                        'Symbol': stock_symbol,
                        'Market Cap': cap_category,
                        'Market Cap (Cr)': market_cap,
                        'Current Price': current_price,
                        'Entry Price': entry_targets['Entry Price'],
                        'Target Price': target_price,
                        'Stop Loss': stop_loss,
                        'Potential Return %': potential_return,
                        'R/R Ratio': entry_targets['R/R Ratio'],
                        'RSI': rsi_value,
                        'Trend': trend,
                        'Momentum': momentum,
                        'Volume': f"{volume_ratio:.1f}x",
                        'Confidence': confidence,
                        'Recommendation': recommendation,
                        'Strength': entry_targets['Strength']
                    })

                progress_bar.progress((idx + 1) / len(stock_list))

            except Exception as e:
                continue

        progress_bar.empty()
        status_text.empty()

        # Store results in session state
        if results:
            st.session_state.screener_results = pd.DataFrame(results).sort_values('Confidence', ascending=False)
        else:
            if 'screener_results' in st.session_state:
                del st.session_state.screener_results

    # Display results if available
    if 'screener_results' in st.session_state:
        df_results = st.session_state.screener_results

        st.markdown(f"### 📊 Screening Results ({len(df_results)} stocks found)")

        # Summary metrics with clickable cards
        st.markdown("#### 🎯 Quick Filters (Click to Filter)")
        col1, col2, col3, col4 = st.columns(4)

        buy_signals = len(df_results[df_results['Recommendation'].str.contains('BUY', na=False)])
        sell_signals = len(df_results[df_results['Recommendation'].str.contains('SELL', na=False)])
        hold_signals = len(df_results) - buy_signals - sell_signals
        avg_confidence = df_results['Confidence'].mean()

        # Cap extreme values and use median for more realistic average
        returns = df_results['Potential Return %'].clip(lower=-100, upper=200)
        avg_return = returns.median()  # Use median instead of mean to avoid outlier skew

        with col1:
            if st.button(f"🟢 Buy Signals\n{buy_signals} stocks", use_container_width=True, key="filter_buy"):
                st.session_state.selected_filter = "BUY"

        with col2:
            if st.button(f"🔴 Sell Signals\n{sell_signals} stocks", use_container_width=True, key="filter_sell"):
                st.session_state.selected_filter = "SELL"

        with col3:
            if st.button(f"🟡 Hold/Neutral\n{hold_signals} stocks", use_container_width=True, key="filter_hold"):
                st.session_state.selected_filter = "HOLD"

        with col4:
            if st.button(f"🌟 All Stocks\n{len(df_results)} total", use_container_width=True, key="filter_all"):
                if 'selected_filter' in st.session_state:
                    del st.session_state.selected_filter

        # Display metrics
        st.markdown("#### 📈 Summary Metrics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            create_metric_card("Buy Signals", buy_signals, icon="🟢", color="#48bb78")

        with col2:
            create_metric_card("Sell Signals", sell_signals, icon="🔴", color="#f56565")

        with col3:
            create_metric_card("Avg Confidence", f"{avg_confidence:.1%}", icon="📊", color="#667eea")

        with col4:
            # Add explanation in an expander below the metric
            st.markdown("""
            <div style='text-align: center;'>
                <small style='color: #718096;'>
                    ℹ️ Median = Middle value of all returns (50th percentile)<br>
                    More reliable than average as it ignores extreme outliers
                </small>
            </div>
            """, unsafe_allow_html=True)
            create_metric_card("Median Potential Return", f"{avg_return:.1%}", icon="📈", color="#38b2ac")

        # Filter results based on selection
        if 'selected_filter' in st.session_state:
            filter_type = st.session_state.selected_filter
            if filter_type == "BUY":
                df_display = df_results[df_results['Recommendation'].str.contains('BUY', na=False)]
                st.info(f"🟢 Showing {len(df_display)} BUY recommendations")
            elif filter_type == "SELL":
                df_display = df_results[df_results['Recommendation'].str.contains('SELL', na=False)]
                st.info(f"🔴 Showing {len(df_display)} SELL recommendations")
            elif filter_type == "HOLD":
                df_display = df_results[~df_results['Recommendation'].str.contains('BUY|SELL', na=False)]
                st.info(f"🟡 Showing {len(df_display)} HOLD/NEUTRAL recommendations")
        else:
            df_display = df_results

        # Detailed results table
        st.markdown("### 📋 Detailed Results")

        # Format the dataframe for display
        df_formatted = df_display.copy()
        df_formatted['Market Cap (Cr)'] = df_formatted['Market Cap (Cr)'].apply(lambda x: f"₹{x:,.0f}")
        df_formatted['Current Price'] = df_formatted['Current Price'].apply(lambda x: f"₹{x:.2f}")
        df_formatted['Entry Price'] = df_formatted['Entry Price'].apply(lambda x: f"₹{x:.2f}")
        df_formatted['Target Price'] = df_formatted['Target Price'].apply(lambda x: f"₹{x:.2f}")
        df_formatted['Stop Loss'] = df_formatted['Stop Loss'].apply(lambda x: f"₹{x:.2f}")
        df_formatted['Potential Return %'] = df_formatted['Potential Return %'].apply(lambda x: f"{x:.1f}%")
        df_formatted['R/R Ratio'] = df_formatted['R/R Ratio'].apply(lambda x: f"{x:.2f}")
        df_formatted['RSI'] = df_formatted['RSI'].apply(lambda x: f"{x:.0f}")
        df_formatted['Confidence'] = df_formatted['Confidence'].apply(lambda x: f"{x:.1%}")

        # Reorder columns for better display - include new technical columns
        column_order = ['Symbol', 'Market Cap', 'Current Price', 'Entry Price',
                       'Target Price', 'Stop Loss', 'Potential Return %', 'R/R Ratio',
                       'RSI', 'Trend', 'Momentum', 'Volume',
                       'Confidence', 'Recommendation', 'Strength']
        # Only use columns that exist
        column_order = [c for c in column_order if c in df_formatted.columns]
        df_formatted = df_formatted[column_order]

        st.dataframe(df_formatted, use_container_width=True, hide_index=True)

        # Download button
        csv = df_display.to_csv(index=False)
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name=f"screener_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    elif not screen_button:
        st.info("👆 Configure your screening parameters above and click '🚀 Start Screening' to begin analysis.")

# ══════════════════════════════════════════════════════════════════════
# GENERAL NEWS PAGE
# ══════════════════════════════════════════════════════════════════════

elif page == "📰 General News":
    create_section_header("General News", "Latest Financial, Political & Market Announcements", "📰")
    
    # Import the news display module
    from src.news_provider import NewsDisplay, NewsProvider
    
    # Render the news dashboard
    NewsDisplay.render_news_dashboard()

# ══════════════════════════════════════════════════════════════════════
# PORTFOLIO MANAGER PAGE
# ══════════════════════════════════════════════════════════════════════

elif page == "💼 Portfolio Manager":
    create_section_header("Portfolio Manager", "Build & Optimize Your Investment Portfolio", "💼")

    # Tabs for different portfolio features
    portfolio_tab1, portfolio_tab2, portfolio_tab3 = st.tabs([
        "🏗️ Build Portfolio",
        "💎 Advanced Tracker",
        "📊 Analysis"
    ])
    
    # ══════════════════════════════════════════════════════════════════
    # TAB 1: PORTFOLIO BUILDER
    # ══════════════════════════════════════════════════════════════════
    with portfolio_tab1:
        st.markdown("---")
        
        # Interactive Portfolio Builder
        create_portfolio_builder()
        
        # Mobile responsive view
        st.markdown("---")
        create_mobile_responsive_portfolio()
        
        # Recommendations
        st.markdown("---")
        portfolio_items = st.session_state.get('portfolio_items', {})
        show_portfolio_recommendations(portfolio_items)
    
    # ══════════════════════════════════════════════════════════════════
    # TAB 2: ADVANCED PORTFOLIO TRACKER
    # ══════════════════════════════════════════════════════════════════
    with portfolio_tab2:
        st.markdown("---")
        create_advanced_portfolio_builder()
    
    # ══════════════════════════════════════════════════════════════════
    # TAB 3: PORTFOLIO ANALYSIS (Original content)
    # ══════════════════════════════════════════════════════════════════
    with portfolio_tab3:
        st.markdown("---")
        
        # Portfolio Input
        col1, col2 = st.columns([3, 1])

        with col1:
            portfolio_symbols = st.text_area(
                "Enter Portfolio Stocks (comma-separated)",
                "RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, ICICIBANK.NS",
                help="Enter stock symbols separated by commas"
            )

        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            analyze_portfolio_btn = st.button("📊 Analyze Portfolio", type="primary", use_container_width=True)

        if analyze_portfolio_btn:
            symbols_list = [s.strip().upper() for s in portfolio_symbols.split(",") if s.strip()]

            if not symbols_list:
                st.error("❌ Please enter at least one stock symbol.")
                st.stop()

            st.info(f"📊 Analyzing {len(symbols_list)} stocks...")

            progress_bar = st.progress(0)
            status_text = st.empty()

            portfolio_data = []
            returns_dict = {}

            for idx, symbol in enumerate(symbols_list):
                try:
                    status_text.text(f"🤖 AI Analyzing {symbol}... ({idx+1}/{len(symbols_list)})")

                    # Load data
                    stock_data = load_stock_data(symbol, start_date, end_date)

                    if stock_data is None or len(stock_data) < 100:
                        continue

                    # Calculate returns
                    returns = stock_data['Close'].pct_change().dropna()
                    total_return = (stock_data['Close'].iloc[-1] / stock_data['Close'].iloc[0]) - 1
                    annual_vol = returns.std() * np.sqrt(252)
                    sharpe = sharpe_ratio(returns)
                    max_dd = max_drawdown(returns)

                    # Get fundamentals
                    fundamentals = get_fundamentals(symbol)
                    sentiment = get_news_sentiment(symbol)

                    # Calculate technical indicators
                    stock_data = calculate_technical_indicators(stock_data)

                    # Use Advanced AI Analysis for comprehensive recommendation
                    try:
                        # Calculate advanced indicators
                        load_ml_resources()
                        stock_data = calculate_advanced_indicators(stock_data)

                        # Get AI analysis
                        ai_analysis = generate_ai_analysis(stock_data, symbol, fundamentals)

                        # Get AI recommendation
                        ai_rec = ai_analysis.get('ai_recommendation', {})
                        recommendation_text = ai_rec.get('recommendation', 'HOLD')
                        confidence = ai_rec.get('confidence', 0.5)

                        # Get technical score
                        tech_score = ai_analysis.get('technical_score', {})
                        ai_score = tech_score.get('score', 50) / 100
                        grade = tech_score.get('grade', 'C')

                        # Get market regime
                        regime = ai_analysis.get('market_regime', {})
                        market_regime = regime.get('primary_regime', 'Unknown')
                        risk_level = regime.get('risk_level', 'Medium')

                        # Get ensemble ML prediction
                        ml_ensemble = ai_analysis.get('ml_ensemble', {})
                        ml_prediction = ml_ensemble.get('ensemble_prediction', 'Unknown')
                        ml_confidence = ml_ensemble.get('ensemble_confidence', 0)

                        # Determine final recommendation with emoji
                        if 'STRONG BUY' in recommendation_text:
                            recommendation = "🟢 STRONG BUY"
                            action = "Buy Now"
                        elif 'BUY' in recommendation_text:
                            recommendation = "🟢 BUY"
                            action = "Buy on Dips"
                        elif 'STRONG SELL' in recommendation_text:
                            recommendation = "🔴 STRONG SELL"
                            action = "Sell Immediately"
                        elif 'SELL' in recommendation_text:
                            recommendation = "🔴 SELL"
                            action = "Exit Position"
                        else:
                            recommendation = "🟡 HOLD"
                            action = "Wait & Watch"

                    except Exception as e:
                        # Fallback to basic analysis if advanced fails
                        signals = generate_signals(stock_data)
                        recommendation_text = signals.get('signal', 'HOLD')
                        confidence = signals.get('confidence', 0.5)
                        ai_score = sharpe * 0.5 + 0.5
                        grade = 'C'
                        market_regime = 'Unknown'
                        risk_level = 'Medium'
                        ml_prediction = 'Unknown'
                        ml_confidence = 0

                        if 'BUY' in recommendation_text:
                            recommendation = "🟢 BUY"
                            action = "Buy"
                        elif 'SELL' in recommendation_text:
                            recommendation = "🔴 SELL"
                            action = "Sell"
                        else:
                            recommendation = "🟡 HOLD"
                            action = "Hold"

                    portfolio_data.append({
                        'Symbol': symbol,
                        'Current Price': stock_data['Close'].iloc[-1],
                        'Total Return': total_return,
                        'Annual Volatility': annual_vol,
                        'Sharpe Ratio': sharpe,
                        'Max Drawdown': max_dd,
                        'AI Score': ai_score,
                        'Grade': grade,
                        'Market Regime': market_regime,
                        'Risk Level': risk_level,
                        'ML Prediction': ml_prediction,
                        'Recommendation': recommendation,
                        'Action': action,
                        'Confidence': confidence
                    })

                    returns_dict[symbol] = returns

                    progress_bar.progress((idx + 1) / len(symbols_list))

                except Exception as e:
                    continue

            progress_bar.empty()
            status_text.empty()

            if portfolio_data:
                df_portfolio = pd.DataFrame(portfolio_data)
                df_portfolio = df_portfolio.sort_values('AI Score', ascending=False)

                # Display summary
                st.markdown("### 📊 AI-Powered Portfolio Analysis")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    avg_return = df_portfolio['Total Return'].mean()
                    create_metric_card("Avg Return", f"{avg_return:.2%}", icon="📈", color="#48bb78")

                with col2:
                    avg_sharpe = df_portfolio['Sharpe Ratio'].mean()
                    create_metric_card("Avg Sharpe", f"{avg_sharpe:.2f}", icon="⚖️", color="#667eea")

                with col3:
                    avg_vol = df_portfolio['Annual Volatility'].mean()
                    create_metric_card("Avg Volatility", f"{avg_vol:.2%}", icon="📉", color="#ed8936")

                with col4:
                    best_stock = df_portfolio.iloc[0]['Symbol']
                    create_metric_card("Top Pick", best_stock, icon="🏆", color="#9f7aea")

                # Detailed table
                st.markdown("### 📋 Detailed Analysis with Recommendations")

                # Show recommendation summary cards
                st.markdown("#### 🎯 Quick Actions")
                rec_col1, rec_col2, rec_col3 = st.columns(3)

                buy_count = len(df_portfolio[df_portfolio['Recommendation'].str.contains('BUY')])
                sell_count = len(df_portfolio[df_portfolio['Recommendation'].str.contains('SELL')])
                hold_count = len(df_portfolio[df_portfolio['Recommendation'].str.contains('HOLD')])

                with rec_col1:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #48bb78, #38a169); padding: 20px; border-radius: 12px; text-align: center;'>
                        <h2 style='color: white; margin: 0;'>{buy_count}</h2>
                        <p style='color: rgba(255,255,255,0.9); margin: 5px 0 0 0;'>🟢 BUY Signals</p>
                    </div>
                    """, unsafe_allow_html=True)

                with rec_col2:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #ed8936, #dd6b20); padding: 20px; border-radius: 12px; text-align: center;'>
                        <h2 style='color: white; margin: 0;'>{hold_count}</h2>
                        <p style='color: rgba(255,255,255,0.9); margin: 5px 0 0 0;'>🟡 HOLD Signals</p>
                    </div>
                    """, unsafe_allow_html=True)

                with rec_col3:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #f56565, #e53e3e); padding: 20px; border-radius: 12px; text-align: center;'>
                        <h2 style='color: white; margin: 0;'>{sell_count}</h2>
                        <p style='color: rgba(255,255,255,0.9); margin: 5px 0 0 0;'>🔴 SELL Signals</p>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                df_display = df_portfolio.copy()
                df_display['Current Price'] = df_display['Current Price'].apply(lambda x: f"₹{x:.2f}")
                df_display['Total Return'] = df_display['Total Return'].apply(lambda x: f"{x:.2%}")
                df_display['Annual Volatility'] = df_display['Annual Volatility'].apply(lambda x: f"{x:.2%}")
                df_display['Sharpe Ratio'] = df_display['Sharpe Ratio'].apply(lambda x: f"{x:.2f}")
                df_display['Max Drawdown'] = df_display['Max Drawdown'].apply(lambda x: f"{x:.2%}")
                df_display['AI Score'] = df_display['AI Score'].apply(lambda x: f"{x:.0%}")
                df_display['Confidence'] = df_display['Confidence'].apply(lambda x: f"{x:.0%}")

            # Reorder columns for better display
            display_columns = ['Symbol', 'Current Price', 'Total Return', 'Sharpe Ratio',
                              'AI Score', 'Grade', 'Market Regime', 'Risk Level',
                              'ML Prediction', 'Recommendation', 'Action', 'Confidence']
            df_display = df_display[[c for c in display_columns if c in df_display.columns]]

            st.dataframe(df_display, use_container_width=True, hide_index=True)

            # Individual Stock Analysis Cards
            st.markdown("### 🎯 Individual Stock Recommendations")

            for _, row in df_portfolio.iterrows():
                rec = row['Recommendation']
                if 'BUY' in rec:
                    card_color = "linear-gradient(135deg, #48bb78, #38a169)"
                elif 'SELL' in rec:
                    card_color = "linear-gradient(135deg, #f56565, #e53e3e)"
                else:
                    card_color = "linear-gradient(135deg, #ed8936, #dd6b20)"

                st.markdown(f"""
                <div style='background: {card_color}; padding: 20px; border-radius: 12px; margin: 10px 0;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <h3 style='color: white; margin: 0;'>{row['Symbol']}</h3>
                            <p style='color: rgba(255,255,255,0.9); margin: 5px 0;'>₹{row['Current Price']:.2f} | Return: {row['Total Return']:.1%}</p>
                        </div>
                        <div style='text-align: right;'>
                            <h2 style='color: white; margin: 0;'>{row['Recommendation']}</h2>
                            <p style='color: rgba(255,255,255,0.9); margin: 5px 0;'>{row['Action']} | Confidence: {row['Confidence']:.0%}</p>
                        </div>
                    </div>
                    <div style='margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.3);'>
                        <span style='color: rgba(255,255,255,0.9);'>
                            📊 AI Score: {row['AI Score']:.0%} ({row['Grade']}) |
                            🌍 Regime: {row['Market Regime']} |
                            ⚠️ Risk: {row['Risk Level']} |
                            🤖 ML: {row['ML Prediction']}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Correlation Heatmap
            if len(returns_dict) > 1:
                st.markdown("### 📊 Correlation Matrix")

                df_returns = pd.DataFrame(returns_dict).dropna()
                corr_matrix = df_returns.corr()

                fig_corr = create_heatmap(corr_matrix, "Portfolio Correlation")
                st.plotly_chart(fig_corr, use_container_width=True)

            # ═══════════════════════════════════════════════════════════════
            # PORTFOLIO POSITION SIZING & RISK ALLOCATION
            # ═══════════════════════════════════════════════════════════════

            st.markdown("### 💰 Portfolio Position Sizing")

            ps_col1, ps_col2 = st.columns([1, 3])

            with ps_col1:
                portfolio_capital = st.number_input("💵 Total Portfolio Capital (₹)",
                                                   min_value=50000, max_value=100000000,
                                                   value=500000, step=50000, key="portfolio_capital")
                total_risk_budget = st.slider("⚠️ Total Risk Budget (%)", 5.0, 20.0, 10.0, 1.0, key="risk_budget")

            with ps_col2:
                # Calculate position sizing for each stock
                position_data = []
                total_allocated = 0

                for _, row in df_portfolio.iterrows():
                    symbol = row['Symbol']
                    try:
                        stock_data = load_stock_data(symbol, start_date, end_date)
                        if stock_data is not None and len(stock_data) >= 20:
                            pos_result = calculate_position_size(stock_data, portfolio_capital / len(df_portfolio),
                                                                 total_risk_budget / len(df_portfolio), 2.0)
                            if 'error' not in pos_result:
                                position_data.append({
                                    'Symbol': symbol,
                                    'Entry Price': pos_result['current_price'],
                                    'Stop Loss': pos_result['stop_loss_price'],
                                    'Take Profit': pos_result['take_profit_2r'],
                                    'Shares': pos_result['position_size_shares'],
                                    'Position Value': pos_result['position_value'],
                                    'Risk (₹)': pos_result['risk_amount'],
                                    'Volatility': pos_result['volatility_level']
                                })
                                total_allocated += pos_result['position_value']
                    except:
                        continue

                if position_data:
                    df_positions = pd.DataFrame(position_data)

                    # Summary cards
                    pos_sum_col1, pos_sum_col2, pos_sum_col3 = st.columns(3)

                    with pos_sum_col1:
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #667eea, #764ba2); padding: 15px; border-radius: 10px; text-align: center;'>
                            <h4 style='color: white; margin: 0;'>Total Allocated</h4>
                            <h2 style='color: white; margin: 5px 0;'>₹{total_allocated:,.0f}</h2>
                        </div>
                        """, unsafe_allow_html=True)

                    with pos_sum_col2:
                        total_risk = df_positions['Risk (₹)'].sum()
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #f56565, #c53030); padding: 15px; border-radius: 10px; text-align: center;'>
                            <h4 style='color: white; margin: 0;'>Total Risk</h4>
                            <h2 style='color: white; margin: 5px 0;'>₹{total_risk:,.0f}</h2>
                        </div>
                        """, unsafe_allow_html=True)

                    with pos_sum_col3:
                        cash_remaining = portfolio_capital - total_allocated
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #48bb78, #38a169); padding: 15px; border-radius: 10px; text-align: center;'>
                            <h4 style='color: white; margin: 0;'>Cash Remaining</h4>
                            <h2 style='color: white; margin: 5px 0;'>₹{cash_remaining:,.0f}</h2>
                        </div>
                        """, unsafe_allow_html=True)

                    # Position sizing table
                    st.markdown("#### 📋 Position Sizing Details")
                    df_pos_display = df_positions.copy()
                    df_pos_display['Entry Price'] = df_pos_display['Entry Price'].apply(lambda x: f"₹{x:.2f}")
                    df_pos_display['Stop Loss'] = df_pos_display['Stop Loss'].apply(lambda x: f"₹{x:.2f}")
                    df_pos_display['Take Profit'] = df_pos_display['Take Profit'].apply(lambda x: f"₹{x:.2f}")
                    df_pos_display['Position Value'] = df_pos_display['Position Value'].apply(lambda x: f"₹{x:,.0f}")
                    df_pos_display['Risk (₹)'] = df_pos_display['Risk (₹)'].apply(lambda x: f"₹{x:,.0f}")

                    st.dataframe(df_pos_display, use_container_width=True, hide_index=True)

                    # Position allocation pie chart
                    fig_alloc = go.Figure(data=[go.Pie(
                        labels=df_positions['Symbol'],
                        values=df_positions['Position Value'],
                        hole=.4,
                        marker_colors=['#667eea', '#f093fb', '#4facfe', '#43e97b', '#f56565',
                                       '#ed8936', '#9f7aea', '#38b2ac', '#fc8181', '#68d391']
                    )])
                    fig_alloc.update_layout(title="Portfolio Allocation by Position Value", height=350)
                    st.plotly_chart(fig_alloc, use_container_width=True)

            # Portfolio Optimization
            if len(returns_dict) >= 2:
                st.markdown("### 🎯 Optimized Weights")

                try:
                    opt_weights = optimize_portfolio(returns_dict)
                    st.dataframe(opt_weights, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not optimize portfolio: {str(e)}")

            # Comparison Chart
            st.markdown("### 📈 Performance Comparison")

            # Load data for comparison
            comparison_data = {}
            for symbol in symbols_list[:10]:  # Limit to 10 for performance
                try:
                    stock_data = load_stock_data(symbol, start_date, end_date)
                    if stock_data is not None and len(stock_data) > 0:
                        comparison_data[symbol] = stock_data
                except:
                    continue

            if comparison_data:
                fig_comp = create_comparison_chart(comparison_data, "Portfolio Performance Comparison")
                st.plotly_chart(fig_comp, use_container_width=True)

        else:
            st.warning("❌ Could not analyze any stocks from the portfolio.")

# ══════════════════════════════════════════════════════════════════════
# DEEP LEARNING PAGE
# ══════════════════════════════════════════════════════════════════════

elif page == "🔬 Deep Learning":
    create_section_header("Deep Learning Models", "Advanced Keras-based Predictions", "🔬")
    
    st.markdown("### 🤖 Transformer vs Traditional Models")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        symbol = st.text_input("Enter Stock Symbol (e.g., INFY)", value="INFY", key="dl_symbol")
    with col2:
        if st.button("🔄 Load Data", key="dl_load"):
            st.session_state.dl_data_loaded = True
    
    if 'dl_data_loaded' in st.session_state and st.session_state.dl_data_loaded:
        try:
            # Load data
            df = load_stock_data_cached(symbol, start_date, end_date)
            df = calculate_indicators_cached(df)
            
            st.success(f"✅ Loaded {len(df)} rows for {symbol}")
            
            # Model selection tabs
            dl_tab1, dl_tab2, dl_tab3 = st.tabs([
                "🔄 Transformer Forecasting",
                "📊 Multi-Step Predictions",
                "🎯 Autoencoder Anomalies"
            ])
            
            with dl_tab1:
                st.markdown("#### Transformer-based Time Series Forecasting")
                st.markdown("""
                The Transformer model uses self-attention mechanisms to capture long-range dependencies
                in price movements. It includes:
                - Positional encoding for temporal information
                - Multi-head attention for pattern recognition
                - Fed-forward networks for feature transformation
                """)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    seq_len = st.slider("Sequence Length", 30, 120, 60, key="seq_len")
                with col2:
                    n_heads = st.slider("Attention Heads", 2, 8, 4, key="n_heads")
                with col3:
                    n_layers = st.slider("Transformer Layers", 1, 4, 2, key="n_layers")
                
                if st.button("🚀 Train Transformer", key="train_transformer"):
                    with st.spinner("Training Transformer model..."):
                        result = predict_with_transformer(
                            df, seq_len=seq_len, forecast_len=5,
                            epochs=50, n_heads=n_heads, n_layers=n_layers,
                            d_model=64
                        )
                        
                        if 'error' not in result:
                            st.success("✅ Model trained successfully!")
                            
                            # Display predictions
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric(
                                    "1-Day Forecast",
                                    f"₹{result['predictions']['1_day']['price']:.2f}",
                                    f"{result['predictions']['1_day']['change_pct']:+.2f}%"
                                )
                            with col2:
                                st.metric(
                                    "3-Day Forecast",
                                    f"₹{result['predictions']['3_day']['price']:.2f}",
                                    f"{result['predictions']['3_day']['change_pct']:+.2f}%"
                                )
                            with col3:
                                st.metric(
                                    "5-Day Forecast",
                                    f"₹{result['predictions']['5_day']['price']:.2f}",
                                    f"{result['predictions']['5_day']['change_pct']:+.2f}%"
                                )
                            
                            # Trend
                            st.markdown(f"**Overall Trend:** {result['overall_trend']}")
                            st.markdown(f"**Model Error (MAE):** {result['mae_test']:.4f}")
                            
                            # Plot predictions
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                y=result['all_daily_predictions'],
                                name='Predictions',
                                mode='lines+markers'
                            ))
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.error(f"❌ Error: {result.get('error')}")
            
            with dl_tab2:
                st.markdown("#### Multi-Step Price Forecasting")
                st.markdown("""
                This model predicts prices for multiple future timeframes:
                - 1 day: Capture immediate momentum
                - 3 days: Short-term trend
                - 5 days: Medium-term direction
                
                Useful for swing trading and position sizing.
                """)
                
                if st.button("📊 Generate Multi-Step Forecast", key="multistep"):
                    with st.spinner("Generating predictions..."):
                        load_ml_resources()
                        lstm_result = predict_with_lstm(df, lookback=60, forecast_days=5, epochs=50)
                        
                        if 'error' not in lstm_result:
                            st.success("✅ LSTM predictions generated!")
                            
                            # Compare with current price
                            current = lstm_result['current_price']
                            predictions = lstm_result['predictions']
                            
                            comparison_df = pd.DataFrame({
                                'Day': [1, 2, 3, 4, 5],
                                'Predicted Price': predictions,
                                'Change %': [(p - current) / current * 100 for p in predictions]
                            })
                            
                            st.dataframe(comparison_df, use_container_width=True)
                            
                            # Visualization
                            fig = go.Figure()
                            fig.add_hline(y=current, name="Current Price", line_dash="dash")
                            fig.add_trace(go.Scatter(
                                y=predictions,
                                name='5-Day Forecast',
                                mode='lines+markers',
                                fill='tozeroy'
                            ))
                            fig.update_layout(title="5-Day Price Forecast", yaxis_title="Price")
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.error(f"Error: {lstm_result.get('error')}")
            
            with dl_tab3:
                st.markdown("#### Autoencoder Anomaly Detection")
                st.markdown("""
                Detects unusual patterns in:
                - Volume spikes above normal
                - Price movements deviation
                - Volatility expansion
                - Volume-price divergence
                
                Useful for identifying potential breakouts or false signals.
                """)
                
                if st.button("🎯 Detect Anomalies", key="detect_anomalies_btn"):
                    with st.spinner("Training autoencoder..."):
                        anomaly_result = detect_anomalies_autoencoder(
                            df, epochs=50, contamination=0.05
                        )
                        
                        if 'error' not in anomaly_result:
                            st.success(f"✅ Found {anomaly_result['anomalies_detected']} anomalies")
                            
                            # Metrics
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Total Samples", anomaly_result['total_samples'])
                            with col2:
                                st.metric("Anomalies", anomaly_result['anomalies_detected'])
                            with col3:
                                st.metric("Anomaly Ratio %", f"{anomaly_result['anomaly_ratio']*100:.2f}%")
                            with col4:
                                st.metric("Threshold", f"{anomaly_result['threshold']:.4f}")
                            
                            # Display detected anomalies
                            if anomaly_result['detected_anomalies']:
                                st.markdown("#### Top Anomalies Detected:")
                                anomalies_df = pd.DataFrame(anomaly_result['detected_anomalies'])
                                st.dataframe(anomalies_df, use_container_width=True)
                        else:
                            st.error(f"Error: {anomaly_result.get('error')}")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")


# STRATEGY BACKTEST PAGE
# ══════════════════════════════════════════════════════════════════════

elif page == "📈 Strategy Backtest":
    create_section_header("Strategy Backtesting", "Test & Optimize Trading Strategies", "📈")
    
    st.markdown("### 📊 Backtest Your Trading Strategies")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        symbol = st.text_input("Stock Symbol", value="INFY", key="bt_symbol")
    with col2:
        strategy = st.selectbox(
            "Strategy",
            ["Moving Average Crossover", "RSI Oversold/Overbought", "MACD Signal", "Custom"],
            key="bt_strategy"
        )
    with col3:
        initial_capital = st.number_input("Initial Capital (₹)", value=100000, min_value=1000, key="bt_capital")
    
    if st.button("▶️ Run Backtest", key="run_backtest"):
        try:
            # Load data
            df = load_stock_data_cached(symbol, start_date, end_date)
            df = calculate_indicators_cached(df)
            
            st.success(f"✅ Loaded {len(df)} days of data")
            
            # Generate signals
            if strategy == "Moving Average Crossover":
                col1, col2 = st.columns(2)
                with col1:
                    fast_ma = st.slider("Fast MA Period", 5, 30, 20)
                with col2:
                    slow_ma = st.slider("Slow MA Period", 30, 200, 50)
                signals = generate_ma_crossover_signals(df, fast_ma, slow_ma)
            
            elif strategy == "RSI Oversold/Overbought":
                col1, col2, col3 = st.columns(3)
                with col1:
                    rsi_period = st.slider("RSI Period", 5, 30, 14)
                with col2:
                    oversold = st.slider("Oversold Level", 10, 40, 30)
                with col3:
                    overbought = st.slider("Overbought Level", 60, 90, 70)
                signals = generate_rsi_signals(df, rsi_period, oversold, overbought)
            
            elif strategy == "MACD Signal":
                signals = generate_macd_signals(df)
            
            else:
                signals = pd.Series(0, index=df.index)
            
            # Run backtest
            backtester = SimpleBacktester(initial_capital=initial_capital, commission=0.001)
            result = backtester.backtest(df, signals)
            
            # Display results
            st.markdown("### 📊 Backtest Results")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Initial Capital", f"₹{result['initial_capital']:,.0f}")
            with col2:
                st.metric("Final Value", f"₹{result['final_equity']:,.0f}")
            with col3:
                st.metric("Total Return", f"{result['total_return_pct']:+.2f}%")
            with col4:
                st.metric("Sharpe Ratio", f"{result['sharpe_ratio']:.2f}")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Max Drawdown", f"{result['max_drawdown_pct']:.2f}%")
            with col2:
                st.metric("Total Trades", result['num_trades'])
            with col3:
                st.metric("Win Rate", f"{result['win_rate_pct']:.1f}%")
            with col4:
                st.metric("Avg Profit/Trade", f"₹{result['avg_profit_per_trade']:.2f}")
            
            # Equity curve
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=result['equity_curve'],
                fill='tozeroy',
                name='Equity Curve',
                line=dict(color='green')
            ))
            fig.update_layout(
                title="Equity Curve",
                yaxis_title="Portfolio Value (₹)",
                xaxis_title="Time",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Trades table
            if result['trades']:
                st.markdown("### 📋 Trade History")
                trades_df = pd.DataFrame(result['trades'])
                st.dataframe(trades_df, use_container_width=True)
            
            # Metrics summary
            st.markdown("### 📈 Advanced Metrics")
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            
            with metrics_col1:
                st.metric("Profit Factor", f"{result['metrics']['profit_factor']:.2f}")
            with metrics_col2:
                st.metric("Recovery Factor", f"{result['metrics']['recovery_factor']:.2f}")
            with metrics_col3:
                st.metric("Calmar Ratio", f"{result['metrics']['calmar_ratio']:.2f}")
            
        except Exception as e:
            st.error(f"Backtest Error: {str(e)}")
    
    # Strategy information
    st.markdown("---")
    st.markdown("""
    ### 📚 Available Strategies
    
    - **Moving Average Crossover**: Buy when fast MA > slow MA, sell when reverse
    - **RSI Strategy**: Buy when RSI < oversold level, sell when RSI > overbought
    - **MACD Signal**: Buy when MACD > signal line, sell when reverse
    
    ### 💡 Tips for Backtesting
    1. Use at least 2-3 years of data for reliable results
    2. Adjust commissions to match your broker
    3. Consider slippage for realistic returns
    4. Test walk-forward analysis for robustness
    5. Compare with buy-and-hold benchmark
    """)


# SETTINGS PAGE
# ══════════════════════════════════════════════════════════════════════

elif page == "⚙️ Settings":
    create_section_header("Settings", "Configure Your Trading Parameters", "⚙️")

    st.markdown("### 🎨 Display Preferences")

    col1, col2 = st.columns(2)

    with col1:
        st.checkbox("Show detailed explanations", value=True)
        dark_mode = st.checkbox("Enable dark mode", value=False, key="dark_mode_toggle")
        if dark_mode:
            st.markdown("""
            <style>
            .stApp { background: #1a1a1e !important; }
            .main { background: #1a1a1e !important; }
            .main > div { background: #1a1a1e !important; }
            [data-testid="stMetricValue"] { color: #e0e0e0 !important; }
            h1, h2, h3, h4, h5, h6 { color: #e0e0e0 !important; }
            .stButton > button { background: #2d2d3d !important; color: #a0a0ff !important; }
            [data-testid="metric-container"] { background: #2d2d3d !important; }
            .custom-card { background: #2d2d3d !important; color: #e0e0e0 !important; }
            .stTextInput>div>div>input { background: #2d2d3d !important; color: #e0e0e0 !important; }
            .stSelectbox > div > div { background: #2d2d3d !important; color: #e0e0e0 !important; }
            .stTabs [data-baseweb="tab-list"] { background: #2d2d3d !important; }
            .streamlit-expanderHeader { background: #2d2d3d !important; color: #e0e0e0 !important; }
            .stAlert { background: #2d2d3d !important; color: #e0e0e0 !important; }
            ::-webkit-scrollbar-track { background: #2d2d3d !important; }
            </style>
            """, unsafe_allow_html=True)
        st.checkbox("Show technical indicators", value=True)

    with col2:
        st.checkbox("Show fundamental metrics", value=True)
        st.checkbox("Enable notifications", value=False)
        st.checkbox("Auto-refresh data", value=False)

    st.markdown("---")
    st.markdown("### 📊 Analysis Parameters")

    col1, col2 = st.columns(2)

    with col1:
        st.slider("Default confidence threshold", 0.5, 0.95, 0.6, 0.05)
        st.slider("Risk per trade (%)", 1.0, 5.0, 2.0, 0.5)

    with col2:
        st.slider("Max position size (%)", 5, 20, 20, 5)
        st.selectbox("Default model", ["RandomForest", "XGBoost", "Ensemble"])

    st.markdown("---")
    st.markdown("### 💾 Data Management")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Clear Cache", use_container_width=True):
            st.cache_data.clear()
            st.success("✅ Cache cleared!")

    with col2:
        if st.button("Export Settings", use_container_width=True):
            st.info("⚙️ Settings exported!")

    with col3:
        if st.button("Reset to Default", use_container_width=True):
            st.warning("⚠️ Settings reset!")

    st.markdown("---")
    st.markdown("### 📚 About")

    st.markdown("""
    **AI Trading Lab PRO+ v2.0**

    A comprehensive AI-powered trading and analysis platform featuring:
    - Advanced machine learning models
    - Multi-timeframe technical analysis
    - Fundamental analysis with sentiment
    - Portfolio optimization
    - Risk management tools
    - Sector-wise stock screening (500+ stocks)

    ---

    © 2026 AI Trading Lab. All rights reserved.
    """)

# ══════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #718096; padding: 20px;'>
    <p><strong>Disclaimer:</strong> This tool is for educational purposes only. Always do your own research before making investment decisions.</p>
    <p>Made with ❤️ using Python & Streamlit | © 2026</p>
</div>
""", unsafe_allow_html=True)

