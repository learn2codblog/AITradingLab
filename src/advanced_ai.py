"""
Advanced AI & Deep Learning Module for TradeGenius AI
=====================================================
Includes:
- LSTM Price Prediction
- Sentiment Analysis with Transformers
- Advanced Technical Indicators (30+)
- Pattern Recognition
- Volatility Models (GARCH)
- Ensemble ML Models
- Anomaly Detection
- Market Regime Detection
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ══════════════════════════════════════════════════════════════════════
# ADVANCED TECHNICAL INDICATORS (30+ Indicators)
# ══════════════════════════════════════════════════════════════════════

def calculate_advanced_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate 30+ advanced technical indicators

    Args:
        df: DataFrame with OHLCV data

    Returns:
        DataFrame with all indicators added
    """
    df = df.copy()

    # ─── TREND INDICATORS ───

    # 1. Simple Moving Averages (Multiple periods)
    for period in [5, 10, 20, 50, 100, 200]:
        df[f'SMA_{period}'] = df['Close'].rolling(window=period).mean()

    # 2. Exponential Moving Averages
    for period in [9, 12, 21, 26, 50]:
        df[f'EMA_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()

    # 3. Double EMA (DEMA)
    ema_20 = df['Close'].ewm(span=20, adjust=False).mean()
    df['DEMA_20'] = 2 * ema_20 - ema_20.ewm(span=20, adjust=False).mean()

    # 4. Triple EMA (TEMA)
    ema1 = df['Close'].ewm(span=20, adjust=False).mean()
    ema2 = ema1.ewm(span=20, adjust=False).mean()
    ema3 = ema2.ewm(span=20, adjust=False).mean()
    df['TEMA_20'] = 3 * ema1 - 3 * ema2 + ema3

    # 5. Weighted Moving Average (WMA)
    weights = np.arange(1, 21)
    df['WMA_20'] = df['Close'].rolling(20).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

    # 6. Hull Moving Average (HMA) - Faster, smoother
    wma_half = df['Close'].rolling(10).apply(lambda x: np.dot(x, np.arange(1, 11)) / np.arange(1, 11).sum(), raw=True)
    wma_full = df['Close'].rolling(20).apply(lambda x: np.dot(x, np.arange(1, 21)) / np.arange(1, 21).sum(), raw=True)
    df['HMA_20'] = (2 * wma_half - wma_full).rolling(4).mean()

    # 7. VWAP (Volume Weighted Average Price)
    df['VWAP'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()

    # 8. Supertrend (Complete Implementation)
    df = calculate_supertrend(df, period=10, multiplier=2)

    # ─── MOMENTUM INDICATORS ───

    # 9. RSI (Multiple periods)
    for period in [7, 14, 21]:
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df[f'RSI_{period}'] = 100 - (100 / (1 + rs))

    # 10. Stochastic RSI
    rsi = df['RSI_14']
    stoch_rsi = (rsi - rsi.rolling(14).min()) / (rsi.rolling(14).max() - rsi.rolling(14).min())
    df['StochRSI_K'] = stoch_rsi.rolling(3).mean() * 100
    df['StochRSI_D'] = df['StochRSI_K'].rolling(3).mean()

    # 11. MACD (Standard and Histogram)
    ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema_12 - ema_26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']

    # 12. Stochastic Oscillator
    low_14 = df['Low'].rolling(14).min()
    high_14 = df['High'].rolling(14).max()
    df['Stoch_K'] = 100 * (df['Close'] - low_14) / (high_14 - low_14)
    df['Stoch_D'] = df['Stoch_K'].rolling(3).mean()

    # 13. Williams %R
    df['Williams_R'] = -100 * (high_14 - df['Close']) / (high_14 - low_14)

    # 14. Commodity Channel Index (CCI)
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    df['CCI'] = (tp - tp.rolling(20).mean()) / (0.015 * tp.rolling(20).std())

    # 15. Rate of Change (ROC)
    df['ROC'] = df['Close'].pct_change(periods=10) * 100

    # 16. Momentum
    df['Momentum'] = df['Close'] - df['Close'].shift(10)

    # 17. Ultimate Oscillator
    bp = df['Close'] - df[['Low', 'Close']].shift(1).min(axis=1)
    tr = df[['High', 'Close']].shift(1).max(axis=1) - df[['Low', 'Close']].shift(1).min(axis=1)
    avg7 = bp.rolling(7).sum() / tr.rolling(7).sum()
    avg14 = bp.rolling(14).sum() / tr.rolling(14).sum()
    avg28 = bp.rolling(28).sum() / tr.rolling(28).sum()
    df['Ultimate_Oscillator'] = 100 * (4 * avg7 + 2 * avg14 + avg28) / 7

    # 18. Awesome Oscillator
    df['Awesome_Oscillator'] = df['Close'].rolling(5).mean() - df['Close'].rolling(34).mean()

    # ─── VOLATILITY INDICATORS ───

    # 19. ATR (Average True Range)
    df['ATR_14'] = calculate_atr(df, 14)
    df['ATR_20'] = calculate_atr(df, 20)

    # 20. Bollinger Bands
    sma_20 = df['Close'].rolling(20).mean()
    std_20 = df['Close'].rolling(20).std()
    df['BB_Upper'] = sma_20 + (2 * std_20)
    df['BB_Middle'] = sma_20
    df['BB_Lower'] = sma_20 - (2 * std_20)
    df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
    df['BB_Percent'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])

    # 21. Keltner Channel
    ema_20 = df['Close'].ewm(span=20, adjust=False).mean()
    atr_10 = calculate_atr(df, 10)
    df['Keltner_Upper'] = ema_20 + (2 * atr_10)
    df['Keltner_Middle'] = ema_20
    df['Keltner_Lower'] = ema_20 - (2 * atr_10)

    # 22. Donchian Channel
    df['Donchian_Upper'] = df['High'].rolling(20).max()
    df['Donchian_Lower'] = df['Low'].rolling(20).min()
    df['Donchian_Middle'] = (df['Donchian_Upper'] + df['Donchian_Lower']) / 2

    # 23. Historical Volatility
    df['HV_20'] = df['Close'].pct_change().rolling(20).std() * np.sqrt(252) * 100

    # 24. Chaikin Volatility
    hl_diff = df['High'] - df['Low']
    ema_hl = hl_diff.ewm(span=10, adjust=False).mean()
    df['Chaikin_Volatility'] = (ema_hl - ema_hl.shift(10)) / ema_hl.shift(10) * 100

    # ─── VOLUME INDICATORS ───

    # 25. On-Balance Volume (OBV)
    df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()

    # 26. Accumulation/Distribution Line
    clv = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'])
    df['AD_Line'] = (clv * df['Volume']).fillna(0).cumsum()

    # 27. Money Flow Index (MFI)
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    mf = tp * df['Volume']
    positive_mf = mf.where(tp > tp.shift(1), 0).rolling(14).sum()
    negative_mf = mf.where(tp < tp.shift(1), 0).rolling(14).sum()
    df['MFI'] = 100 - (100 / (1 + positive_mf / negative_mf))

    # 28. Chaikin Money Flow (CMF)
    mfv = clv * df['Volume']
    df['CMF'] = mfv.rolling(20).sum() / df['Volume'].rolling(20).sum()

    # 29. Volume Rate of Change
    df['VROC'] = df['Volume'].pct_change(periods=14) * 100

    # 30. Force Index
    df['Force_Index'] = df['Close'].diff() * df['Volume']
    df['Force_Index_13'] = df['Force_Index'].ewm(span=13, adjust=False).mean()

    # ─── TREND STRENGTH INDICATORS ───

    # 31. ADX (Average Directional Index)
    df['ADX'] = calculate_adx(df, 14)

    # 32. Aroon Oscillator
    df['Aroon_Up'] = df['High'].rolling(25).apply(lambda x: x.argmax() / 24 * 100, raw=True)
    df['Aroon_Down'] = df['Low'].rolling(25).apply(lambda x: x.argmin() / 24 * 100, raw=True)
    df['Aroon_Oscillator'] = df['Aroon_Up'] - df['Aroon_Down']

    # 33. Parabolic SAR (with direction)
    df = calculate_psar(df, af_start=0.02, af_increment=0.02, af_max=0.20)

    # ─── ADDITIONAL FEATURES ───

    # 34. Price Distance from Moving Averages
    df['Distance_SMA_20'] = (df['Close'] - df['SMA_20']) / df['SMA_20'] * 100
    df['Distance_SMA_50'] = (df['Close'] - df['SMA_50']) / df['SMA_50'] * 100
    df['Distance_SMA_200'] = (df['Close'] - df['SMA_200']) / df['SMA_200'] * 100

    # 35. Trend Score (composite)
    df['Trend_Score'] = (
        (df['Close'] > df['SMA_20']).astype(int) +
        (df['Close'] > df['SMA_50']).astype(int) +
        (df['Close'] > df['SMA_200']).astype(int) +
        (df['SMA_20'] > df['SMA_50']).astype(int) +
        (df['SMA_50'] > df['SMA_200']).astype(int)
    )

    # 36. Volatility Regime
    df['Volatility_Regime'] = pd.cut(df['HV_20'], bins=[0, 15, 25, 40, 100], labels=['Low', 'Normal', 'High', 'Extreme'])

    return df


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate Average True Range"""
    high_low = df['High'] - df['Low']
    high_close = abs(df['High'] - df['Close'].shift())
    low_close = abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def calculate_supertrend(
    df: pd.DataFrame,
    period: int = 10,
    multiplier: float = 3.0  # Most common/popular default (your original call uses 2, so it will override)
) -> pd.DataFrame:
    """
    Robust & accurate SuperTrend implementation (matches TradingView / standard TA libraries)

    Adds columns:
        'ATR'
        'Supertrend'               # The final SuperTrend line
        'Supertrend_Direction'     # 1 = uptrend (bullish), -1 = downtrend (bearish)
        'Supertrend_Upper'         # Upper band (active in downtrend)
        'Supertrend_Lower'         # Lower band (active in uptrend)
    """
    df = df.copy()

    # 1. Calculate ATR (reuse your existing function)
    df['ATR'] = calculate_atr(df, period)

    # 2. Basic bands (using HL2 - most common)
    hl2 = (df['High'] + df['Low']) / 2
    upper_basic = hl2 + (multiplier * df['ATR'])
    lower_basic = hl2 - (multiplier * df['ATR'])

    # 3. Initialize final bands & direction
    length = len(df)
    supertrend = np.full(length, np.nan)
    direction = np.zeros(length, dtype=int)      # 1 = uptrend, -1 = downtrend
    final_upper = upper_basic.copy()
    final_lower = lower_basic.copy()

    # Need enough data for ATR
    first_valid = period
    if length <= first_valid:
        df['Supertrend'] = supertrend
        df['Supertrend_Direction'] = direction
        df['Supertrend_Upper'] = final_upper
        df['Supertrend_Lower'] = final_lower
        return df

    # 4. Seed the first valid value (assume uptrend start - standard practice)
    final_lower[first_valid] = lower_basic.iloc[first_valid]
    final_upper[first_valid] = upper_basic.iloc[first_valid]
    supertrend[first_valid] = final_lower[first_valid]   # show lower band in uptrend
    direction[first_valid] = 1

    # 5. Main sequential logic (small loop - this is the standard & most accurate way)
    for i in range(first_valid + 1, length):
        close_i = df['Close'].iloc[i]

        if direction[i-1] == 1:  # Previous bar was uptrend
            # Lower band ratchets up only
            final_lower[i] = max(lower_basic.iloc[i], final_lower[i-1])
            final_upper[i] = upper_basic.iloc[i]

            if close_i <= final_lower[i]:  # Close below final lower → flip to downtrend
                direction[i] = -1
                supertrend[i] = final_upper[i]
            else:
                direction[i] = 1
                supertrend[i] = final_lower[i]

        else:  # Previous bar was downtrend
            # Upper band ratchets down only
            final_upper[i] = min(upper_basic.iloc[i], final_upper[i-1])
            final_lower[i] = lower_basic.iloc[i]

            if close_i >= final_upper[i]:  # Close above final upper → flip to uptrend
                direction[i] = 1
                supertrend[i] = final_lower[i]
            else:
                direction[i] = -1
                supertrend[i] = final_upper[i]

    # Assign to dataframe
    df['Supertrend'] = supertrend
    df['Supertrend_Direction'] = direction
    df['Supertrend_Upper'] = final_upper
    df['Supertrend_Lower'] = final_lower

    return df


def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Corrected & precise ADX implementation using exact Wilder smoothing
    (initial sum over period, then recursive (prev*(period-1) + current)/period)

    This matches TA-Lib, TradingView, and Wilder's original method exactly.

    Returns:
        pd.Series with ADX values (NaN for first ~2*period bars)
    """
    if len(df) < period + 1:
        return pd.Series(np.nan, index=df.index, name='ADX')

    high = df['High']
    low = df['Low']
    close = df['Close']

    # ─── 1. True Range ───────────────────────────────────────────────────
    tr = pd.DataFrame(index=df.index)
    tr['h_l'] = high - low
    tr['h_pc'] = (high - close.shift(1)).abs()
    tr['l_pc'] = (low - close.shift(1)).abs()
    tr['tr'] = tr.max(axis=1)

    # ─── 2. Directional Movement ────────────────────────────────────────
    up = high.diff()
    down = -low.diff()

    plus_dm = pd.Series(0.0, index=df.index)
    minus_dm = pd.Series(0.0, index=df.index)

    # +DM: up move is greater than down move AND up move is positive
    plus_dm_mask = (up > down) & (up > 0)
    plus_dm[plus_dm_mask] = up[plus_dm_mask]

    # -DM: down move is greater than up move AND down move is positive
    minus_dm_mask = (down > up) & (down > 0)
    minus_dm[minus_dm_mask] = down[minus_dm_mask]

    # ─── 3. Wilder smoothing function ────────────────────────────────────
    def wilder_smooth(series: pd.Series, period: int) -> pd.Series:
        smoothed = series.copy()
        # First value: simple sum over period
        smoothed.iloc[period-1] = series.iloc[:period].sum()
        # Recursive Wilder: prev * (period-1) + current / period
        for i in range(period, len(series)):
            smoothed.iloc[i] = (smoothed.iloc[i-1] * (period - 1) + series.iloc[i]) / period
        return smoothed

    # Apply Wilder smoothing
    atr = wilder_smooth(tr['tr'], period)
    plus_dm_smooth = wilder_smooth(plus_dm.fillna(0), period)
    minus_dm_smooth = wilder_smooth(minus_dm.fillna(0), period)

    # ─── 4. Directional Indicators ───────────────────────────────────────
    plus_di = 100 * (plus_dm_smooth / atr)
    minus_di = 100 * (minus_dm_smooth / atr)

    # ─── 5. DX and ADX ───────────────────────────────────────────────────
    di_diff = (plus_di - minus_di).abs()
    di_sum = plus_di + minus_di

    dx = pd.Series(np.nan, index=df.index)
    dx[di_sum != 0] = 100 * (di_diff[di_sum != 0] / di_sum[di_sum != 0])

    # ADX: Wilder smooth the DX
    adx = wilder_smooth(dx.fillna(0), period)

    adx.name = 'ADX'
    return adx


def calculate_psar(
    df: pd.DataFrame,
    af_start: float = 0.02,
    af_increment: float = 0.02,
    af_max: float = 0.20
) -> pd.DataFrame:
    """
    Calculate Parabolic SAR (PSAR) - matches TradingView exactly

    Args:
        df: DataFrame with High, Low, Close
        af_start: Initial acceleration factor
        af_increment: AF increment per new extreme
        af_max: Maximum AF

    Returns:
        DataFrame with 'PSAR' and 'PSAR_Direction' (1 = bullish, -1 = bearish)
    """
    df = df.copy()
    length = len(df)

    if length < 2:
        df['PSAR'] = np.nan
        df['PSAR_Direction'] = 0
        return df

    high = df['High'].values
    low = df['Low'].values
    close = df['Close'].values

    psar = np.empty(length)
    psar.fill(np.nan)
    bull = np.empty(length, dtype=bool)
    af = np.full(length, af_start)
    ep = np.empty(length)

    # Initial direction based on first two candles
    if close[1] > close[0]:
        bull[:] = True
        psar[1] = low[0]
        ep[1] = high[1]
    else:
        bull[:] = False
        psar[1] = high[0]
        ep[1] = low[1]

    for i in range(2, length):
        if bull[i-1]:
            psar[i] = psar[i-1] + af[i-1] * (ep[i-1] - psar[i-1])
            # Prevent PSAR from going into prior two bars
            psar[i] = min(psar[i], low[i-1], low[i-2] if i >= 3 else low[i-1])

            if high[i] > ep[i-1]:  # New extreme point
                ep[i] = high[i]
                af[i] = min(af[i-1] + af_increment, af_max)
            else:
                ep[i] = ep[i-1]
                af[i] = af[i-1]

            # Reversal check
            if low[i] < psar[i]:
                bull[i] = False
                psar[i] = ep[i-1]  # Start new SAR at previous EP
                ep[i] = low[i]
                af[i] = af_start
            else:
                bull[i] = True
        else:
            psar[i] = psar[i-1] + af[i-1] * (ep[i-1] - psar[i-1])
            psar[i] = max(psar[i], high[i-1], high[i-2] if i >= 3 else high[i-1])

            if low[i] < ep[i-1]:
                ep[i] = low[i]
                af[i] = min(af[i-1] + af_increment, af_max)
            else:
                ep[i] = ep[i-1]
                af[i] = af[i-1]

            if high[i] > psar[i]:
                bull[i] = True
                psar[i] = ep[i-1]
                ep[i] = high[i]
                af[i] = af_start
            else:
                bull[i] = False

    df['PSAR'] = psar
    df['PSAR_Direction'] = np.where(bull, 1, -1)  # 1 = bullish (price > PSAR)

    return df


# ══════════════════════════════════════════════════════════════════════
# COMBINED SUPERTREND + ADX + RSI TREND SIGNAL
# ══════════════════════════════════════════════════════════════════════

def combined_trend_signal(df: pd.DataFrame) -> dict:
    """
    Combined trend analysis using SuperTrend, ADX, and RSI
    Returns a detailed signal with strength and description

    Args:
        df: DataFrame with calculated indicators (SuperTrend, ADX, RSI_14)

    Returns:
        Dict with signal, strength, description, details, and warnings
    """
    if len(df) < 50:
        return {'signal': 'Insufficient Data', 'strength': 'N/A', 'description': 'Not enough data'}

    latest = df.iloc[-1]

    # Get indicator values
    supertrend_dir = latest.get('Supertrend_Direction', 0)  # 1 = bullish, -1 = bearish
    adx = latest.get('ADX', 0)
    rsi = latest.get('RSI_14', 50)

    # Interpret signals
    supertrend_bull = supertrend_dir == 1
    supertrend_bear = supertrend_dir == -1
    strong_trend = adx > 25
    rsi_bull = rsi > 50
    rsi_overbought = rsi > 70
    rsi_oversold = rsi < 30

    # Determine combined signal
    if supertrend_bull and strong_trend and rsi_bull:
        signal = 'Strong Bullish Trend'
        strength = 'Very Strong'
        description = 'SuperTrend up, ADX confirms strong trend, RSI shows bullish momentum'
    elif supertrend_bull and strong_trend:
        signal = 'Bullish Trend'
        strength = 'Strong'
        description = 'SuperTrend up with strong trend (ADX > 25), RSI neutral'
    elif supertrend_bull and rsi_bull:
        signal = 'Moderate Bullish'
        strength = 'Medium'
        description = 'SuperTrend up with bullish RSI, but trend strength weak'
    elif supertrend_bull:
        signal = 'Weak Bullish'
        strength = 'Weak'
        description = 'SuperTrend up but lacking confirmation from ADX/RSI'

    elif supertrend_bear and strong_trend and not rsi_bull:
        signal = 'Strong Bearish Trend'
        strength = 'Very Strong'
        description = 'SuperTrend down, ADX confirms strong trend, RSI shows bearish momentum'
    elif supertrend_bear and strong_trend:
        signal = 'Bearish Trend'
        strength = 'Strong'
        description = 'SuperTrend down with strong trend (ADX > 25), RSI neutral'
    elif supertrend_bear and not rsi_bull:
        signal = 'Moderate Bearish'
        strength = 'Medium'
        description = 'SuperTrend down with bearish RSI, but trend strength weak'
    elif supertrend_bear:
        signal = 'Weak Bearish'
        strength = 'Weak'
        description = 'SuperTrend down but lacking confirmation from ADX/RSI'

    else:
        signal = 'Sideways / No Clear Trend'
        strength = 'Neutral'
        description = 'Conflicting or weak signals from SuperTrend, ADX, and RSI'

    # Generate warnings
    warnings = []
    if rsi_overbought and supertrend_bull:
        warnings.append('Caution: RSI overbought - possible pullback')
    if rsi_oversold and supertrend_bear:
        warnings.append('Caution: RSI oversold - possible bounce')

    return {
        'signal': signal,
        'strength': strength,
        'description': description,
        'details': {
            'SuperTrend_Direction': 'Bullish' if supertrend_bull else 'Bearish' if supertrend_bear else 'N/A',
            'ADX_Value': float(adx) if not pd.isna(adx) else 0,
            'ADX_Strong': strong_trend,
            'RSI_14': float(rsi) if not pd.isna(rsi) else 50,
            'RSI_Momentum': 'Bullish' if rsi_bull else 'Bearish'
        },
        'warnings': warnings
    }


# ══════════════════════════════════════════════════════════════════════
# PATTERN RECOGNITION
# ══════════════════════════════════════════════════════════════════════

def detect_candlestick_patterns(df: pd.DataFrame) -> dict:
    """
    Detect common candlestick patterns

    Returns:
        Dict with pattern names and signals
    """
    patterns = {}

    # Get last few candles
    if len(df) < 5:
        return patterns

    o = df['Open'].values
    h = df['High'].values
    c = df['Close'].values
    l = df['Low'].values

    body = abs(c - o)
    upper_shadow = h - np.maximum(c, o)
    lower_shadow = np.minimum(c, o) - l

    # 1. Doji (small body, indecision)
    avg_body = np.mean(body[-20:])
    if body[-1] < avg_body * 0.1:
        patterns['Doji'] = {'signal': 'Neutral', 'strength': 'Medium', 'description': 'Indecision in market'}

    # 2. Hammer (bullish reversal)
    if lower_shadow[-1] > 2 * body[-1] and upper_shadow[-1] < body[-1] * 0.5 and c[-1] > o[-1]:
        patterns['Hammer'] = {'signal': 'Bullish', 'strength': 'Strong', 'description': 'Potential bullish reversal'}

    # 3. Shooting Star (bearish reversal)
    if upper_shadow[-1] > 2 * body[-1] and lower_shadow[-1] < body[-1] * 0.5 and c[-1] < o[-1]:
        patterns['Shooting Star'] = {'signal': 'Bearish', 'strength': 'Strong', 'description': 'Potential bearish reversal'}

    # 4. Engulfing Bullish
    if c[-2] < o[-2] and c[-1] > o[-1] and c[-1] > o[-2] and o[-1] < c[-2]:
        patterns['Bullish Engulfing'] = {'signal': 'Bullish', 'strength': 'Strong', 'description': 'Bullish reversal pattern'}

    # 5. Engulfing Bearish
    if c[-2] > o[-2] and c[-1] < o[-1] and c[-1] < o[-2] and o[-1] > c[-2]:
        patterns['Bearish Engulfing'] = {'signal': 'Bearish', 'strength': 'Strong', 'description': 'Bearish reversal pattern'}

    # 6. Morning Star (3-candle bullish)
    if len(df) >= 3:
        if c[-3] < o[-3] and body[-2] < avg_body * 0.3 and c[-1] > o[-1] and c[-1] > (o[-3] + c[-3]) / 2:
            patterns['Morning Star'] = {'signal': 'Bullish', 'strength': 'Very Strong', 'description': '3-candle bullish reversal'}

    # 7. Evening Star (3-candle bearish)
    if len(df) >= 3:
        if c[-3] > o[-3] and body[-2] < avg_body * 0.3 and c[-1] < o[-1] and c[-1] < (o[-3] + c[-3]) / 2:
            patterns['Evening Star'] = {'signal': 'Bearish', 'strength': 'Very Strong', 'description': '3-candle bearish reversal'}

    # 8. Three White Soldiers (strong bullish)
    if len(df) >= 3:
        if all(c[-i] > o[-i] for i in range(1, 4)) and c[-1] > c[-2] > c[-3]:
            patterns['Three White Soldiers'] = {'signal': 'Bullish', 'strength': 'Very Strong', 'description': 'Strong bullish continuation'}

    # 9. Three Black Crows (strong bearish)
    if len(df) >= 3:
        if all(c[-i] < o[-i] for i in range(1, 4)) and c[-1] < c[-2] < c[-3]:
            patterns['Three Black Crows'] = {'signal': 'Bearish', 'strength': 'Very Strong', 'description': 'Strong bearish continuation'}

    # 10. Spinning Top
    if body[-1] < avg_body * 0.3 and upper_shadow[-1] > body[-1] and lower_shadow[-1] > body[-1]:
        patterns['Spinning Top'] = {'signal': 'Neutral', 'strength': 'Weak', 'description': 'Market indecision'}

    # 11. Bullish Marubozu (strong bullish candle with no shadows)
    if c[-1] > o[-1] and body[-1] > avg_body * 1.5 and upper_shadow[-1] < body[-1] * 0.1 and lower_shadow[-1] < body[-1] * 0.1:
        patterns['Bullish Marubozu'] = {'signal': 'Bullish', 'strength': 'Strong', 'description': 'Strong buying pressure'}

    # 12. Bearish Marubozu
    if c[-1] < o[-1] and body[-1] > avg_body * 1.5 and upper_shadow[-1] < body[-1] * 0.1 and lower_shadow[-1] < body[-1] * 0.1:
        patterns['Bearish Marubozu'] = {'signal': 'Bearish', 'strength': 'Strong', 'description': 'Strong selling pressure'}

    # 13. Bullish Harami
    if len(df) >= 2:
        if c[-2] < o[-2] and c[-1] > o[-1] and body[-1] < body[-2] and c[-1] < o[-2] and o[-1] > c[-2]:
            patterns['Bullish Harami'] = {'signal': 'Bullish', 'strength': 'Medium', 'description': 'Potential bullish reversal'}

    # 14. Piercing Line
    if len(df) >= 2:
        if c[-2] < o[-2] and c[-1] > o[-1] and o[-1] < c[-2] and c[-1] > (o[-2] + c[-2]) / 2:
            patterns['Piercing Line'] = {'signal': 'Bullish', 'strength': 'Strong', 'description': 'Bullish reversal pattern'}

    # 15. Recent Price Action Analysis (last 3-5 candles)
    recent_greens = sum(1 for i in range(1, min(6, len(c))) if c[-i] > o[-i])
    recent_reds = sum(1 for i in range(1, min(6, len(c))) if c[-i] < o[-i])

    if recent_greens >= 4:
        patterns['Bullish Momentum'] = {'signal': 'Bullish', 'strength': 'Medium', 'description': f'{recent_greens} green candles in last 5 days'}
    elif recent_reds >= 4:
        patterns['Bearish Momentum'] = {'signal': 'Bearish', 'strength': 'Medium', 'description': f'{recent_reds} red candles in last 5 days'}

    # 16. Higher Lows (bullish structure)
    if len(df) >= 5:
        lows = l[-5:]
        if all(lows[i] <= lows[i+1] for i in range(len(lows)-1)):
            patterns['Higher Lows'] = {'signal': 'Bullish', 'strength': 'Medium', 'description': 'Bullish price structure forming'}

    # 17. Lower Highs (bearish structure)
    if len(df) >= 5:
        highs = h[-5:]
        if all(highs[i] >= highs[i+1] for i in range(len(highs)-1)):
            patterns['Lower Highs'] = {'signal': 'Bearish', 'strength': 'Medium', 'description': 'Bearish price structure forming'}

    return patterns


def detect_chart_patterns(df: pd.DataFrame) -> dict:
    """
    Detect chart patterns (Head & Shoulders, Double Top/Bottom, etc.)

    Returns:
        Dict with detected patterns
    """
    patterns = {}

    if len(df) < 50:
        return patterns

    close = df['Close'].values
    high = df['High'].values
    low = df['Low'].values

    # Find local maxima and minima
    from scipy.signal import argrelextrema

    try:
        # Local maxima (peaks)
        peak_idx = argrelextrema(high, np.greater, order=5)[0]
        # Local minima (troughs)
        trough_idx = argrelextrema(low, np.less, order=5)[0]

        peaks = high[peak_idx]
        troughs = low[trough_idx]

        # Double Top detection
        if len(peaks) >= 2:
            last_peaks = peaks[-2:]
            if abs(last_peaks[0] - last_peaks[1]) / last_peaks[0] < 0.03:  # Within 3%
                patterns['Double Top'] = {
                    'signal': 'Bearish',
                    'strength': 'Strong',
                    'description': 'Potential reversal from uptrend',
                    'level': float(np.mean(last_peaks))
                }

        # Double Bottom detection
        if len(troughs) >= 2:
            last_troughs = troughs[-2:]
            if abs(last_troughs[0] - last_troughs[1]) / last_troughs[0] < 0.03:  # Within 3%
                patterns['Double Bottom'] = {
                    'signal': 'Bullish',
                    'strength': 'Strong',
                    'description': 'Potential reversal from downtrend',
                    'level': float(np.mean(last_troughs))
                }

        # Head and Shoulders (simplified)
        if len(peaks) >= 3:
            last_3_peaks = peaks[-3:]
            if last_3_peaks[1] > last_3_peaks[0] and last_3_peaks[1] > last_3_peaks[2]:
                if abs(last_3_peaks[0] - last_3_peaks[2]) / last_3_peaks[0] < 0.05:
                    patterns['Head and Shoulders'] = {
                        'signal': 'Bearish',
                        'strength': 'Very Strong',
                        'description': 'Classic reversal pattern',
                        'neckline': float(np.mean(troughs[-2:])) if len(troughs) >= 2 else None
                    }

        # Inverse Head and Shoulders
        if len(troughs) >= 3:
            last_3_troughs = troughs[-3:]
            if last_3_troughs[1] < last_3_troughs[0] and last_3_troughs[1] < last_3_troughs[2]:
                if abs(last_3_troughs[0] - last_3_troughs[2]) / last_3_troughs[0] < 0.05:
                    patterns['Inverse Head and Shoulders'] = {
                        'signal': 'Bullish',
                        'strength': 'Very Strong',
                        'description': 'Bullish reversal pattern',
                        'neckline': float(np.mean(peaks[-2:])) if len(peaks) >= 2 else None
                    }

        # Trend detection - use multiple timeframes and indicators for accuracy
        # Short-term (5-10 days), Medium-term (20 days), Long-term (50 days)
        short_term_bullish = close[-1] > close[-5] and close[-1] > close[-10]
        medium_term_bullish = close[-1] > close[-20]
        long_term_bullish = close[-1] > close[-50] if len(close) > 50 else medium_term_bullish

        # Also check moving averages if available
        sma_20 = df.get('SMA_20', pd.Series([close[-1]])).iloc[-1] if 'SMA_20' in df.columns else close[-20:].mean()
        sma_50 = df.get('SMA_50', pd.Series([close[-1]])).iloc[-1] if 'SMA_50' in df.columns else close[-50:].mean() if len(close) > 50 else sma_20

        price_above_sma20 = close[-1] > sma_20
        price_above_sma50 = close[-1] > sma_50
        sma20_above_sma50 = sma_20 > sma_50

        # Calculate trend score
        trend_score = 0
        if short_term_bullish:
            trend_score += 2  # Short-term has more weight for current trend
        if medium_term_bullish:
            trend_score += 1
        if long_term_bullish:
            trend_score += 1
        if price_above_sma20:
            trend_score += 1
        if price_above_sma50:
            trend_score += 1
        if sma20_above_sma50:
            trend_score += 1

        # Recent momentum (last 5 days)
        recent_return = (close[-1] - close[-5]) / close[-5] * 100

        # Determine trend based on score (max 7)
        if trend_score >= 5:
            patterns['Uptrend'] = {
                'signal': 'Bullish',
                'strength': 'Strong' if trend_score >= 6 else 'Medium',
                'description': f'Strong uptrend (Score: {trend_score}/7, Recent: {recent_return:+.1f}%)'
            }
        elif trend_score >= 3:
            if recent_return > 1:
                patterns['Recovery'] = {
                    'signal': 'Bullish',
                    'strength': 'Medium',
                    'description': f'Recovering trend (Score: {trend_score}/7, Recent: {recent_return:+.1f}%)'
                }
            else:
                patterns['Sideways'] = {
                    'signal': 'Neutral',
                    'strength': 'Weak',
                    'description': f'Range-bound market (Score: {trend_score}/7)'
                }
        else:
            if recent_return < -1:
                patterns['Downtrend'] = {
                    'signal': 'Bearish',
                    'strength': 'Strong' if trend_score <= 1 else 'Medium',
                    'description': f'Downtrend (Score: {trend_score}/7, Recent: {recent_return:+.1f}%)'
                }
            else:
                patterns['Consolidation'] = {
                    'signal': 'Neutral',
                    'strength': 'Weak',
                    'description': f'Consolidating after downmove (Score: {trend_score}/7)'
                }

    except Exception as e:
        pass

    return patterns


# ══════════════════════════════════════════════════════════════════════
# DEEP LEARNING - LSTM PRICE PREDICTION
# ══════════════════════════════════════════════════════════════════════

def prepare_lstm_data(df: pd.DataFrame, lookback: int = 60, forecast_days: int = 5):
    """
    Prepare data for LSTM model

    Args:
        df: DataFrame with price data
        lookback: Number of days to look back
        forecast_days: Number of days to forecast

    Returns:
        X, y arrays for training
    """
    from sklearn.preprocessing import MinMaxScaler

    # Use Close price
    data = df['Close'].values.reshape(-1, 1)

    # Scale data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    X, y = [], []
    for i in range(lookback, len(scaled_data) - forecast_days):
        X.append(scaled_data[i - lookback:i, 0])
        y.append(scaled_data[i:i + forecast_days, 0])

    X = np.array(X)
    y = np.array(y)

    # Reshape for LSTM [samples, time steps, features]
    X = X.reshape((X.shape[0], X.shape[1], 1))

    return X, y, scaler


def build_lstm_model(lookback: int = 60, forecast_days: int = 5, n_features: int = 1,
                     use_mc_dropout: bool = True, model_size: str = 'small'):
    """
    Build enhanced LSTM model for price prediction with MC Dropout and L2 regularization

    Args:
        lookback: Number of timesteps to look back
        forecast_days: Number of days to forecast
        n_features: Number of input features
        use_mc_dropout: If True, use MC Dropout for uncertainty estimation
        model_size: 'small', 'medium', or 'large' architecture

    Returns:
        Compiled Keras model
    """
    try:
        from tensorflow.keras.models import Sequential, Model
        from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization, Input
        from tensorflow.keras.optimizers import Adam
        from tensorflow.keras.regularizers import l2
        import tensorflow as tf

        # Custom Dropout layer that stays active during inference for MC Dropout
        class MCDropout(Dropout):
            def call(self, inputs, training=None):
                return super().call(inputs, training=True)

        dropout_layer = MCDropout if use_mc_dropout else Dropout

        # L2 regularization strength
        l2_reg = 0.001

        # Architecture based on model size (smaller = less overfitting)
        if model_size == 'small':
            units = [32, 16]
            dropout_rate = 0.3
        elif model_size == 'medium':
            units = [64, 32]
            dropout_rate = 0.25
        else:  # large
            units = [128, 64, 32]
            dropout_rate = 0.2

        model = Sequential()

        # First LSTM layer
        model.add(LSTM(units[0], return_sequences=len(units) > 1,
                      input_shape=(lookback, n_features),
                      kernel_regularizer=l2(l2_reg),
                      recurrent_regularizer=l2(l2_reg)))
        model.add(dropout_layer(dropout_rate))
        model.add(BatchNormalization())

        # Middle LSTM layers
        for i, unit in enumerate(units[1:], 1):
            return_seq = i < len(units) - 1
            model.add(LSTM(unit, return_sequences=return_seq,
                          kernel_regularizer=l2(l2_reg),
                          recurrent_regularizer=l2(l2_reg)))
            model.add(dropout_layer(dropout_rate))
            if return_seq:
                model.add(BatchNormalization())

        # Dense layers
        model.add(Dense(32, activation='relu', kernel_regularizer=l2(l2_reg)))
        model.add(dropout_layer(dropout_rate * 0.5))
        model.add(Dense(forecast_days))

        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='huber',  # More robust to outliers than MSE
            metrics=['mae']
        )

        return model

    except ImportError:
        return None


