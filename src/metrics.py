# metrics.py
import numpy as np
import pandas as pd

def sharpe_ratio(returns: pd.Series, rf=0.05 / 252):
    if len(returns) < 10:
        return np.nan
    excess = returns - rf
    return np.sqrt(252) * excess.mean() / (excess.std() + 1e-10)

def max_drawdown(returns: pd.Series):
    equity = (1 + returns).cumprod()
    peak = equity.cummax()
    drawdown = (equity - peak) / peak
    return drawdown.min()

def sortino_ratio(returns: pd.Series, rf=0.05 / 252):
    excess = returns - rf
    downside_std = excess[excess < 0].std() + 1e-10
    return np.sqrt(252) * excess.mean() / downside_std

def backtest_strategy(stock, model_preds, model_probs, confidence_thresh=0.6):
    stock['Position'] = np.where(model_probs.shift(1) > confidence_thresh, 1, 0)
    stock['Strat_Ret'] = stock['Close'].pct_change() * stock['Position']
    eq_strategy = (1 + stock['Strat_Ret']).cumprod()
    return eq_strategy
