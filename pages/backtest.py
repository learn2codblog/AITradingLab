# -*- coding: utf-8 -*-
"""
Strategy Backtest page module for AI Trading Lab PRO+
Comprehensive backtesting framework with advanced metrics and visualizations
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from ui.components import create_section_header, create_metric_card, get_theme_colors
from src.data_loader import load_stock_data
from src.symbol_utils import normalize_symbol


def render_strategy_backtest():
    """Render the comprehensive Strategy Backtest page."""
    theme_colors = get_theme_colors()
    gradient_bg = theme_colors.get('gradient_bg', 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)')
    
    st.markdown(f"""
    <div style='background: {gradient_bg}; padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: center;'>
        <h1 style='color: white; margin: 0;'>📈 Strategy Backtesting Lab</h1>
        <p style='color: rgba(255,255,255,0.9); margin: 10px 0 0 0;'>
            Professional Backtesting Framework with Advanced Analytics & Risk Management
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Strategy configuration
    st.markdown("### 🎯 Strategy Configuration")
    
    config_col1, config_col2 = st.columns([2, 1])
    
    with config_col1:
        strategy = st.selectbox(
            "Select Trading Strategy",
            [
                "Moving Average Crossover",
                "RSI Mean Reversion",
                "MACD Momentum",
                "Bollinger Bands Breakout",
                "SuperTrend Following",
                "Multi-Indicator Combo",
                "Custom Strategy"
            ],
            key="backtest_strategy",
            help="Choose a pre-built strategy to backtest"
        )
    
    with config_col2:
        backtest_mode = st.selectbox(
            "Backtest Mode",
            ["Standard", "Walk-Forward", "Monte Carlo"],
            help="Standard: Single run | Walk-Forward: Rolling optimization | Monte Carlo: Randomized scenarios"
        )

    
    # Parameters based on strategy
    st.markdown("### ⚙️ Strategy Parameters")
    
    params = render_strategy_parameters(strategy)
    
    # Test configuration
    st.markdown("### 📊 Backtest Configuration")
    
    test_col1, test_col2, test_col3, test_col4 = st.columns(4)
    
    with test_col1:
        symbol = st.text_input("Stock Symbol", "RELIANCE.NS", key="backtest_symbol")
    
    with test_col2:
        start_date = st.date_input("Start Date", pd.to_datetime("2020-01-01"), key="backtest_start")
    
    with test_col3:
        end_date = st.date_input("End Date", pd.to_datetime("today"), key="backtest_end")
    
    with test_col4:
        initial_capital = st.number_input("Initial Capital (₹)", min_value=10000, value=100000, step=10000)
    
    # Risk Management Settings
    with st.expander("🛡️ Risk Management Settings", expanded=False):
        risk_col1, risk_col2, risk_col3, risk_col4, risk_col5 = st.columns(5)

        with risk_col1:
            position_size = st.slider("Position Size (%)", 10, 100, 100, help="% of capital per trade")

        with risk_col2:
            stop_loss = st.slider("Stop Loss (%)", 0, 20, 5, help="Maximum loss per trade")

        with risk_col3:
            take_profit = st.slider("Take Profit (%)", 0, 50, 15, help="Target profit per trade")

        with risk_col4:
            max_exposure = st.slider("Max Exposure (%)", 5, 100, 25, help="Cap capital at risk per position")

        with risk_col5:
            allow_shorts = st.checkbox("Allow Shorts", value=True, help="Enable short selling")

    # Advanced Settings
    with st.expander("⚙️ Advanced Settings", expanded=False):
        adv_col1, adv_col2, adv_col3, adv_col4 = st.columns(4)

        with adv_col1:
            commission = st.number_input("Commission (%)", 0.0, 1.0, 0.1, step=0.05, help="Variable commission per trade")

        with adv_col2:
            commission_fixed = st.number_input("Fixed Commission (₹)", 0.0, 1000.0, 0.0, step=1.0, help="Flat fee per trade")

        with adv_col3:
            slippage = st.number_input("Slippage (%)", 0.0, 1.0, 0.1, step=0.05, help="Base slippage")

        with adv_col4:
            tax_rate = st.number_input("Tax Rate (%)", 0.0, 30.0, 15.0, help="Capital gains tax rate")

        adv_col5, adv_col6, adv_col7 = st.columns(3)

        with adv_col5:
            slippage_spike = st.number_input("Spike Slippage (%)", 0.0, 2.0, 0.2, step=0.05, help="Extra slippage on volume spikes")

        with adv_col6:
            volume_spike_mult = st.slider("Volume Spike Multiplier", 1.0, 5.0, 1.5, step=0.1)

        with adv_col7:
            short_margin = st.slider("Short Margin (%)", 100, 300, 150, step=10, help="Margin required for shorts")

    # Run backtest button
    if st.button("🚀 Run Backtest", type="primary", use_container_width=True):
        run_backtest(
            symbol, start_date, end_date, strategy, params, backtest_mode,
            initial_capital, position_size, stop_loss, take_profit,
            max_exposure, allow_shorts, short_margin,
            commission, commission_fixed, slippage, slippage_spike, volume_spike_mult,
            tax_rate, theme_colors
        )


