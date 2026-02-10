"""
Risk Management Module for TradeGenius AI
==========================================
Includes:
- Position sizing calculations
- Backtesting framework
- Feature importance analysis
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


def calculate_position_size(df: pd.DataFrame, capital: float, risk_percent: float = 2.0,
                           atr_multiplier: float = 2.0) -> dict:
    """
    Calculate optimal position size using ATR-based stop loss

    Args:
        df: DataFrame with OHLCV and ATR data
        capital: Total trading capital
        risk_percent: Maximum risk per trade as percentage (default 2%)
        atr_multiplier: ATR multiplier for stop loss (default 2.0)

    Returns:
        Dict with position sizing recommendations
    """
    if len(df) < 20:
        return {'error': 'Insufficient data for position sizing'}

    current_price = df['Close'].iloc[-1]

    # Calculate ATR if not present
    if 'ATR_14' in df.columns:
        atr = df['ATR_14'].iloc[-1]
    else:
        high_low = df['High'] - df['Low']
        high_close = abs(df['High'] - df['Close'].shift())
        low_close = abs(df['Low'] - df['Close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(14).mean().iloc[-1]

    # Calculate stop loss distance
    stop_loss_distance = atr * atr_multiplier
    stop_loss_price = current_price - stop_loss_distance
    stop_loss_percent = (stop_loss_distance / current_price) * 100

    # Calculate position size based on risk
    risk_amount = capital * (risk_percent / 100)
    shares = int(risk_amount / stop_loss_distance)
    position_value = shares * current_price
    position_percent = (position_value / capital) * 100

    # Calculate take profit levels (using R:R ratios)
    take_profit_1r = current_price + stop_loss_distance  # 1:1
    take_profit_2r = current_price + (stop_loss_distance * 2)  # 2:1
    take_profit_3r = current_price + (stop_loss_distance * 3)  # 3:1

    # Volatility assessment
    daily_volatility = df['Close'].pct_change().std() * 100
    annual_volatility = daily_volatility * np.sqrt(252)

    if annual_volatility > 50:
        volatility_level = 'Very High'
        recommended_risk = min(risk_percent, 1.0)
    elif annual_volatility > 35:
        volatility_level = 'High'
        recommended_risk = min(risk_percent, 1.5)
    elif annual_volatility > 20:
        volatility_level = 'Normal'
        recommended_risk = risk_percent
    else:
        volatility_level = 'Low'
        recommended_risk = min(risk_percent * 1.5, 3.0)

    return {
        'current_price': float(current_price),
        'atr_14': float(atr),
        'stop_loss_price': float(stop_loss_price),
        'stop_loss_distance': float(stop_loss_distance),
        'stop_loss_percent': float(stop_loss_percent),
        'position_size_shares': int(shares),
        'position_value': float(position_value),
        'position_percent_of_capital': float(position_percent),
        'risk_amount': float(risk_amount),
        'take_profit_1r': float(take_profit_1r),
        'take_profit_2r': float(take_profit_2r),
        'take_profit_3r': float(take_profit_3r),
        'daily_volatility': float(daily_volatility),
        'annual_volatility': float(annual_volatility),
        'volatility_level': volatility_level,
        'recommended_risk_percent': float(recommended_risk)
    }


def backtest_strategy(df: pd.DataFrame, signal_col: str = None,
                     initial_capital: float = 100000,
                     position_size_pct: float = 10,
                     max_exposure_pct: float = 25,
                     stop_loss_pct: float = 5,
                     take_profit_pct: float = 10,
                     commission_pct: float = 0.1,
                     commission_fixed: float = 20,
                     slippage_pct: float = 0.05,
                     allow_short: bool = True) -> dict:
    """
    Realistic backtesting framework with transaction costs, slippage, and short selling

    Args:
        df: DataFrame with OHLCV and signal data
        signal_col: Column with signals (1=Buy, -1=Sell/Short, 0=Hold)
        initial_capital: Starting capital (default 100000)
        position_size_pct: Position size as % of capital (default 10%)
        max_exposure_pct: Maximum capital at risk (default 25%)
        stop_loss_pct: Stop loss percentage (default 5%)
        take_profit_pct: Take profit percentage (default 10%)
        commission_pct: Commission as % of trade value (default 0.1%)
        commission_fixed: Fixed commission per trade (default 20)
        slippage_pct: Slippage as % of price (default 0.05%)
        allow_short: Allow short selling (default True)

    Returns:
        Dict with comprehensive backtest results and risk metrics
    """
    df_bt = df.copy()

    # If no signal column provided, we will compute signals on-the-fly per-step
    # using only historical data up to the decision point. This allows using
    # a recent lookback window for decision-making while retaining older data
    # for other calculations.
    if signal_col is None or signal_col not in df_bt.columns:
        if 'RSI_14' in df_bt.columns and 'MACD' in df_bt.columns:
            # signal_col remains None -> compute per-row below
            signal_col = None
        else:
            return {'error': 'No signal column provided and cannot generate signals (missing RSI/MACD)'}

    # Calculate volume-based slippage multiplier
    if 'Volume' in df_bt.columns:
        avg_volume = df_bt['Volume'].rolling(20).mean()
        volume_ratio = df_bt['Volume'] / avg_volume
        # Higher slippage on volume spikes
        slippage_multiplier = 1 + np.clip((volume_ratio - 1) * 0.5, 0, 2)
    else:
        slippage_multiplier = pd.Series(1.0, index=df_bt.index)

    def calculate_transaction_cost(shares: int, price: float, is_buy: bool, vol_mult: float = 1.0) -> float:
        """Calculate total transaction cost including commission and slippage"""
        trade_value = shares * price
        commission = max(commission_fixed, trade_value * (commission_pct / 100))
        slippage_cost = trade_value * (slippage_pct / 100) * vol_mult
        return commission + slippage_cost

    def get_execution_price(price: float, is_buy: bool, vol_mult: float = 1.0) -> float:
        """Get execution price with slippage"""
        slippage = price * (slippage_pct / 100) * vol_mult
        return price + slippage if is_buy else price - slippage

    # Initialize tracking variables
    capital = initial_capital
    position = 0  # Positive = long, Negative = short
    entry_price = 0
    position_type = None  # 'long' or 'short'
    trades = []
    equity_curve = []
    daily_returns = []
    total_costs = 0

    # Simulate trading
    for i in range(len(df_bt)):
        row = df_bt.iloc[i]
        current_price = row['Close']

        # Skip rows with NaN prices
        if pd.isna(current_price) or current_price <= 0:
            continue

        # If a precomputed signal column is provided, use it. Otherwise compute
        # a signal based on recent historical data only (to simulate live decisions).
        if signal_col is not None:
            signal = row[signal_col] if not pd.isna(row[signal_col]) else 0
        else:
            # Define how many past days to use for decision-making. If the caller
            # has set an attribute `decision_lookback` on the DataFrame (not ideal)
            # we would read it; otherwise default to using the last 60 days.
            decision_lookback = getattr(df_bt, '_decision_lookback', None)
            if decision_lookback is None:
                decision_lookback = 60

            window_start = max(0, i - int(decision_lookback))
            df_window = df_bt.iloc[window_start:i+1]

            # Compute RSI on window
            try:
                delta = df_window['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(14).mean()
                loss = -delta.where(delta < 0, 0).rolling(14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                rsi_last = rsi.iloc[-1] if not rsi.empty else np.nan
            except Exception:
                rsi_last = np.nan

            # Compute MACD on window
            try:
                ema_fast = df_window['Close'].ewm(span=12, adjust=False).mean()
                ema_slow = df_window['Close'].ewm(span=26, adjust=False).mean()
                macd = ema_fast - ema_slow
                macd_signal = macd.ewm(span=9, adjust=False).mean()
                macd_last = macd.iloc[-1]
                macd_prev = macd.iloc[-2] if len(macd) > 1 else macd_last
                macd_signal_last = macd_signal.iloc[-1]
                macd_signal_prev = macd_signal.iloc[-2] if len(macd_signal) > 1 else macd_signal_last
            except Exception:
                macd_last = macd_prev = macd_signal_last = macd_signal_prev = 0

            buy = (not np.isnan(rsi_last) and rsi_last < 35) or (
                (macd_last > macd_signal_last) and (macd_prev <= macd_signal_prev)
            )
            sell = (not np.isnan(rsi_last) and rsi_last > 65) or (
                (macd_last < macd_signal_last) and (macd_prev >= macd_signal_prev)
            )

            signal = 1 if buy else (-1 if sell else 0)
        vol_mult = slippage_multiplier.iloc[i] if i < len(slippage_multiplier) else 1.0
        if pd.isna(vol_mult):
            vol_mult = 1.0

        # Calculate current equity (mark-to-market)
        if position > 0:  # Long position
            current_equity = capital + (position * current_price)
        elif position < 0:  # Short position
            current_equity = capital + (abs(position) * (entry_price - current_price + entry_price))
        else:
            current_equity = capital

        equity_curve.append({
            'date': df_bt.index[i] if hasattr(df_bt.index[i], 'strftime') else i,
            'equity': current_equity,
            'price': current_price,
            'position': position
        })

        # Track daily returns for risk metrics
        if len(equity_curve) > 1:
            prev_equity = equity_curve[-2]['equity']
            daily_ret = (current_equity - prev_equity) / prev_equity if prev_equity > 0 else 0
            daily_returns.append(daily_ret)

        # Check stop loss / take profit if in position
        if position != 0:
            if position > 0:  # Long position
                pnl_pct = ((current_price - entry_price) / entry_price) * 100
            else:  # Short position
                pnl_pct = ((entry_price - current_price) / entry_price) * 100

            should_close = False
            exit_type = None

            # Stop loss hit
            if pnl_pct <= -stop_loss_pct:
                should_close = True
                exit_type = 'STOP_LOSS'
            # Take profit hit
            elif pnl_pct >= take_profit_pct:
                should_close = True
                exit_type = 'TAKE_PROFIT'

            if should_close:
                exec_price = get_execution_price(current_price, position < 0, vol_mult)
                cost = calculate_transaction_cost(abs(position), exec_price, position < 0, vol_mult)
                total_costs += cost

                if position > 0:  # Close long
                    proceeds = position * exec_price - cost
                    capital += proceeds
                else:  # Close short
                    # Return borrowed shares + profit/loss
                    close_cost = abs(position) * exec_price + cost
                    pnl = abs(position) * (entry_price - exec_price) - cost
                    capital += pnl

                trades.append({
                    'type': exit_type,
                    'direction': 'LONG' if position > 0 else 'SHORT',
                    'entry': entry_price,
                    'exit': exec_price,
                    'pnl_pct': pnl_pct,
                    'shares': abs(position),
                    'cost': cost
                })
                position = 0
                entry_price = 0
                position_type = None
                continue

        # Execute signals with max exposure check
        current_exposure_pct = abs(position * current_price) / current_equity * 100 if current_equity > 0 else 0

        if signal == 1 and position <= 0:  # Buy signal
            # Close short first if exists
            if position < 0:
                exec_price = get_execution_price(current_price, True, vol_mult)
                cost = calculate_transaction_cost(abs(position), exec_price, True, vol_mult)
                total_costs += cost
                # Cover short: buy back shares
                pnl = abs(position) * (entry_price - exec_price) - cost
                capital += pnl
                trades.append({
                    'type': 'COVER_SHORT',
                    'direction': 'SHORT',
                    'entry': entry_price,
                    'exit': exec_price,
                    'pnl_pct': ((entry_price - exec_price) / entry_price) * 100,
                    'shares': abs(position),
                    'cost': cost
                })
                position = 0
                entry_price = 0
                position_type = None

            # Calculate position size
            position_value = capital * (position_size_pct / 100)
            shares = int(position_value / current_price)

            if shares > 0 and current_exposure_pct + (shares * current_price / current_equity * 100) <= max_exposure_pct:
                exec_price = get_execution_price(current_price, True, vol_mult)
                cost = calculate_transaction_cost(shares, exec_price, True, vol_mult)
                total_costs += cost

                position = shares
                entry_price = exec_price
                capital -= (shares * exec_price + cost)
                position_type = 'long'

        elif signal == -1 and position >= 0 and allow_short:  # Sell/Short signal
            # Close long first if exists
            if position > 0:
                exec_price = get_execution_price(current_price, False, vol_mult)
                cost = calculate_transaction_cost(position, exec_price, False, vol_mult)
                total_costs += cost
                proceeds = position * exec_price - cost
                capital += proceeds
                trades.append({
                    'type': 'CLOSE_LONG',
                    'direction': 'LONG',
                    'entry': entry_price,
                    'exit': exec_price,
                    'pnl_pct': ((exec_price - entry_price) / entry_price) * 100,
                    'shares': position,
                    'cost': cost
                })
                position = 0
                entry_price = 0
                position_type = None

            # Calculate short position size
            position_value = capital * (position_size_pct / 100)
            shares = int(position_value / current_price)

            if shares > 0 and current_exposure_pct + (shares * current_price / current_equity * 100) <= max_exposure_pct:
                exec_price = get_execution_price(current_price, False, vol_mult)
                cost = calculate_transaction_cost(shares, exec_price, False, vol_mult)
                total_costs += cost

                position = -shares  # Negative for short
                entry_price = exec_price
                capital += (shares * exec_price - cost)  # Receive proceeds from short sale
                position_type = 'short'

    # Calculate final metrics
    final_equity = equity_curve[-1]['equity'] if equity_curve else initial_capital
    total_return = (final_equity - initial_capital) / initial_capital * 100

    # Risk metrics
    if daily_returns:
        sharpe_ratio = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252) if np.std(daily_returns) > 0 else 0
        max_drawdown = 0
        peak = initial_capital
        for equity in [e['equity'] for e in equity_curve]:
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak * 100
            max_drawdown = max(max_drawdown, drawdown)

        win_rate = sum(1 for t in trades if t['pnl_pct'] > 0) / len(trades) * 100 if trades else 0
        avg_win = np.mean([t['pnl_pct'] for t in trades if t['pnl_pct'] > 0]) if trades else 0
        avg_loss = np.mean([t['pnl_pct'] for t in trades if t['pnl_pct'] < 0]) if trades else 0
        profit_factor = abs(sum(t['pnl_pct'] for t in trades if t['pnl_pct'] > 0) / sum(t['pnl_pct'] for t in trades if t['pnl_pct'] < 0)) if trades else 0

    else:
        sharpe_ratio = 0
        max_drawdown = 0
        win_rate = 0
        avg_win = 0
        avg_loss = 0
        profit_factor = 0

    return {
        'total_return_pct': float(total_return),
        'final_equity': float(final_equity),
        'total_trades': len(trades),
        'winning_trades': sum(1 for t in trades if t['pnl_pct'] > 0),
        'losing_trades': sum(1 for t in trades if t['pnl_pct'] < 0),
        'win_rate_pct': float(win_rate),
        'avg_win_pct': float(avg_win),
        'avg_loss_pct': float(avg_loss),
        'profit_factor': float(profit_factor),
        'sharpe_ratio': float(sharpe_ratio),
        'max_drawdown_pct': float(max_drawdown),
        'total_costs': float(total_costs),
        'net_return_pct': float(total_return - (total_costs / initial_capital * 100)),
        'trades': trades[:50],  # Limit to first 50 trades for display
        'equity_curve': equity_curve[::10]  # Sample every 10th point for performance
    }


def calculate_feature_importance(df: pd.DataFrame, target_col: str = 'Target') -> dict:
    """
    Calculate feature importance using Random Forest and correlation analysis

    Args:
        df: DataFrame with indicator data
        target_col: Target column name (will create if not exists)

    Returns:
        Dict with feature importance rankings and scores
    """
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler

    df_analysis = df.copy()

    # Create target if not exists (1 = price up tomorrow, 0 = down)
    if target_col not in df_analysis.columns:
        df_analysis[target_col] = (df_analysis['Close'].shift(-1) > df_analysis['Close']).astype(int)

    # Select numeric feature columns (exclude OHLCV and target)
    exclude_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close', target_col]
    feature_cols = [col for col in df_analysis.columns
                   if col not in exclude_cols
                   and df_analysis[col].dtype in ['float64', 'float32', 'int64', 'int32']]

    if len(feature_cols) < 3:
        return {'error': 'Not enough numeric features for analysis'}

    # Drop NaN and replace infinities
    df_clean = df_analysis[feature_cols + [target_col]].copy()
    df_clean.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_clean = df_clean.dropna()

    if len(df_clean) < 100:
        return {'error': 'Insufficient data after removing NaN values'}

    X = df_clean[feature_cols].values
    y = df_clean[target_col].values

    # Validate numeric input: ensure no infinities or NaNs remain
    if not np.isfinite(X).all():
        # Remove rows with invalid numeric values
        finite_mask = np.isfinite(X).all(axis=1)
        X = X[finite_mask]
        y = y[finite_mask]

    if X.size == 0 or y.size == 0:
        return {'error': 'No valid numeric data after removing invalid values'}

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train Random Forest for importance
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_scaled, y)

    # Get importance scores
    importances = rf.feature_importances_

    # Calculate correlation with target
    correlations = {}
    for col in feature_cols:
        corr = df_clean[col].corr(df_clean[target_col])
        correlations[col] = corr if not np.isnan(corr) else 0

    # Create ranked list
    importance_df = pd.DataFrame({
        'feature': feature_cols,
        'rf_importance': importances,
        'correlation': [correlations[col] for col in feature_cols]
    })

    # Combined score (weighted average)
    importance_df['combined_score'] = (
        0.7 * importance_df['rf_importance'] / importance_df['rf_importance'].max() +
        0.3 * importance_df['correlation'].abs() / importance_df['correlation'].abs().max()
    )

    importance_df = importance_df.sort_values('combined_score', ascending=False)

    return {
        'top_features': importance_df.head(15).to_dict('records'),
        'all_features': importance_df.to_dict('records'),
        'best_features': importance_df.head(10)['feature'].tolist(),
        'model_accuracy': float(rf.score(X_scaled, y))
    }