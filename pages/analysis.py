"""
Stock Analysis page module for AI Trading Lab PRO+
"""
import streamlit as st
import pandas as pd

from ui.components import (
    create_section_header,
    create_info_card,
    create_metric_card,
    create_price_chart,
    create_volume_chart,
    create_gauge_chart,
)

from src.symbol_utils import normalize_symbol
from src.data_loader import load_stock_data
from src.fundamental_analysis import get_fundamentals, get_news_sentiment, get_analyst_ratings
from src.technical_indicators import calculate_technical_indicators, get_trend
from src.price_targets import calculate_entry_target_prices
from src.price_targets_enhanced import (
    calculate_multi_timeframe_levels,
    generate_buy_sell_explanation,
)
from src.risk_management import calculate_risk_metrics


def render_stock_analysis(start_date, end_date):
    """Render the Stock Analysis page. Expects `start_date` and `end_date` from the main app."""
    create_section_header("Stock Analysis", "Comprehensive Technical & Fundamental Analysis", "📊")

    # Input Section
    with st.container():
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

        with col1:
            raw_symbol = st.text_input("Enter Stock Symbol", "RELIANCE.NS", help="e.g., RELIANCE.NS, TCS.NS")
            symbol = normalize_symbol(raw_symbol)

        with col2:
            analysis_type = st.selectbox("Analysis Type", ["Complete", "Technical Only", "Fundamental Only"])

        with col3:
            prediction_days = st.number_input("Prediction Days", 1, 30, 5)

        with col4:
            st.markdown("<br>", unsafe_allow_html=True)
            analyze_button = st.button("🔍 Analyze Stock", type="primary", use_container_width=True)

    if analyze_button and symbol:
        with st.spinner(f"Analyzing {symbol}..."):
            # Load data (ensure symbol normalized)
            try:
                from src.symbol_utils import normalize_symbol as _ns
                load_sym = _ns(symbol)
            except Exception:
                load_sym = symbol
            stock_data = load_stock_data(load_sym, start_date, end_date)

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
                    'Target Price': current_price * 1.15,
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
                            badge_icon = "🟢"
                        elif 'SELL' in recommendation:
                            badge_icon = "🔴"
                        else:
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
