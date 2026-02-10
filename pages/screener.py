"""
Smart Screener page module for AI Trading Lab PRO+
Advanced stock screening with comprehensive filtering and signals
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ui.components import get_theme_colors
from src.data_loader import load_stock_data
from src.symbol_utils import normalize_symbol
from src.stock_universe import (
    get_nifty_50, 
    get_stocks_by_sector, 
    get_stocks_by_market_cap,
    get_all_stocks,
    NIFTY_50,
    LARGE_CAP,
    MID_CAP,
    SMALL_CAP
)


def render_smart_screener():
    """Render the advanced Smart Screener page with comprehensive filtering."""
    theme_colors = get_theme_colors()
    
    st.markdown(f"""
    <div style='background: {theme_colors['gradient_bg']}; padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: center;'>
        <h1 style='color: white; margin: 0;'>🎯 Advanced Stock Screener</h1>
        <p style='color: rgba(255,255,255,0.9); margin: 10px 0 0 0;'>
            Professional Stock Screening with Advanced Indicators & Trading Signals
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Screening Configuration
    st.markdown("### ⚙️ Screening Configuration")
    
    config_col1, config_col2, config_col3, config_col4 = st.columns(4)
    
    with config_col1:
        market_type = st.selectbox(
            "📊 Market Type",
            ["Nifty 50", "Nifty Next 50", "Nifty 100", "Nifty 200", "Nifty 500", "All NSE Stocks"],
            help="Select broad market universe"
        )
    
    with config_col2:
        sector_filter = st.multiselect(
            "🏢 Sector Filter",
            ["All Sectors", "Banking", "IT", "Pharma", "Auto", "FMCG", "Energy", "Metals", "Realty", "Media", "PSU"],
            default=["All Sectors"],
            help="Select one or more sectors"
        )
    
    with config_col3:
        market_cap = st.multiselect(
            "💰 Market Cap",
            ["All", "Large Cap", "Mid Cap", "Small Cap"],
            default=["All"],
            help="Filter by market capitalization"
        )
    
    with config_col4:
        num_stocks = st.number_input(
            "📈 No. of Stocks",
            min_value=10,
            max_value=500,
            value=50,
            step=10,
            help="Number of stocks to screen"
        )
    
    # Screening Strategy & Filters
    st.markdown("### 🔍 Screening Strategy & Filters")
    
    strategy_col1, strategy_col2, strategy_col3 = st.columns(3)
    
    with strategy_col1:
        screen_type = st.selectbox(
            "🎯 Strategy Type",
            [
                "Comprehensive (All Indicators)",
                "Bullish Momentum", 
                "Bearish Momentum", 
                "Trend Following",
                "Mean Reversion",
                "Breakout",
                "Oversold Recovery",
                "Overbought Correction",
                "High Volume Surge",
                "Low Volatility"
            ],
            help="Select screening strategy"
        )
    
    with strategy_col2:
        min_score = st.slider(
            "📊 Minimum Score",
            0, 100, 65,
            help="Minimum technical score (0-100)"
        )
    
    with strategy_col3:
        timeframe = st.selectbox(
            "📅 Timeframe",
            ["Short Term (1-5 days)", "Medium Term (1-4 weeks)", "Long Term (1-3 months)"],
            help="Investment timeframe"
        )
    
    # Quick Filters
    st.markdown("### ⚡ Quick Filters")
    
    quick_col1, quick_col2, quick_col3, quick_col4, quick_col5 = st.columns(5)
    
    with quick_col1:
        only_buy = st.checkbox("✅ Only Buy Signals", value=False)
    
    with quick_col2:
        only_sell = st.checkbox("❌ Only Sell Signals", value=False)
    
    with quick_col3:
        strong_trend = st.checkbox("💪 Strong Trend (ADX>25)", value=False)
    
    with quick_col4:
        high_volume = st.checkbox("📊 High Volume", value=False)
    
    with quick_col5:
        low_risk = st.checkbox("🛡️ Low Risk", value=False)
    
    # Advanced Technical Filters
    with st.expander("🔬 Advanced Technical Filters", expanded=False):
        adv_col1, adv_col2, adv_col3, adv_col4 = st.columns(4)
        
        with adv_col1:
            rsi_filter = st.selectbox(
                "📊 RSI Filter",
                ["All", "Oversold (RSI < 30)", "Neutral (30-70)", "Overbought (RSI > 70)", "Bullish Zone (30-50)"],
                help="Filter stocks by RSI levels"
            )
        
        with adv_col2:
            macd_filter = st.selectbox(
                "📈 MACD Filter",
                ["All", "Bullish (MACD > Signal)", "Bearish (MACD < Signal)", "Bullish Crossover", "Bearish Crossover"],
                help="Filter by MACD signals"
            )
        
        with adv_col3:
            trend_filter = st.selectbox(
                "📉 Trend Filter",
                ["All", "Strong Uptrend", "Uptrend", "Sideways", "Downtrend", "Strong Downtrend"],
                help="Filter by price trend strength"
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
                ["All", "Bullish Patterns", "Bearish Patterns", "Reversal Patterns", "Continuation Patterns"],
                help="Filter by chart patterns (if detected)"
            )
        
        with adv_col6:
            pe_filter = st.selectbox(
                "💰 P/E Ratio",
                ["All", "Undervalued (PE < 15)", "Fair Value (15-25)", "Growth (25-40)", "Premium (> 40)"],
                help="Filter by Price-to-Earnings ratio"
            )
        
        with adv_col7:
            momentum_filter = st.selectbox(
                "⚡ Momentum",
                ["All", "Strong Bullish", "Bullish", "Neutral", "Bearish", "Strong Bearish"],
                help="Filter by momentum strength"
            )
        
        with adv_col8:
            ai_analysis_mode = st.selectbox(
                "🤖 AI Analysis Mode",
                ["Standard", "Deep Analysis (Slower)", "Quick Scan"],
                help="Standard: Balanced speed/accuracy | Deep: More indicators, slower | Quick: Fast screening"
            )
    
    # Run Screener Button
    if st.button("🚀 Run Advanced Screener", use_container_width=True, type="primary"):
        with st.spinner(f"🔄 Screening {num_stocks} stocks... This may take 2-5 minutes for large datasets."):
            
            # Build filter configuration
            filter_config = {
                'market_type': market_type,
                'sectors': sector_filter,
                'market_caps': market_cap,
                'num_stocks': num_stocks,
                'screen_type': screen_type,
                'min_score': min_score,
                'timeframe': timeframe,
                'only_buy': only_buy,
                'only_sell': only_sell,
                'strong_trend': strong_trend,
                'high_volume': high_volume,
                'low_risk': low_risk,
                'rsi_filter': rsi_filter,
                'macd_filter': macd_filter,
                'trend_filter': trend_filter,
                'volume_filter': volume_filter,
                'pattern_filter': pattern_filter,
                'pe_filter': pe_filter,
                'momentum_filter': momentum_filter,
                'ai_analysis_mode': ai_analysis_mode
            }
            
            # Run screener
            results = run_advanced_screener(filter_config)
            
            # Store results in session state
            st.session_state.screener_results = results
            st.session_state.screener_timestamp = datetime.now()
    
    # Display Results
    if 'screener_results' in st.session_state and st.session_state.screener_results:
        display_screener_results(st.session_state.screener_results, theme_colors)


