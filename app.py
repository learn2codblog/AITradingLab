import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from src.data_loader import load_stock_data
from src.fundamental_analysis import get_fundamentals, get_news_sentiment, get_analyst_ratings
from src.technical_indicators import calculate_technical_indicators
from src.feature_engineering import engineer_advanced_features, select_best_features
from src.models import train_random_forest, train_xgboost, train_gradient_boosting, build_lstm_model, build_dense_model
from src.metrics import sharpe_ratio, backtest_strategy, max_drawdown
from src.portfolio_optimizer import optimize_portfolio
from src.price_targets import calculate_entry_target_prices, get_nifty50_constituents, screening_is_buy_signal
from src.price_targets_enhanced import (
    calculate_multi_timeframe_levels,
    generate_buy_sell_explanation,
    get_nifty50_by_sector,
    get_all_nifty50,
    get_nifty_top_n,
    get_sector_stocks_from_universe,
    get_all_available_sectors,
)
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix, roc_auc_score
from tensorflow.keras.callbacks import EarlyStopping

# ────────────────────────────────────────────────
# Page header + top control panel (moved from sidebar for modern UI)
# ────────────────────────────────────────────────
st.set_page_config(page_title="AI Trading Lab PRO+", layout="wide")
st.title("🚀 AI Trading Lab PRO+ – Enhanced ML/DL/Fundamentals/Portfolio/Sentiment")

# Top control panel
with st.container():
    c1, c2 = st.columns([2, 1])
    with c1:
        symbol = st.text_input("Main Stock Symbol", "RELIANCE.NS").upper().strip()
        symbols_compare = st.text_area(
            "Portfolio Stocks (comma separated)",
            "RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, ICICIBANK.NS"
        )
        index_symbol = st.text_input("Benchmark Index", "^NSEI")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", pd.to_datetime("2010-01-01"))
        with col2:
            end_date = st.date_input("End Date", pd.to_datetime("today"))
        future_days = st.slider("Prediction Horizon (days)", 1, 30, 5)
        model_type = st.selectbox("Model", ["RandomForest", "XGBoost"])
    
    with c2:
        st.subheader("Screener & Actions")
        screener_type = st.radio("Universe:", ["Top N (file)", "By Sector"], index=0)

        # Get all available sectors (from enhanced database)
        all_sectors = get_all_available_sectors()
        selected_sector = None
        sector_universe_size = 100  # Default for sector screening

        universe_size = st.number_input("Universe Size (for Top N)", min_value=50, max_value=500, value=50, step=50)

        if screener_type == "By Sector":
            selected_sector = st.selectbox("Choose Sector:", all_sectors)
            sector_universe_size = st.number_input(
                "Max stocks per sector",
                min_value=5,
                max_value=200,
                value=50,
                step=10,
                help="Number of stocks to analyze from this sector"
            )
            st.info(f"📊 Analyzing from comprehensive stock database (beyond Nifty 50)")

        confidence_thresh = st.slider("Confidence Threshold for Signals", 0.5, 0.95, 0.6)
        portfolio_size = st.number_input("Portfolio Size (use first N symbols)", min_value=1, max_value=400, value=5)
        allow_small_dataset = st.checkbox("Allow small dataset (proceed with warning)", value=False)
        st.markdown("---")
        run_button = st.button("Run Full Analysis", type="primary")
        fundamental_btn = st.button("Run Fundamental Analysis")
        technical_btn = st.button("Run Technical Analysis")
        portfolio_btn = st.button("Run Portfolio Analysis")
        nifty50_btn = st.button("🎯 Screener", type="secondary")

# ────────────────────────────────────────────────
#  MAIN LOGIC
# ────────────────────────────────────────────────
# --- FUNDAMENTAL ONLY
if fundamental_btn:
    if not symbol:
        st.error("Please enter a valid main stock symbol for fundamental analysis.")
        st.stop()
    st.subheader(f"Fundamental Analysis – {symbol}")
    with st.spinner("Fetching fundamentals and sentiment..."):
        fund = get_fundamentals(symbol)
        sentiment = get_news_sentiment(symbol)
        analyst = get_analyst_ratings(symbol)
    fund_display = {
        "ROE": f"{fund.get('ROE', 0):.2%}",
        "Trailing P/E": f"{fund.get('PE', 0):.1f}",
        "Profit Margin": f"{fund.get('ProfitMargin', 0):.2%}",
        "Revenue Growth": f"{fund.get('RevenueGrowth', 0):.2%}",
        "EPS Growth": f"{fund.get('EPSGrowth', 0):.2%}",
        "Beta": f"{fund.get('Beta', 1):.2f}",
        "Market Cap (Cr)": f"{fund.get('MarketCap', 0) / 1e7:,.1f}",
        "News Sentiment": f"{sentiment:.2f} (heuristic)",
        "Analyst Target": f"{analyst.get('TargetPrice', 'N/A')}",
        "Analyst Rec": f"{analyst.get('RecommendationKey', 'N/A')}"
    }
    st.table(pd.Series(fund_display, name="Value"))

