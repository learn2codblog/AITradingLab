"""
Portfolio Metrics Module for TradeGenius AI
"""

import numpy as np
import pandas as pd


def sharpe_ratio(returns, risk_free_rate=0.05, periods=252):
    """
    Calculate Sharpe Ratio

    Args:
        returns: Series or array of returns
        risk_free_rate: Annual risk-free rate
        periods: Trading periods per year (252 for daily)

    Returns:
        Sharpe ratio
    """
    if isinstance(returns, pd.Series):
        returns = returns.dropna()

    if len(returns) == 0:
        return 0

    excess_returns = returns - risk_free_rate / periods

    if np.std(returns) == 0:
        return 0

    return np.sqrt(periods) * np.mean(excess_returns) / np.std(returns)


def sortino_ratio(returns, risk_free_rate=0.05, periods=252):
    """
    Calculate Sortino Ratio (downside risk adjusted)

    Args:
        returns: Series or array of returns
        risk_free_rate: Annual risk-free rate
        periods: Trading periods per year

    Returns:
        Sortino ratio
    """
    if isinstance(returns, pd.Series):
        returns = returns.dropna()

    if len(returns) == 0:
        return 0

    excess_returns = returns - risk_free_rate / periods

    # Downside deviation
    negative_returns = returns[returns < 0]

    if len(negative_returns) == 0 or np.std(negative_returns) == 0:
        return sharpe_ratio(returns, risk_free_rate, periods)

    downside_std = np.std(negative_returns)

    return np.sqrt(periods) * np.mean(excess_returns) / downside_std


def max_drawdown(prices):
    """
    Calculate Maximum Drawdown

    Args:
        prices: Series or array of prices

    Returns:
        Maximum drawdown as decimal (negative)
    """
    if isinstance(prices, pd.Series):
        prices = prices.dropna()

    if len(prices) == 0:
        return 0

    # Calculate running maximum
    running_max = np.maximum.accumulate(prices)

    # Calculate drawdown
    drawdown = (prices - running_max) / running_max

    return drawdown.min()


def calmar_ratio(returns, prices, periods=252):
    """
    Calculate Calmar Ratio (return / max drawdown)

    Args:
        returns: Series of returns
        prices: Series of prices
        periods: Periods per year

    Returns:
        Calmar ratio
    """
    if isinstance(returns, pd.Series):
        returns = returns.dropna()

    annual_return = np.mean(returns) * periods
    mdd = abs(max_drawdown(prices))

    if mdd == 0:
        return 0

    return annual_return / mdd


def _safe_align(returns, benchmark_returns):
    """
    Safely align two return series by index (date-aware) with inner join.
    Falls back to length-based alignment for non-Series inputs.
    """
    if isinstance(returns, pd.Series) and isinstance(benchmark_returns, pd.Series):
        returns, benchmark_returns = returns.align(benchmark_returns, join='inner')
        returns = returns.dropna()
        benchmark_returns = benchmark_returns.dropna()
        # Re-align after dropna in case indices diverged
        returns, benchmark_returns = returns.align(benchmark_returns, join='inner')
    else:
        # Fallback for arrays
        if isinstance(returns, pd.Series):
            returns = returns.dropna().values
        if isinstance(benchmark_returns, pd.Series):
            benchmark_returns = benchmark_returns.dropna().values
        min_len = min(len(returns), len(benchmark_returns))
        returns = np.array(returns[-min_len:])
        benchmark_returns = np.array(benchmark_returns[-min_len:])
    return returns, benchmark_returns


def information_ratio(returns, benchmark_returns, periods=252):
    """
    Calculate Information Ratio

    Args:
        returns: Strategy returns
        benchmark_returns: Benchmark returns
        periods: Periods per year

    Returns:
        Information ratio
    """
    returns, benchmark_returns = _safe_align(returns, benchmark_returns)

    if len(returns) == 0:
        return 0

    excess_returns = returns - benchmark_returns
    tracking_error = np.std(excess_returns)

    if tracking_error == 0:
        return 0

    return np.sqrt(periods) * np.mean(excess_returns) / tracking_error


