"""
Risk Management Module
Provides risk assessment, position sizing, and risk metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional


def calculate_position_size(
    portfolio_value: float,
    risk_per_trade: float,
    entry_price: float,
    stop_loss_price: float
) -> int:
    """
    Calculate position size based on risk management rules

    Parameters:
    -----------
    portfolio_value : float
        Total portfolio value
    risk_per_trade : float
        Percentage of portfolio to risk per trade (e.g., 0.02 for 2%)
    entry_price : float
        Entry price for the position
    stop_loss_price : float
        Stop loss price

    Returns:
    --------
    int : Number of shares to buy
    """
    if entry_price <= 0 or stop_loss_price <= 0:
        return 0

    risk_amount = portfolio_value * risk_per_trade
    risk_per_share = abs(entry_price - stop_loss_price)

    if risk_per_share == 0:
        return 0

    position_size = int(risk_amount / risk_per_share)

    # Ensure position doesn't exceed 20% of portfolio
    max_shares = int((portfolio_value * 0.2) / entry_price)

    return min(position_size, max_shares)


def calculate_var(returns: pd.Series, confidence_level: float = 0.95) -> float:
    """
    Calculate Value at Risk (VaR)

    Parameters:
    -----------
    returns : pd.Series
        Series of returns
    confidence_level : float
        Confidence level (default: 0.95 for 95%)

    Returns:
    --------
    float : VaR value
    """
    if len(returns) == 0:
        return 0.0

    return np.percentile(returns, (1 - confidence_level) * 100)


def calculate_cvar(returns: pd.Series, confidence_level: float = 0.95) -> float:
    """
    Calculate Conditional Value at Risk (CVaR) / Expected Shortfall

    Parameters:
    -----------
    returns : pd.Series
        Series of returns
    confidence_level : float
        Confidence level

    Returns:
    --------
    float : CVaR value
    """
    if len(returns) == 0:
        return 0.0

    var = calculate_var(returns, confidence_level)
    cvar = returns[returns <= var].mean()

    return cvar if not np.isnan(cvar) else 0.0


def calculate_risk_metrics(data: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate comprehensive risk metrics

    Parameters:
    -----------
    data : pd.DataFrame
        DataFrame with price data (must have 'Close' column)

    Returns:
    --------
    dict : Dictionary of risk metrics
    """
    if 'Close' not in data.columns or len(data) < 2:
        return {}

    # Calculate returns
    returns = data['Close'].pct_change().dropna()

    if len(returns) == 0:
        return {}

    # Calculate metrics
    metrics = {
        'volatility': returns.std() * np.sqrt(252),  # Annualized
        'var_95': calculate_var(returns, 0.95),
        'cvar_95': calculate_cvar(returns, 0.95),
        'var_99': calculate_var(returns, 0.99),
        'cvar_99': calculate_cvar(returns, 0.99),
        'downside_deviation': returns[returns < 0].std() * np.sqrt(252),
        'max_daily_loss': returns.min(),
        'max_daily_gain': returns.max(),
        'average_return': returns.mean(),
        'skewness': returns.skew(),
        'kurtosis': returns.kurtosis(),
    }

    return metrics


def calculate_kelly_criterion(
    win_rate: float,
    avg_win: float,
    avg_loss: float
) -> float:
    """
    Calculate Kelly Criterion for optimal position sizing

    Parameters:
    -----------
    win_rate : float
        Probability of winning (0 to 1)
    avg_win : float
        Average winning percentage
    avg_loss : float
        Average losing percentage

    Returns:
    --------
    float : Kelly percentage (fraction of capital to risk)
    """
    if avg_loss == 0:
        return 0.0

    win_loss_ratio = abs(avg_win / avg_loss)
    kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio

    # Apply half-Kelly for safety
    kelly = max(0, kelly) * 0.5

    # Cap at 25% of portfolio
    return min(kelly, 0.25)


