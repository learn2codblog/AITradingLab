"""
Data Loader Module for TradeGenius AI
Handles loading stock data from Yahoo Finance
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta


def load_stock_data(symbol: str, start_date=None, end_date=None, period: str = "3y") -> pd.DataFrame:
    """
    Load stock data from Yahoo Finance

    Args:
        symbol: Stock symbol (e.g., 'RELIANCE.NS')
        start_date: Start date for data
        end_date: End date for data
        period: Period if dates not specified ('1y', '2y', '3y', '5y')

    Returns:
        DataFrame with OHLCV data
    """
    try:
        ticker = yf.Ticker(symbol)

        if start_date and end_date:
            # Convert dates if they're date objects
            if hasattr(start_date, 'strftime'):
                start_date = start_date.strftime('%Y-%m-%d')
            if hasattr(end_date, 'strftime'):
                end_date = end_date.strftime('%Y-%m-%d')

            df = ticker.history(start=start_date, end=end_date)
        else:
            df = ticker.history(period=period)

        if df.empty:
            return None

        # Clean column names
        df.columns = [col.replace(' ', '_') for col in df.columns]

        # Ensure standard column names
        column_mapping = {
            'Open': 'Open',
            'High': 'High',
            'Low': 'Low',
            'Close': 'Close',
            'Volume': 'Volume',
            'Dividends': 'Dividends',
            'Stock_Splits': 'Stock_Splits'
        }

        # Rename if needed
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})

        # Remove timezone if present
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)

        return df

    except Exception as e:
        print(f"Error loading data for {symbol}: {e}")
        return None


def get_stock_info(symbol: str) -> dict:
    """
    Get stock information

    Args:
        symbol: Stock symbol

    Returns:
        Dict with stock info
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info
    except Exception as e:
        print(f"Error getting info for {symbol}: {e}")
        return {}


def get_multiple_stocks(symbols: list, start_date=None, end_date=None, period: str = "1y") -> dict:
    """
    Load data for multiple stocks

    Args:
        symbols: List of stock symbols
        start_date: Start date
        end_date: End date
        period: Period if dates not specified

    Returns:
        Dict mapping symbols to DataFrames
    """
    data = {}
    for symbol in symbols:
        df = load_stock_data(symbol, start_date, end_date, period)
        if df is not None and not df.empty:
            data[symbol] = df
    return data


def validate_symbol(symbol: str) -> bool:
    """
    Check if a stock symbol is valid

    Args:
        symbol: Stock symbol to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return 'regularMarketPrice' in info or 'currentPrice' in info
    except:
        return False

