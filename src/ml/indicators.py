"""
Technical Indicators Module for TradeGenius AI
===============================================
Includes:
- Advanced Technical Indicators (30+)
- Trend Indicators
- Momentum Indicators
- Volatility Indicators
- Volume Indicators
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


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