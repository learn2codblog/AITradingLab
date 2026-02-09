"""
Technical Indicators Module for TradeGenius AI
"""

import pandas as pd
import numpy as np


def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate technical indicators for stock data

    Args:
        df: DataFrame with OHLCV data

    Returns:
        DataFrame with indicators added
    """
    df = df.copy()

    # ─── MOVING AVERAGES ───
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    df['SMA200'] = df['Close'].rolling(window=200).mean()

    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()

    # ─── RSI ───
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI14'] = 100 - (100 / (1 + rs))

    # ─── MACD ───
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']

    # ─── BOLLINGER BANDS ───
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (2 * bb_std)
    df['BB_Lower'] = df['BB_Middle'] - (2 * bb_std)
    df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']

    # ─── ATR (Average True Range) ───
    high_low = df['High'] - df['Low']
    high_close = abs(df['High'] - df['Close'].shift())
    low_close = abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR14'] = tr.rolling(window=14).mean()

    # ─── STOCHASTIC ───
    low_14 = df['Low'].rolling(14).min()
    high_14 = df['High'].rolling(14).max()
    df['Stoch_K'] = 100 * (df['Close'] - low_14) / (high_14 - low_14)
    df['Stoch_D'] = df['Stoch_K'].rolling(3).mean()

    # ─── VOLUME INDICATORS ───
    df['Volume_SMA20'] = df['Volume'].rolling(window=20).mean()
    df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA20']

    # OBV
    df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()

    # ─── ADX (Average Directional Index) ───
    plus_dm = df['High'].diff()
    minus_dm = df['Low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0

    tr_14 = tr.rolling(14).sum()
    plus_di = 100 * (plus_dm.rolling(14).sum() / tr_14)
    minus_di = abs(100 * (minus_dm.rolling(14).sum() / tr_14))

    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    df['ADX'] = dx.rolling(14).mean()

    # ─── CCI (Commodity Channel Index) ───
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    df['CCI'] = (tp - tp.rolling(20).mean()) / (0.015 * tp.rolling(20).std())

    # ─── Williams %R ───
    df['Williams_R'] = -100 * (high_14 - df['Close']) / (high_14 - low_14)

    # ─── ROC (Rate of Change) ───
    df['ROC'] = df['Close'].pct_change(periods=10) * 100

    # ─── MFI (Money Flow Index) ───
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    mf = tp * df['Volume']
    positive_mf = mf.where(tp > tp.shift(1), 0).rolling(14).sum()
    negative_mf = mf.where(tp < tp.shift(1), 0).rolling(14).sum()
    df['MFI'] = 100 - (100 / (1 + positive_mf / negative_mf))

    # ─── MOMENTUM ───
    df['Momentum'] = df['Close'] - df['Close'].shift(10)

    # ─── PRICE CHANGES ───
    df['Daily_Return'] = df['Close'].pct_change()
    df['Cumulative_Return'] = (1 + df['Daily_Return']).cumprod() - 1

    return df


def calculate_support_resistance(df: pd.DataFrame, window: int = 20) -> dict:
    """
    Calculate support and resistance levels

    Args:
        df: DataFrame with OHLCV data
        window: Lookback window

    Returns:
        Dict with support and resistance levels
    """
    recent_data = df.tail(window)

    support = recent_data['Low'].min()
    resistance = recent_data['High'].max()

    current_price = df['Close'].iloc[-1]

    return {
        'Support': support,
        'Resistance': resistance,
        'Current': current_price,
        'Distance_to_Support': (current_price - support) / current_price * 100,
        'Distance_to_Resistance': (resistance - current_price) / current_price * 100
    }


def get_trend(df: pd.DataFrame) -> str:
    """
    Determine the current trend

    Args:
        df: DataFrame with indicators

    Returns:
        Trend string ('Bullish', 'Bearish', 'Neutral')
    """
    if len(df) < 50:
        return 'Neutral'

    latest = df.iloc[-1]

    # Check moving average alignment
    price = latest['Close']
    sma20 = latest.get('SMA20', price)
    sma50 = latest.get('SMA50', price)
    sma200 = latest.get('SMA200', price)

    bullish_signals = 0
    bearish_signals = 0

    # Price above/below MAs
    if price > sma20:
        bullish_signals += 1
    else:
        bearish_signals += 1

    if price > sma50:
        bullish_signals += 1
    else:
        bearish_signals += 1

    if price > sma200:
        bullish_signals += 1
    else:
        bearish_signals += 1

    # MA alignment
    if sma20 > sma50 > sma200:
        bullish_signals += 2
    elif sma20 < sma50 < sma200:
        bearish_signals += 2

    # RSI
    rsi = latest.get('RSI14', 50)
    if rsi > 50:
        bullish_signals += 1
    else:
        bearish_signals += 1

    # MACD
    macd = latest.get('MACD', 0)
    if macd > 0:
        bullish_signals += 1
    else:
        bearish_signals += 1

    if bullish_signals > bearish_signals + 2:
        return 'Bullish'
    elif bearish_signals > bullish_signals + 2:
        return 'Bearish'
    else:
        return 'Neutral'


def generate_signals(df: pd.DataFrame) -> dict:
    """
    Generate trading signals based on indicators

    Args:
        df: DataFrame with indicators

    Returns:
        Dict with signals
    """
    if len(df) < 50:
        return {'signal': 'HOLD', 'strength': 'Weak', 'confidence': 0.5}

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    buy_signals = 0
    sell_signals = 0
    total_signals = 0

    # RSI signals
    rsi = latest.get('RSI14', 50)
    if rsi < 30:
        buy_signals += 2
    elif rsi > 70:
        sell_signals += 2
    elif rsi < 40:
        buy_signals += 1
    elif rsi > 60:
        sell_signals += 1
    total_signals += 2

    # MACD crossover
    macd = latest.get('MACD', 0)
    macd_signal = latest.get('MACD_Signal', 0)
    prev_macd = prev.get('MACD', 0)
    prev_signal = prev.get('MACD_Signal', 0)

    if macd > macd_signal and prev_macd <= prev_signal:
        buy_signals += 2  # Bullish crossover
    elif macd < macd_signal and prev_macd >= prev_signal:
        sell_signals += 2  # Bearish crossover
    total_signals += 2

    # Price vs Bollinger Bands
    price = latest['Close']
    bb_upper = latest.get('BB_Upper', price * 1.1)
    bb_lower = latest.get('BB_Lower', price * 0.9)

    if price < bb_lower:
        buy_signals += 1
    elif price > bb_upper:
        sell_signals += 1
    total_signals += 1

    # Trend
    trend = get_trend(df)
    if trend == 'Bullish':
        buy_signals += 1
    elif trend == 'Bearish':
        sell_signals += 1
    total_signals += 1

    # Volume confirmation
    volume_ratio = latest.get('Volume_Ratio', 1)
    if volume_ratio > 1.5:
        if buy_signals > sell_signals:
            buy_signals += 1
        else:
            sell_signals += 1
    total_signals += 1

    # Calculate final signal
    net_signal = buy_signals - sell_signals
    confidence = abs(net_signal) / total_signals

    if net_signal > 2:
        signal = 'STRONG BUY'
        strength = 'Strong'
    elif net_signal > 0:
        signal = 'BUY'
        strength = 'Moderate'
    elif net_signal < -2:
        signal = 'STRONG SELL'
        strength = 'Strong'
    elif net_signal < 0:
        signal = 'SELL'
        strength = 'Moderate'
    else:
        signal = 'HOLD'
        strength = 'Weak'

    return {
        'signal': signal,
        'strength': strength,
        'confidence': min(confidence + 0.3, 0.95),
        'buy_signals': buy_signals,
        'sell_signals': sell_signals,
        'trend': trend
    }

