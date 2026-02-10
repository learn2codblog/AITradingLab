"""
Volatility Analysis Module for TradeGenius AI
==============================================
Includes:
- GARCH volatility forecasting
- Volatility regime detection
- EWMA volatility fallback
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


def forecast_volatility_garch(df: pd.DataFrame, p: int = 1, q: int = 1,
                              horizon: int = 5) -> dict:
    """
    Forecast volatility using GARCH model or EWMA fallback

    Args:
        df: DataFrame with price data (must have 'Close' column)
        p: GARCH p parameter (AR order)
        q: GARCH q parameter (MA order)
        horizon: Forecast horizon in days

    Returns:
        Dict with volatility forecast and model info
    """
    if len(df) < 100:
        return {'error': 'Insufficient data for volatility forecasting (need 100+ days)'}

    # Calculate returns in percentage
    returns = df['Close'].pct_change().dropna() * 100

    try:
        # Try using arch library for proper GARCH
        from arch import arch_model

        # Fit GARCH model
        model = arch_model(returns, vol='Garch', p=p, q=q, rescale=True)
        result = model.fit(disp='off', show_warning=False)

        # Forecast volatility
        forecast = result.forecast(horizon=horizon)

        # Get forecasted variance and convert to daily volatility (in decimal)
        forecasted_variance = forecast.variance.iloc[-1].values
        forecasted_volatility = np.sqrt(forecasted_variance) / 100  # Convert back to decimal

        # Current conditional volatility
        current_cond_vol = np.sqrt(result.conditional_volatility.iloc[-1]) / 100

        # Model diagnostics
        aic = result.aic
        bic = result.bic

        # Annualized volatility
        annual_vol = forecasted_volatility[-1] * np.sqrt(252) * 100

        return {
            'method': 'GARCH',
            'model': f'GARCH({p},{q})',
            'current_daily_vol': float(current_cond_vol),
            'forecasted_daily_vol': forecasted_volatility.tolist(),
            'forecast_horizon': horizon,
            'avg_forecast_vol': float(np.mean(forecasted_volatility)),
            'annualized_vol_pct': float(annual_vol),
            'aic': float(aic),
            'bic': float(bic),
            'vol_trend': 'Increasing' if forecasted_volatility[-1] > forecasted_volatility[0] else 'Decreasing'
        }

    except ImportError:
        # Fallback to EWMA volatility if arch not installed
        pass
    except Exception as e:
        # Fallback on any GARCH error
        pass

    # EWMA Volatility Fallback
    try:
        # EWMA with lambda = 0.94 (RiskMetrics standard)
        lambda_param = 0.94

        # Calculate squared returns
        sq_returns = (returns / 100) ** 2

        # EWMA variance
        ewma_var = sq_returns.ewm(alpha=(1 - lambda_param), adjust=False).mean()
        current_vol = np.sqrt(ewma_var.iloc[-1])

        # Simple forecast: assume volatility mean-reverts slowly
        long_term_vol = np.sqrt(sq_returns.mean())

        # Forecast volatility with mean reversion
        forecasted_vol = []
        vol = current_vol
        for i in range(horizon):
            # Mean reversion towards long-term vol
            vol = 0.97 * vol + 0.03 * long_term_vol
            forecasted_vol.append(vol)

        forecasted_volatility = np.array(forecasted_vol)
        annual_vol = forecasted_volatility[-1] * np.sqrt(252) * 100

        return {
            'method': 'EWMA',
            'model': f'EWMA(lambda={lambda_param})',
            'current_daily_vol': float(current_vol),
            'forecasted_daily_vol': forecasted_volatility.tolist(),
            'forecast_horizon': horizon,
            'avg_forecast_vol': float(np.mean(forecasted_volatility)),
            'annualized_vol_pct': float(annual_vol),
            'long_term_vol': float(long_term_vol),
            'vol_trend': 'Increasing' if forecasted_volatility[-1] > forecasted_volatility[0] else 'Decreasing',
            'note': 'Install arch package for proper GARCH: pip install arch'
        }

    except Exception as e:
        return {'error': f'Volatility forecasting failed: {str(e)}'}


def get_volatility_regime(df: pd.DataFrame) -> dict:
    """
    Classify current volatility regime and provide trading recommendations

    Args:
        df: DataFrame with price data

    Returns:
        Dict with regime classification and recommendations
    """
    if len(df) < 60:
        return {'error': 'Insufficient data for regime detection'}

    # Calculate various volatility measures
    returns = df['Close'].pct_change().dropna()

    # 10-day and 30-day realized volatility
    vol_10d = returns.tail(10).std() * np.sqrt(252) * 100
    vol_30d = returns.tail(30).std() * np.sqrt(252) * 100
    vol_60d = returns.tail(60).std() * np.sqrt(252) * 100

    # Historical percentiles
    rolling_vol = returns.rolling(20).std() * np.sqrt(252) * 100
    current_vol_percentile = (rolling_vol.iloc[-1] < rolling_vol).mean() * 100

    # Classify regime
    if vol_10d > 40:
        regime = 'Extreme Volatility'
        color = 'red'
        position_size_adj = 0.5
        recommendation = 'Reduce position sizes significantly. Consider hedging.'
    elif vol_10d > 30:
        regime = 'High Volatility'
        color = 'orange'
        position_size_adj = 0.7
        recommendation = 'Use smaller positions. Widen stop-losses.'
    elif vol_10d > 20:
        regime = 'Normal Volatility'
        color = 'yellow'
        position_size_adj = 1.0
        recommendation = 'Standard position sizing. Normal trading rules apply.'
    elif vol_10d > 12:
        regime = 'Low Volatility'
        color = 'green'
        position_size_adj = 1.2
        recommendation = 'Can increase position sizes. Tighten stop-losses.'
    else:
        regime = 'Very Low Volatility'
        color = 'blue'
        position_size_adj = 1.3
        recommendation = 'Watch for volatility expansion. Good for option selling.'

    # Volatility trend
    if vol_10d > vol_30d * 1.2:
        vol_trend = 'Expanding'
        trend_recommendation = 'Volatility is increasing. Be cautious with new positions.'
    elif vol_10d < vol_30d * 0.8:
        vol_trend = 'Contracting'
        trend_recommendation = 'Volatility is decreasing. Good time to establish positions.'
    else:
        vol_trend = 'Stable'
        trend_recommendation = 'Volatility is stable. Normal trading conditions.'

    return {
        'regime': regime,
        'color': color,
        'vol_10d': float(vol_10d),
        'vol_30d': float(vol_30d),
        'vol_60d': float(vol_60d),
        'vol_percentile': float(current_vol_percentile),
        'vol_trend': vol_trend,
        'position_size_adjustment': float(position_size_adj),
        'recommendation': recommendation,
        'trend_recommendation': trend_recommendation
    }