def run_advanced_screener(config: dict) -> list:
    """Run advanced stock screener with comprehensive filtering."""
    try:
        # Get stock universe
        stocks = get_stock_universe(config['market_type'], config['sectors'], config['num_stocks'])
        
        if not stocks:
            st.error("❌ No stocks found matching criteria")
            return []
        
        st.info(f"📊 Analyzing {len(stocks)} stocks from {config['market_type']}...")
        
        results = []
        progress_bar = st.progress(0)
        
        for idx, symbol in enumerate(stocks):
            try:
                # Update progress
                progress_bar.progress((idx + 1) / len(stocks))
                
                # Load data based on AI Analysis Mode
                ai_mode = config.get('ai_analysis_mode', 'Standard')
                if ai_mode == "Quick Scan":
                    # Quick scan: Less data, faster
                    df = load_stock_data(normalize_symbol(symbol), period='3mo')
                    min_bars = 40
                elif ai_mode == "Deep Analysis (Slower)":
                    # Deep analysis: More data for better accuracy
                    df = load_stock_data(normalize_symbol(symbol), period='1y')
                    min_bars = 120
                else:
                    # Standard: Balanced
                    df = load_stock_data(normalize_symbol(symbol), period='6mo')
                    min_bars = 60
                
                if df is None or len(df) < min_bars:
                    continue
                
                # Calculate indicators based on analysis mode
                from src.advanced_ai import calculate_advanced_indicators, combined_trend_signal
                df = calculate_advanced_indicators(df)
                
                # Deep analysis: Add ML prediction if available
                ml_confidence = 0
                if ai_mode == "Deep Analysis (Slower)":
                    try:
                        from src.advanced_ai import predict_with_lstm
                        prediction = predict_with_lstm(
                            df, 
                            lookback=30, 
                            forecast_days=5,
                            epochs=10,
                            model_size='small'
                        )
                        if prediction and 'confidence' in prediction:
                            ml_confidence = prediction['confidence']
                    except Exception:
                        ml_confidence = 0
                
                # Get latest data
                latest = df.iloc[-1]
                
                # Calculate comprehensive score
                score_data = calculate_comprehensive_score(df, config['screen_type'])
                
                # Apply minimum score filter
                if score_data['total_score'] < config['min_score']:
                    continue
                
                # Generate trading signals
                signals = generate_trading_signals(df, config['timeframe'])
                
                # Apply quick filters
                if config['only_buy'] and signals['action'] != 'BUY':
                    continue
                if config['only_sell'] and signals['action'] != 'SELL':
                    continue
                if config['strong_trend'] and latest.get('ADX', 0) < 25:
                    continue
                if config['high_volume'] and latest.get('Volume', 0) < df['Volume'].rolling(20).mean().iloc[-1] * 1.3:
                    continue
                if config['low_risk'] and score_data['risk_score'] > 60:
                    continue
                
                # Apply advanced technical filters
                rsi = float(latest.get('RSI_14', 50))
                macd = float(latest.get('MACD', 0))
                macd_signal = float(latest.get('MACD_Signal', 0))
                volume_ratio = float(latest.get('Volume', 0) / df['Volume'].rolling(20).mean().iloc[-1])
                
                # RSI Filter
                if config['rsi_filter'] != "All":
                    if "Oversold" in config['rsi_filter'] and rsi >= 30:
                        continue
                    elif "Overbought" in config['rsi_filter'] and rsi <= 70:
                        continue
                    elif "Neutral" in config['rsi_filter'] and (rsi < 30 or rsi > 70):
                        continue
                    elif "Bullish Zone" in config['rsi_filter'] and (rsi < 30 or rsi > 50):
                        continue
                
                # MACD Filter
                if config['macd_filter'] != "All":
                    if "Bullish (MACD > Signal)" in config['macd_filter'] and macd <= macd_signal:
                        continue
                    elif "Bearish (MACD < Signal)" in config['macd_filter'] and macd >= macd_signal:
                        continue
                    elif "Bullish Crossover" in config['macd_filter']:
                        # Check if MACD just crossed above signal (in last 3 bars)
                        macd_prev = df['MACD'].iloc[-3:].values
                        signal_prev = df['MACD_Signal'].iloc[-3:].values
                        if not (any(macd_prev < signal_prev) and macd > macd_signal):
                            continue
                    elif "Bearish Crossover" in config['macd_filter']:
                        macd_prev = df['MACD'].iloc[-3:].values
                        signal_prev = df['MACD_Signal'].iloc[-3:].values
                        if not (any(macd_prev > signal_prev) and macd < macd_signal):
                            continue
                
                # Trend Filter (determine trend strength)
                trend_score = int(latest.get('Trend_Score', 0))
                adx = float(latest.get('ADX', 0))
                if adx > 40 and trend_score >= 4:
                    trend_strength = "Strong Uptrend"
                elif adx > 25 and trend_score >= 3:
                    trend_strength = "Uptrend"
                elif adx < 20:
                    trend_strength = "Sideways"
                elif adx > 25 and trend_score <= 2:
                    trend_strength = "Downtrend"
                elif adx > 40 and trend_score <= 1:
                    trend_strength = "Strong Downtrend"
                else:
                    trend_strength = "Sideways"
                
                if config['trend_filter'] != "All" and config['trend_filter'] != trend_strength:
                    continue
                
                # Volume Filter
                if config['volume_filter'] != "All":
                    if "High Volume" in config['volume_filter'] and volume_ratio < 1.5:
                        continue
                    elif "Above Average" in config['volume_filter'] and volume_ratio < 1.0:
                        continue
                    elif "Low Volume" in config['volume_filter'] and volume_ratio >= 0.7:
                        continue
                
                # Momentum calculation
                momentum_val = float(df['Close'].pct_change(10).iloc[-1] * 100) if len(df) > 10 else 0
                if rsi > 60 and macd > macd_signal and momentum_val > 5:
                    momentum = "Strong Bullish"
                elif rsi > 50 and macd > 0:
                    momentum = "Bullish"
                elif rsi < 40 and macd < macd_signal and momentum_val < -5:
                    momentum = "Strong Bearish"
                elif rsi < 50 and macd < 0:
                    momentum = "Bearish"
                else:
                    momentum = "Neutral"
                
                if config['momentum_filter'] != "All" and config['momentum_filter'] != momentum:
                    continue
                
                # Pattern Filter (basic pattern detection)
                pattern_type = detect_pattern(df)
                if config['pattern_filter'] != "All":
                    if "Bullish Patterns" in config['pattern_filter'] and pattern_type not in ["Bullish"]:
                        continue
                    elif "Bearish Patterns" in config['pattern_filter'] and pattern_type not in ["Bearish"]:
                        continue
                
                # P/E Ratio Filter (try to get from yfinance if available)
                pe_ratio = 0
                try:
                    import yfinance as yf
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    pe_ratio = info.get('trailingPE', 0) or info.get('forwardPE', 0) or 0
                except:
                    pe_ratio = 0
                
                if config['pe_filter'] != "All" and pe_ratio > 0:
                    if "Undervalued" in config['pe_filter'] and pe_ratio >= 15:
                        continue
                    elif "Fair Value" in config['pe_filter'] and (pe_ratio < 15 or pe_ratio > 25):
                        continue
                    elif "Growth" in config['pe_filter'] and (pe_ratio < 25 or pe_ratio > 40):
                        continue
                    elif "Premium" in config['pe_filter'] and pe_ratio <= 40:
                        continue
                
                # Compile result
                result = {
                    'Symbol': symbol,
                    'Price': float(latest['Close']),
                    'Action': signals['action'],
                    'Signal_Strength': signals['strength'],
                    'Score': int(score_data['total_score']),
                    'Entry_Price': float(signals['entry_price']),
                    'Stop_Loss': float(signals['stop_loss']),
                    'Target_1': float(signals['target_1']),
                    'Target_2': float(signals['target_2']),
                    'Risk_Reward': signals['risk_reward'],
                    'RSI': float(latest.get('RSI_14', 50)),
                    'ADX': float(latest.get('ADX', 0)),
                    'SuperTrend': 'Bullish' if latest.get('Supertrend_Direction', 0) == 1 else 'Bearish',
                    'MACD': 'Bullish' if latest.get('MACD', 0) > latest.get('MACD_Signal', 0) else 'Bearish',
                    'Volume_Ratio': float(latest.get('Volume', 0) / df['Volume'].rolling(20).mean().iloc[-1]),
                    'Volatility': float(latest.get('ATR_14', 0) / latest['Close'] * 100),
                    'Trend_Score': int(latest.get('Trend_Score', 0)),
                    'Momentum': momentum,
                    'Trend': trend_strength,
                    'Pattern': pattern_type,
                    'PE_Ratio': round(pe_ratio, 2) if pe_ratio > 0 else "N/A",
                    'Risk_Level': score_data['risk_level'],
                    'Reason': signals['reason'],
                    'Technical_Summary': score_data['summary']
                }
                
                results.append(result)
                
            except Exception as e:
                # Silent skip on individual stock errors
                continue
        
        progress_bar.empty()
        
        # Sort by score
        results = sorted(results, key=lambda x: x['Score'], reverse=True)
        
        st.success(f"✅ Screening complete! Found {len(results)} stocks matching criteria.")
        
        return results
        
    except Exception as e:
        st.error(f"❌ Screener error: {e}")
        return []


