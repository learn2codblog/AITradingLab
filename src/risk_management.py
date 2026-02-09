"""
Risk Management Module for TradeGenius AI
"""

import numpy as np
import pandas as pd


def calculate_risk_metrics(df: pd.DataFrame, risk_free_rate: float = 0.05) -> dict:
    """
    Calculate comprehensive risk metrics

    Args:
        df: DataFrame with OHLCV data and indicators
        risk_free_rate: Annual risk-free rate

    Returns:
        Dict with risk metrics
    """
    if len(df) < 20:
        return {
            'volatility': 0,
            'var_95': 0,
            'max_drawdown': 0,
            'sharpe_ratio': 0,
            'sortino_ratio': 0
        }

    # Calculate daily returns
    if 'Daily_Return' in df.columns:
        returns = df['Daily_Return'].dropna()
    else:
        returns = df['Close'].pct_change().dropna()

    # Volatility (annualized)
    daily_vol = returns.std()
    annual_vol = daily_vol * np.sqrt(252)

    # Value at Risk (95% confidence)
    var_95 = np.percentile(returns, 5)

    # Maximum Drawdown
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_dd = drawdown.min()

    # Sharpe Ratio
    excess_returns = returns.mean() - risk_free_rate / 252
    sharpe = (excess_returns / daily_vol) * np.sqrt(252) if daily_vol > 0 else 0

    # Sortino Ratio (downside deviation)
    negative_returns = returns[returns < 0]
    downside_std = negative_returns.std() if len(negative_returns) > 0 else daily_vol
    sortino = (excess_returns / downside_std) * np.sqrt(252) if downside_std > 0 else 0

    # Maximum daily loss
    max_daily_loss = returns.min()

    # Maximum daily gain
    max_daily_gain = returns.max()

    # Average true range for volatility
    atr = df.get('ATR14', pd.Series([0])).iloc[-1]
    atr_percent = (atr / df['Close'].iloc[-1] * 100) if atr > 0 else 0

    # Win rate
    win_rate = (returns > 0).sum() / len(returns)

    # Average win and loss
    avg_win = returns[returns > 0].mean() if len(returns[returns > 0]) > 0 else 0
    avg_loss = returns[returns < 0].mean() if len(returns[returns < 0]) > 0 else 0

    # Profit factor
    gross_profit = returns[returns > 0].sum()
    gross_loss = abs(returns[returns < 0].sum())
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

    return {
        'volatility': annual_vol,
        'daily_volatility': daily_vol,
        'var_95': var_95,
        'max_drawdown': max_dd,
        'sharpe_ratio': sharpe,
        'sortino_ratio': sortino,
        'max_daily_loss': max_daily_loss,
        'max_daily_gain': max_daily_gain,
        'atr_percent': atr_percent,
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'profit_factor': profit_factor,
        'downside_deviation': downside_std * np.sqrt(252)
    }


def calculate_stop_loss_take_profit(df: pd.DataFrame, method: str = 'atr',
                                     atr_multiplier: float = 2.0,
                                     percent: float = 0.05) -> dict:
    """
    Calculate stop loss and take profit levels

    Args:
        df: DataFrame with OHLCV data
        method: 'atr', 'percent', or 'support_resistance'
        atr_multiplier: Multiplier for ATR-based calculation
        percent: Percentage for percent-based calculation

    Returns:
        Dict with SL and TP levels
    """
    current_price = df['Close'].iloc[-1]

    if method == 'atr':
        # ATR-based stop loss
        if 'ATR14' in df.columns:
            atr = df['ATR14'].iloc[-1]
        else:
            high_low = df['High'] - df['Low']
            high_close = abs(df['High'] - df['Close'].shift())
            low_close = abs(df['Low'] - df['Close'].shift())
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = tr.tail(14).mean()

        stop_loss = current_price - atr_multiplier * atr
        take_profit = current_price + atr_multiplier * 1.5 * atr  # 1.5:1 R/R

    elif method == 'percent':
        stop_loss = current_price * (1 - percent)
        take_profit = current_price * (1 + percent * 2)  # 2:1 R/R

    elif method == 'support_resistance':
        # Find recent support and resistance
        lookback = min(50, len(df))
        recent = df.tail(lookback)

        support = recent['Low'].min()
        resistance = recent['High'].max()

        stop_loss = support * 0.98  # Just below support
        take_profit = resistance * 1.02  # Just above resistance

    else:
        # Default to percent
        stop_loss = current_price * 0.95
        take_profit = current_price * 1.10

    # Calculate risk/reward
    risk = current_price - stop_loss
    reward = take_profit - current_price
    rr_ratio = reward / risk if risk > 0 else 0

    # Risk percentage
    risk_percent = (risk / current_price) * 100
    reward_percent = (reward / current_price) * 100

    return {
        'current_price': round(current_price, 2),
        'stop_loss': round(stop_loss, 2),
        'take_profit': round(take_profit, 2),
        'risk_reward_ratio': round(rr_ratio, 2),
        'risk_percent': round(risk_percent, 2),
        'reward_percent': round(reward_percent, 2),
        'method': method
    }


