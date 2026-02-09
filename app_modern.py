"""
AI Trading Lab PRO+
Modern UI Application with Enhanced Features
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Import backend modules
from src.data_loader import load_stock_data
from src.fundamental_analysis import get_fundamentals, get_news_sentiment, get_analyst_ratings
from src.technical_indicators import calculate_technical_indicators
from src.feature_engineering import engineer_advanced_features, select_best_features
from src.models import train_random_forest, train_xgboost
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
from src.risk_management import calculate_risk_metrics, calculate_stop_loss_take_profit

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

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# ══════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ══════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="AI Trading Lab PRO+",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

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
    st.markdown('<div style="text-align: right; padding-top: 12px;"><span class="version-badge">⚡ v2.1.1</span></div>', unsafe_allow_html=True)

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

nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns(5)

with nav_col1:
    home_btn = st.button("🏠 Home", use_container_width=True, key="nav_home")
with nav_col2:
    analysis_btn = st.button("📊 Stock Analysis", use_container_width=True, key="nav_analysis")
with nav_col3:
    screener_btn = st.button("🎯 Smart Screener", use_container_width=True, key="nav_screener")
with nav_col4:
    portfolio_btn = st.button("💼 Portfolio Manager", use_container_width=True, key="nav_portfolio")
with nav_col5:
    settings_btn = st.button("⚙️ Settings", use_container_width=True, key="nav_settings")

# Determine active page
if 'active_page' not in st.session_state:
    st.session_state.active_page = "🏠 Home"

if home_btn:
    st.session_state.active_page = "🏠 Home"
elif analysis_btn:
    st.session_state.active_page = "📊 Stock Analysis"
elif screener_btn:
    st.session_state.active_page = "🎯 Smart Screener"
elif portfolio_btn:
    st.session_state.active_page = "💼 Portfolio Manager"
elif settings_btn:
    st.session_state.active_page = "⚙️ Settings"

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

            # Calculate indicators
            stock_data = calculate_technical_indicators(stock_data)
            stock_data.dropna(inplace=True)

            # Get fundamentals
            fundamentals = get_fundamentals(symbol)
            sentiment = get_news_sentiment(symbol)
            analyst_info = get_analyst_ratings(symbol)

            # Price & Target Calculation
            entry_targets = calculate_entry_target_prices(stock_data, fundamentals=fundamentals)

            # ─── PRICE OVERVIEW ───
            st.markdown("### 💹 Price Overview")

            current_price = entry_targets['Current Price']
            entry_price = entry_targets['Entry Price']
            target_price = entry_targets['Target Price']
            stop_loss = entry_targets['Stop Loss']
            rr_ratio = entry_targets['R/R Ratio']

            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                create_metric_card("Current Price", f"₹{current_price:.2f}", icon="💰", color="#667eea")

            with col2:
                create_metric_card("Entry Price", f"₹{entry_price:.2f}", icon="🎯", color="#48bb78")

            with col3:
                create_metric_card("Target Price", f"₹{target_price:.2f}", icon="🚀", color="#38b2ac")

            with col4:
                create_metric_card("Stop Loss", f"₹{stop_loss:.2f}", icon="🛑", color="#f56565")

            with col5:
                create_metric_card("R/R Ratio", f"{rr_ratio:.2f}:1", icon="⚖️", color="#ed8936")

            st.markdown("<br>", unsafe_allow_html=True)

            # ─── SIGNAL & RECOMMENDATION ───
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

            # ─── CHARTS ───
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
                    signal = latest.get('Signal_Line', 0)
                    st.markdown("#### MACD Status")
                    if macd > signal:
                        st.success(f"🟢 Bullish (MACD: {macd:.2f} > Signal: {signal:.2f})")
                    else:
                        st.error(f"🔴 Bearish (MACD: {macd:.2f} < Signal: {signal:.2f})")

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

            # ─── FUNDAMENTALS ───
            if analysis_type in ["Complete", "Fundamental Only"]:
                st.markdown("### 💰 Fundamental Metrics")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    roe = fundamentals.get('ROE', 0)
                    create_metric_card("ROE", f"{roe:.2%}", icon="📊", color="#667eea")

                with col2:
                    pe = fundamentals.get('PE', 0)
                    create_metric_card("P/E Ratio", f"{pe:.1f}", icon="💹", color="#38b2ac")

                with col3:
                    profit_margin = fundamentals.get('ProfitMargin', 0)
                    create_metric_card("Profit Margin", f"{profit_margin:.2%}", icon="💰", color="#48bb78")

                with col4:
                    revenue_growth = fundamentals.get('RevenueGrowth', 0)
                    create_metric_card("Revenue Growth", f"{revenue_growth:.2%}", icon="📈", color="#9f7aea")

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
        # Build stock list
        if screening_mode == "📊 Sector Focus":
            stock_list = get_sector_stocks_from_universe(selected_sector, stocks_limit)
            st.info(f"📊 Screening {len(stock_list)} stocks from {selected_sector} sector...")
        elif screening_mode == "💎 Market Cap Focus":
            stock_list = get_nifty_top_n(n=stocks_limit)
            cap_filter = selected_cap.split()[0].lower() if selected_cap else "all"
            st.info(f"💎 Screening {len(stock_list)} {cap_filter} cap stocks...")
        else:
            stock_list = get_nifty_top_n(n=stocks_limit)
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

                # Get fundamentals
                fundamentals = get_fundamentals(stock_symbol)

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
        df_formatted['Confidence'] = df_formatted['Confidence'].apply(lambda x: f"{x:.1%}")

        # Reorder columns for better display
        column_order = ['Symbol', 'Market Cap', 'Market Cap (Cr)', 'Current Price', 'Entry Price',
                       'Target Price', 'Stop Loss', 'Potential Return %', 'R/R Ratio',
                       'Confidence', 'Recommendation', 'Strength']
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
# PORTFOLIO MANAGER PAGE
# ══════════════════════════════════════════════════════════════════════

elif page == "💼 Portfolio Manager":
    create_section_header("Portfolio Manager", "Build & Optimize Your Investment Portfolio", "💼")

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
                status_text.text(f"Loading {symbol}... ({idx+1}/{len(symbols_list)})")

                # Load data
                stock_data = load_stock_data(symbol, start_date, end_date)

                if stock_data is None or len(stock_data) < 250:
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

                # Calculate fundamental score
                roe = fundamentals.get("ROE", 0)
                growth = fundamentals.get("RevenueGrowth", 0) + fundamentals.get("EPSGrowth", 0)
                margin = fundamentals.get("ProfitMargin", 0)
                pe = fundamentals.get("PE", 50)

                fund_score = (
                    min(roe * 4, 2.0) +
                    min(growth * 2, 1.5) +
                    min(margin * 3, 1.0) -
                    min(pe / 50, 1.0) +
                    sentiment * 0.3
                )

                ai_score = sharpe * 0.5 + fund_score * 0.5

                portfolio_data.append({
                    'Symbol': symbol,
                    'Total Return': total_return,
                    'Annual Volatility': annual_vol,
                    'Sharpe Ratio': sharpe,
                    'Max Drawdown': max_dd,
                    'Fund Score': fund_score,
                    'AI Score': ai_score
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
            st.markdown("### 📊 Portfolio Summary")

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
            st.markdown("### 📋 Detailed Analysis")

            df_display = df_portfolio.copy()
            df_display['Total Return'] = df_display['Total Return'].apply(lambda x: f"{x:.2%}")
            df_display['Annual Volatility'] = df_display['Annual Volatility'].apply(lambda x: f"{x:.2%}")
            df_display['Sharpe Ratio'] = df_display['Sharpe Ratio'].apply(lambda x: f"{x:.2f}")
            df_display['Max Drawdown'] = df_display['Max Drawdown'].apply(lambda x: f"{x:.2%}")
            df_display['Fund Score'] = df_display['Fund Score'].apply(lambda x: f"{x:.2f}")
            df_display['AI Score'] = df_display['AI Score'].apply(lambda x: f"{x:.2f}")

            st.dataframe(df_display, use_container_width=True, hide_index=True)

            # Correlation Heatmap
            if len(returns_dict) > 1:
                st.markdown("### 📊 Correlation Matrix")

                df_returns = pd.DataFrame(returns_dict).dropna()
                corr_matrix = df_returns.corr()

                fig_corr = create_heatmap(corr_matrix, "Portfolio Correlation")
                st.plotly_chart(fig_corr, use_container_width=True)

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
# SETTINGS PAGE
# ══════════════════════════════════════════════════════════════════════

elif page == "⚙️ Settings":
    create_section_header("Settings", "Configure Your Trading Parameters", "⚙️")

    st.markdown("### 🎨 Display Preferences")

    col1, col2 = st.columns(2)

    with col1:
        st.checkbox("Show detailed explanations", value=True)
        st.checkbox("Enable dark mode", value=False)
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

