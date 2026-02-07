# technical_indicators.py
"""
Technical Analysis Module
Calculates price-based and volume-based technical indicators
Used for short-term trend identification and pattern recognition
"""

import ta
import pandas as pd


def calculate_technical_indicators(stock: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate comprehensive technical indicators from OHLCV data
    
    Categories of indicators:
    
    1. TREND INDICATORS
       - SMA: Simple Moving Averages (5, 20, 50, 200 periods)
       - EMA: Exponential Moving Averages (12, 26 periods)
       - MACD: Moving Average Convergence Divergence
       - ADX: Average Directional Index
       - CCI: Commodity Channel Index
    
    2. MOMENTUM INDICATORS
       - RSI: Relative Strength Index (7, 14, 28 periods)
       - Stochastic: %K and %D (14 periods)
    
    3. VOLATILITY INDICATORS
       - ATR: Average True Range (14 periods)
       - Vol_5d, Vol_20d: 5-day and 20-day rolling volatility
    
    4. VOLUME INDICATORS
       - OBV: On-Balance Volume
       - Volume_MA20: 20-day volume moving average
       - Volume_Ratio: Current volume vs average
    
    5. RETURNS
       - Ret_1d, Ret_5d, Ret_20d: Daily, 5-day, 20-day returns
    
    Args:
        stock: DataFrame with OHLCV columns (Open, High, Low, Close, Volume)
    
    Returns:
        DataFrame with added technical indicator columns
    """
    # ────── TREND INDICATORS ──────┐
    stock['SMA5'] = ta.trend.sma_indicator(stock['Close'], window=5)
    stock['SMA20'] = ta.trend.sma_indicator(stock['Close'], window=20)
    stock['SMA50'] = ta.trend.sma_indicator(stock['Close'], window=50)
    stock['SMA200'] = ta.trend.sma_indicator(stock['Close'], window=200)
    stock['EMA12'] = ta.trend.ema_indicator(stock['Close'], window=12)
    stock['EMA26'] = ta.trend.ema_indicator(stock['Close'], window=26)
    stock['MACD'] = ta.trend.macd_diff(stock['Close'])
    stock['ADX'] = ta.trend.adx(stock['High'], stock['Low'], stock['Close'])
    stock['CCI'] = ta.trend.cci(stock['High'], stock['Low'], stock['Close'], window=20)
    
    # ────── MOMENTUM INDICATORS ──────┐
    stock['RSI7'] = ta.momentum.rsi(stock['Close'], window=7)
    stock['RSI14'] = ta.momentum.rsi(stock['Close'], window=14)
    stock['RSI28'] = ta.momentum.rsi(stock['Close'], window=28)
    stock['Stoch_K'] = ta.momentum.stoch(stock['High'], stock['Low'], stock['Close'], window=14)
    stock['Stoch_D'] = ta.momentum.stoch_signal(stock['High'], stock['Low'], stock['Close'], window=14)
    
    # ────── VOLATILITY INDICATORS ──────┐
    try:
        stock['ATR'] = ta.volatility.average_true_range(stock['High'], stock['Low'], stock['Close'], window=14)
    except AttributeError:
        stock['ATR'] = ta.volatility.atr(stock['High'], stock['Low'], stock['Close'], window=14)
    stock['Vol_5d'] = stock['Close'].pct_change().rolling(5).std()
    stock['Vol_20d'] = stock['Close'].pct_change().rolling(20).std()
    
    # ────── VOLUME INDICATORS ──────┐
    stock['OBV'] = ta.volume.on_balance_volume(stock['Close'], stock['Volume'])
    stock['Volume_MA20'] = stock['Volume'].rolling(20).mean()
    stock['Volume_Ratio'] = stock['Volume'] / stock['Volume_MA20']
    
    # ────── RETURNS ──────┐
    stock['Ret_1d'] = stock['Close'].pct_change(1)
    stock['Ret_5d'] = stock['Close'].pct_change(5)
    stock['Ret_20d'] = stock['Close'].pct_change(20)
    
    return stock