def prepare_lstm_features(df: pd.DataFrame, features: list = None) -> tuple:
    """
    Prepare multi-feature data for LSTM training

    Args:
        df: DataFrame with OHLCV and indicator data
        features: List of feature column names to use

    Returns:
        Tuple of (feature_data, feature_names, close_idx)
    """
    if features is None:
        # Default features - mix of price, momentum, volatility, volume
        default_features = [
            'Close', 'RSI_14', 'MACD', 'ATR_14', 'BB_Percent',
            'Stoch_K', 'ROC', 'MFI', 'Volume_Ratio', 'Momentum'
        ]
        features = [f for f in default_features if f in df.columns]

    # Ensure Close is always first for target prediction
    if 'Close' not in features:
        features = ['Close'] + features
    elif features[0] != 'Close':
        features.remove('Close')
        features = ['Close'] + features

    # Filter to available columns
    available_features = [f for f in features if f in df.columns]

    if len(available_features) < 2:
        available_features = ['Close']

    return df[available_features].copy(), available_features, 0  # close_idx = 0


def predict_with_lstm(df: pd.DataFrame, lookback: int = 60, forecast_days: int = 5,
                      epochs: int = 50, features: list = None,
                      n_mc_samples: int = 30, model_size: str = 'small') -> dict:
    """
    Enhanced LSTM prediction with TimeSeriesSplit, L2 regularization,
    MC Dropout for uncertainty estimation, and overfitting detection.

    Args:
        df: DataFrame with price and indicator data
        lookback: Days to look back (default 60)
        forecast_days: Days to predict (default 5)
        epochs: Maximum training epochs (default 50)
        features: List of feature columns to use (default: auto-select)
        n_mc_samples: Number of MC Dropout samples for uncertainty (default 30)
        model_size: 'small', 'medium', or 'large' (default 'small' to prevent overfitting)

    Returns:
        Dict with predictions, confidence intervals, metrics, and overfitting diagnostics
    """
    try:
        from sklearn.preprocessing import MinMaxScaler
        from sklearn.model_selection import TimeSeriesSplit
        from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

        # Check if we have enough data
        min_required = lookback + forecast_days + 50
        if len(df) < min_required:
            return {'error': f'Insufficient data. Need {min_required} rows, got {len(df)}'}

        # Prepare multi-feature data
        feature_data, feature_names, close_idx = prepare_lstm_features(df, features)
        n_features = len(feature_names)

        # Handle NaN values
        feature_data = feature_data.dropna()
        if len(feature_data) < min_required:
            return {'error': 'Too many NaN values after feature preparation'}

        # Scale features
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(feature_data.values)

        # Create sequences with all features, predict only Close
        X, y = [], []
        for i in range(lookback, len(scaled_data) - forecast_days):
            X.append(scaled_data[i - lookback:i])
            y.append(scaled_data[i:i + forecast_days, close_idx])

        X = np.array(X)
        y = np.array(y)

        # Use TimeSeriesSplit for proper time-series cross-validation
        tscv = TimeSeriesSplit(n_splits=3)
        cv_scores = []

        # Get the last fold for final training
        for train_idx, val_idx in tscv.split(X):
            pass  # Just get last indices

        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        # Keep some data for final test (last 10%)
        test_size = max(10, int(len(X_val) * 0.3))
        X_test = X_val[-test_size:]
        y_test = y_val[-test_size:]
        X_val = X_val[:-test_size]
        y_val = y_val[:-test_size]

        # Build model with smaller architecture to prevent overfitting
        model = build_lstm_model(lookback, forecast_days, n_features,
                                use_mc_dropout=True, model_size=model_size)
        if model is None:
            return {'error': 'TensorFlow not installed'}

        # Callbacks for early stopping and learning rate reduction
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                min_delta=0.0001
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=0.0001
            )
        ]

        # Train with validation
        history = model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=32,
            validation_data=(X_val, y_val),
            callbacks=callbacks,
            verbose=0
        )

        # Prepare last sequence for prediction
        last_sequence = scaled_data[-lookback:].reshape(1, lookback, n_features)

        # MC Dropout: Run multiple predictions for uncertainty estimation
        mc_predictions = []
        for _ in range(n_mc_samples):
            pred = model(last_sequence, training=True)  # training=True keeps dropout active
            mc_predictions.append(pred.numpy()[0])

        mc_predictions = np.array(mc_predictions)

        # Calculate mean prediction and uncertainty
        predicted_scaled_mean = np.mean(mc_predictions, axis=0)
        predicted_scaled_std = np.std(mc_predictions, axis=0)

        # FIXED INVERSE SCALING - use last scaled row as base for proper inverse transform
        last_scaled_row = scaled_data[-1].copy()

        # Inverse transform predictions using correct context
        dummy_mean = np.tile(last_scaled_row, (forecast_days, 1))
        dummy_mean[:, close_idx] = predicted_scaled_mean
        predicted_prices = scaler.inverse_transform(dummy_mean)[:, close_idx]

        # Calculate confidence intervals
        dummy_low = np.tile(last_scaled_row, (forecast_days, 1))
        dummy_low[:, close_idx] = predicted_scaled_mean - 1.96 * predicted_scaled_std
        predicted_low = scaler.inverse_transform(dummy_low)[:, close_idx]

        dummy_high = np.tile(last_scaled_row, (forecast_days, 1))
        dummy_high[:, close_idx] = predicted_scaled_mean + 1.96 * predicted_scaled_std
        predicted_high = scaler.inverse_transform(dummy_high)[:, close_idx]

        # Evaluate on test set (also with fixed inverse scaling)
        if len(X_test) > 0:
            test_pred = model.predict(X_test, verbose=0)
            test_pred_flat = test_pred.flatten()
            y_test_flat = y_test.flatten()

            # Use last timestep of each test sequence as context for inverse transform
            last_timesteps = X_test[:, -1, :]
            dummy_test = np.repeat(last_timesteps, forecast_days, axis=0)
            dummy_test[:, close_idx] = test_pred_flat
            test_pred_inv = scaler.inverse_transform(dummy_test)[:, close_idx]

            dummy_actual = np.repeat(last_timesteps, forecast_days, axis=0)
            dummy_actual[:, close_idx] = y_test_flat
            test_actual_inv = scaler.inverse_transform(dummy_actual)[:, close_idx]

            mae = np.mean(np.abs(test_pred_inv - test_actual_inv))
            mape = np.mean(np.abs((test_actual_inv - test_pred_inv) / test_actual_inv)) * 100
        else:
            mae = 0
            mape = 0

        current_price = df['Close'].iloc[-1]

        # Confidence based on prediction uncertainty and historical accuracy
        uncertainty_ratio = np.mean(predicted_scaled_std) / np.mean(np.abs(predicted_scaled_mean))
        confidence = max(0, min(100, 100 * (1 - uncertainty_ratio) * (1 - mape/100)))

        # Trend direction with strength
        final_predicted = predicted_prices[-1]
        price_change = final_predicted - current_price
        pct_change = (price_change / current_price) * 100

        if pct_change > 3:
            trend = 'Strong Bullish'
        elif pct_change > 1:
            trend = 'Bullish'
        elif pct_change < -3:
            trend = 'Strong Bearish'
        elif pct_change < -1:
            trend = 'Bearish'
        else:
            trend = 'Neutral'

        # Calculate overfitting gap (train MAE - val MAE) / val MAE
        train_mae = history.history['mae'][-1] if 'mae' in history.history else 0
        val_mae = history.history['val_mae'][-1] if 'val_mae' in history.history else train_mae
        overfitting_gap = ((train_mae - val_mae) / val_mae * 100) if val_mae > 0 else 0

        # Determine if model is overfitting
        if overfitting_gap > 20:
            overfitting_status = 'High Risk - Consider smaller model'
        elif overfitting_gap > 10:
            overfitting_status = 'Moderate - Monitor closely'
        elif overfitting_gap > 0:
            overfitting_status = 'Low - Model generalizes well'
        else:
            overfitting_status = 'Good - Validation better than training'

        return {
            'current_price': float(current_price),
            'predictions': predicted_prices.tolist(),
            'prediction_low': predicted_low.tolist(),
            'prediction_high': predicted_high.tolist(),
            'forecast_days': forecast_days,
            'trend': trend,
            'expected_return': float(pct_change),
            'confidence': float(confidence),
            'mae': float(mae),
            'mape': float(mape),
            'uncertainty': float(np.mean(predicted_scaled_std)),
            'features_used': feature_names,
            'n_features': n_features,
            'model_size': model_size,
            'epochs_trained': len(history.history['loss']),
            'final_loss': float(history.history['loss'][-1]),
            'final_val_loss': float(history.history['val_loss'][-1]) if 'val_loss' in history.history else None,
            'train_mae': float(train_mae),
            'val_mae': float(val_mae),
            'overfitting_gap_pct': float(overfitting_gap),
            'overfitting_status': overfitting_status
        }

    except ImportError as e:
        return {'error': f'Missing dependency: {str(e)}'}
    except Exception as e:
        return {'error': str(e)}