def get_stock_universe(market_type: str, sectors: list, num_stocks: int) -> list:
    """Get stock universe based on market type and sector filters."""
    stocks = []
    
    # Get base universe
    if market_type == "Nifty 50":
        stocks = get_nifty_50()
    elif market_type == "Nifty Next 50":
        # Get large cap stocks excluding Nifty 50
        all_large_cap = get_stocks_by_market_cap('large')
        nifty_50_list = get_nifty_50()
        stocks = [s for s in all_large_cap if s not in nifty_50_list]
    elif market_type == "Nifty 100":
        stocks = get_stocks_by_market_cap('large')
    elif market_type == "Nifty 200":
        # Combine large and mid cap
        stocks = get_stocks_by_market_cap('large') + get_stocks_by_market_cap('mid')
    elif market_type == "Nifty 500":
        # Combine all market caps
        stocks = (get_stocks_by_market_cap('large') + 
                 get_stocks_by_market_cap('mid') + 
                 get_stocks_by_market_cap('small'))
    else:  # All NSE Stocks
        stocks = get_all_stocks()
    
    # Apply sector filter
    if "All Sectors" not in sectors:
        sector_stocks = []
        # Map sector names to actual keys in SECTOR_STOCKS
        sector_mapping = {
            "Banking": "Banking",
            "IT": "IT",
            "Pharma": "Pharma & Healthcare",
            "Auto": "Automobile",
            "FMCG": "FMCG",
            "Energy": "Energy & Power",
            "Metals": "Metals & Mining",
            "Realty": "Realty",
            "Media": "Media & Entertainment",
            "PSU": "Energy & Power"  # Fallback to Energy for PSU
        }
        
        for sector in sectors:
            mapped_sector = sector_mapping.get(sector, sector)
            sector_list = get_stocks_by_sector(mapped_sector)
            if sector_list:
                sector_stocks.extend(sector_list)
        
        # Intersect with base universe
        if sector_stocks:
            stocks = list(set(stocks) & set(sector_stocks))
    
    # Remove duplicates and limit to requested number
    stocks = list(set(stocks))
    return stocks[:num_stocks]


