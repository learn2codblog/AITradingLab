# data_loader.py
"""
Data Loading Module
Handles downloading and preprocessing OHLCV market data
"""

import yfinance as yf
import pandas as pd
import numpy as np


def load_stock_data(ticker: str, start, end) -> pd.DataFrame:
    """
    Download OHLCV (Open, High, Low, Close, Volume) data for a stock
    
    Args:
        ticker: Stock ticker symbol (e.g., 'RELIANCE.NS', 'AAPL')
        start: Start date for data range
        end: End date for data range
    
    Returns:
        DataFrame with OHLCV columns or None if download fails
    """
    try:
        df = yf.download(ticker, start=start, end=end, progress=False)
        if df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    except Exception as e:
        print(f"Error loading data for {ticker}: {e}")
        return None