def calculate_stop_loss_take_profit(
    entry_price: float,
    atr: float,
    risk_reward_ratio: float = 2.0,
    atr_multiplier: float = 2.0
) -> Tuple[float, float]:
    """
    Calculate dynamic stop loss and take profit levels based on ATR

    Parameters:
    -----------
    entry_price : float
        Entry price
    atr : float
        Average True Range
    risk_reward_ratio : float
        Risk to reward ratio (default: 2.0)
    atr_multiplier : float
        ATR multiplier for stop loss (default: 2.0)

    Returns:
    --------
    tuple : (stop_loss, take_profit)
    """
    stop_loss = entry_price - (atr * atr_multiplier)
    take_profit = entry_price + (atr * atr_multiplier * risk_reward_ratio)

    return round(stop_loss, 2), round(take_profit, 2)


def calculate_portfolio_risk(
    positions: Dict[str, Dict],
    correlation_matrix: pd.DataFrame
) -> Dict[str, float]:
    """
    Calculate portfolio-level risk metrics

    Parameters:
    -----------
    positions : dict
        Dictionary of positions with weights and volatilities
        Format: {symbol: {'weight': 0.2, 'volatility': 0.3}}
    correlation_matrix : pd.DataFrame
        Correlation matrix of returns

    Returns:
    --------
    dict : Portfolio risk metrics
    """
    symbols = list(positions.keys())
    weights = np.array([positions[s]['weight'] for s in symbols])

    # Calculate portfolio variance
    portfolio_variance = 0
    for i, symbol_i in enumerate(symbols):
        for j, symbol_j in enumerate(symbols):
            if symbol_i in correlation_matrix.index and symbol_j in correlation_matrix.columns:
                corr = correlation_matrix.loc[symbol_i, symbol_j]
                vol_i = positions[symbol_i].get('volatility', 0)
                vol_j = positions[symbol_j].get('volatility', 0)
                portfolio_variance += weights[i] * weights[j] * vol_i * vol_j * corr

    portfolio_std = np.sqrt(max(0, portfolio_variance))

    return {
        'portfolio_volatility': portfolio_std,
        'diversification_ratio': sum([positions[s]['volatility'] * positions[s]['weight']
                                     for s in symbols]) / portfolio_std if portfolio_std > 0 else 0,
        'concentration_risk': max(weights)
    }


def assess_trade_risk(
    entry_price: float,
    stop_loss: float,
    take_profit: float,
    position_size: int,
    portfolio_value: float
) -> Dict[str, float]:
    """
    Assess risk for a specific trade

    Parameters:
    -----------
    entry_price : float
        Entry price
    stop_loss : float
        Stop loss price
    take_profit : float
        Take profit price
    position_size : int
        Number of shares
    portfolio_value : float
        Total portfolio value

    Returns:
    --------
    dict : Trade risk assessment
    """
    position_value = entry_price * position_size
    risk_amount = abs(entry_price - stop_loss) * position_size
    reward_amount = abs(take_profit - entry_price) * position_size

    return {
        'position_value': position_value,
        'position_pct': (position_value / portfolio_value * 100) if portfolio_value > 0 else 0,
        'risk_amount': risk_amount,
        'risk_pct': (risk_amount / portfolio_value * 100) if portfolio_value > 0 else 0,
        'reward_amount': reward_amount,
        'reward_pct': (reward_amount / portfolio_value * 100) if portfolio_value > 0 else 0,
        'risk_reward_ratio': (reward_amount / risk_amount) if risk_amount > 0 else 0
    }


def check_risk_limits(trade_assessment: Dict[str, float]) -> Dict[str, bool]:
    """
    Check if trade meets risk management criteria

    Parameters:
    -----------
    trade_assessment : dict
        Output from assess_trade_risk

    Returns:
    --------
    dict : Risk checks with pass/fail status
    """
    checks = {
        'position_size_ok': trade_assessment['position_pct'] <= 20,  # Max 20% per position
        'risk_acceptable': trade_assessment['risk_pct'] <= 2,         # Max 2% risk per trade
        'risk_reward_ok': trade_assessment['risk_reward_ratio'] >= 1.5, # Min 1.5:1 RR ratio
    }

    checks['all_checks_pass'] = all(checks.values())

    return checks