def detect_pattern(df: pd.DataFrame) -> str:
    """
    Detect basic chart patterns from price data.
    Returns: "Bullish", "Bearish", "Reversal", "Continuation", or "Neutral"
    """
    try:
        if len(df) < 20:
            return "Neutral"
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Get price data
        close = latest['Close']
        prev_close = prev['Close']
        high = df['High'].iloc[-5:].max()
        low = df['Low'].iloc[-5:].min()
        
        # Calculate price change
        price_change_pct = ((close - prev_close) / prev_close) * 100
        
        # Get indicators
        rsi = latest.get('RSI_14', 50)
        macd = latest.get('MACD', 0)
        macd_signal = latest.get('MACD_Signal', 0)
        bb_percent = latest.get('BB_Percent', 0.5)
        
        # Bullish patterns
        if (price_change_pct > 2 and 
            rsi > 50 and rsi < 70 and 
            macd > macd_signal and 
            bb_percent > 0.5):
            return "Bullish"
        
        # Bearish patterns
        if (price_change_pct < -2 and 
            rsi < 50 and rsi > 30 and 
            macd < macd_signal and 
            bb_percent < 0.5):
            return "Bearish"
        
        # Reversal patterns (oversold/overbought)
        if (rsi < 30 or rsi > 70) and abs(price_change_pct) > 1:
            return "Reversal"
        
        # Continuation (trending)
        if abs(price_change_pct) > 1 and latest.get('ADX', 0) > 25:
            return "Continuation"
        
        return "Neutral"
        
    except Exception:
        return "Neutral"