def calculate_position_size(account_balance: float, risk_percent: float,
                            entry_price: float, stop_loss: float) -> dict:
    """
    Calculate position size based on risk management

    Args:
        account_balance: Total account balance
        risk_percent: Percentage of account to risk (e.g., 0.02 for 2%)
        entry_price: Entry price
        stop_loss: Stop loss price

    Returns:
        Dict with position sizing
    """
    # Risk amount
    risk_amount = account_balance * risk_percent

    # Risk per share
    risk_per_share = abs(entry_price - stop_loss)

    if risk_per_share == 0:
        return {
            'shares': 0,
            'position_value': 0,
            'risk_amount': risk_amount,
            'error': 'Stop loss equals entry price'
        }

    # Number of shares
    shares = int(risk_amount / risk_per_share)

    # Position value
    position_value = shares * entry_price

    # Actual risk
    actual_risk = shares * risk_per_share

    # Position as percentage of account
    position_percent = (position_value / account_balance) * 100

    return {
        'shares': shares,
        'position_value': round(position_value, 2),
        'position_percent': round(position_percent, 2),
        'risk_amount': round(risk_amount, 2),
        'actual_risk': round(actual_risk, 2),
        'risk_per_share': round(risk_per_share, 2),
        'max_loss': round(actual_risk, 2)
    }


def calculate_portfolio_risk(weights: dict, returns_df: pd.DataFrame) -> dict:
    """
    Calculate portfolio-level risk metrics

    Args:
        weights: Dict mapping symbols to weights
        returns_df: DataFrame with returns for each symbol

    Returns:
        Dict with portfolio risk metrics
    """
    # Convert weights to array
    symbols = list(weights.keys())
    weight_array = np.array([weights[s] for s in symbols])

    # Get returns for these symbols
    available = [s for s in symbols if s in returns_df.columns]

    if len(available) == 0:
        return {'error': 'No matching symbols in returns data'}

    returns = returns_df[available].values
    weights_subset = np.array([weights[s] for s in available])
    weights_subset = weights_subset / weights_subset.sum()  # Normalize

    # Portfolio returns
    portfolio_returns = np.dot(returns, weights_subset)

    # Covariance matrix
    cov_matrix = np.cov(returns.T) * 252

    # Portfolio variance and volatility
    portfolio_variance = np.dot(weights_subset.T, np.dot(cov_matrix, weights_subset))
    portfolio_volatility = np.sqrt(portfolio_variance)

    # Portfolio beta (if market returns available)
    portfolio_mean_return = np.mean(portfolio_returns) * 252

    # Value at Risk
    var_95 = np.percentile(portfolio_returns, 5)
    var_99 = np.percentile(portfolio_returns, 1)

    # Maximum drawdown
    cumulative = (1 + portfolio_returns).cumprod()
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - running_max) / running_max
    max_dd = drawdown.min()

    # Diversification ratio
    individual_vols = np.std(returns, axis=0) * np.sqrt(252)
    weighted_avg_vol = np.dot(weights_subset, individual_vols)
    diversification_ratio = weighted_avg_vol / portfolio_volatility if portfolio_volatility > 0 else 1

    return {
        'portfolio_volatility': portfolio_volatility,
        'portfolio_return': portfolio_mean_return,
        'var_95_daily': var_95,
        'var_99_daily': var_99,
        'max_drawdown': max_dd,
        'diversification_ratio': diversification_ratio,
        'num_assets': len(available)
    }