def render_strategy_parameters(strategy: str) -> dict:
    """Render strategy-specific parameters and return config."""
    params = {}
    
    param_col1, param_col2, param_col3, param_col4 = st.columns(4)
    
    if strategy == "Moving Average Crossover":
        with param_col1:
            params['fast_ma'] = st.slider("Fast MA Period", 5, 50, 10, key="fast_ma")
        with param_col2:
            params['slow_ma'] = st.slider("Slow MA Period", 20, 200, 50, key="slow_ma")
        with param_col3:
            params['ma_type'] = st.selectbox("MA Type", ["SMA", "EMA"], key="ma_type")
        with param_col4:
            st.markdown("**Signal**: Fast MA crosses Slow MA")
    
    elif strategy == "RSI Mean Reversion":
        with param_col1:
            params['rsi_period'] = st.slider("RSI Period", 5, 21, 14, key="rsi_period")
        with param_col2:
            params['overbought'] = st.slider("Overbought Level", 60, 90, 70, key="overbought")
        with param_col3:
            params['oversold'] = st.slider("Oversold Level", 10, 40, 30, key="oversold")
        with param_col4:
            params['exit_middle'] = st.checkbox("Exit at RSI=50", value=True, key="exit_middle")
    
    elif strategy == "MACD Momentum":
        with param_col1:
            params['fast_period'] = st.slider("Fast EMA", 8, 20, 12, key="fast_period")
        with param_col2:
            params['slow_period'] = st.slider("Slow EMA", 21, 40, 26, key="slow_period")
        with param_col3:
            params['signal_period'] = st.slider("Signal Period", 5, 15, 9, key="signal_period")
        with param_col4:
            params['histogram_threshold'] = st.slider("Histogram Threshold", 0.0, 2.0, 0.0, key="histogram_threshold")
    
    elif strategy == "Bollinger Bands Breakout":
        with param_col1:
            params['bb_period'] = st.slider("BB Period", 10, 50, 20, key="bb_period")
        with param_col2:
            params['bb_std'] = st.slider("Standard Deviations", 1.0, 3.0, 2.0, step=0.5, key="bb_std")
        with param_col3:
            params['breakout_type'] = st.selectbox("Breakout Type", ["Upper", "Lower", "Both"], key="breakout_type")
        with param_col4:
            params['confirmation'] = st.checkbox("Require Volume Confirmation", value=False)
    
    elif strategy == "SuperTrend Following":
        with param_col1:
            params['atr_period'] = st.slider("ATR Period", 5, 20, 10, key="atr_period")
        with param_col2:
            params['atr_multiplier'] = st.slider("ATR Multiplier", 1.0, 5.0, 3.0, step=0.5, key="atr_multiplier")
        with param_col3:
            params['trend_filter'] = st.selectbox("Trend Filter", ["None", "ADX > 25", "Volume > Avg"], key="trend_filter")
        with param_col4:
            st.markdown("**Signal**: Price crosses SuperTrend")
    
    elif strategy == "Multi-Indicator Combo":
        with param_col1:
            params['use_ma'] = st.checkbox("Use MA", value=True, key="use_ma")
            if params['use_ma']:
                params['ma_period'] = st.slider("MA Period", 10, 100, 50, key="combo_ma")
        with param_col2:
            params['use_rsi'] = st.checkbox("Use RSI", value=True, key="use_rsi")
            if params['use_rsi']:
                params['rsi_threshold'] = st.slider("RSI Buy Below", 20, 50, 40, key="combo_rsi")
        with param_col3:
            params['use_macd'] = st.checkbox("Use MACD", value=True, key="use_macd")
        with param_col4:
            params['require_all'] = st.checkbox("Require All Signals", value=True, key="require_all")
    
    return params