def calculate_comprehensive_score(df: pd.DataFrame, strategy: str) -> dict:
    """Calculate comprehensive technical score with multiple indicators."""
    latest = df.iloc[-1]
    
    # Individual component scores
    trend_score = 0
    momentum_score = 0
    volatility_score = 0
    volume_score = 0
    
    # Trend indicators (30 points)
    supertrend_dir = latest.get('Supertrend_Direction', 0)
    adx = latest.get('ADX', 0)
    ma_trend = latest.get('Trend_Score', 0)
    
    if supertrend_dir == 1:
        trend_score += 10
    if adx > 25:
        trend_score += 10
    if adx > 35:
        trend_score += 5
    trend_score += min(ma_trend * 2, 10)
    
    # Momentum indicators (30 points)
    rsi = latest.get('RSI_14', 50)
    macd = latest.get('MACD', 0)
    macd_signal = latest.get('MACD_Signal', 0)
    stoch_k = latest.get('Stoch_K', 50)
    
    if strategy in ["Bullish Momentum", "Comprehensive (All Indicators)"]:
        if rsi > 50 and rsi < 70:
            momentum_score += 10
        if macd > macd_signal:
            momentum_score += 10
        if stoch_k > 50 and stoch_k < 80:
            momentum_score += 10
    elif strategy in ["Bearish Momentum"]:
        if rsi < 50 and rsi > 30:
            momentum_score += 10
        if macd < macd_signal:
            momentum_score += 10
        if stoch_k < 50 and stoch_k > 20:
            momentum_score += 10
    
    # Volatility indicators (20 points)
    atr_pct = latest.get('ATR_14', 0) / latest['Close'] * 100 if latest['Close'] > 0 else 0
    bb_percent = latest.get('BB_Percent', 0.5)
    
    if strategy == "Low Volatility":
        if atr_pct < 2:
            volatility_score += 10
        if 0.3 < bb_percent < 0.7:
            volatility_score += 10
    else:
        if 1 < atr_pct < 3:
            volatility_score += 10
        if 0.2 < bb_percent < 0.8:
            volatility_score += 10
    
    # Volume indicators (20 points)
    vol_ratio = latest.get('Volume', 0) / df['Volume'].rolling(20).mean().iloc[-1]
    obv_trend = df['OBV'].diff().iloc[-5:].mean() if 'OBV' in df.columns else 0
    
    if vol_ratio > 1.2:
        volume_score += 10
    if vol_ratio > 1.5:
        volume_score += 5
    if obv_trend > 0:
        volume_score += 5
    
    # Calculate total score
    total_score = trend_score + momentum_score + volatility_score + volume_score
    
    # Risk assessment
    risk_score = 0
    if atr_pct > 3:
        risk_score += 30
    if adx < 20:
        risk_score += 20
    if vol_ratio < 0.5:
        risk_score += 20
    if rsi > 75 or rsi < 25:
        risk_score += 30
    
    risk_level = "Low" if risk_score < 30 else "Medium" if risk_score < 60 else "High"
    
    # Generate summary
    summary = f"Trend: {trend_score}/30 | Momentum: {momentum_score}/30 | Vol: {volatility_score}/20 | Volume: {volume_score}/20"
    
    return {
        'total_score': total_score,
        'trend_score': trend_score,
        'momentum_score': momentum_score,
        'volatility_score': volatility_score,
        'volume_score': volume_score,
        'risk_score': risk_score,
        'risk_level': risk_level,
        'summary': summary
    }