# --- TECHNICAL ONLY
if technical_btn:
    if not symbol:
        st.error("Please enter a valid main stock symbol for technical analysis.")
        st.stop()
    st.subheader(f"Technical Analysis – {symbol}")
    with st.spinner("Loading data and calculating indicators..."):
        stock = load_stock_data(symbol, start_date, end_date)
        if stock is None or len(stock) < 30:
            st.error("Could not load sufficient price history for technical analysis.")
            st.stop()
        stock = calculate_technical_indicators(stock)
        stock.dropna(inplace=True)

    # Compute supports/resistances (20,50,200 day)
    s20 = stock['Low'].rolling(20).min().iloc[-1]
    r20 = stock['High'].rolling(20).max().iloc[-1]
    s50 = stock['Low'].rolling(50).min().iloc[-1]
    r50 = stock['High'].rolling(50).max().iloc[-1]
    s200 = stock['Low'].rolling(200).min().iloc[-1] if len(stock) >= 200 else np.nan
    r200 = stock['High'].rolling(200).max().iloc[-1] if len(stock) >= 200 else np.nan

    latest = stock.iloc[-1]
    price = latest['Close']
    trend = 'Neutral'
    # Simple trend logic
    if price > latest.get('SMA200', price) and latest.get('SMA50', price) > latest.get('SMA200', price):
        trend = 'Strong Bullish'
    elif price > latest.get('SMA50', price) and latest.get('SMA20', price) > latest.get('SMA50', price):
        trend = 'Bullish'
    elif price < latest.get('SMA200', price):
        trend = 'Bearish'

    st.markdown(f"**Latest Close:** ₹{price:.2f}")
    st.markdown(f"**Trend:** {trend}")

    # Calculate Entry/Target Prices
    fundamentals = get_fundamentals(symbol)
    entry_targets = calculate_entry_target_prices(stock, fundamentals=fundamentals)
    
    # Display Entry/Target Information
    st.subheader("📍 Entry & Target Levels")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Price", f"₹{entry_targets['Current Price']:.2f}")
    with col2:
        st.metric("Entry Price", f"₹{entry_targets['Entry Price']:.2f}")
    with col3:
        st.metric("Target Price", f"₹{entry_targets['Target Price']:.2f}")
    with col4:
        st.metric("Stop Loss", f"₹{entry_targets['Stop Loss']:.2f}")
    
    # Risk/Reward Display
    st.subheader("⚖️ Risk Analysis")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Risk Amount", f"₹{entry_targets['Risk Amount']:.2f}")
    with col2:
        st.metric("Reward Amount", f"₹{entry_targets['Reward Amount']:.2f}")
    with col3:
        st.metric("R/R Ratio", f"{entry_targets['R/R Ratio']:.2f}:1")
    
    # Confidence Score
    st.subheader("💪 Signal Strength")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### {entry_targets['Strength']}")
        st.markdown(f"**Confidence Score:** {entry_targets['Confidence Score']:.1%}")
    with col2:
        st.write("**Reasons:**")
        st.markdown(entry_targets['Confidence Reasons'])

    # ─── Multi-timeframe Analysis ──────────────────────────
    st.subheader('📈 Multi-Timeframe Support & Resistance')
    
    try:
        mtf_levels = calculate_multi_timeframe_levels(stock)
        mtf_rows = []
        for timeframe, levels in mtf_levels.items():
            support = levels.get('Support', 0)
            resistance = levels.get('Resistance', 0)
            dist_sup = levels.get('Distance to Support', 0)
            dist_res = levels.get('Distance to Resistance', 0)
            mtf_rows.append({
                'Timeframe': timeframe,
                'Support': f"₹{support:.2f}",
                'Dist to Support %': f"{dist_sup:.2f}%",
                'Resistance': f"₹{resistance:.2f}",
                'Dist to Resistance %': f"{dist_res:.2f}%",
            })
        mtf_df = pd.DataFrame(mtf_rows)
        st.dataframe(mtf_df, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not calculate multi-timeframe levels: {str(e)}")
    
    st.subheader('Support & Resistance (Standard)')
    sr_df = pd.DataFrame({
        'Period': ['20d', '50d', '200d'],
        'Support': [f"₹{s20:.2f}", f"₹{s50:.2f}", f"₹{s200:.2f}" if not np.isnan(s200) else 'N/A'],
        'Resistance': [f"₹{r20:.2f}", f"₹{r50:.2f}", f"₹{r200:.2f}" if not np.isnan(r200) else 'N/A']
    })
    st.table(sr_df)
    
    # ─── Detailed Buy/Sell Explanation ──────────────────────
    st.subheader('🎯 Buy/Sell/Hold Recommendation')
    
    try:
        fundamentals = get_fundamentals(symbol)
        explanation = generate_buy_sell_explanation(stock, fundamentals)

        # Display recommendation with emoji
        emoji_map = {
            '🟢 STRONG BUY': '🟢',
            '🟡 BUY': '🟡',
            '🟠 HOLD / ACCUMULATE ON DIPS': '🟠',
            '🔴 STRONG SELL / AVOID': '🔴',
            '🔴 SELL / EXIT': '🔴',
            '➖ HOLD / WAIT': '⚪'
        }

        rec_text = explanation.get('Recommendation', '')
        rec_emoji = emoji_map.get(rec_text, '⚪')

        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"### {rec_emoji}")
            st.markdown(f"**{rec_text}**")
        with col2:
            st.markdown(f"**Action:** {explanation.get('Action', '')}")
            st.markdown(f"**Explanation:** {explanation.get('Main Explanation', '')}")

        # Display signals
        col1, col2, col3 = st.columns(3)

        with col1:
            bullish = explanation.get('Bullish Signals', [])
            if bullish:
                st.markdown("**✅ Bullish Signals:**")
                for signal in bullish:
                    st.markdown(f"  • {signal}")
            else:
                st.markdown("**✅ Bullish Signals:** None")

        with col2:
            bearish = explanation.get('Bearish Signals', [])
            if bearish:
                st.markdown("**❌ Bearish Signals:**")
                for signal in bearish:
                    st.markdown(f"  • {signal}")
            else:
                st.markdown("**❌ Bearish Signals:** None")

        with col3:
            neutral = explanation.get('Neutral Signals', [])
            if neutral:
                st.markdown("**⚪ Neutral Signals:**")
                for signal in neutral:
                    st.markdown(f"  • {signal}")
            else:
                st.markdown("**⚪ Neutral Signals:** None")
    except Exception as e:
        st.warning(f"Could not generate detailed explanation: {str(e)}")
    
    st.subheader('Key Levels')
    levels_df = pd.DataFrame({
        'Level': ['Support (20d)', 'SMA20', 'SMA50', 'SMA200', 'Resistance (20d)'],
        'Price': [
            f"₹{entry_targets['Support (20d)']:.2f}",
            f"₹{entry_targets['SMA20']:.2f}",
            f"₹{entry_targets['SMA50']}" if entry_targets['SMA50'] != 'N/A' else 'N/A',
            f"₹{entry_targets['SMA200']}" if entry_targets['SMA200'] != 'N/A' else 'N/A',
            f"₹{entry_targets['Resistance (20d)']:.2f}"
        ]
    })
    st.table(levels_df)