def beta(returns, market_returns):
    """
    Calculate Beta (market sensitivity)

    Args:
        returns: Asset returns
        market_returns: Market returns

    Returns:
        Beta coefficient
    """
    returns, market_returns = _safe_align(returns, market_returns)

    if len(returns) < 2:
        return 1

    covariance = np.cov(returns, market_returns)[0, 1]
    market_variance = np.var(market_returns)

    if market_variance == 0:
        return 1

    return covariance / market_variance


def alpha(returns, market_returns, risk_free_rate=0.05, periods=252):
    """
    Calculate Alpha (excess return over market)

    Args:
        returns: Asset returns
        market_returns: Market returns
        risk_free_rate: Annual risk-free rate
        periods: Periods per year

    Returns:
        Alpha
    """
    returns, market_returns = _safe_align(returns, market_returns)

    if len(returns) == 0:
        return 0

    asset_return = np.mean(returns) * periods
    market_return = np.mean(market_returns) * periods
    asset_beta = beta(returns, market_returns)

    # CAPM Alpha
    expected_return = risk_free_rate + asset_beta * (market_return - risk_free_rate)

    return asset_return - expected_return


def value_at_risk(returns, confidence=0.95):
    """
    Calculate Value at Risk

    Args:
        returns: Series of returns
        confidence: Confidence level (0.95 = 95%)

    Returns:
        VaR as positive decimal
    """
    if isinstance(returns, pd.Series):
        returns = returns.dropna()

    if len(returns) == 0:
        return 0

    return abs(np.percentile(returns, (1 - confidence) * 100))


def expected_shortfall(returns, confidence=0.95):
    """
    Calculate Expected Shortfall (CVaR)

    Args:
        returns: Series of returns
        confidence: Confidence level

    Returns:
        Expected shortfall as positive decimal
    """
    if isinstance(returns, pd.Series):
        returns = returns.dropna()

    if len(returns) == 0:
        return 0

    var = value_at_risk(returns, confidence)
    return abs(np.mean(returns[returns <= -var]))


def win_rate(returns):
    """
    Calculate win rate (percentage of positive returns)

    Args:
        returns: Series of returns

    Returns:
        Win rate as decimal
    """
    if isinstance(returns, pd.Series):
        returns = returns.dropna()

    if len(returns) == 0:
        return 0

    return np.sum(returns > 0) / len(returns)


def profit_factor(returns):
    """
    Calculate profit factor (gross profits / gross losses)

    Args:
        returns: Series of returns

    Returns:
        Profit factor
    """
    if isinstance(returns, pd.Series):
        returns = returns.dropna()

    profits = np.sum(returns[returns > 0])
    losses = abs(np.sum(returns[returns < 0]))

    if losses == 0:
        return float('inf') if profits > 0 else 0

    return profits / losses


def calculate_all_metrics(returns, prices=None, benchmark_returns=None):
    """
    Calculate all performance metrics

    Args:
        returns: Series of returns
        prices: Series of prices (optional)
        benchmark_returns: Benchmark returns (optional)

    Returns:
        Dict with all metrics
    """
    metrics = {
        'sharpe_ratio': sharpe_ratio(returns),
        'sortino_ratio': sortino_ratio(returns),
        'value_at_risk_95': value_at_risk(returns, 0.95),
        'expected_shortfall': expected_shortfall(returns, 0.95),
        'win_rate': win_rate(returns),
        'profit_factor': profit_factor(returns),
        'annual_return': np.mean(returns) * 252,
        'annual_volatility': np.std(returns) * np.sqrt(252)
    }

    if prices is not None:
        metrics['max_drawdown'] = max_drawdown(prices)
        metrics['calmar_ratio'] = calmar_ratio(returns, prices)

    if benchmark_returns is not None:
        metrics['information_ratio'] = information_ratio(returns, benchmark_returns)
        metrics['beta'] = beta(returns, benchmark_returns)
        metrics['alpha'] = alpha(returns, benchmark_returns)

    return metrics