def generate_trading_signals(df: pd.DataFrame, timeframe: str) -> dict:
    """Generate comprehensive trading signals with entry, stop loss, and targets."""
    latest = df.iloc[-1]
    current_price = float(latest['Close'])
    
    # Get key indicators
    supertrend_dir = latest.get('Supertrend_Direction', 0)
    supertrend_val = float(latest.get('Supertrend', current_price))
    atr = float(latest.get('ATR_14', current_price * 0.02))
    rsi = float(latest.get('RSI_14', 50))
    adx = float(latest.get('ADX', 0))
    bb_upper = float(latest.get('BB_Upper', current_price * 1.02))
    bb_lower = float(latest.get('BB_Lower', current_price * 0.98))
    
    # Determine action
    action = "HOLD"
    strength = "Weak"
    reason = "Neutral market conditions"
    
    if supertrend_dir == 1 and rsi < 70 and adx > 20:
        action = "BUY"
        strength = "Strong" if adx > 30 and rsi > 50 else "Moderate"
        reason = f"Bullish trend confirmed (SuperTrend: ₹{supertrend_val:.2f}, ADX: {adx:.1f})"
    elif supertrend_dir == -1 and rsi > 30 and adx > 20:
        action = "SELL"
        strength = "Strong" if adx > 30 and rsi < 50 else "Moderate"
        reason = f"Bearish trend confirmed (SuperTrend: ₹{supertrend_val:.2f}, ADX: {adx:.1f})"
    elif rsi < 30:
        action = "BUY"
        strength = "Weak"
        reason = f"Oversold conditions (RSI: {rsi:.1f})"
    elif rsi > 70:
        action = "SELL"
        strength = "Weak"
        reason = f"Overbought conditions (RSI: {rsi:.1f})"
    
    # Calculate entry, stop loss, and targets based on timeframe
    if timeframe == "Short Term (1-5 days)":
        atr_multiplier_sl = 1.5
        atr_multiplier_t1 = 2.0
        atr_multiplier_t2 = 3.0
    elif timeframe == "Medium Term (1-4 weeks)":
        atr_multiplier_sl = 2.0
        atr_multiplier_t1 = 3.0
        atr_multiplier_t2 = 5.0
    else:  # Long Term
        atr_multiplier_sl = 2.5
        atr_multiplier_t1 = 4.0
        atr_multiplier_t2 = 7.0
    
    if action == "BUY":
        entry_price = min(current_price, bb_lower * 1.01)
        stop_loss = max(supertrend_val, current_price - (atr * atr_multiplier_sl))
        target_1 = current_price + (atr * atr_multiplier_t1)
        target_2 = min(bb_upper, current_price + (atr * atr_multiplier_t2))
    elif action == "SELL":
        entry_price = max(current_price, bb_upper * 0.99)
        stop_loss = min(supertrend_val, current_price + (atr * atr_multiplier_sl))
        target_1 = current_price - (atr * atr_multiplier_t1)
        target_2 = max(bb_lower, current_price - (atr * atr_multiplier_t2))
    else:  # HOLD
        entry_price = current_price
        stop_loss = current_price - (atr * atr_multiplier_sl)
        target_1 = current_price + (atr * atr_multiplier_t1)
        target_2 = current_price + (atr * atr_multiplier_t2)
    
    # Calculate risk-reward ratio
    risk = abs(entry_price - stop_loss)
    reward = abs(target_1 - entry_price)
    risk_reward = f"1:{(reward/risk):.2f}" if risk > 0 else "N/A"
    
    return {
        'action': action,
        'strength': strength,
        'reason': reason,
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'target_1': target_1,
        'target_2': target_2,
        'risk_reward': risk_reward
    }


