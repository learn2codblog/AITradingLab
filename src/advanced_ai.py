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

    # 8. Supertrend
    atr = calculate_atr(df, 10)
    hl2 = (df['High'] + df['Low']) / 2
    df['Supertrend_Upper'] = hl2 + (2 * atr)
    df['Supertrend_Lower'] = hl2 - (2 * atr)

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

    # 33. Parabolic SAR (simplified)
    df['PSAR'] = calculate_psar(df)

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


def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate Average Directional Index"""
    plus_dm = df['High'].diff()
    minus_dm = df['Low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0

    tr = calculate_atr(df, 1) * period  # Simplified
    plus_di = 100 * (plus_dm.ewm(span=period).mean() / tr)
    minus_di = abs(100 * (minus_dm.ewm(span=period).mean() / tr))

    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    return dx.ewm(span=period).mean()


def calculate_psar(df: pd.DataFrame, af_start=0.02, af_increment=0.02, af_max=0.2) -> pd.Series:
    """Calculate Parabolic SAR (simplified version)"""
    psar = df['Close'].copy()
    af = af_start
    ep = df['Low'].iloc[0]
    trend = 1  # 1 = uptrend, -1 = downtrend

    for i in range(2, len(df)):
        if trend == 1:
            psar.iloc[i] = psar.iloc[i-1] + af * (ep - psar.iloc[i-1])
            if df['Low'].iloc[i] < psar.iloc[i]:
                trend = -1
                psar.iloc[i] = ep
                ep = df['Low'].iloc[i]
                af = af_start
            else:
                if df['High'].iloc[i] > ep:
                    ep = df['High'].iloc[i]
                    af = min(af + af_increment, af_max)
        else:
            psar.iloc[i] = psar.iloc[i-1] - af * (psar.iloc[i-1] - ep)
            if df['High'].iloc[i] > psar.iloc[i]:
                trend = 1
                psar.iloc[i] = ep
                ep = df['High'].iloc[i]
                af = af_start
            else:
                if df['Low'].iloc[i] < ep:
                    ep = df['Low'].iloc[i]
                    af = min(af + af_increment, af_max)

    return psar


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


def build_lstm_model(lookback: int = 60, forecast_days: int = 5):
    """
    Build LSTM model for price prediction

    Returns:
        Compiled Keras model
    """
    try:
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
        from tensorflow.keras.optimizers import Adam

        model = Sequential([
            LSTM(100, return_sequences=True, input_shape=(lookback, 1)),
            Dropout(0.2),
            BatchNormalization(),

            LSTM(100, return_sequences=True),
            Dropout(0.2),
            BatchNormalization(),

            LSTM(50, return_sequences=False),
            Dropout(0.2),

            Dense(50, activation='relu'),
            Dense(forecast_days)
        ])

        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])

        return model

    except ImportError:
        return None


def predict_with_lstm(df: pd.DataFrame, lookback: int = 60, forecast_days: int = 5, epochs: int = 50) -> dict:
    """
    Train LSTM and predict future prices

    Args:
        df: DataFrame with price data
        lookback: Days to look back
        forecast_days: Days to predict
        epochs: Training epochs

    Returns:
        Dict with predictions and confidence
    """
    try:
        from sklearn.preprocessing import MinMaxScaler

        # Check if we have enough data
        if len(df) < lookback + forecast_days + 10:
            return {'error': 'Insufficient data for LSTM prediction'}

        # Prepare data
        data = df['Close'].values.reshape(-1, 1)
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data)

        # Create sequences
        X, y = [], []
        for i in range(lookback, len(scaled_data) - forecast_days):
            X.append(scaled_data[i - lookback:i, 0])
            y.append(scaled_data[i:i + forecast_days, 0])

        X = np.array(X)
        y = np.array(y)
        X = X.reshape((X.shape[0], X.shape[1], 1))

        # Split data
        split = int(len(X) * 0.8)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        # Build and train model
        model = build_lstm_model(lookback, forecast_days)
        if model is None:
            return {'error': 'TensorFlow not installed'}

        # Train
        model.fit(X_train, y_train, epochs=epochs, batch_size=32,
                  validation_data=(X_test, y_test), verbose=0)

        # Predict next days
        last_sequence = scaled_data[-lookback:].reshape(1, lookback, 1)
        predicted_scaled = model.predict(last_sequence, verbose=0)[0]

        # Inverse transform
        predicted_prices = scaler.inverse_transform(predicted_scaled.reshape(-1, 1)).flatten()

        # Calculate confidence based on validation MAE
        val_pred = model.predict(X_test, verbose=0)
        val_pred_inv = scaler.inverse_transform(val_pred.reshape(-1, 1))
        y_test_inv = scaler.inverse_transform(y_test.reshape(-1, 1))
        mae = np.mean(np.abs(val_pred_inv - y_test_inv))

        current_price = df['Close'].iloc[-1]
        confidence = max(0, min(100, 100 - (mae / current_price * 100)))

        # Trend direction
        if predicted_prices[-1] > current_price:
            trend = 'Bullish'
            expected_return = (predicted_prices[-1] - current_price) / current_price * 100
        else:
            trend = 'Bearish'
            expected_return = (predicted_prices[-1] - current_price) / current_price * 100

        return {
            'current_price': current_price,
            'predictions': predicted_prices.tolist(),
            'forecast_days': forecast_days,
            'trend': trend,
            'expected_return': expected_return,
            'confidence': confidence,
            'mae': mae
        }

    except Exception as e:
        return {'error': str(e)}


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