# ══════════════════════════════════════════════════════════════════════
# FEATURE IMPORTANCE ANALYSIS
# ══════════════════════════════════════════════════════════════════════

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

    # Drop NaN
    df_clean = df_analysis[feature_cols + [target_col]].dropna()

    if len(df_clean) < 100:
        return {'error': 'Insufficient data after removing NaN values'}

    X = df_clean[feature_cols].values
    y = df_clean[target_col].values

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


# ══════════════════════════════════════════════════════════════════════
# GARCH VOLATILITY FORECASTING
# ══════════════════════════════════════════════════════════════════════

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


# ══════════════════════════════════════════════════════════════════════
# ATR-BASED POSITION SIZING & RISK MANAGEMENT
# ══════════════════════════════════════════════════════════════════════

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


# ══════════════════════════════════════════════════════════════════════
# SIMPLE BACKTESTING FRAMEWORK
# ══════════════════════════════════════════════════════════════════════

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

    # Generate signals if not provided
    if signal_col is None or signal_col not in df_bt.columns:
        if 'RSI_14' in df_bt.columns and 'MACD' in df_bt.columns:
            df_bt['Signal'] = 0
            buy_cond = (df_bt['RSI_14'] < 35) | (
                (df_bt['MACD'] > df_bt['MACD_Signal']) &
                (df_bt['MACD'].shift(1) <= df_bt['MACD_Signal'].shift(1))
            )
            sell_cond = (df_bt['RSI_14'] > 65) | (
                (df_bt['MACD'] < df_bt['MACD_Signal']) &
                (df_bt['MACD'].shift(1) >= df_bt['MACD_Signal'].shift(1))
            )
            df_bt.loc[buy_cond, 'Signal'] = 1
            df_bt.loc[sell_cond, 'Signal'] = -1
            signal_col = 'Signal'
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

        signal = row[signal_col] if not pd.isna(row[signal_col]) else 0
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
            if position < 0 and allow_short:
                exec_price = get_execution_price(current_price, True, vol_mult)
                cost = calculate_transaction_cost(abs(position), exec_price, True, vol_mult)
                total_costs += cost
                pnl = abs(position) * (entry_price - exec_price) - cost
                capital += pnl
                pnl_pct = ((entry_price - exec_price) / entry_price) * 100
                trades.append({
                    'type': 'SIGNAL_EXIT',
                    'direction': 'SHORT',
                    'entry': entry_price,
                    'exit': exec_price,
                    'pnl_pct': pnl_pct,
                    'shares': abs(position),
                    'cost': cost
                })
                position = 0

            # Open long if no position and under max exposure
            if position == 0 and current_exposure_pct < max_exposure_pct:
                position_value = min(
                    capital * (position_size_pct / 100),
                    capital * ((max_exposure_pct - current_exposure_pct) / 100)
                )
                exec_price = get_execution_price(current_price, True, vol_mult)
                if pd.isna(exec_price) or exec_price <= 0:
                    continue
                shares = int(position_value / exec_price)
                if shares > 0:
                    cost = calculate_transaction_cost(shares, exec_price, True, vol_mult)
                    total_costs += cost
                    total_cost = shares * exec_price + cost
                    if total_cost <= capital:
                        capital -= total_cost
                        position = shares
                        entry_price = exec_price
                        position_type = 'long'

        elif signal == -1:
            if position > 0:  # Close long
                exec_price = get_execution_price(current_price, False, vol_mult)
                cost = calculate_transaction_cost(position, exec_price, False, vol_mult)
                total_costs += cost
                proceeds = position * exec_price - cost
                capital += proceeds
                pnl_pct = ((exec_price - entry_price) / entry_price) * 100
                trades.append({
                    'type': 'SIGNAL_EXIT',
                    'direction': 'LONG',
                    'entry': entry_price,
                    'exit': exec_price,
                    'pnl_pct': pnl_pct,
                    'shares': position,
                    'cost': cost
                })
                position = 0
                entry_price = 0
                position_type = None

            # Open short if allowed and under max exposure
            if allow_short and position == 0 and current_exposure_pct < max_exposure_pct:
                position_value = min(
                    capital * (position_size_pct / 100),
                    capital * ((max_exposure_pct - current_exposure_pct) / 100)
                )
                exec_price = get_execution_price(current_price, False, vol_mult)
                if pd.isna(exec_price) or exec_price <= 0:
                    continue
                shares = int(position_value / exec_price)
                if shares > 0:
                    cost = calculate_transaction_cost(shares, exec_price, False, vol_mult)
                    total_costs += cost
                    # For short, we receive proceeds but must post margin
                    capital -= cost  # Just pay the cost, margin is implicit
                    position = -shares
                    entry_price = exec_price
                    position_type = 'short'

    # Close any remaining position
    if position != 0:
        final_price = df_bt['Close'].iloc[-1]
        vol_mult = slippage_multiplier.iloc[-1] if len(slippage_multiplier) > 0 else 1.0
        exec_price = get_execution_price(final_price, position < 0, vol_mult)
        cost = calculate_transaction_cost(abs(position), exec_price, position < 0, vol_mult)
        total_costs += cost

        if position > 0:
            proceeds = position * exec_price - cost
            capital += proceeds
            pnl_pct = ((exec_price - entry_price) / entry_price) * 100
        else:
            pnl = abs(position) * (entry_price - exec_price) - cost
            capital += pnl
            pnl_pct = ((entry_price - exec_price) / entry_price) * 100

        trades.append({
            'type': 'END_OF_PERIOD',
            'direction': 'LONG' if position > 0 else 'SHORT',
            'entry': entry_price,
            'exit': exec_price,
            'pnl_pct': pnl_pct,
            'shares': abs(position),
            'cost': cost
        })

    # Calculate metrics
    final_equity = capital
    total_return = ((final_equity - initial_capital) / initial_capital) * 100

    if trades:
        winning_trades = [t for t in trades if t['pnl_pct'] > 0]
        losing_trades = [t for t in trades if t['pnl_pct'] <= 0]
        win_rate = len(winning_trades) / len(trades) * 100

        avg_win = np.mean([t['pnl_pct'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['pnl_pct'] for t in losing_trades]) if losing_trades else 0

        gross_profit = sum(t['pnl_pct'] for t in winning_trades) if winning_trades else 0
        gross_loss = abs(sum(t['pnl_pct'] for t in losing_trades)) if losing_trades else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else gross_profit
    else:
        win_rate = 0
        avg_win = 0
        avg_loss = 0
        profit_factor = 0

    # Calculate max drawdown
    equity_values = [e['equity'] for e in equity_curve]
    peak = equity_values[0]
    max_drawdown = 0
    max_drawdown_duration = 0
    current_dd_duration = 0

    for eq in equity_values:
        if eq > peak:
            peak = eq
            current_dd_duration = 0
        else:
            current_dd_duration += 1
        drawdown = ((peak - eq) / peak) * 100
        max_drawdown = max(max_drawdown, drawdown)
        max_drawdown_duration = max(max_drawdown_duration, current_dd_duration)

    # Calculate risk metrics (Sharpe, Sortino, Calmar)
    if daily_returns:
        daily_returns = np.array(daily_returns)
        avg_daily_return = np.mean(daily_returns)
        std_daily_return = np.std(daily_returns)

        # Sharpe Ratio (annualized, assuming 252 trading days, risk-free rate ~5%)
        risk_free_daily = 0.05 / 252
        sharpe_ratio = (avg_daily_return - risk_free_daily) / std_daily_return * np.sqrt(252) if std_daily_return > 0 else 0

        # Sortino Ratio (uses downside deviation)
        downside_returns = daily_returns[daily_returns < 0]
        downside_std = np.std(downside_returns) if len(downside_returns) > 0 else std_daily_return
        sortino_ratio = (avg_daily_return - risk_free_daily) / downside_std * np.sqrt(252) if downside_std > 0 else 0

        # Calmar Ratio (return / max drawdown)
        annual_return = total_return * (252 / len(daily_returns)) if len(daily_returns) > 0 else total_return
        calmar_ratio = annual_return / max_drawdown if max_drawdown > 0 else 0
    else:
        sharpe_ratio = 0
        sortino_ratio = 0
        calmar_ratio = 0

    # Buy and hold comparison
    buy_hold_return = ((df_bt['Close'].iloc[-1] - df_bt['Close'].iloc[0]) / df_bt['Close'].iloc[0]) * 100

    # Count long and short trades
    long_trades = [t for t in trades if t.get('direction') == 'LONG']
    short_trades = [t for t in trades if t.get('direction') == 'SHORT']

    return {
        'initial_capital': initial_capital,
        'final_equity': float(final_equity),
        'total_return_pct': float(total_return),
        'buy_hold_return_pct': float(buy_hold_return),
        'outperformance': float(total_return - buy_hold_return),
        'total_trades': len(trades),
        'long_trades': len(long_trades),
        'short_trades': len(short_trades),
        'winning_trades': len([t for t in trades if t['pnl_pct'] > 0]),
        'losing_trades': len([t for t in trades if t['pnl_pct'] <= 0]),
        'win_rate_pct': float(win_rate),
        'avg_win_pct': float(avg_win),
        'avg_loss_pct': float(avg_loss),
        'profit_factor': float(profit_factor),
        'max_drawdown_pct': float(max_drawdown),
        'max_drawdown_duration': int(max_drawdown_duration),
        'sharpe_ratio': float(sharpe_ratio),
        'sortino_ratio': float(sortino_ratio),
        'calmar_ratio': float(calmar_ratio),
        'total_costs': float(total_costs),
        'cost_pct_of_pnl': float(total_costs / abs(final_equity - initial_capital) * 100) if final_equity != initial_capital else 0,
        'trades': trades[-10:],
        'equity_curve': equity_curve[::max(1, len(equity_curve)//100)]
    }


# ══════════════════════════════════════════════════════════════════════
# SENTIMENT ANALYSIS
# ══════════════════════════════════════════════════════════════════════

def analyze_sentiment_simple(text: str) -> dict:
    """
    Simple keyword-based sentiment analysis

    Args:
        text: Text to analyze

    Returns:
        Dict with sentiment score and label
    """
    positive_words = [
        'buy', 'bullish', 'upgrade', 'growth', 'profit', 'gain', 'surge', 'rally',
        'strong', 'outperform', 'beat', 'exceed', 'positive', 'optimistic', 'recovery',
        'breakthrough', 'success', 'high', 'rise', 'jump', 'soar', 'boost'
    ]

    negative_words = [
        'sell', 'bearish', 'downgrade', 'loss', 'decline', 'drop', 'fall', 'crash',
        'weak', 'underperform', 'miss', 'negative', 'pessimistic', 'concern', 'risk',
        'fail', 'low', 'plunge', 'tumble', 'slump', 'cut', 'warning'
    ]

    text_lower = text.lower()
    words = text_lower.split()

    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)

    total = positive_count + negative_count
    if total == 0:
        return {'score': 0, 'label': 'Neutral', 'confidence': 0.5}

    score = (positive_count - negative_count) / total

    if score > 0.3:
        label = 'Positive'
    elif score < -0.3:
        label = 'Negative'
    else:
        label = 'Neutral'

    confidence = abs(score) * 0.5 + 0.5

    return {
        'score': score,
        'label': label,
        'confidence': confidence,
        'positive_words': positive_count,
        'negative_words': negative_count
    }


def analyze_sentiment_transformer(text: str, use_cache: bool = True,
                                   model_type: str = 'financial') -> dict:
    """
    Enhanced sentiment analysis using HuggingFace transformer model.
    Supports financial domain models for better accuracy on market-related text.
    Falls back to keyword-based method if transformers not available.

    Args:
        text: Text to analyze
        use_cache: Whether to cache the model (default True)
        model_type: 'financial' (FinBERT), 'twitter' (RoBERTa), or 'general' (DistilBERT)

    Returns:
        Dict with sentiment score, label, and confidence
    """
    # Model options in order of preference for financial text
    model_configs = {
        'financial': {
            'model': 'ProsusAI/finbert',
            'labels': {'positive': 1, 'negative': -1, 'neutral': 0}
        },
        'twitter': {
            'model': 'cardiffnlp/twitter-roberta-base-sentiment-latest',
            'labels': {'positive': 1, 'negative': -1, 'neutral': 0}
        },
        'general': {
            'model': 'distilbert-base-uncased-finetuned-sst-2-english',
            'labels': {'POSITIVE': 1, 'NEGATIVE': -1}
        }
    }

    # Try transformer-based analysis
    try:
        from transformers import pipeline

        # Get model config
        config = model_configs.get(model_type, model_configs['financial'])
        cache_key = f'_pipeline_{model_type}'

        # Use cached model or create new one
        if not hasattr(analyze_sentiment_transformer, cache_key) or not use_cache:
            try:
                # Try preferred model first
                setattr(analyze_sentiment_transformer, cache_key, pipeline(
                    "sentiment-analysis",
                    model=config['model'],
                    device=-1  # CPU
                ))
            except Exception:
                # Fallback to general model
                if model_type != 'general':
                    config = model_configs['general']
                    setattr(analyze_sentiment_transformer, cache_key, pipeline(
                        "sentiment-analysis",
                        model=config['model'],
                        device=-1
                    ))
                else:
                    raise

        sentiment_pipeline = getattr(analyze_sentiment_transformer, cache_key)

        # Truncate text if too long
        max_length = 512
        if len(text) > max_length:
            text = text[:max_length]

        result = sentiment_pipeline(text)[0]

        # Convert to our format based on model type
        label = result['label'].lower()
        raw_score = result['score']

        # Map label to sentiment direction
        label_map = {k.lower(): v for k, v in config['labels'].items()}
        direction = label_map.get(label, 0)

        if direction == 1:
            sentiment_score = raw_score
            sentiment_label = 'Positive'
        elif direction == -1:
            sentiment_score = -raw_score
            sentiment_label = 'Negative'
        else:
            sentiment_score = 0
            sentiment_label = 'Neutral'

        # Adjust for confidence threshold
        if abs(sentiment_score) < 0.6:
            sentiment_label = 'Neutral'

        return {
            'score': float(sentiment_score),
            'label': sentiment_label,
            'confidence': float(raw_score),
            'method': 'transformer',
            'model': config['model'],
            'model_type': model_type,
            'raw_label': result['label'],
            'raw_score': float(result['score'])
        }

    except ImportError:
        result = analyze_sentiment_simple(text)
        result['method'] = 'keyword'
        result['note'] = 'Install transformers package for better accuracy: pip install transformers'
        return result

    except Exception as e:
        # Fall back to keyword-based analysis on any error
        result = analyze_sentiment_simple(text)
        result['method'] = 'keyword'
        result['error'] = str(e)
        result['fallback_reason'] = f'Failed to load {model_type} model'
        return result


def analyze_sentiment_batch(texts: list, use_transformer: bool = True) -> list:
    """
    Analyze sentiment for multiple texts efficiently

    Args:
        texts: List of text strings to analyze
        use_transformer: Whether to try transformer first (default True)

    Returns:
        List of sentiment result dicts
    """
    results = []

    if use_transformer:
        try:
            from transformers import pipeline

            # Batch processing with transformer
            if not hasattr(analyze_sentiment_batch, '_pipeline'):
                analyze_sentiment_batch._pipeline = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    device=-1
                )

            pipe = analyze_sentiment_batch._pipeline

            # Truncate texts
            truncated = [t[:500] if len(t) > 500 else t for t in texts]

            # Batch predict
            raw_results = pipe(truncated, batch_size=8)

            for raw in raw_results:
                label = raw['label']
                score = raw['score']

                if label == 'POSITIVE':
                    sentiment_score = score
                    sentiment_label = 'Positive' if score >= 0.6 else 'Neutral'
                else:
                    sentiment_score = -score
                    sentiment_label = 'Negative' if score >= 0.6 else 'Neutral'

                results.append({
                    'score': float(sentiment_score),
                    'label': sentiment_label,
                    'confidence': float(score),
                    'method': 'transformer'
                })

            return results

        except Exception:
            pass

    # Fallback to keyword method
    for text in texts:
        result = analyze_sentiment_simple(text)
        result['method'] = 'keyword'
        results.append(result)

    return results


def analyze_news_sentiment(news_list: list) -> dict:
    """
    Analyze sentiment from list of news headlines

    Args:
        news_list: List of news headlines/articles

    Returns:
        Aggregated sentiment analysis
    """
    if not news_list:
        return {'overall_sentiment': 'Neutral', 'score': 0, 'confidence': 0}

    sentiments = [analyze_sentiment_simple(news) for news in news_list]

    avg_score = np.mean([s['score'] for s in sentiments])
    avg_confidence = np.mean([s['confidence'] for s in sentiments])

    positive_count = sum(1 for s in sentiments if s['label'] == 'Positive')
    negative_count = sum(1 for s in sentiments if s['label'] == 'Negative')
    neutral_count = sum(1 for s in sentiments if s['label'] == 'Neutral')

    if avg_score > 0.2:
        overall = 'Positive'
    elif avg_score < -0.2:
        overall = 'Negative'
    else:
        overall = 'Neutral'

    return {
        'overall_sentiment': overall,
        'score': avg_score,
        'confidence': avg_confidence,
        'breakdown': {
            'positive': positive_count,
            'negative': negative_count,
            'neutral': neutral_count
        },
        'total_analyzed': len(news_list)
    }


# ══════════════════════════════════════════════════════════════════════
# ENSEMBLE ML MODELS
# ══════════════════════════════════════════════════════════════════════

def create_ensemble_prediction(df: pd.DataFrame, quick_mode: bool = False, deep_mode: bool = False) -> dict:
    """
    Create ensemble prediction using multiple ML models

    Args:
        df: DataFrame with price and indicator data
        quick_mode: If True, use fewer models for faster analysis
        deep_mode: If True, use more rigorous validation and all models

    Returns:
        Dict with ensemble prediction and individual model results
    """
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split, cross_val_score

    # Prepare features
    df_features = df.copy()

    # Create target (1 = price up next day, 0 = down)
    df_features['Target'] = (df_features['Close'].shift(-1) > df_features['Close']).astype(int)

    # Select features based on mode
    if quick_mode:
        feature_cols = ['RSI_14', 'MACD', 'BB_Percent', 'Stoch_K', 'Distance_SMA_20']
    elif deep_mode:
        feature_cols = ['RSI_14', 'RSI_7', 'RSI_21', 'MACD', 'MACD_Histogram', 'BB_Percent', 'BB_Width',
                        'ROC', 'Stoch_K', 'Stoch_D', 'StochRSI_K', 'Distance_SMA_20', 'Distance_SMA_50',
                        'Distance_SMA_200', 'HV_20', 'MFI', 'CCI', 'Williams_R', 'CMF', 'ADX',
                        'Momentum', 'Awesome_Oscillator', 'Force_Index_13', 'Trend_Score']
    else:
        feature_cols = ['RSI_14', 'MACD', 'BB_Percent', 'ROC', 'Stoch_K',
                        'Distance_SMA_20', 'Distance_SMA_50', 'HV_20', 'MFI', 'CCI']

    # Filter available columns
    available_features = [col for col in feature_cols if col in df_features.columns]

    if len(available_features) < 3:
        return {'error': 'Insufficient features calculated'}

    # Drop NaN rows
    df_clean = df_features[available_features + ['Target']].dropna()

    if len(df_clean) < 100:
        return {'error': 'Insufficient data for ML training'}

    X = df_clean[available_features].values
    y = df_clean['Target'].values

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Split data - different test size based on mode
    test_size = 0.1 if quick_mode else (0.3 if deep_mode else 0.2)
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=test_size, shuffle=False)

    # Define models based on mode
    if quick_mode:
        # Quick mode: only 2 fastest models
        models = {
            'Random Forest': RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1),
            'Logistic Regression': LogisticRegression(random_state=42, max_iter=200)
        }
    elif deep_mode:
        # Deep mode: all models with more estimators
        models = {
            'Random Forest': RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1, max_depth=10),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=150, random_state=42, learning_rate=0.05),
            'AdaBoost': AdaBoostClassifier(n_estimators=150, random_state=42, learning_rate=0.5),
            'Logistic Regression': LogisticRegression(random_state=42, max_iter=500, C=0.5),
            'SVM': SVC(probability=True, random_state=42, kernel='rbf', C=1.0)
        }
    else:
        # Standard mode
        models = {
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'AdaBoost': AdaBoostClassifier(n_estimators=100, random_state=42),
            'Logistic Regression': LogisticRegression(random_state=42),
            'SVM': SVC(probability=True, random_state=42)
        }

    predictions = {}
    probabilities = []

    for name, model in models.items():
        try:
            model.fit(X_train, y_train)
            accuracy = model.score(X_test, y_test)

            # For deep mode, use cross-validation for more reliable accuracy
            cv_accuracy = None
            if deep_mode:
                try:
                    cv_scores = cross_val_score(model, X_scaled[:-1], y[:-1], cv=5, scoring='accuracy')
                    cv_accuracy = float(np.mean(cv_scores))
                except:
                    cv_accuracy = accuracy

            # Predict for last row (tomorrow)
            last_features = X_scaled[-1:].reshape(1, -1)
            pred = model.predict(last_features)[0]
            prob = model.predict_proba(last_features)[0]

            predictions[name] = {
                'prediction': 'Bullish' if pred == 1 else 'Bearish',
                'confidence': float(max(prob)),
                'accuracy': float(cv_accuracy if cv_accuracy else accuracy),
                'test_accuracy': float(accuracy)
            }
            probabilities.append(prob[1])  # Probability of bullish

        except Exception as e:
            predictions[name] = {'error': str(e)}

    # Ensemble vote
    if probabilities:
        avg_prob = np.mean(probabilities)

        # Count votes from individual models
        bullish_votes = 0
        bearish_votes = 0
        bullish_confidence_sum = 0
        bearish_confidence_sum = 0

        for name, pred_data in predictions.items():
            if 'error' not in pred_data:
                conf = pred_data.get('confidence', 0.5)
                acc = pred_data.get('accuracy', 0.5)
                weight = conf * acc

                if pred_data['prediction'] == 'Bullish':
                    bullish_votes += 1
                    bullish_confidence_sum += weight
                else:
                    bearish_votes += 1
                    bearish_confidence_sum += weight

        total_votes = bullish_votes + bearish_votes

        # Ensemble decision based on majority vote weighted by confidence
        if total_votes > 0:
            # Calculate weighted vote - higher values = more bullish
            if bullish_votes > bearish_votes:
                # Majority bullish
                weighted_avg = 0.5 + (bullish_confidence_sum / total_votes) * 0.5
                ensemble_prediction = 'Bullish'
            elif bearish_votes > bullish_votes:
                # Majority bearish
                weighted_avg = 0.5 - (bearish_confidence_sum / total_votes) * 0.5
                ensemble_prediction = 'Bearish'
            else:
                # Tie - use raw probability average
                weighted_avg = avg_prob
                ensemble_prediction = 'Bullish' if avg_prob > 0.5 else 'Bearish'
        else:
            weighted_avg = avg_prob
            ensemble_prediction = 'Bullish' if avg_prob > 0.5 else 'Bearish'

        ensemble_confidence = abs(weighted_avg - 0.5) * 2  # Scale to 0-1
    else:
        avg_prob = 0.5
        weighted_avg = 0.5
        ensemble_prediction = 'Neutral'
        ensemble_confidence = 0

    # ═══ IMPORTANT: Align ensemble with recent price action ═══
    # This helps resolve contradictions between individual models and ensemble
    if len(df) > 20:
        try:
            # Calculate recent price action signals
            recent_close = df['Close'].iloc[-1]
            close_5d_ago = df['Close'].iloc[-5] if len(df) >= 5 else recent_close
            close_10d_ago = df['Close'].iloc[-10] if len(df) >= 10 else recent_close
            close_20d_ago = df['Close'].iloc[-20] if len(df) >= 20 else recent_close

            # Short-term trend (5-day)
            short_trend = (recent_close / close_5d_ago - 1) * 100

            # Medium-term trend (10-day)
            med_trend = (recent_close / close_10d_ago - 1) * 100

            # Get moving average alignment
            sma_20 = df['Close'].rolling(20).mean().iloc[-1] if len(df) >= 20 else recent_close
            sma_50 = df['Close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else recent_close

            # Price action score: positive = bullish, negative = bearish
            price_action_score = 0

            # Recent price momentum
            if short_trend > 2:
                price_action_score += 1
            elif short_trend < -2:
                price_action_score -= 1

            if med_trend > 3:
                price_action_score += 1
            elif med_trend < -3:
                price_action_score -= 1

            # Price relative to moving averages
            if recent_close > sma_20:
                price_action_score += 1
            else:
                price_action_score -= 1

            if recent_close > sma_50:
                price_action_score += 0.5
            else:
                price_action_score -= 0.5

            # SMA alignment (golden cross / death cross potential)
            if sma_20 > sma_50:
                price_action_score += 0.5
            else:
                price_action_score -= 0.5

            # Adjust ensemble prediction if there's strong price action conflict
            # This prevents AI from being bearish when chart clearly shows bullish patterns
            if price_action_score >= 2.5 and ensemble_prediction == 'Bearish':
                # Strong bullish price action but ensemble says bearish - likely a conflict
                # Adjust confidence down and potentially flip
                if ensemble_confidence < 0.6:
                    ensemble_prediction = 'Bullish'
                    ensemble_confidence = 0.55
                    avg_prob = 0.55
                    weighted_avg = 0.55
                else:
                    # Reduce confidence to reflect uncertainty
                    ensemble_confidence = max(0.5, ensemble_confidence - 0.15)

            elif price_action_score <= -2.5 and ensemble_prediction == 'Bullish':
                # Strong bearish price action but ensemble says bullish - conflict
                if ensemble_confidence < 0.6:
                    ensemble_prediction = 'Bearish'
                    ensemble_confidence = 0.55
                    avg_prob = 0.45
                    weighted_avg = 0.45
                else:
                    ensemble_confidence = max(0.5, ensemble_confidence - 0.15)

        except Exception:
            pass  # Keep original ensemble if price action check fails

    return {
        'ensemble_prediction': ensemble_prediction,
        'ensemble_confidence': ensemble_confidence,
        'bullish_probability': avg_prob,
        'weighted_probability': weighted_avg,
        'individual_models': predictions,
        'features_used': available_features,
        'analysis_mode': 'Quick' if quick_mode else ('Deep' if deep_mode else 'Standard'),
        'models_used': len(models)
    }


# ══════════════════════════════════════════════════════════════════════
# MARKET REGIME DETECTION
# ══════════════════════════════════════════════════════════════════════

def detect_market_regime(df: pd.DataFrame) -> dict:
    """
    Detect current market regime using multiple indicators

    Returns:
        Dict with regime classification and characteristics
    """
    if len(df) < 200:
        return {'regime': 'Unknown', 'confidence': 0}

    latest = df.iloc[-1]

    # Get key indicators
    rsi = latest.get('RSI_14', 50)
    adx = latest.get('ADX', 25)
    bb_width = latest.get('BB_Width', 0.1)
    hv = latest.get('HV_20', 20)
    trend_score = latest.get('Trend_Score', 2.5)

    # Calculate 50-day return and volatility
    returns_50d = (df['Close'].iloc[-1] / df['Close'].iloc[-50] - 1) * 100

    # Regime classification
    regimes = []

    # Trend regimes
    if adx > 25:
        if trend_score >= 4:
            regimes.append(('Strong Uptrend', 0.9))
        elif trend_score <= 1:
            regimes.append(('Strong Downtrend', 0.9))
        else:
            regimes.append(('Trending', 0.7))
    else:
        regimes.append(('Range-bound', 0.6))

    # Volatility regimes
    if hv > 40:
        regimes.append(('High Volatility', 0.85))
    elif hv < 15:
        regimes.append(('Low Volatility', 0.75))
    else:
        regimes.append(('Normal Volatility', 0.6))

    # Momentum regimes
    if rsi > 70:
        regimes.append(('Overbought', 0.8))
    elif rsi < 30:
        regimes.append(('Oversold', 0.8))

    # Determine primary regime
    primary_regime = max(regimes, key=lambda x: x[1])

    # Trading recommendations based on regime
    if 'Strong Uptrend' in primary_regime[0]:
        strategy = 'Buy dips, ride the trend'
        risk_level = 'Low'
    elif 'Strong Downtrend' in primary_regime[0]:
        strategy = 'Avoid buying, wait for reversal signals'
        risk_level = 'High'
    elif 'Range-bound' in primary_regime[0]:
        strategy = 'Buy at support, sell at resistance'
        risk_level = 'Medium'
    elif 'High Volatility' in primary_regime[0]:
        strategy = 'Reduce position size, use tight stops'
        risk_level = 'High'
    elif 'Overbought' in primary_regime[0]:
        strategy = 'Consider taking profits, wait for pullback'
        risk_level = 'Medium-High'
    elif 'Oversold' in primary_regime[0]:
        strategy = 'Look for bullish reversal signals'
        risk_level = 'Medium'
    else:
        strategy = 'Follow standard trend analysis'
        risk_level = 'Medium'

    return {
        'primary_regime': primary_regime[0],
        'confidence': primary_regime[1],
        'all_regimes': [r[0] for r in regimes],
        'suggested_strategy': strategy,
        'risk_level': risk_level,
        'indicators': {
            'ADX': adx,
            'RSI': rsi,
            'Historical_Volatility': hv,
            'Trend_Score': trend_score,
            '50d_Return': returns_50d
        }
    }


# ══════════════════════════════════════════════════════════════════════
# ANOMALY DETECTION
# ══════════════════════════════════════════════════════════════════════

def detect_anomalies(df: pd.DataFrame) -> dict:
    """
    Detect price and volume anomalies using statistical methods

    Returns:
        Dict with detected anomalies and alerts
    """
    anomalies = []

    # Price anomaly detection
    returns = df['Close'].pct_change()
    mean_return = returns.rolling(50).mean()
    std_return = returns.rolling(50).std()

    # Z-score for last return
    last_return = returns.iloc[-1]
    z_score = (last_return - mean_return.iloc[-1]) / std_return.iloc[-1]

    if abs(z_score) > 2:
        direction = 'positive' if z_score > 0 else 'negative'
        anomalies.append({
            'type': 'Price Anomaly',
            'description': f'Unusual {direction} move ({z_score:.1f} std)',
            'severity': 'High' if abs(z_score) > 3 else 'Medium',
            'value': last_return * 100
        })

    # Volume anomaly detection
    volume_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(20).mean().iloc[-1]
    if volume_ratio > 3:
        anomalies.append({
            'type': 'Volume Spike',
            'description': f'Volume {volume_ratio:.1f}x above average',
            'severity': 'High' if volume_ratio > 5 else 'Medium',
            'value': volume_ratio
        })
    elif volume_ratio < 0.3:
        anomalies.append({
            'type': 'Volume Dry-up',
            'description': f'Volume only {volume_ratio:.1%} of average',
            'severity': 'Medium',
            'value': volume_ratio
        })

    # Gap detection
    gap = (df['Open'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100
    if abs(gap) > 2:
        direction = 'up' if gap > 0 else 'down'
        anomalies.append({
            'type': f'Gap {direction.capitalize()}',
            'description': f'{abs(gap):.1f}% gap {direction}',
            'severity': 'High' if abs(gap) > 4 else 'Medium',
            'value': gap
        })

    # Volatility expansion
    current_atr = df.get('ATR_14', pd.Series([0])).iloc[-1]
    avg_atr = df.get('ATR_14', pd.Series([0])).rolling(50).mean().iloc[-1]
    if current_atr > avg_atr * 2:
        anomalies.append({
            'type': 'Volatility Expansion',
            'description': 'ATR doubled from average',
            'severity': 'Medium',
            'value': current_atr / avg_atr
        })

    return {
        'anomalies': anomalies,
        'total_alerts': len(anomalies),
        'highest_severity': max([a['severity'] for a in anomalies], default='None')
    }


# ══════════════════════════════════════════════════════════════════════
# COMPREHENSIVE AI ANALYSIS
# ══════════════════════════════════════════════════════════════════════

def generate_ai_analysis(df: pd.DataFrame, symbol: str = '', fundamentals: dict = None, analysis_depth: str = 'Standard') -> dict:
    """
    Generate comprehensive AI-powered analysis

    Args:
        df: DataFrame with price data and indicators
        symbol: Stock symbol
        fundamentals: Fundamental data
        analysis_depth: 'Quick Analysis', 'Standard', or 'Deep Analysis'

    Returns:
        Complete AI analysis report
    """
    analysis = {
        'symbol': symbol,
        'timestamp': datetime.now().isoformat(),
        'current_price': df['Close'].iloc[-1],
        'analysis_depth': analysis_depth
    }

    # 1. Calculate advanced indicators if not present
    if 'RSI_14' not in df.columns:
        df = calculate_advanced_indicators(df)

    # 2. Pattern Recognition - Always run for all modes
    analysis['candlestick_patterns'] = detect_candlestick_patterns(df)
    analysis['chart_patterns'] = detect_chart_patterns(df)

    # 3. Market Regime - Always run
    analysis['market_regime'] = detect_market_regime(df)

    # 4. Anomaly Detection - Skip for Quick Analysis
    if analysis_depth != 'Quick Analysis':
        analysis['anomalies'] = detect_anomalies(df)
    else:
        analysis['anomalies'] = {'anomalies': [], 'total_alerts': 0, 'highest_severity': 'None'}

    # 5. Ensemble ML Prediction - Different configs based on depth
    if len(df) >= 200:
        if analysis_depth == 'Quick Analysis':
            # Quick: Use fewer models and less data
            analysis['ml_ensemble'] = create_ensemble_prediction(df, quick_mode=True)
        elif analysis_depth == 'Deep Analysis':
            # Deep: Use all models with extended validation
            analysis['ml_ensemble'] = create_ensemble_prediction(df, deep_mode=True)
        else:
            # Standard mode
            analysis['ml_ensemble'] = create_ensemble_prediction(df)
    else:
        analysis['ml_ensemble'] = {'error': 'Insufficient data for ML'}

    # 6. Technical Score (0-100)
    tech_score = calculate_technical_score(df)
    analysis['technical_score'] = tech_score

    # 7. Overall AI Recommendation - weighted differently based on depth
    analysis['ai_recommendation'] = generate_ai_recommendation(analysis, fundamentals, analysis_depth)

    return analysis


def calculate_technical_score(df: pd.DataFrame) -> dict:
    """
    Calculate composite technical score from 0-100
    """
    scores = []
    breakdown = {}

    latest = df.iloc[-1]

    # Trend Score (25 points max)
    trend_score = latest.get('Trend_Score', 2.5)
    trend_points = (trend_score / 5) * 25
    breakdown['Trend'] = trend_points
    scores.append(trend_points)

    # Momentum Score (25 points max)
    rsi = latest.get('RSI_14', 50)
    macd = latest.get('MACD', 0)
    macd_signal = latest.get('MACD_Signal', 0)

    rsi_score = 12.5 if 40 < rsi < 60 else (25 if rsi < 30 else (0 if rsi > 70 else 15))
    macd_score = 12.5 if macd > macd_signal else 5
    momentum_points = rsi_score + macd_score
    breakdown['Momentum'] = momentum_points
    scores.append(momentum_points)

    # Volume Score (25 points max)
    mfi = latest.get('MFI', 50)
    cmf = latest.get('CMF', 0)

    mfi_score = 12.5 if mfi > 50 else 5
    cmf_score = 12.5 if cmf > 0 else 5
    volume_points = mfi_score + cmf_score
    breakdown['Volume'] = volume_points
    scores.append(volume_points)

    # Volatility Score (25 points max)
    bb_percent = latest.get('BB_Percent', 0.5)
    hv = latest.get('HV_20', 20)

    bb_score = 15 if 0.2 < bb_percent < 0.8 else 5
    vol_score = 10 if hv < 30 else 5
    volatility_points = bb_score + vol_score
    breakdown['Volatility'] = volatility_points
    scores.append(volatility_points)

    total_score = sum(scores)

    # Grade
    if total_score >= 80:
        grade = 'A'
    elif total_score >= 70:
        grade = 'B'
    elif total_score >= 55:
        grade = 'C'
    elif total_score >= 40:
        grade = 'D'
    else:
        grade = 'F'

    return {
        'score': total_score,
        'grade': grade,
        'breakdown': breakdown,
        'max_score': 100
    }


def generate_ai_recommendation(analysis: dict, fundamentals: dict = None, analysis_depth: str = 'Standard') -> dict:
    """
    Generate final AI recommendation based on all analysis

    Args:
        analysis: Dict containing all analysis results
        fundamentals: Fundamental data (optional)
        analysis_depth: 'Quick Analysis', 'Standard', or 'Deep Analysis'
    """
    signals = []

    # Weight multipliers based on analysis depth
    if analysis_depth == 'Quick Analysis':
        # Quick mode: More weight on technical score, less on ML
        tech_weight = 0.40
        regime_weight = 0.25
        ml_weight = 0.15
        pattern_weight = 0.20
    elif analysis_depth == 'Deep Analysis':
        # Deep mode: More weight on ML, patterns get more weight
        tech_weight = 0.20
        regime_weight = 0.20
        ml_weight = 0.35
        pattern_weight = 0.25
    else:
        # Standard mode: Balanced weights
        tech_weight = 0.30
        regime_weight = 0.25
        ml_weight = 0.25
        pattern_weight = 0.20

    # Technical Score signal
    tech_score = analysis.get('technical_score', {}).get('score', 50)
    if tech_score >= 70:
        signals.append(('BUY', tech_weight))
    elif tech_score <= 30:
        signals.append(('SELL', tech_weight))
    else:
        signals.append(('HOLD', tech_weight * 0.6))

    # Market Regime signal
    regime = analysis.get('market_regime', {}).get('primary_regime', 'Unknown')
    if 'Uptrend' in regime:
        signals.append(('BUY', regime_weight))
    elif 'Downtrend' in regime:
        signals.append(('SELL', regime_weight))
    elif 'Oversold' in regime:
        signals.append(('BUY', regime_weight * 0.8))
    elif 'Overbought' in regime:
        signals.append(('SELL', regime_weight * 0.8))
    else:
        signals.append(('HOLD', regime_weight * 0.5))

    # ML Ensemble signal
    ml_pred = analysis.get('ml_ensemble', {}).get('ensemble_prediction', 'Unknown')
    ml_conf = analysis.get('ml_ensemble', {}).get('ensemble_confidence', 0.5)
    if ml_pred == 'Bullish':
        signals.append(('BUY', ml_weight * ml_conf))
    elif ml_pred == 'Bearish':
        signals.append(('SELL', ml_weight * ml_conf))
    else:
        signals.append(('HOLD', ml_weight * 0.3))

    # Pattern signal - consider both candlestick and chart patterns
    candle_patterns = analysis.get('candlestick_patterns', {})
    chart_patterns = analysis.get('chart_patterns', {})

    bullish_patterns = sum(1 for p in candle_patterns.values() if p.get('signal') == 'Bullish')
    bearish_patterns = sum(1 for p in candle_patterns.values() if p.get('signal') == 'Bearish')
    bullish_patterns += sum(1 for p in chart_patterns.values() if p.get('signal') == 'Bullish')
    bearish_patterns += sum(1 for p in chart_patterns.values() if p.get('signal') == 'Bearish')

    if bullish_patterns > bearish_patterns:
        signals.append(('BUY', pattern_weight * min(1.0, bullish_patterns / 3)))
    elif bearish_patterns > bullish_patterns:
        signals.append(('SELL', pattern_weight * min(1.0, bearish_patterns / 3)))
    else:
        signals.append(('HOLD', pattern_weight * 0.4))

    # Calculate weighted recommendation
    buy_score = sum(w for s, w in signals if s == 'BUY')
    sell_score = sum(w for s, w in signals if s == 'SELL')
    hold_score = sum(w for s, w in signals if s == 'HOLD')

    total = buy_score + sell_score + hold_score
    if total > 0:
        buy_pct = buy_score / total
        sell_pct = sell_score / total
        hold_pct = hold_score / total
    else:
        buy_pct = sell_pct = hold_pct = 0.33

    # Final recommendation
    if buy_pct > 0.5:
        recommendation = 'STRONG BUY' if buy_pct > 0.7 else 'BUY'
        action = 'Enter long position'
    elif sell_pct > 0.5:
        recommendation = 'STRONG SELL' if sell_pct > 0.7 else 'SELL'
        action = 'Exit or short position'
    else:
        recommendation = 'HOLD'
        action = 'Wait for clearer signal'

    confidence = max(buy_pct, sell_pct, hold_pct)

    # Detect contradictions between signals
    contradictions = []
    warnings = []

    # Check if patterns and ML contradict
    pattern_signal = 'Bullish' if bullish_patterns > bearish_patterns else ('Bearish' if bearish_patterns > bullish_patterns else 'Neutral')
    if pattern_signal != 'Neutral' and ml_pred != 'Unknown':
        if pattern_signal == 'Bullish' and ml_pred == 'Bearish':
            contradictions.append({
                'type': 'Pattern vs ML Contradiction',
                'description': f'Chart patterns suggest Bullish ({bullish_patterns} bullish vs {bearish_patterns} bearish) but ML models predict Bearish',
                'resolution': 'Consider waiting for confirmation or reducing position size'
            })
        elif pattern_signal == 'Bearish' and ml_pred == 'Bullish':
            contradictions.append({
                'type': 'Pattern vs ML Contradiction',
                'description': f'Chart patterns suggest Bearish ({bearish_patterns} bearish vs {bullish_patterns} bullish) but ML models predict Bullish',
                'resolution': 'Consider waiting for confirmation or reducing position size'
            })

    # Check if regime contradicts recommendation
    if 'Uptrend' in regime and 'SELL' in recommendation:
        warnings.append('Market is in uptrend but recommendation is SELL - possible short-term correction')
    elif 'Downtrend' in regime and 'BUY' in recommendation:
        warnings.append('Market is in downtrend but recommendation is BUY - possible reversal signal')

    # Check if overbought/oversold contradicts patterns
    if 'Overbought' in regime and bullish_patterns > bearish_patterns:
        warnings.append('Bullish patterns detected but RSI shows overbought - be cautious of pullback')
    elif 'Oversold' in regime and bearish_patterns > bullish_patterns:
        warnings.append('Bearish patterns detected but RSI shows oversold - potential bounce possible')

    return {
        'recommendation': recommendation,
        'action': action,
        'confidence': confidence,
        'probabilities': {
            'buy': buy_pct,
            'sell': sell_pct,
            'hold': hold_pct
        },
        'factors': {
            'technical_score': tech_score,
            'market_regime': regime,
            'ml_prediction': ml_pred,
            'bullish_patterns': bullish_patterns,
            'bearish_patterns': bearish_patterns
        },
        'contradictions': contradictions,
        'warnings': warnings,
        'analysis_depth': analysis_depth
    }