def run_backtest(symbol, start_date, end_date, strategy, params, mode,
                initial_capital, position_size_pct, stop_loss_pct, take_profit_pct,
                max_exposure_pct, allow_shorts, short_margin_pct,
                commission_pct, commission_fixed, slippage_pct, slippage_spike_pct,
                volume_spike_mult, tax_rate_pct, theme_colors):
    """Execute comprehensive backtest with advanced metrics."""

    with st.spinner("🔄 Running backtest... Please wait..."):
        try:
            # Load data
            normalized_symbol = normalize_symbol(symbol)
            df = load_stock_data(normalized_symbol, start_date, end_date)

            if df is None or len(df) < 100:
                st.error("❌ Insufficient data for backtesting. Minimum 100 bars required.")
                return

            df = df.copy()
            df.columns = [col.lower() for col in df.columns]
            if 'volume' in df.columns:
                df['volume_ma20'] = df['volume'].rolling(20).mean()

            st.info(f"📊 Loaded {len(df)} bars from {df.index[0].date()} to {df.index[-1].date()}")

            # Calculate indicators
            df = calculate_indicators(df, strategy, params)

            # Generate signals
            df = generate_signals(df, strategy, params)

            # Run backtest simulation
            results, trades = simulate_trades(
                df, initial_capital, position_size_pct, max_exposure_pct, stop_loss_pct,
                take_profit_pct, commission_pct, commission_fixed, slippage_pct,
                slippage_spike_pct, volume_spike_mult, allow_shorts, short_margin_pct
            )

            # Calculate advanced metrics
            metrics = calculate_advanced_metrics(results, initial_capital, df, tax_rate_pct)
            metrics.update(calculate_trade_metrics(trades))

            # Persist backtest and trades
            try:
                from src.supabase_client import get_supabase_client
                supabase = get_supabase_client()
                user_id = st.session_state.get('user_id')
                if user_id and supabase.is_connected():
                    test_name = f"{strategy} {normalized_symbol} {datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                    result_data = {
                        'symbol': normalized_symbol,
                        'strategy': strategy,
                        'start_date': str(start_date),
                        'end_date': str(end_date),
                        'initial_capital': initial_capital,
                        'params': params,
                        'risk': {
                            'position_size_pct': position_size_pct,
                            'max_exposure_pct': max_exposure_pct,
                            'stop_loss_pct': stop_loss_pct,
                            'take_profit_pct': take_profit_pct,
                            'allow_shorts': allow_shorts,
                            'short_margin_pct': short_margin_pct
                        },
                        'costs': {
                            'commission_pct': commission_pct,
                            'commission_fixed': commission_fixed,
                            'slippage_pct': slippage_pct,
                            'slippage_spike_pct': slippage_spike_pct,
                            'volume_spike_mult': volume_spike_mult
                        },
                        'metrics': metrics
                    }

                    backtest_id = supabase.save_backtest_result(
                        user_id=user_id,
                        test_name=test_name,
                        strategy_type=strategy,
                        symbol=normalized_symbol,
                        result_data=result_data,
                        performance_metrics=metrics
                    )

                    if backtest_id and trades:
                        supabase.save_backtest_trades(user_id, backtest_id, trades)

                    supabase.log_activity(
                        user_id=user_id,
                        activity_type='backtest_run',
                        description=f"Backtest run for {normalized_symbol}",
                        action_details={
                            'symbol': normalized_symbol,
                            'strategy': strategy,
                            'start_date': str(start_date),
                            'end_date': str(end_date),
                            'initial_capital': initial_capital,
                            'position_size_pct': position_size_pct,
                            'max_exposure_pct': max_exposure_pct,
                            'stop_loss_pct': stop_loss_pct,
                            'take_profit_pct': take_profit_pct,
                            'allow_shorts': allow_shorts,
                            'short_margin_pct': short_margin_pct,
                            'commission_pct': commission_pct,
                            'commission_fixed': commission_fixed,
                            'slippage_pct': slippage_pct,
                            'slippage_spike_pct': slippage_spike_pct,
                            'volume_spike_mult': volume_spike_mult
                        },
                        status='success'
                    )
                    supabase.log_trading_activity(
                        user_id=user_id,
                        activity_type='backtest_run',
                        description=f"Backtest run for {normalized_symbol}",
                        symbol=normalized_symbol,
                        source='backtest',
                        details={
                            'strategy': strategy,
                            'start_date': str(start_date),
                            'end_date': str(end_date),
                            'initial_capital': initial_capital,
                            'position_size_pct': position_size_pct,
                            'max_exposure_pct': max_exposure_pct,
                            'stop_loss_pct': stop_loss_pct,
                            'take_profit_pct': take_profit_pct,
                            'allow_shorts': allow_shorts,
                            'short_margin_pct': short_margin_pct,
                            'commission_pct': commission_pct,
                            'commission_fixed': commission_fixed,
                            'slippage_pct': slippage_pct,
                            'slippage_spike_pct': slippage_spike_pct,
                            'volume_spike_mult': volume_spike_mult
                        },
                        status='success'
                    )
            except Exception:
                pass

            # Display results
            display_backtest_results(results, metrics, df, theme_colors)

        except Exception as e:
            st.error(f"❌ Error running backtest: {str(e)}")
            st.exception(e)


def calculate_indicators(df, strategy, params):
    """Calculate technical indicators for the strategy."""

    # Moving Average Crossover
    if strategy == "Moving Average Crossover":
        df['fast_ma'] = df['close'].rolling(window=params['fast_ma']).mean()
        df['slow_ma'] = df['close'].rolling(window=params['slow_ma']).mean()

    # RSI Mean Reversion
    elif strategy == "RSI Mean Reversion":
        df['rsi'] = compute_rsi(df['close'], params['rsi_period'])

    # MACD Momentum
    elif strategy == "MACD Momentum":
        df['macd'], df['macd_signal'], df['macd_hist'] = compute_macd(
            df['close'],
            params['fast_period'],
            params['slow_period'],
            params['signal_period']
        )

    # Bollinger Bands Breakout
    elif strategy == "Bollinger Bands Breakout":
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = compute_bollinger_bands(
            df['close'],
            params['bb_period'],
            params['bb_std']
        )

    # SuperTrend Following
    elif strategy == "SuperTrend Following":
        df['supertrend'] = compute_supertrend(df, params['atr_period'], params['atr_multiplier'])

    # Multi-Indicator Combo
    elif strategy == "Multi-Indicator Combo":
        if params.get('use_ma'):
            df['combo_ma'] = df['close'].rolling(window=params['ma_period']).mean()
        if params.get('use_rsi'):
            df['rsi'] = compute_rsi(df['close'], params.get('rsi_period', 14))
        if params.get('use_macd'):
            df['macd'], df['macd_signal'], df['macd_hist'] = compute_macd(df['close'])

    return df


def generate_signals(df, strategy, params):
    """Generate buy/sell signals based on the strategy."""
    df['signal'] = 0

    # Moving Average Crossover
    if strategy == "Moving Average Crossover":
        df.loc[df['fast_ma'] > df['slow_ma'], 'signal'] = 1
        df.loc[df['fast_ma'] < df['slow_ma'], 'signal'] = -1

    # RSI Mean Reversion
    elif strategy == "RSI Mean Reversion":
        df.loc[df['rsi'] < params['oversold'], 'signal'] = 1
        df.loc[df['rsi'] > params['overbought'], 'signal'] = -1
        if params['exit_middle']:
            df.loc[df['rsi'] == 50, 'signal'] = 0

    # MACD Momentum
    elif strategy == "MACD Momentum":
        df.loc[df['macd_hist'] > params['histogram_threshold'], 'signal'] = 1
        df.loc[df['macd_hist'] < -params['histogram_threshold'], 'signal'] = -1

    # Bollinger Bands Breakout
    elif strategy == "Bollinger Bands Breakout":
        if params['breakout_type'] == "Upper":
            df.loc[df['close'] > df['bb_upper'], 'signal'] = 1
        elif params['breakout_type'] == "Lower":
            df.loc[df['close'] < df['bb_lower'], 'signal'] = -1
        else:  # Both
            df.loc[df['close'] > df['bb_upper'], 'signal'] = 1
            df.loc[df['close'] < df['bb_lower'], 'signal'] = -1

    # SuperTrend Following
    elif strategy == "SuperTrend Following":
        df.loc[df['close'] > df['supertrend'], 'signal'] = 1
        df.loc[df['close'] < df['supertrend'], 'signal'] = -1

    # Multi-Indicator Combo
    elif strategy == "Multi-Indicator Combo":
        signal_frames = []
        if params.get('use_ma'):
            signal_ma = pd.Series(0, index=df.index)
            signal_ma[df['close'] > df['combo_ma']] = 1
            signal_ma[df['close'] < df['combo_ma']] = -1
            signal_frames.append(signal_ma.rename('signal_ma'))
        if params.get('use_rsi'):
            signal_rsi = pd.Series(0, index=df.index)
            threshold = params.get('rsi_threshold', 40)
            signal_rsi[df['rsi'] < threshold] = 1
            signal_rsi[df['rsi'] > 100 - threshold] = -1
            signal_frames.append(signal_rsi.rename('signal_rsi'))
        if params.get('use_macd'):
            signal_macd = pd.Series(0, index=df.index)
            signal_macd[df['macd_hist'] > 0] = 1
            signal_macd[df['macd_hist'] < 0] = -1
            signal_frames.append(signal_macd.rename('signal_macd'))

        if signal_frames:
            signal_df = pd.concat(signal_frames, axis=1)
            if params.get('require_all'):
                df['signal'] = signal_df.min(axis=1)
            else:
                df['signal'] = signal_df.max(axis=1)

    return df


def simulate_trades(df, initial_capital, position_size_pct, max_exposure_pct, stop_loss_pct, take_profit_pct,
                    commission_pct, commission_fixed, slippage_pct, slippage_spike_pct,
                    volume_spike_mult, allow_shorts, short_margin_pct):
    """Simulate trades based on signals and calculate equity curve."""
    df = df.copy()

    df['position'] = 0
    df['position_size'] = 0
    df['entry_price'] = np.nan
    df['exit_price'] = np.nan
    df['pnl'] = 0.0
    df['commission'] = 0.0
    df['slippage'] = 0.0
    df['equity'] = initial_capital
    df['cash'] = initial_capital

    position = 0
    shares = 0
    entry_price = 0.0
    entry_commission = 0.0
    entry_slippage = 0.0
    entry_time = None
    margin_hold = 0.0
    stop_loss = np.nan
    take_profit = np.nan
    cash = initial_capital
    trades = []

    def _effective_slippage(idx: int) -> float:
        base = slippage_pct
        if 'volume' in df.columns and 'volume_ma20' in df.columns:
            volume = df['volume'].iloc[idx]
            volume_ma = df['volume_ma20'].iloc[idx]
            if pd.notna(volume_ma) and volume_ma > 0 and volume > volume_ma * volume_spike_mult:
                base += slippage_spike_pct
        return base

    for i in range(1, len(df)):
        price = df['close'].iloc[i]
        signal = df['signal'].iloc[i]

        # Carry forward equity based on current position value
        equity = cash + (shares * price if position != 0 else 0.0)
        df.at[df.index[i], 'equity'] = equity
        df.at[df.index[i], 'cash'] = cash
        df.at[df.index[i], 'position'] = position
        df.at[df.index[i], 'position_size'] = shares

        if position == 0 and signal != 0:
            if signal == -1 and not allow_shorts:
                continue

            # Enter new position
            allowed_pct = min(position_size_pct, max_exposure_pct)
            max_exposure = allowed_pct / 100 * equity
            shares = int(max_exposure / price)
            if shares > 0:
                effective_slippage = _effective_slippage(i)
                if signal == 1:
                    entry_fill = price * (1 + effective_slippage / 100)
                else:
                    entry_fill = price * (1 - effective_slippage / 100)

                entry_commission = entry_fill * shares * (commission_pct / 100) + commission_fixed
                entry_slippage = abs(entry_fill - price) * shares

                if signal == 1:
                    total_cost = entry_fill * shares + entry_commission
                    if total_cost > cash:
                        continue
                    cash -= total_cost
                    stop_loss = entry_fill * (1 - stop_loss_pct / 100)
                    take_profit = entry_fill * (1 + take_profit_pct / 100)
                    margin_hold = 0.0
                else:
                    required_margin = entry_fill * shares * (short_margin_pct / 100)
                    if required_margin > cash:
                        continue
                    cash += (entry_fill * shares - entry_commission)
                    cash -= required_margin
                    margin_hold = required_margin
                    stop_loss = entry_fill * (1 + stop_loss_pct / 100)
                    take_profit = entry_fill * (1 - take_profit_pct / 100)

                position = signal
                entry_price = entry_fill
                entry_time = df.index[i]

                df.at[df.index[i], 'entry_price'] = entry_fill
                df.at[df.index[i], 'commission'] += entry_commission
                df.at[df.index[i], 'slippage'] += entry_slippage
                df.at[df.index[i], 'position'] = position
                df.at[df.index[i], 'position_size'] = shares
                df.at[df.index[i], 'cash'] = cash

            continue

        if position != 0:
            exit_reason = None
            if position == 1:
                if price <= stop_loss:
                    exit_reason = 'stop'
                elif price >= take_profit:
                    exit_reason = 'target'
                elif signal == -1:
                    exit_reason = 'signal'
            else:
                if price >= stop_loss:
                    exit_reason = 'stop'
                elif price <= take_profit:
                    exit_reason = 'target'
                elif signal == 1:
                    exit_reason = 'signal'

            if exit_reason:
                effective_slippage = _effective_slippage(i)
                if position == 1:
                    exit_fill = price * (1 - effective_slippage / 100)
                else:
                    exit_fill = price * (1 + effective_slippage / 100)

                exit_commission = exit_fill * shares * (commission_pct / 100) + commission_fixed
                exit_slippage = abs(exit_fill - price) * shares

                if position == 1:
                    cash += (exit_fill * shares - exit_commission)
                    pnl = (exit_fill - entry_price) * shares - entry_commission - exit_commission
                else:
                    cash += margin_hold
                    cash -= (exit_fill * shares + exit_commission)
                    pnl = (entry_price - exit_fill) * shares - entry_commission - exit_commission

                df.at[df.index[i], 'exit_price'] = exit_fill
                df.at[df.index[i], 'pnl'] = pnl
                df.at[df.index[i], 'commission'] += exit_commission
                df.at[df.index[i], 'slippage'] += exit_slippage

                if entry_time is not None:
                    return_pct = (pnl / (abs(entry_price * shares))) if shares else 0.0
                    trades.append({
                        'symbol': df.get('symbol', None),
                        'strategy_type': None,
                        'side': 'long' if position == 1 else 'short',
                        'entry_time': pd.to_datetime(entry_time).isoformat(),
                        'exit_time': pd.to_datetime(df.index[i]).isoformat(),
                        'entry_price': float(entry_price),
                        'exit_price': float(exit_fill),
                        'shares': int(shares),
                        'pnl': float(pnl),
                        'return_pct': float(return_pct),
                        'commission': float(entry_commission + exit_commission),
                        'slippage': float(entry_slippage + exit_slippage)
                    })

                position = 0
                shares = 0
                entry_price = 0.0
                entry_commission = 0.0
                entry_slippage = 0.0
                entry_time = None
                margin_hold = 0.0
                stop_loss = np.nan
                take_profit = np.nan
                df.at[df.index[i], 'cash'] = cash
                df.at[df.index[i], 'position'] = position
                df.at[df.index[i], 'position_size'] = shares

    # Final equity
    df.at[df.index[-1], 'equity'] = cash + (shares * df['close'].iloc[-1] if position != 0 else 0.0)
    df.at[df.index[-1], 'cash'] = cash

    return df, trades


def calculate_advanced_metrics(results, initial_capital, df, tax_rate_pct):
    """Calculate and return advanced backtest metrics."""
    metrics = {}

    # Total Return
    total_return = results['equity'].iloc[-1] - initial_capital
    metrics['total_return'] = total_return
    metrics['total_return_pct'] = (total_return / initial_capital) * 100

    # Annualized Return
    num_years = (df.index[-1] - df.index[0]).days / 365.25
    metrics['annualized_return'] = (results['equity'].iloc[-1] / initial_capital) ** (1 / num_years) - 1

    # Volatility (Annualized)
    daily_returns = results['equity'].pct_change().dropna()
    metrics['volatility'] = daily_returns.std() * np.sqrt(252)

    # Sharpe Ratio
    risk_free_rate = 0.035
    sharpe_ratio = (metrics['annualized_return'] - risk_free_rate) / metrics['volatility']
    metrics['sharpe_ratio'] = sharpe_ratio

    # Maximum Drawdown
    rolling_max = results['equity'].cummax()
    drawdown = (results['equity'] - rolling_max) / rolling_max
    metrics['max_drawdown'] = drawdown.min()

    # Calmar Ratio
    metrics['calmar_ratio'] = metrics['annualized_return'] / -metrics['max_drawdown']

    # Sortino Ratio
    downside_returns = daily_returns[daily_returns < 0]
    sortino_ratio = (metrics['annualized_return'] - risk_free_rate) / downside_returns.std()
    metrics['sortino_ratio'] = sortino_ratio

    # Tax-Adjusted Return
    metrics['tax_adjusted_return'] = metrics['total_return'] * (1 - tax_rate_pct / 100)

    return metrics