# --- NIFTY 50 SCREENER
if nifty50_btn:
    # Build universe
    if screener_type == "By Sector" and selected_sector:
        st.subheader(f"🎯 Screener – {selected_sector} Sector (Enhanced Universe)")
        # Use the enhanced function that pulls from larger database
        universe = get_sector_stocks_from_universe(selected_sector, sector_universe_size)
        st.info(f"📊 Analyzing {len(universe)} stocks from {selected_sector} sector (beyond Nifty 50)")
    else:
        st.subheader(f"🎯 Screener – Universe (top {universe_size} if available)")
        universe = get_nifty_top_n(n=universe_size)
        st.info(f"Scanning {len(universe)} symbols from universe file or Nifty 50.")

    if len(universe) == 0:
        st.warning(f"No stocks found for sector: {selected_sector}")
        st.stop()

    st.info(f"This may take a few minutes for {len(universe)} stocks...")

    screening_results = []
    all_results = []
    progress = st.progress(0)
    progress_text = st.empty()

    for i, sym in enumerate(universe):
        progress_text.text(f"Analyzing {sym}... ({i+1}/{len(universe)})")
        try:
            df = load_stock_data(sym, start_date, end_date)
            if df is None or len(df) < 60:
                all_results.append({'Symbol': sym, 'Status': 'Insufficient data'})
                progress.progress((i+1)/len(universe))
                continue

            df = calculate_technical_indicators(df)
            df = df.dropna()
            if len(df) == 0:
                all_results.append({'Symbol': sym, 'Status': 'No indicators'})
                progress.progress((i+1)/len(universe))
                continue

            fund = get_fundamentals(sym)
            entry_targets = calculate_entry_target_prices(df, fundamentals=fund)
            current_price = entry_targets.get('Current Price', np.nan)

            # Verbose explanation for each stock
            try:
                explanation = generate_buy_sell_explanation(df, fund)
            except Exception:
                explanation = {}

            is_buy = screening_is_buy_signal(entry_targets, current_price, margin=0.02)

            row = {
                'Symbol': sym,
                'Current Price': current_price,
                'Entry Price': entry_targets.get('Entry Price', np.nan),
                'Target Price': entry_targets.get('Target Price', np.nan),
                'Stop Loss': entry_targets.get('Stop Loss', np.nan),
                'R/R Ratio': entry_targets.get('R/R Ratio', np.nan),
                'Confidence': entry_targets.get('Confidence Score', np.nan),
                'Strength': entry_targets.get('Strength', ''),
                'Is_Buy': bool(is_buy),
                'Bullish_Count': explanation.get('Bullish Count', len(explanation.get('Bullish Signals', []))),
                'Bearish_Count': explanation.get('Bearish Count', len(explanation.get('Bearish Signals', []))),
                'Main_Explanation': explanation.get('Main Explanation', '')
            }

            all_results.append(row)

            if is_buy:
                screening_results.append(row)

        except Exception as e:
            all_results.append({'Symbol': sym, 'Status': f'Error: {str(e)[:80]}'} )

        progress.progress((i+1)/len(universe))

    progress.empty()
    progress_text.empty()

    all_df = pd.DataFrame(all_results)
    if not all_df.empty:
        st.subheader("🔎 Scan Summary")
        st.dataframe(all_df[['Symbol', 'Is_Buy', 'Confidence', 'Bullish_Count', 'Bearish_Count', 'Main_Explanation']].fillna('N/A'), use_container_width=True)
        st.download_button(label="📥 Download Full Scan", data=all_df.to_csv(index=False), file_name=f"screener_scan_{pd.Timestamp.now().date()}.csv", mime="text/csv")

    if screening_results:
        screening_df = pd.DataFrame(screening_results)
        screening_df = screening_df.sort_values('Confidence', ascending=False)
        st.subheader(f"✅ Found {len(screening_df)} Buy Opportunities")
        st.dataframe(screening_df, use_container_width=True)
        st.download_button(label="📥 Download Buy Results", data=screening_df.to_csv(index=False), file_name=f"screener_buys_{pd.Timestamp.now().date()}.csv", mime="text/csv")

        st.subheader("📊 Top 5 Recommendations")
        top5 = screening_df.head(5)
        for idx, row in top5.iterrows():
            with st.expander(f"{row['Symbol']} - {row.get('Strength','')} (Confidence {row.get('Confidence','')})"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Current", f"₹{row['Current Price']:.2f}")
                with col2:
                    st.metric("Entry", f"₹{row['Entry Price']:.2f}")
                with col3:
                    st.metric("Target", f"₹{row['Target Price']:.2f}")
                with col4:
                    st.metric("R/R", f"{row['R/R Ratio']:.2f}:1")
                st.write(f"**Upside Potential:** {((row['Target Price'] - row['Current Price']) / row['Current Price'] * 100):.1f}%")
    else:
        st.warning("No buy signals found in current market conditions for the selected universe.")
        # Show top candidates by bullish_count even if none flagged as buy
        if not all_df.empty:
            cand = all_df.sort_values(['Bullish_Count','Bearish_Count'], ascending=[False, True]).head(10)
            st.subheader("Top candidates to watch")
            st.dataframe(cand[['Symbol','Is_Buy','Bullish_Count','Bearish_Count','Confidence']].fillna('N/A'), use_container_width=True)

# --- PORTFOLIO ONLY
if portfolio_btn:
    st.subheader('Portfolio Analysis')
    symbols_list = [s.strip().upper() for s in symbols_compare.split(',') if s.strip()][:portfolio_size]
    if not symbols_list:
        st.error('Please provide portfolio symbols in the sidebar input.')
        st.stop()

    recommendations = []
    progress = st.progress(0)
    for i, sym in enumerate(symbols_list):
        df = load_stock_data(sym, start_date, end_date)
        if df is None or len(df) < 60:
            recommendations.append({'Symbol': sym, 'Recommendation': 'Insufficient data'})
            progress.progress((i+1)/len(symbols_list))
            continue

        # Fundamental score with robust NaN handling
        f = get_fundamentals(sym)
        sent = get_news_sentiment(sym)
        
        # Replace NaN with safe defaults (neutral, non-penalizing)
        def safe_val(val, default):
            return default if pd.isna(val) else float(val)
        
        roe = safe_val(f.get('ROE'), 0.0)
        growth = safe_val(f.get('RevenueGrowth'), 0.0) + safe_val(f.get('EPSGrowth'), 0.0)
        margin = safe_val(f.get('ProfitMargin'), 0.0)
        pe = safe_val(f.get('PE'), 20.0)  # Default to moderate PE (not expensive)
        beta = safe_val(f.get('Beta'), 1.0)
        sentiment = sent if not pd.isna(sent) else 0.0
        
        # Check if fundamentals are available (at least some non-default values)
        fund_available = not (pd.isna(f.get('ROE')) and pd.isna(f.get('PE')) and pd.isna(f.get('RevenueGrowth')))
        
        # Calculate fundamental score with safeguards
        fund_score = (
            min(roe * 4, 2.0) +
            min(growth * 2, 1.5) +
            min(margin * 3, 1.0) -
            min(pe / 50, 1.0) -
            max(beta - 1.2, 0) * 0.5 +
            sentiment * 0.3
        )

        # Technical trend and normalized technical score
        df = calculate_technical_indicators(df)
        df = df.dropna()
        latest = df.iloc[-1]

        # Component scores for technicals
        sma_alignment = 1.0 if (latest.get('SMA5', 0) > latest.get('SMA20', 0) and latest.get('SMA20', 0) > latest.get('SMA50', 0)) else 0.0
        ema_cross = 1.0 if latest.get('EMA12', 0) > latest.get('EMA26', 0) else 0.0
        macd_pos = 1.0 if latest.get('MACD', 0) > 0 else 0.0
        rsi14 = latest.get('RSI14', 50)
        rsi_score = min(max((rsi14 - 30) / 40, 0.0), 1.0)  # maps [30,70] -> [0,1]
        vol_ratio = latest.get('Volume_Ratio', 1.0)
        vol_score = min(max((vol_ratio - 1.0) / 2.0, 0.0), 1.0)

        tech_raw = sma_alignment * 1.5 + ema_cross * 0.8 + macd_pos * 0.7 + rsi_score * 1.0 + vol_score * 0.5
        tech_norm = tech_raw / 4.5  # normalize to ~0-1

        # Normalize fundamental score (approximate mapping)
        fund_norm = min(max((fund_score + 1.0) / 3.0, 0.0), 1.0)

        # Weighted combination (adjust weights if fundamentals unavailable)
        if fund_available:
            # Normal weighting: 60% technical, 40% fundamental
            combined = 0.6 * tech_norm + 0.4 * fund_norm
        else:
            # If fundamentals missing, weight technical higher
            combined = 0.75 * tech_norm + 0.25 * fund_norm
            
        # Recommendation thresholds
        if combined >= 0.65:
            rec = 'Hold'
        elif combined >= 0.45:
            rec = 'Watch / Partial Hold'
        else:
            rec = 'Consider Sell'
        
        # Add note if fundamentals unavailable
        fund_note = '' if fund_available else ' [Limited Fund Data]'

        recommendations.append({
            'Symbol': sym,
            'FundScore': round(fund_score, 2) if fund_available else 'N/A',
            'FundNorm': round(fund_norm, 2) if fund_available else 'N/A',
            'TechNorm': round(tech_norm, 2),
            'Combined': round(combined, 2),
            'Recommendation': rec + fund_note
        })
        progress.progress((i+1)/len(symbols_list))
    progress.empty()

    st.table(pd.DataFrame(recommendations))
    
    # Explanation box
    with st.expander("📊 How Portfolio Scoring Works"):
        st.markdown("""
        ### Scoring Components:
        
        **FundNorm (Fundamental Score 0-1)**
        - Based on: ROE, Revenue Growth, Profit Margin, PE Ratio, Beta, News Sentiment
        - **N/A** = Robust fundamentals data not available for this stock (common for international/small stocks)
        - When unavailable: System uses only technical trend (75% weight instead of 40%)
        
        **TechNorm (Technical Score 0-1)**
        - Based on: SMA Alignment, EMA Crossover, MACD, RSI, Volume Trend
        - Available for all stocks with sufficient price history
        
        **Combined Score**
        - **With fundamentals**: Combined = 60% Tech + 40% Fund
        - **Without fundamentals**: Combined = 75% Tech + 25% Fund (technical signals weighted higher)
        - Range: 0.0 (Bearish) to 1.0 (Bullish)
        
        ### Recommendations:
        - **Hold** (≥0.65): Strong buy/hold signal across metrics
        - **Watch/Partial Hold** (0.45-0.65): Mixed signals, monitor closely
        - **Consider Sell** (<0.45): Weak technicals or poor fundamentals
        
        ### Key Points:
        - **[Limited Fund Data]** means fundamentals weren't available, recommendation is based primarily on price trends
        - This is normal for many stocks and doesn't mean "avoid" – just that company metrics weren't fetchable
        - Technical analysis alone can still provide valid trading signals
        """)

    # Aggregate guidance
    recs = [r['Recommendation'] for r in recommendations if 'Recommendation' in r]
    sell_count = sum(1 for r in recs if 'Sell' in r)
    hold_count = sum(1 for r in recs if 'Hold' in r and 'Partial' not in r)
    if sell_count > hold_count:
        st.warning('Portfolio-level suggestion: Review holdings, several stocks flagged for selling.')
    else:
        st.success('Portfolio-level suggestion: No urgent sell signals; consider holding or monitoring.')

# Full analysis (existing flow)
if run_button:
    if not symbol:
        st.error("Please enter a valid main stock symbol.")
        st.stop()

    with st.spinner(f"Loading data for {symbol} and benchmark..."):
        stock = load_stock_data(symbol, start_date, end_date)
        index_data = load_stock_data(index_symbol, start_date, end_date)
        if stock is None or len(stock) < 300:
            st.error(f"Could not load sufficient data for {symbol}")
            st.stop()
        if index_data is None:
            st.warning("Could not load benchmark index; skipping relative features.")

    # Dynamic minimum history calculation (accounts for long rolling windows)
    required_lookback = max(200, 252)  # SMA200 and 252-day rolling beta
    required_min = max(300, required_lookback + int(future_days) + 20)

    if len(stock) < required_min and not allow_small_dataset:
        st.error(
            f"Insufficient historical data: need at least {required_min} days for indicators (found {len(stock)}). "
            "Increase the date range or enable 'Allow small dataset' in the sidebar to proceed with reduced data."
        )
        st.stop()
    elif len(stock) < required_min and allow_small_dataset:
        st.warning(
            f"Proceeding with smaller dataset ({len(stock)} days). Some indicators will be truncated and model performance may be degraded."
        )

    # ─── Technical Indicators ───────────────────────────────
    stock = calculate_technical_indicators(stock)
    
    # Fill NaN values from technical indicators (common for early rows in rolling windows)
    # Use backfill first, then forward fill for any remaining NaNs
    tech_cols = [col for col in stock.columns if col not in ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']]
    stock[tech_cols] = stock[tech_cols].bfill().ffill()

    # ─── Advanced Feature Engineering ───────────────────────
    with st.spinner("Engineering features..."):
        # Get fundamental metrics for feature creation
        fundamentals = get_fundamentals(symbol)
        
        # Engineer advanced features
        stock = engineer_advanced_features(
            stock,
            fundamentals=fundamentals,
            index_data=index_data if index_data is not None else None
        )
    
    # Fill NaN values intelligently instead of dropping them
    initial_rows = len(stock)
    
    # First, identify and remove columns with >70% NaN (truly broken features)
    nan_ratio = stock.isna().sum() / len(stock)
    broken_cols = nan_ratio[nan_ratio > 0.7].index.tolist()
    if broken_cols:
        st.warning(f"Removing {len(broken_cols)} features with >70% missing values")
        stock = stock.drop(columns=broken_cols)
    
    # Fill remaining NaN values with forward fill then backward fill
    stock = stock.ffill().bfill()
    
    rows_after_engineering = len(stock)
    
    if rows_after_engineering == 0:
        st.error(
            f"Feature engineering resulted in 0 usable rows (started with {initial_rows}). "
            "This is unexpected. Enable 'Allow small dataset' in the sidebar to use raw data without full feature engineering."
        )
        st.stop()
    else:
        st.info(f"Feature engineering complete: {initial_rows} rows → {rows_after_engineering} rows (removed broken features, filled NaNs)")

    # ─── Target Variable ───────────────────────────────────
    stock['Future_Ret'] = stock['Close'].pct_change(periods=future_days).shift(-future_days)
    median_ret = stock['Future_Ret'].median()
    stock['Target'] = (stock['Future_Ret'] > median_ret).astype(int)
    
    # Drop ONLY rows where Target is NaN (end of series)
    # Don't drop all NaNs, just the target NaNs which indicate incomplete forward-looking data
    stock = stock[stock['Target'].notna()].copy()
    
    rows_before_target = rows_after_engineering
    rows_after_target = len(stock)
    
    if rows_after_target < rows_before_target:
        st.info(f"Target creation: Dropped {rows_before_target - rows_after_target} rows (forward-looking period), {rows_after_target} rows remain for training.")

    # Final data sufficiency check after engineering
    final_min = 50  # absolute minimum rows required to train/test
    if len(stock) < final_min:
        st.warning(f"Not enough data after processing to train the model (need at least {final_min} rows, found {len(stock)}).")
        st.stop()

    # If original required_min was not met and user didn't allow small dataset, stop earlier
    if len(stock) < required_min and not allow_small_dataset:
        st.warning(
            f"Not enough data after processing for full indicator set (need ~{required_min} rows, found {len(stock)}).\n"
            "Enable 'Allow small dataset' in the sidebar to proceed anyway (results may be degraded)."
        )
        st.stop()

    # ─── Feature Selection ──────────────────────────────────
    # Final NaN check and fill before feature selection
    remaining_nans = stock.isna().sum().sum()
    if remaining_nans > 0:
        st.warning(f"Filling {remaining_nans} remaining NaN values before feature selection")
        stock = stock.ffill().bfill()
    
    # Exclude target and price columns
    exclude_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Target', 'Future_Ret']
    all_features = [col for col in stock.columns if col not in exclude_cols]
    
    # Select best features (prioritized)
    selected_features = select_best_features(all_features, max_features=60)
    
    st.info(f"Using {len(selected_features)} engineered features for model training")

    X = stock[selected_features]
    y = stock['Target']

    # ─── Model Training ─────────────────────────────────────
    st.subheader(f"{model_type} Model – {symbol}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, shuffle=False
    )

    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc = scaler.transform(X_test)

    # Model Selection and Training
    with st.spinner(f"Training {model_type}..."):
        if model_type == "RandomForest":
            model = train_random_forest(X_train_sc, y_train, n_estimators=500, max_depth=15)
        elif model_type == "XGBoost":
            model = train_xgboost(X_train_sc, y_train, n_estimators=500, max_depth=8, learning_rate=0.05)
        
        preds = model.predict(X_test_sc)
        probs = model.predict_proba(X_test_sc)[:, 1]

    # ─── Enhanced Model Evaluation ──────────────────────────
    acc = accuracy_score(y_test, preds)
    precision = precision_score(y_test, preds, zero_division=0)
    recall = recall_score(y_test, preds, zero_division=0)
    f1 = f1_score(y_test, preds, zero_division=0)
    roc_auc = roc_auc_score(y_test, probs)

    # Display metrics in columns
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Accuracy", f"{acc:.2%}")
    with col2:
        st.metric("Precision", f"{precision:.2%}")
    with col3:
        st.metric("Recall", f"{recall:.2%}")
    with col4:
        st.metric("F1-Score", f"{f1:.2%}")
    with col5:
        st.metric("ROC-AUC", f"{roc_auc:.2%}")

    # Classification Report
    col_rep1, col_rep2 = st.columns(2)
    with col_rep1:
        st.text("📊 Classification Report:")
        st.text(classification_report(y_test, preds, zero_division=0))
    with col_rep2:
        st.text("🔲 Confusion Matrix:")
        st.text(confusion_matrix(y_test, preds))

    # Feature Importance
    if hasattr(model, 'feature_importances_'):
        st.subheader("Feature Importance (Top 15)")
        feature_imp = pd.DataFrame({
            'Feature': selected_features,
            'Importance': model.feature_importances_
        }).sort_values('Importance', ascending=False).head(15)
        
        fig_imp, ax_imp = plt.subplots(figsize=(10, 6))
        ax_imp.barh(feature_imp['Feature'], feature_imp['Importance'], color='steelblue')
        ax_imp.set_xlabel('Importance Score')
        ax_imp.invert_yaxis()
        st.pyplot(fig_imp)

    # ─── Backtest ──────────────────────────────────────────
    test_df = stock.loc[X_test.index].copy()
    test_df['Pred'] = preds
    test_df['Prob'] = probs
    test_df['Mkt_Ret'] = test_df['Close'].pct_change()
    
    # Long-only with confidence threshold
    test_df['Position'] = np.where(test_df['Prob'].shift(1) > confidence_thresh, 1, 0)
    test_df['Strat_Ret'] = test_df['Mkt_Ret'] * test_df['Position']

    eq_market = (1 + test_df['Mkt_Ret']).cumprod()
    eq_strategy = (1 + test_df['Strat_Ret']).cumprod()

    st.subheader("Strategy vs Buy & Hold")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(eq_market, label="Buy & Hold", linewidth=2)
    ax.plot(eq_strategy, label="AI Strategy", linewidth=2)
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

    strat_sharpe = sharpe_ratio(test_df['Strat_Ret'].dropna())
    strat_sortino = max_drawdown(test_df['Strat_Ret'].dropna())
    strat_dd = max_drawdown(test_df['Strat_Ret'].dropna())
    mkt_sharpe = sharpe_ratio(test_df['Mkt_Ret'].dropna())

    col1, col2, col3 = st.columns(3)
    col1.metric("Strategy Sharpe", f"{strat_sharpe:.2f}", delta=f"{strat_sharpe - mkt_sharpe:.2f} vs market")
    col2.metric("Max Drawdown", f"{strat_dd:.1%}")
    col3.metric("Sortino", f"{strat_sortino:.2f}")

    # ─── Fundamentals & Sentiment ──────────────────────────
    st.subheader(f"Fundamentals & Sentiment – {symbol}")
    fund = get_fundamentals(symbol)
    sentiment = get_news_sentiment(symbol)

    fund_display = {
        "ROE": f"{fund.get('ROE', 0):.2%}",
        "Trailing P/E": f"{fund.get('PE', 0):.1f}",
        "Profit Margin": f"{fund.get('ProfitMargin', 0):.2%}",
        "Revenue Growth": f"{fund.get('RevenueGrowth', 0):.2%}",
        "EPS Growth": f"{fund.get('EPSGrowth', 0):.2%}",
        "Beta": f"{fund.get('Beta', 1):.2f}",
        "Market Cap (Cr)": f"{fund.get('MarketCap', 0) / 1e7:,.1f}",
        "News Sentiment": f"{sentiment:.2f} (heuristic score)"
    }

    st.table(pd.Series(fund_display, name="Value"))

    # ─── Portfolio Optimization ──────────────────────────
    st.subheader("AI Portfolio Analysis")
    symbols_list = [s.strip().upper() for s in symbols_compare.split(",") if s.strip()]
    
    portfolio_rows = []
    returns_dict = {}

    progress = st.progress(0)
    for i, sym in enumerate(symbols_list):
        df = load_stock_data(sym, start_date, end_date)
        if df is None or len(df) < 250:
            continue

        ret_series = df['Close'].pct_change().dropna()
        total_return = (df['Close'][-1] / df['Close'][0]) - 1
        ann_vol = ret_series.std() * np.sqrt(252)
        ann_sharpe = sharpe_ratio(ret_series)

        f = get_fundamentals(sym)
        sent = get_news_sentiment(sym)

        # Enhanced fundamental score
        roe = f.get("ROE", 0)
        growth = f.get("RevenueGrowth", 0) + f.get("EPSGrowth", 0)
        margin = f.get("ProfitMargin", 0)
        pe = f.get("PE", 50)
        beta = f.get("Beta", 1.0)

        fund_score = (
            min(roe * 4, 2.0) +
            min(growth * 2, 1.5) +
            min(margin * 3, 1.0) -
            min(pe / 50, 1.0) -
            max(beta - 1.2, 0) * 0.5 +
            sent * 0.3
        )

        portfolio_rows.append({
            "Symbol": sym,
            "Total Return": total_return,
            "Ann Volatility": ann_vol,
            "Sharpe": ann_sharpe,
            "Fund+Sent Score": fund_score,
            "AI Score": ann_sharpe * 0.5 + fund_score * 0.5
        })

        returns_dict[sym] = ret_series

        progress.progress((i + 1) / max(1, len(symbols_list)))

    progress.empty()

    if portfolio_rows:
        df_port = pd.DataFrame(portfolio_rows)
        df_port = df_port.sort_values("AI Score", ascending=False)

        st.dataframe(
            df_port.style.format({
                "Total Return": "{:.1%}",
                "Ann Volatility": "{:.1%}",
                "Sharpe": "{:.2f}",
                "Fund+Sent Score": "{:.2f}",
                "AI Score": "{:.2f}"
            })
        )

        # Correlation Heatmap
        if len(returns_dict) > 1:
            df_returns = pd.DataFrame(returns_dict).dropna()
            corr = df_returns.corr()

            st.subheader("Portfolio Correlation")
            fig_corr, ax_corr = plt.subplots(figsize=(8, 6))
            cax = ax_corr.matshow(corr, cmap='coolwarm')
            fig_corr.colorbar(cax)
            ax_corr.set_xticklabels([''] + list(corr.columns), rotation=45)
            ax_corr.set_yticklabels([''] + list(corr.index))
            st.pyplot(fig_corr)

        # Simple Efficient Frontier / Weights (mean-variance optimization)
        if len(returns_dict) >= 2:
            st.subheader("Optimized Portfolio Weights")
            opt_weights = optimize_portfolio(returns_dict)
            st.dataframe(opt_weights)

    else:
        st.warning("No valid stocks analyzed.")
