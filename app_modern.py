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
from src.technical_indicators import calculate_technical_indicators, generate_signals, get_trend
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
from src.advanced_ai import (
    calculate_advanced_indicators,
    detect_candlestick_patterns,
    detect_chart_patterns,
    detect_market_regime,
    detect_anomalies,
    create_ensemble_prediction,
    generate_ai_analysis,
    predict_with_lstm,
    analyze_news_sentiment
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

nav_col1, nav_col2, nav_col3, nav_col4, nav_col5, nav_col6 = st.columns(6)

with nav_col1:
    home_btn = st.button("🏠 Home", use_container_width=True, key="nav_home")
with nav_col2:
    analysis_btn = st.button("📊 Analysis", use_container_width=True, key="nav_analysis")
with nav_col3:
    ai_btn = st.button("🤖 AI Deep Analysis", use_container_width=True, key="nav_ai")
with nav_col4:
    screener_btn = st.button("🎯 Screener", use_container_width=True, key="nav_screener")
with nav_col5:
    portfolio_btn = st.button("💼 Portfolio", use_container_width=True, key="nav_portfolio")
with nav_col6:
    settings_btn = st.button("⚙️ Settings", use_container_width=True, key="nav_settings")

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
                    stock_data = calculate_advanced_indicators(stock_data)
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

                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #1e3a8a, #7c3aed); padding: 20px; border-radius: 12px; margin-bottom: 20px;'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div>
                                <h4 style='color: rgba(255,255,255,0.8); margin: 0;'>Ensemble Prediction (5 ML Models)</h4>
                                <h2 style='color: white; margin: 5px 0;'>{ensemble_pred}</h2>
                            </div>
                            <div style='text-align: right;'>
                                <h4 style='color: rgba(255,255,255,0.8); margin: 0;'>Bullish Probability</h4>
                                <h2 style='color: white; margin: 5px 0;'>{ml_results.get('bullish_probability', 0):.1%}</h2>
                            </div>
                        </div>
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

