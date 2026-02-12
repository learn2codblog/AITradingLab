"""
Portfolio Optimizer Module for TradeGenius AI
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
import signal
import threading

try:
    from .logger import get_logger
except ImportError:
    import logging
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger('portfolio_optimizer')

# Default timeout for optimization (seconds)
OPTIMIZER_TIMEOUT = 30


def optimize_portfolio(returns_df, risk_free_rate=0.05, target_return=None):
    """
    Optimize portfolio weights using Modern Portfolio Theory

    Args:
        returns_df: DataFrame with returns for each asset
        risk_free_rate: Annual risk-free rate
        target_return: Target portfolio return (optional)

    Returns:
        Dict with optimal weights and portfolio stats
    """
    if isinstance(returns_df, pd.DataFrame):
        returns = returns_df.values
        assets = returns_df.columns.tolist()
    else:
        returns = returns_df
        assets = [f'Asset_{i}' for i in range(returns.shape[1])]

    n_assets = returns.shape[1]

    # Calculate mean returns and covariance
    mean_returns = np.mean(returns, axis=0) * 252  # Annualized
    cov_matrix = np.cov(returns.T) * 252  # Annualized

    def portfolio_volatility(weights):
        return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

    def portfolio_return(weights):
        return np.dot(weights, mean_returns)

    def negative_sharpe(weights):
        ret = portfolio_return(weights)
        vol = portfolio_volatility(weights)
        return -(ret - risk_free_rate) / vol if vol > 0 else 0

    # Constraints
    constraints = [
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Weights sum to 1
    ]

    if target_return is not None:
        constraints.append({
            'type': 'eq',
            'fun': lambda x: portfolio_return(x) - target_return
        })

    # Bounds (0 to 1 for each weight, no shorting)
    bounds = tuple((0, 1) for _ in range(n_assets))

    # Initial guess (equal weights)
    initial_weights = np.array([1/n_assets] * n_assets)

    # Optimize for maximum Sharpe ratio with iteration limit to prevent hangs
    try:
        result = minimize(
            negative_sharpe,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000, 'ftol': 1e-9}
        )
        optimal_weights = result.x
        success = result.success
    except Exception as e:
        logger.warning(f"Portfolio optimization failed: {e}. Using equal weights.")
        optimal_weights = initial_weights
        success = False

    # Calculate portfolio statistics
    portfolio_ret = portfolio_return(optimal_weights)
    portfolio_vol = portfolio_volatility(optimal_weights)
    sharpe = (portfolio_ret - risk_free_rate) / portfolio_vol if portfolio_vol > 0 else 0

    return {
        'weights': dict(zip(assets, optimal_weights)),
        'expected_return': portfolio_ret,
        'volatility': portfolio_vol,
        'sharpe_ratio': sharpe,
        'success': success
    }


def calculate_efficient_frontier(returns_df, n_points=50, risk_free_rate=0.05):
    """
    Calculate efficient frontier points

    Args:
        returns_df: DataFrame with returns for each asset
        n_points: Number of points on the frontier
        risk_free_rate: Annual risk-free rate

    Returns:
        Dict with frontier data
    """
    if isinstance(returns_df, pd.DataFrame):
        returns = returns_df.values
    else:
        returns = returns_df

    n_assets = returns.shape[1]
    mean_returns = np.mean(returns, axis=0) * 252

    # Range of target returns
    min_ret = np.min(mean_returns)
    max_ret = np.max(mean_returns)
    target_returns = np.linspace(min_ret, max_ret, n_points)

    frontier_volatilities = []
    frontier_returns = []
    frontier_weights = []

    for target in target_returns:
        try:
            result = optimize_portfolio(returns_df, risk_free_rate, target_return=target)
            if result['success']:
                frontier_returns.append(result['expected_return'])
                frontier_volatilities.append(result['volatility'])
                frontier_weights.append(result['weights'])
        except:
            continue

    return {
        'returns': frontier_returns,
        'volatilities': frontier_volatilities,
        'weights': frontier_weights
    }


def calculate_portfolio_metrics(weights, returns_df, risk_free_rate=0.05):
    """
    Calculate metrics for a given portfolio

    Args:
        weights: Dict or array of weights
        returns_df: DataFrame with returns
        risk_free_rate: Annual risk-free rate

    Returns:
        Dict with portfolio metrics
    """
    if isinstance(weights, dict):
        weights_array = np.array([weights.get(col, 0) for col in returns_df.columns])
    else:
        weights_array = np.array(weights)

    returns = returns_df.values

    # Portfolio returns
    portfolio_returns = np.dot(returns, weights_array)

    # Annualized metrics
    annual_return = np.mean(portfolio_returns) * 252
    annual_volatility = np.std(portfolio_returns) * np.sqrt(252)

    # Sharpe ratio
    sharpe = (annual_return - risk_free_rate) / annual_volatility if annual_volatility > 0 else 0

    # Maximum drawdown
    cumulative = (1 + portfolio_returns).cumprod()
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - running_max) / running_max
    max_dd = drawdown.min()

    # Value at Risk (95%)
    var_95 = np.percentile(portfolio_returns, 5)

    return {
        'annual_return': annual_return,
        'annual_volatility': annual_volatility,
        'sharpe_ratio': sharpe,
        'max_drawdown': max_dd,
        'var_95': var_95,
        'total_return': cumulative[-1] - 1 if len(cumulative) > 0 else 0
    }


def risk_parity_weights(returns_df):
    """
    Calculate risk parity portfolio weights

    Args:
        returns_df: DataFrame with returns

    Returns:
        Dict with weights
    """
    if isinstance(returns_df, pd.DataFrame):
        returns = returns_df.values
        assets = returns_df.columns.tolist()
    else:
        returns = returns_df
        assets = [f'Asset_{i}' for i in range(returns.shape[1])]

    n_assets = returns.shape[1]

    # Calculate volatilities
    volatilities = np.std(returns, axis=0)

    # Inverse volatility weights
    inv_vol = 1 / volatilities
    inv_vol = np.where(np.isinf(inv_vol), 0, inv_vol)

    # Normalize
    weights = inv_vol / np.sum(inv_vol)

    return dict(zip(assets, weights))


def minimum_variance_portfolio(returns_df):
    """
    Calculate minimum variance portfolio weights

    Args:
        returns_df: DataFrame with returns

    Returns:
        Dict with weights
    """
    if isinstance(returns_df, pd.DataFrame):
        returns = returns_df.values
        assets = returns_df.columns.tolist()
    else:
        returns = returns_df
        assets = [f'Asset_{i}' for i in range(returns.shape[1])]

    n_assets = returns.shape[1]
    cov_matrix = np.cov(returns.T)

    def portfolio_variance(weights):
        return np.dot(weights.T, np.dot(cov_matrix, weights))

    constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
    bounds = tuple((0, 1) for _ in range(n_assets))
    initial_weights = np.array([1/n_assets] * n_assets)

    try:
        result = minimize(
            portfolio_variance,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000, 'ftol': 1e-9}
        )
        return dict(zip(assets, result.x))
    except Exception as e:
        logger.warning(f"Minimum variance optimization failed: {e}. Using equal weights.")
        return dict(zip(assets, initial_weights))

