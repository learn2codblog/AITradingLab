# portfolio_optimizer.py
import pandas as pd
import numpy as np
from scipy.optimize import minimize

def optimize_portfolio(returns_dict):
    cov_matrix = pd.DataFrame(returns_dict).cov()
    num_assets = len(returns_dict)
    bounds = tuple((0, 1) for _ in range(num_assets))
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    init_guess = np.array([1. / num_assets] * num_assets)

    opt = minimize(
        portfolio_volatility,
        init_guess,
        args=(cov_matrix,),
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )

    if opt.success:
        return pd.DataFrame({
            "Stock": list(returns_dict.keys()),
            "Weight": opt.x * 100
        }).sort_values("Weight", ascending=False)
    else:
        return pd.DataFrame({
            "Stock": list(returns_dict.keys()),
            "Weight": np.array([100 / num_assets] * num_assets)
        })

def portfolio_volatility(weights, cov_matrix):
    return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