def display_screener_results(results: list, theme_colors: dict):
    """Display screening results with comprehensive details."""
    if not results:
        st.warning("No stocks found matching criteria. Try adjusting filters.")
        return
    
    st.markdown("---")
    st.markdown(f"### 📊 Screening Results ({len(results)} stocks)")
    
    # Summary statistics
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    buy_signals = len([r for r in results if r['Action'] == 'BUY'])
    sell_signals = len([r for r in results if r['Action'] == 'SELL'])
    avg_score = np.mean([r['Score'] for r in results])
    strong_signals = len([r for r in results if r['Signal_Strength'] == 'Strong'])
    
    with summary_col1:
        st.metric("🟢 Buy Signals", buy_signals)
    with summary_col2:
        st.metric("🔴 Sell Signals", sell_signals)
    with summary_col3:
        st.metric("📊 Avg Score", f"{avg_score:.1f}")
    with summary_col4:
        st.metric("💪 Strong Signals", strong_signals)
    
    # Top 5 picks
    st.markdown("### 🌟 Top 5 Picks")
    top_5 = results[:5]
    
    cols = st.columns(5)
    for idx, result in enumerate(top_5):
        with cols[idx]:
            signal_color = "#48bb78" if result['Action'] == 'BUY' else "#f56565" if result['Action'] == 'SELL' else "#ed8936"
            st.markdown(f"""
            <div style='background: {theme_colors['card_bg']}; padding: 12px; border-radius: 8px; border-left: 4px solid {signal_color}; height: 180px;'>
                <h3 style='margin: 0; color: {theme_colors['text']};'>{result['Symbol']}</h3>
                <p style='margin: 4px 0; color: {signal_color}; font-weight: bold; font-size: 1.1em;'>{result['Action']}</p>
                <p style='margin: 2px 0; color: {theme_colors['text_secondary']}; font-size: 0.85em;'>Score: {result['Score']}/100</p>
                <p style='margin: 2px 0; color: {theme_colors['text_secondary']}; font-size: 0.85em;'>Entry: ₹{result['Entry_Price']:.2f}</p>
                <p style='margin: 2px 0; color: {theme_colors['text_secondary']}; font-size: 0.85em;'>Target: ₹{result['Target_1']:.2f}</p>
                <p style='margin: 2px 0; color: {theme_colors['text_secondary']}; font-size: 0.85em;'>SL: ₹{result['Stop_Loss']:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Results table
    st.markdown("### 📋 Detailed Results")
    
    # Create DataFrame
    df_results = pd.DataFrame(results)
    
    # Format columns - include new advanced filter columns
    display_cols = [
        'Symbol', 'Action', 'Score', 'Entry_Price', 'Stop_Loss', 
        'Target_1', 'Risk_Reward', 'RSI', 'ADX', 'Momentum',
        'Trend', 'Pattern', 'PE_Ratio', 'Risk_Level', 'Reason'
    ]
    
    # Only include columns that exist in results
    available_cols = [col for col in display_cols if col in df_results.columns]
    display_df = df_results[available_cols].copy()
    
    # Rename columns for display
    column_names = {
        'Symbol': 'Symbol',
        'Action': 'Signal', 
        'Score': 'Score',
        'Entry_Price': 'Entry (₹)',
        'Stop_Loss': 'Stop Loss (₹)',
        'Target_1': 'Target (₹)',
        'Risk_Reward': 'R:R',
        'RSI': 'RSI',
        'ADX': 'ADX',
        'Momentum': '⚡ Momentum',
        'Trend': '📉 Trend',
        'Pattern': '🔮 Pattern',
        'PE_Ratio': '💰 P/E',
        'Risk_Level': 'Risk',
        'Reason': 'Analysis'
    }
    
    display_df.columns = [column_names.get(col, col) for col in available_cols]
    
    # Apply styling
    def highlight_signal(row):
        if row['Signal'] == 'BUY':
            return ['background-color: rgba(72, 187, 120, 0.2)'] * len(row)
        elif row['Signal'] == 'SELL':
            return ['background-color: rgba(245, 101, 101, 0.2)'] * len(row)
        else:
            return [''] * len(row)
    
    styled_df = display_df.style.apply(highlight_signal, axis=1).background_gradient(
        subset=['Score'], 
        cmap='RdYlGn',
        vmin=0,
        vmax=100
    )
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True, height=400)
    
    # Export options
    col1, col2 = st.columns([3, 1])
    
    with col2:
        csv = df_results.to_csv(index=False)
        st.download_button(
            label="📥 Export CSV",
            data=csv,
            file_name=f"screener_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )