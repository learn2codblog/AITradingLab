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
        risk_col1, risk_col2, risk_col3, risk_col4 = st.columns(4)
        
        with risk_col1:
            position_size = st.slider("Position Size (%)", 10, 100, 100, help="% of capital per trade")
        
        with risk_col2:
            stop_loss = st.slider("Stop Loss (%)", 0, 20, 5, help="Maximum loss per trade")
        
        with risk_col3:
            take_profit = st.slider("Take Profit (%)", 0, 50, 15, help="Target profit per trade")
        
        with risk_col4:
            max_positions = st.number_input("Max Positions", 1, 10, 1, help="Maximum concurrent positions")
    
    # Advanced Settings
    with st.expander("⚙️ Advanced Settings", expanded=False):
        adv_col1, adv_col2, adv_col3 = st.columns(3)
        
        with adv_col1:
            commission = st.number_input("Commission (%)", 0.0, 1.0, 0.1, step=0.05, help="Trading commission per trade")
        
        with adv_col2:
            slippage = st.number_input("Slippage (%)", 0.0, 1.0, 0.1, step=0.05, help="Estimated slippage")
        
        with adv_col3:
            tax_rate = st.number_input("Tax Rate (%)", 0.0, 30.0, 15.0, help="Capital gains tax rate")
    
    # Run backtest button
    if st.button("🚀 Run Backtest", type="primary", use_container_width=True):
        run_backtest(
            symbol, start_date, end_date, strategy, params, backtest_mode,
            initial_capital, position_size, stop_loss, take_profit, 
            max_positions, commission, slippage, tax_rate, theme_colors
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
                max_positions, commission_pct, slippage_pct, tax_rate_pct, theme_colors):
    """Execute comprehensive backtest with advanced metrics."""
    
    with st.spinner("🔄 Running backtest... Please wait..."):
        try:
            # Load data
            normalized_symbol = normalize_symbol(symbol)
            df = load_stock_data(normalized_symbol, start_date, end_date)
            
            if df is None or len(df) < 100:
                st.error("❌ Insufficient data for backtesting. Minimum 100 bars required.")
                return
            
            st.info(f"📊 Loaded {len(df)} bars from {df.index[0].date()} to {df.index[-1].date()}")
            
            # Calculate indicators
            df = calculate_indicators(df, strategy, params)
            
            # Generate signals
            df = generate_signals(df, strategy, params)
            
            # Run backtest simulation
            results = simulate_trades(
                df, initial_capital, position_size_pct, stop_loss_pct,
                take_profit_pct, commission_pct, slippage_pct
            )
            
            # Calculate advanced metrics
            metrics = calculate_advanced_metrics(results, initial_capital, df, tax_rate_pct)
            
            # Display results
            display_backtest_results(results, metrics, df, strategy, theme_colors)
            
        except Exception as e:
            st.error(f"❌ Backtest failed: {str(e)}")
            import traceback
            st.code(traceback.format_exc())


def calculate_indicators(df: pd.DataFrame, strategy: str, params: dict) -> pd.DataFrame:
    """Calculate technical indicators based on strategy."""
    df = df.copy()
    
    if strategy == "Moving Average Crossover":
        if params.get('ma_type') == 'EMA':
            df['Fast_MA'] = df['Close'].ewm(span=params['fast_ma']).mean()
            df['Slow_MA'] = df['Close'].ewm(span=params['slow_ma']).mean()
        else:
            df['Fast_MA'] = df['Close'].rolling(window=params['fast_ma']).mean()
            df['Slow_MA'] = df['Close'].rolling(window=params['slow_ma']).mean()
    
    elif strategy == "RSI Mean Reversion":
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=params['rsi_period']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=params['rsi_period']).mean()
        rs = gain / (loss + 1e-10)
        df['RSI'] = 100 - (100 / (1 + rs))
    
    elif strategy == "MACD Momentum":
        fast_ema = df['Close'].ewm(span=params['fast_period']).mean()
        slow_ema = df['Close'].ewm(span=params['slow_period']).mean()
        df['MACD'] = fast_ema - slow_ema
        df['Signal_Line'] = df['MACD'].ewm(span=params['signal_period']).mean()
        df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']
    
    elif strategy == "Bollinger Bands Breakout":
        df['BB_Middle'] = df['Close'].rolling(window=params['bb_period']).mean()
        bb_std = df['Close'].rolling(window=params['bb_period']).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * params['bb_std'])
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * params['bb_std'])
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
    
    elif strategy == "SuperTrend Following":
        # Calculate ATR
        df['TR'] = df[['High', 'Low', 'Close']].apply(
            lambda x: max(x['High'] - x['Low'], 
                         abs(x['High'] - df['Close'].shift(1).loc[x.name]) if pd.notna(df['Close'].shift(1).loc[x.name]) else 0,
                         abs(x['Low'] - df['Close'].shift(1).loc[x.name]) if pd.notna(df['Close'].shift(1).loc[x.name]) else 0),
            axis=1
        )
        df['ATR'] = df['TR'].rolling(window=params['atr_period']).mean()
        
        # Calculate SuperTrend
        df['Basic_UB'] = (df['High'] + df['Low']) / 2 + params['atr_multiplier'] * df['ATR']
        df['Basic_LB'] = (df['High'] + df['Low']) / 2 - params['atr_multiplier'] * df['ATR']
        
        df['SuperTrend'] = 0.0
        df['SuperTrend_Direction'] = 1
        
        for i in range(params['atr_period'], len(df)):
            if df['Close'].iloc[i] <= df['Basic_UB'].iloc[i-1]:
                df.iloc[i, df.columns.get_loc('SuperTrend')] = df['Basic_UB'].iloc[i]
            else:
                df.iloc[i, df.columns.get_loc('SuperTrend')] = df['Basic_LB'].iloc[i]
            
            if df['Close'].iloc[i] > df['SuperTrend'].iloc[i]:
                df.iloc[i, df.columns.get_loc('SuperTrend_Direction')] = 1
            else:
                df.iloc[i, df.columns.get_loc('SuperTrend_Direction')] = -1
        
        # Trend filters
        if params.get('trend_filter') == "ADX > 25":
            # Simple ADX calculation
            df['ADX'] = 25  # Placeholder
        elif params.get('trend_filter') == "Volume > Avg":
            df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
    
    elif strategy == "Multi-Indicator Combo":
        if params.get('use_ma'):
            df['MA'] = df['Close'].rolling(window=params.get('ma_period', 50)).mean()
        if params.get('use_rsi'):
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / (loss + 1e-10)
            df['RSI'] = 100 - (100 / (1 + rs))
        if params.get('use_macd'):
            fast_ema = df['Close'].ewm(span=12).mean()
            slow_ema = df['Close'].ewm(span=26).mean()
            df['MACD'] = fast_ema - slow_ema
            df['Signal_Line'] = df['MACD'].ewm(span=9).mean()
    
    return df


def generate_signals(df: pd.DataFrame, strategy: str, params: dict) -> pd.DataFrame:
    """Generate trading signals based on strategy."""
    df = df.copy()
    df['Signal'] = 0

def generate_signals(df: pd.DataFrame, strategy: str, params: dict) -> pd.DataFrame:
    """Generate trading signals based on strategy."""
    df = df.copy()
    df['Signal'] = 0
    
    if strategy == "Moving Average Crossover":
        df.loc[df['Fast_MA'] > df['Slow_MA'], 'Signal'] = 1
        df.loc[df['Fast_MA'] < df['Slow_MA'], 'Signal'] = -1
    
    elif strategy == "RSI Mean Reversion":
        df.loc[df['RSI'] < params['oversold'], 'Signal'] = 1
        df.loc[df['RSI'] > params['overbought'], 'Signal'] = -1
        if params.get('exit_middle'):
            df.loc[(df['Signal'].shift(1) == 1) & (df['RSI'] > 50), 'Signal'] = 0
    
    elif strategy == "MACD Momentum":
        threshold = params.get('histogram_threshold', 0)
        df.loc[(df['MACD'] > df['Signal_Line']) & (df['MACD_Histogram'] > threshold), 'Signal'] = 1
        df.loc[(df['MACD'] < df['Signal_Line']) & (df['MACD_Histogram'] < -threshold), 'Signal'] = -1
    
    elif strategy == "Bollinger Bands Breakout":
        if params['breakout_type'] in ["Upper", "Both"]:
            if params.get('confirmation'):
                df.loc[(df['Close'] > df['BB_Upper']) & (df['Volume'] > df['Volume_MA']), 'Signal'] = 1
            else:
                df.loc[df['Close'] > df['BB_Upper'], 'Signal'] = 1
        
        if params['breakout_type'] in ["Lower", "Both"]:
            if params.get('confirmation'):
                df.loc[(df['Close'] < df['BB_Lower']) & (df['Volume'] > df['Volume_MA']), 'Signal'] = -1
            else:
                df.loc[df['Close'] < df['BB_Lower'], 'Signal'] = -1
    
    elif strategy == "SuperTrend Following":
        df.loc[df['SuperTrend_Direction'] == 1, 'Signal'] = 1
        df.loc[df['SuperTrend_Direction'] == -1, 'Signal'] = -1
        
        # Apply trend filter
        if params.get('trend_filter') == "Volume > Avg":
            df.loc[df['Volume'] <= df['Volume_MA'], 'Signal'] = 0
    
    elif strategy == "Multi-Indicator Combo":
        signals = []
        
        if params.get('use_ma'):
            signals.append(df['Close'] > df['MA'])
        if params.get('use_rsi'):
            signals.append(df['RSI'] < params.get('rsi_threshold', 40))
        if params.get('use_macd'):
            signals.append(df['MACD'] > df['Signal_Line'])
        
        if signals:
            if params.get('require_all'):
                # All conditions must be true
                combined = pd.concat(signals, axis=1).all(axis=1)
            else:
                # Any condition can be true
                combined = pd.concat(signals, axis=1).any(axis=1)
            
            df.loc[combined, 'Signal'] = 1
    
    return df


def simulate_trades(df: pd.DataFrame, initial_capital: float, position_size_pct: float,
                   stop_loss_pct: float, take_profit_pct: float, 
                   commission_pct: float, slippage_pct: float) -> dict:
    """Simulate trading with realistic constraints."""
    
    capital = initial_capital
    position = 0
    entry_price = 0
    trades = []
    equity_curve = []
    
    for i in range(len(df)):
        current_price = df['Close'].iloc[i]
        signal = df['Signal'].iloc[i]
        date = df.index[i]
        
        # Check stop loss and take profit
        if position != 0:
            if position > 0:  # Long position
                pnl_pct = (current_price - entry_price) / entry_price * 100
                
                if pnl_pct <= -stop_loss_pct or pnl_pct >= take_profit_pct or signal == -1:
                    # Close position
                    exit_price = current_price * (1 - slippage_pct / 100)
                    trade_pnl = position * (exit_price - entry_price)
                    commission = position * exit_price * commission_pct / 100
                    net_pnl = trade_pnl - commission
                    
                    capital += net_pnl
                    
                    trades.append({
                        'Entry_Date': entry_date,
                        'Exit_Date': date,
                        'Entry_Price': entry_price,
                        'Exit_Price': exit_price,
                        'Position': position,
                        'PnL': net_pnl,
                        'PnL_Pct': pnl_pct,
                        'Reason': 'Stop Loss' if pnl_pct <= -stop_loss_pct else ('Take Profit' if pnl_pct >= take_profit_pct else 'Signal Exit')
                    })
                    
                    position = 0
        
        # Open new position on signal
        if position == 0 and signal == 1:
            entry_price = current_price * (1 + slippage_pct / 100)
            entry_date = date
            position_value = capital * position_size_pct / 100
            commission = position_value * commission_pct / 100
            position = (position_value - commission) / entry_price
        
        # Update equity curve
        if position > 0:
            current_equity = capital + (position * current_price - position * entry_price)
        else:
            current_equity = capital
        
        equity_curve.append({
            'Date': date,
            'Equity': current_equity,
            'DrawdownPct': (current_equity - initial_capital) / initial_capital * 100
        })
    
    return {
        'trades': trades,
        'equity_curve': pd.DataFrame(equity_curve),
        'final_capital': capital
    }


def calculate_advanced_metrics(results: dict, initial_capital: float, 
                               df: pd.DataFrame, tax_rate_pct: float) -> dict:
    """Calculate comprehensive performance metrics."""
    
    trades_df = pd.DataFrame(results['trades'])
    equity_curve = results['equity_curve']
    
    if len(trades_df) == 0:
        return {
            'total_return': 0,
            'total_trades': 0,
            'win_rate': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'profit_factor': 0
        }
    
    # Basic metrics
    total_return = (results['final_capital'] - initial_capital) / initial_capital * 100
    total_trades = len(trades_df)
    winning_trades = len(trades_df[trades_df['PnL'] > 0])
    losing_trades = len(trades_df[trades_df['PnL'] < 0])
    win_rate = winning_trades / total_trades if total_trades > 0 else 0
    
    # Profit factor
    gross_profit = trades_df[trades_df['PnL'] > 0]['PnL'].sum()
    gross_loss = abs(trades_df[trades_df['PnL'] < 0]['PnL'].sum())
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else np.inf
    
    # Sharpe ratio (annualized)
    returns = equity_curve['Equity'].pct_change().dropna()
    sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
    
    # Sortino ratio (annualized)
    downside_returns = returns[returns < 0]
    sortino_ratio = (returns.mean() / downside_returns.std()) * np.sqrt(252) if len(downside_returns) > 0 and downside_returns.std() > 0 else 0
    
    # Maximum drawdown
    running_max = equity_curve['Equity'].expanding().max()
    drawdown = (equity_curve['Equity'] - running_max) / running_max * 100
    max_drawdown = drawdown.min()
    
    # Calmar ratio
    calmar_ratio = (total_return / abs(max_drawdown)) if max_drawdown != 0 else 0
    
    # Average trade
    avg_trade = trades_df['PnL'].mean()
    avg_win = trades_df[trades_df['PnL'] > 0]['PnL'].mean() if winning_trades > 0 else 0
    avg_loss = trades_df[trades_df['PnL'] < 0]['PnL'].mean() if losing_trades > 0 else 0
    
    # Win/Loss ratio
    win_loss_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else np.inf
    
    # Net profit after tax
    taxable_profit = max(results['final_capital'] - initial_capital, 0)
    tax_amount = taxable_profit * tax_rate_pct / 100
    net_profit = results['final_capital'] - initial_capital - tax_amount
    
    # Expectancy
    expectancy = (win_rate * avg_win) - ((1 - win_rate) * abs(avg_loss))
    
    return {
        'total_return': total_return,
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': win_rate,
        'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
        'max_drawdown': max_drawdown,
        'calmar_ratio': calmar_ratio,
        'profit_factor': profit_factor,
        'avg_trade': avg_trade,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'win_loss_ratio': win_loss_ratio,
        'expectancy': expectancy,
        'gross_profit': gross_profit,
        'gross_loss': gross_loss,
        'tax_amount': tax_amount,
        'net_profit': net_profit
    }


def display_backtest_results(results: dict, metrics: dict, df: pd.DataFrame, 
                            strategy: str, theme_colors: dict):
    """Display comprehensive backtest results."""
    
    st.success("✅ Backtest completed successfully!")
    
    # Performance Summary
    st.markdown("### 📊 Performance Summary")
    
    metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
    
    with metric_col1:
        st.metric("Total Return", f"{metrics['total_return']:.2f}%", 
                 delta=f"{metrics['total_return']:.2f}%")
    
    with metric_col2:
        st.metric("Total Trades", metrics['total_trades'])
    
    with metric_col3:
        color = "🟢" if metrics['win_rate'] > 0.5 else "🔴"
        st.metric("Win Rate", f"{color} {metrics['win_rate']:.1%}")
    
    with metric_col4:
        st.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
    
    with metric_col5:
        st.metric("Max Drawdown", f"{metrics['max_drawdown']:.2f}%")
    
    # Advanced Metrics
    st.markdown("### 📈 Advanced Metrics")
    
    adv_col1, adv_col2, adv_col3, adv_col4 = st.columns(4)
    
    # Extract colors to avoid f-string nesting issues
    card_bg = theme_colors.get('card_bg', '#1E1E1E')
    text_color = theme_colors.get('text', '#FFFFFF')
    text_secondary = theme_colors.get('text_secondary', '#A0AEC0')
    
    with adv_col1:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 16px; border-radius: 8px;'>
            <h5 style='margin: 0; color: {text_secondary}'>Profit Factor</h5>
            <h3 style='margin: 8px 0; color: {text_color}'>{metrics['profit_factor']:.2f}</h3>
            <p style='margin: 0; color: {text_secondary}; font-size: 0.85em'>
                Gross Profit / Gross Loss
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with adv_col2:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 16px; border-radius: 8px;'>
            <h5 style='margin: 0; color: {text_secondary}'>Sortino Ratio</h5>
            <h3 style='margin: 8px 0; color: {text_color}'>{metrics['sortino_ratio']:.2f}</h3>
            <p style='margin: 0; color: {text_secondary}; font-size: 0.85em'>
                Risk-adjusted return (downside)
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with adv_col3:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 16px; border-radius: 8px;'>
            <h5 style='margin: 0; color: {text_secondary}'>Calmar Ratio</h5>
            <h3 style='margin: 8px 0; color: {text_color}'>{metrics['calmar_ratio']:.2f}</h3>
            <p style='margin: 0; color: {text_secondary}; font-size: 0.85em'>
                Return / Max Drawdown
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with adv_col4:
        st.markdown(f"""
        <div style='background: {card_bg}; padding: 16px; border-radius: 8px;'>
            <h5 style='margin: 0; color: {text_secondary}'>Expectancy</h5>
            <h3 style='margin: 8px 0; color: {text_color}'>₹{metrics['expectancy']:.2f}</h3>
            <p style='margin: 0; color: {text_secondary}; font-size: 0.85em'>
                Expected profit per trade
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Equity Curve
    st.markdown("### 📈 Equity Curve & Drawdown")
    
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.7, 0.3],
        subplot_titles=("Equity Curve", "Drawdown"),
        vertical_spacing=0.1
    )
    
    equity_curve = results['equity_curve']
    
    # Equity curve
    fig.add_trace(
        go.Scatter(
            x=equity_curve['Date'],
            y=equity_curve['Equity'],
            mode='lines',
            name='Equity',
            line=dict(color='#48bb78', width=2),
            fill='tonexty'
        ),
        row=1, col=1
    )
    
    # Drawdown
    running_max = equity_curve['Equity'].expanding().max()
    drawdown = (equity_curve['Equity'] - running_max) / running_max * 100
    
    fig.add_trace(
        go.Scatter(
            x=equity_curve['Date'],
            y=drawdown,
            mode='lines',
            name='Drawdown',
            line=dict(color='#f56565', width=2),
            fill='tozeroy'
        ),
        row=2, col=1
    )
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Equity (₹)", row=1, col=1)
    fig.update_yaxes(title_text="Drawdown (%)", row=2, col=1)
    
    fig.update_layout(
        height=600,
        showlegend=True,
        template='plotly_dark' if theme_colors.get('is_dark', False) else 'plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Trade Log
    st.markdown("### 📝 Trade Log")
    
    if len(results['trades']) > 0:
        trades_df = pd.DataFrame(results['trades'])
        trades_df['Entry_Date'] = pd.to_datetime(trades_df['Entry_Date']).dt.date
        trades_df['Exit_Date'] = pd.to_datetime(trades_df['Exit_Date']).dt.date
        
        # Format columns
        display_trades = trades_df[[
            'Entry_Date', 'Exit_Date', 'Entry_Price', 'Exit_Price',
            'Position', 'PnL', 'PnL_Pct', 'Reason'
        ]].copy()
        
        display_trades.columns = [
            'Entry Date', 'Exit Date', 'Entry Price (₹)', 'Exit Price (₹)',
            'Quantity', 'P&L (₹)', 'P&L %', 'Exit Reason'
        ]
        
        # Style the dataframe
        def highlight_pnl(row):
            if row['P&L (₹)'] > 0:
                return ['background-color: rgba(72, 187, 120, 0.2)'] * len(row)
            elif row['P&L (₹)'] < 0:
                return ['background-color: rgba(245, 101, 101, 0.2)'] * len(row)
            return [''] * len(row)
        
        styled_trades = display_trades.style.apply(highlight_pnl, axis=1)
        
        st.dataframe(styled_trades, use_container_width=True, hide_index=True)
        
        # Export options
        col1, col2 = st.columns([4, 1])
        with col2:
            csv = trades_df.to_csv(index=False)
            st.download_button(
                label="📥 Export CSV",
                data=csv,
                file_name=f"backtest_trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.warning("No trades executed during this backtest period")