def display_backtest_results(results, metrics, df, theme_colors):
    """Display the backtest results and equity curve."""
    st.markdown("### 📈 Backtest Results")

    # Display metrics
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

    with metrics_col1:
        create_metric_card("Total Return", f"₹{metrics['total_return']:,.2f}", "percentage", theme_colors)
        create_metric_card("Annualized Return", f"{metrics['annualized_return']*100:.2f}%", "percentage", theme_colors)

    with metrics_col2:
        create_metric_card("Volatility", f"{metrics['volatility']*100:.2f}%", "percentage", theme_colors)
        create_metric_card("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}", "ratio", theme_colors)

    with metrics_col3:
        create_metric_card("Max Drawdown", f"{metrics['max_drawdown']*100:.2f}%", "percentage", theme_colors)
        create_metric_card("Calmar Ratio", f"{metrics['calmar_ratio']:.2f}", "ratio", theme_colors)

    # Equity curve
    st.markdown("### 📊 Equity Curve")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=results.index, y=results['equity'], mode='lines', name='Equity Curve'))
    fig.update_layout(title="Equity Curve", xaxis_title="Date", yaxis_title="Equity (₹)", template="plotly")
    st.plotly_chart(fig, use_container_width=True)

    # Drawdown curve
    st.markdown("### 📉 Drawdown Curve")
    drawdown_fig = go.Figure()
    drawdown_fig.add_trace(go.Scatter(x=results.index, y=(results['equity'] - results['equity'].cummax()) / results['equity'].cummax(), mode='lines', name='Drawdown'))
    drawdown_fig.update_layout(title="Drawdown Curve", xaxis_title="Date", yaxis_title="Drawdown (%)", template="plotly")
    st.plotly_chart(drawdown_fig, use_container_width=True)

    # Trade analysis
    st.markdown("### 📊 Trade Analysis")
    trades = results[results['pnl'] != 0]
    if not trades.empty:
        # Trade PnL distribution
        st.subheader("Trade PnL Distribution")
        pnl_fig = go.Figure()
        pnl_fig.add_trace(go.Histogram(x=trades['pnl'], nbinsx=50, name='Trade PnL'))
        pnl_fig.update_layout(title="Trade PnL Distribution", xaxis_title="PnL (₹)", yaxis_title="Frequency", template="plotly")
        st.plotly_chart(pnl_fig, use_container_width=True)

        # Win rate
        win_rate = (trades[trades['pnl'] > 0].shape[0] / trades.shape[0]) * 100
        st.metric("Win Rate", f"{win_rate:.2f}%", delta_color="normal")

        # Average trade duration
        trades['holding_period'] = (trades.index.to_series().diff().dt.days).fillna(0)
        avg_duration = trades['holding_period'].mean()
        st.metric("Avg. Trade Duration", f"{avg_duration:.0f} days", delta_color="normal")

        # Commission and slippage impact
        st.subheader("Commission & Slippage Impact")
        impact_fig = go.Figure()
        impact_fig.add_trace(go.Scatter(x=results.index, y=results['commission'].cumsum(), mode='lines', name='Cumulative Commission'))
        impact_fig.add_trace(go.Scatter(x=results.index, y=results['slippage'].cumsum(), mode='lines', name='Cumulative Slippage'))
        impact_fig.update_layout(title="Commission & Slippage Impact", xaxis_title="Date", yaxis_title="Impact (₹)", template="plotly")
        st.plotly_chart(impact_fig, use_container_width=True)
    else:
        st.info("No trades executed during the backtest period.")


def compute_rsi(close, period=14):
    """Compute Relative Strength Index (RSI)"""
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def compute_macd(close, fast_period=12, slow_period=26, signal_period=9):
    """Compute Moving Average Convergence Divergence (MACD)"""
    exp1 = close.ewm(span=fast_period, adjust=False).mean()
    exp2 = close.ewm(span=slow_period, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=signal_period, adjust=False).mean()
    histogram = macd - signal
    return macd, signal, histogram


def compute_bollinger_bands(close, period=20, std_dev=2):
    """Compute Bollinger Bands"""
    sma = close.rolling(window=period).mean()
    rstd = close.rolling(window=period).std()
    upper = sma + (rstd * std_dev)
    lower = sma - (rstd * std_dev)
    return upper, sma, lower


def compute_supertrend(df, atr_period=10, multiplier=3):
    """Compute SuperTrend indicator"""
    df = df.copy()
    hl2 = (df['high'] + df['low']) / 2
    df['atr'] = hl2.rolling(window=atr_period).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
    df['upperband'] = hl2 + (multiplier * df['atr'])
    df['lowerband'] = hl2 - (multiplier * df['atr'])
    df['supertrend'] = 0.0

    for i in range(1, len(df)):
        if df['close'].iloc[i] <= df['upperband'].iloc[i-1]:
            df['supertrend'].iloc[i] = df['upperband'].iloc[i]
        else:
            df['supertrend'].iloc[i] = df['lowerband'].iloc[i]

    return df['supertrend']
