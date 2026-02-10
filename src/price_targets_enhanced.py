# price_targets_enhanced.py
"""
Enhanced Price Targets Module with Multi-timeframe Analysis and Sector Screening
"""

import os
import pandas as pd
import numpy as np
import yfinance as yf

# Import stock universe module for enhanced sector screening
try:
    from . import stock_universe
except ImportError:
    import stock_universe


def calculate_multi_timeframe_levels(stock: pd.DataFrame) -> dict:
    """
    Calculate support and resistance for multiple timeframes
    
    Args:
        stock: DataFrame with OHLCV data
    
    Returns:
        Dict with support/resistance for 1-day (20-period), weekly (~50-period), monthly (~200-period)
    """
    
    # 1-Day (20-period) - Short-term trading
    support_1d = stock['Low'].tail(20).min()
    resistance_1d = stock['High'].tail(20).max()
    
    # Weekly equivalent (5 trading days × ~10 weeks = 50 periods)
    support_weekly = stock['Low'].tail(50).min() if len(stock) >= 50 else support_1d
    resistance_weekly = stock['High'].tail(50).max() if len(stock) >= 50 else resistance_1d
    
    # Monthly equivalent (20 trading days × ~10 months = 200 periods)
    support_monthly = stock['Low'].tail(200).min() if len(stock) >= 200 else support_1d
    resistance_monthly = stock['High'].tail(200).max() if len(stock) >= 200 else resistance_1d
    
    current_price = stock['Close'].iloc[-1]
    
    return {
        '1-Day': {
            'Support': round(support_1d, 2),
            'Resistance': round(resistance_1d, 2),
            'Distance to Support': round(((current_price - support_1d) / support_1d * 100), 2),
            'Distance to Resistance': round(((resistance_1d - current_price) / current_price * 100), 2)
        },
        'Weekly': {
            'Support': round(support_weekly, 2),
            'Resistance': round(resistance_weekly, 2),
            'Distance to Support': round(((current_price - support_weekly) / support_weekly * 100), 2),
            'Distance to Resistance': round(((resistance_weekly - current_price) / current_price * 100), 2)
        },
        'Monthly': {
            'Support': round(support_monthly, 2),
            'Resistance': round(resistance_monthly, 2),
            'Distance to Support': round(((current_price - support_monthly) / support_monthly * 100), 2),
            'Distance to Resistance': round(((resistance_monthly - current_price) / current_price * 100), 2)
        }
    }


def generate_buy_sell_explanation(stock: pd.DataFrame, fundamentals: dict = None) -> dict:
    """
    Generate detailed buy/sell/hold explanation with reasons
    
    Args:
        stock: DataFrame with indicators
        fundamentals: Fundamental metrics
    
    Returns:
        Dict with recommendation and detailed explanation
    """
    
    latest = stock.iloc[-1]
    current_price = latest['Close']
    
    # Collect signals
    bullish_signals = []
    bearish_signals = []
    neutral_signals = []
    
    # Technical Signals
    sma20 = latest.get('SMA20', current_price)
    sma50 = latest.get('SMA50', current_price)
    sma200 = latest.get('SMA200', current_price)
    ema12 = latest.get('EMA12', current_price)
    ema26 = latest.get('EMA26', current_price)
    rsi14 = latest.get('RSI14', 50)
    macd = latest.get('MACD', 0)
    volume_ratio = latest.get('Volume_Ratio', 1.0)
    
    # Trend Analysis
    if current_price > sma20 > sma50 > sma200:
        bullish_signals.append("✅ Strong uptrend: Price > SMA20 > SMA50 > SMA200")
    elif current_price > sma50:
        bullish_signals.append("✅ Uptrend: Price > SMA50")
    elif current_price < sma200:
        bearish_signals.append("❌ Strong downtrend: Price < SMA200")
    elif current_price < sma50:
        bearish_signals.append("❌ Downtrend: Price < SMA50")
    else:
        neutral_signals.append("➖ Mixed trend: Price between SMAs")
    
    # EMA Cross
    if ema12 > ema26:
        bullish_signals.append("✅ EMA12 > EMA26 (bullish crossover)")
    else:
        bearish_signals.append("❌ EMA12 < EMA26 (bearish crossover)")
    
    # MACD
    if macd > 0:
        bullish_signals.append("✅ MACD positive (upward momentum)")
    else:
        bearish_signals.append("❌ MACD negative (downward momentum)")
    
    # RSI
    if rsi14 < 30:
        bullish_signals.append(f"✅ RSI14 at {rsi14:.0f} (oversold - potential reversal)")
    elif rsi14 > 70:
        bearish_signals.append(f"❌ RSI14 at {rsi14:.0f} (overbought - pullback expected)")
    elif 40 < rsi14 < 60:
        neutral_signals.append(f"➖ RSI14 at {rsi14:.0f} (neutral momentum)")
    else:
        neutral_signals.append(f"➖ RSI14 at {rsi14:.0f}")
    
    # Volume
    if volume_ratio > 1.2:
        bullish_signals.append(f"✅ Volume high ({volume_ratio:.2f}x average) - strong conviction")
    elif volume_ratio < 0.8:
        bearish_signals.append(f"❌ Volume low ({volume_ratio:.2f}x average) - weak move")
    
    # Fundamental Signals
    if fundamentals:
        roe = fundamentals.get('ROE', 0)
        pe = fundamentals.get('PE', 50)
        growth = fundamentals.get('RevenueGrowth', 0)
        
        if roe and roe > 0.20:
            bullish_signals.append(f"✅ Strong ROE ({roe*100:.1f}%) - highly profitable")
        elif roe and roe < 0.10:
            bearish_signals.append(f"❌ Weak ROE ({roe*100:.1f}%) - low profitability")
        
        if pe and 15 < pe < 25:
            bullish_signals.append(f"✅ Fair valuation (PE {pe:.1f})")
        elif pe and pe > 40:
            bearish_signals.append(f"❌ Expensive valuation (PE {pe:.1f}) - high risk")
        elif pe and pe < 15:
            bullish_signals.append(f"✅ Cheap valuation (PE {pe:.1f})")
        
        if growth and growth > 0.15:
            bullish_signals.append(f"✅ Strong growth ({growth*100:.1f}% YoY)")
        elif growth and growth < -0.05:
            bearish_signals.append(f"❌ Negative growth ({growth*100:.1f}%)")
    
    # Decision Logic
    bullish_count = len(bullish_signals)
    bearish_count = len(bearish_signals)
    
    if bullish_count >= 5 and bearish_count == 0:
        recommendation = "🟢 STRONG BUY"
        action = "BUY NOW"
        explanation = f"All technical indicators are bullish. {bullish_count} bullish signals with no bearish concerns."
    elif bullish_count >= 3:
        recommendation = "🟡 BUY"
        action = "BUY ON DIPS"
        explanation = f"Multiple bullish signals ({bullish_count}) indicate upward potential. Wait for pullback to SMA20 for better entry."
    elif bullish_count > bearish_count:
        recommendation = "🟠 HOLD / ACCUMULATE ON DIPS"
        action = "WAIT FOR PULLBACK"
        explanation = f"More bullish ({bullish_count}) than bearish ({bearish_count}) signals. Good entry point on dips."
    elif bearish_count >= 3 and bullish_count <= 1:
        recommendation = "🔴 STRONG SELL / AVOID"
        action = "DO NOT BUY"
        explanation = f"Multiple bearish signals ({bearish_count}) indicate downside risk. Avoid until reversal confirmed."
    elif bearish_count > bullish_count:
        recommendation = "🔴 SELL / EXIT"
        action = "SELL ON RALLIES"
        explanation = f"More bearish ({bearish_count}) than bullish ({bullish_count}) signals. Exit or avoid until recovery."
    else:
        recommendation = "➖ HOLD / WAIT"
        action = "WAIT FOR CLARITY"
        explanation = "Mixed signals. Wait for clearer direction before entering."
    
    return {
        'Recommendation': recommendation,
        'Action': action,
        'Main Explanation': explanation,
        'Bullish Signals': bullish_signals,
        'Bearish Signals': bearish_signals,
        'Neutral Signals': neutral_signals,
        'Bullish Count': bullish_count,
        'Bearish Count': bearish_count
    }


def get_nifty50_by_sector() -> dict:
    """
    Get Nifty 50 stocks organized by sector
    
    Returns:
        Dict mapping sector names to list of stocks
    """
    nifty50_by_sector = {
        'Banking': [
            'HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'AXISBANK.NS', 'KOTAKBANK.NS', 'IDFCFIRSTB.NS'
        ],
        'IT': [
            'TCS.NS', 'INFY.NS', 'WIPRO.NS', 'LTIM.NS', 'HCLTECH.NS', 'TECHM.NS', 'PERSISTENT.NS'
        ],
        'Energy': [
            'RELIANCE.NS', 'POWERGRID.NS', 'NTPC.NS', 'BPCL.NS', 'GAIL.NS', 'IGL.NS', 'TATAPOWER.NS'
        ],
        'Pharma': [
            'SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'ABBOTINDIA.NS'
        ],
        'Auto': [
            'MARUTI.NS', 'BAJAJ-AUTO.NS', 'TATAMOTORS.NS', 'EICHERMOT.NS', 'HEROMOTOCORP.NS', 'M&MFIN.NS'
        ],
        'Metals': [
            'HINDALCO.NS', 'JSWSTEEL.NS', 'TATASTEEL.NS', 'VEDL.NS', 'NMDC.NS'
        ],
        'Cement': [
            'ULTRACEMCO.NS', 'SHREECEM.NS', 'AMBUJACEM.NS', 'ACC.NS', 'DALBHARAT.NS',
            'RAMCOCEM.NS', 'JKCEMENT.NS', 'JKLAKSHMI.NS', 'BIRLACEM.NS', 'PRSMJOHNSN.NS'
        ],
        'FMCG': [
            'NESTLEIND.NS', 'BRITANNIA.NS', 'VBL.NS', 'TATACONSUM.NS', 'HINDUNILVR.NS', 'ITC.NS'
        ],
        'Infra': [
            'LT.NS', 'ADANIGREEN.NS', 'ADANIENT.NS'
        ],
        'Telecom': [
            'BHARTIARTL.NS'
        ],
        'Financials': [
            'BAJAJFINSV.NS', 'HDFC.NS', 'SBICARD.NS', 'SBILIFE.NS', 'MUTHOOTFIN.NS', 'CHOLAFIN.NS'
        ],
        'Consumer': [
            'ASIANPAINT.NS', 'TITAN.NS', 'INDIGO.NS'
        ]
    }
    return nifty50_by_sector


def get_sector_stocks_from_universe(sector: str = None, universe_size: int = 100) -> list:
    """
    Get stocks for a specific sector from a larger universe beyond Nifty 50

    Args:
        sector: Sector name (if None, returns all sectors)
        universe_size: Maximum number of stocks per sector

    Returns:
        List of stock symbols for the sector
    """
    # Try to get from stock_universe module directly
    try:
        # Use the comprehensive sector mapping
        stocks = stock_universe.get_stock_universe_by_sector(sector, universe_size)
        if stocks:
            return stocks
    except Exception as e:
        print(f"Note: Using fallback method. {e}")

    # Try to get by exact sector name
    try:
        stocks = stock_universe.get_stocks_by_sector(sector, universe_size)
        if stocks:
            return stocks
    except Exception:
        pass

    # Final fallback to Nifty 50 by sector
    nifty50 = get_nifty50_by_sector()
    return nifty50.get(sector, [])



def get_all_available_sectors() -> list:
    """
    Get list of all available sectors from the comprehensive database

    Returns:
        List of sector names
    """
    try:
        return stock_universe.get_all_sectors()
    except:
        return list(get_nifty50_by_sector().keys())


def get_all_nifty50() -> list:
    """
    Get flat list of all Nifty 50 stocks
    
    Returns:
        List of all stock symbols
    """
    sector_dict = get_nifty50_by_sector()
    all_stocks = []
    for stocks in sector_dict.values():
        all_stocks.extend(stocks)
    return list(set(all_stocks))  # Remove duplicates


def get_nifty_top_n(n: int = 400) -> list:
    """
    Get top N stocks from comprehensive database across all sectors

    Args:
        n: Number of stocks to return (default 400)

    Returns:
        List of stock symbols from all sectors up to n stocks
    """
    # First try to load from CSV file
    candidates = ["nifty_top_400.csv", "stock_universe.csv", os.path.join("data", "nifty_top_400.csv"), os.path.join("data", "stock_universe.csv")]
    for path in candidates:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                if 'Symbol' in df.columns:
                    symbols = df['Symbol'].astype(str).str.strip().tolist()
                else:
                    symbols = df.iloc[:, 0].astype(str).str.strip().tolist()
                # Return up to n symbols
                return [s for s in symbols if s][:n]
            except Exception:
                continue

    # Use comprehensive stock database from stock_universe module
    try:
        all_stocks = []
        sector_dict = stock_universe.get_indian_stocks_by_sector()
        for sector_name, stocks in sector_dict.items():
            all_stocks.extend(stocks)

        # Remove duplicates and return up to n stocks
        unique_stocks = list(set(all_stocks))
        return unique_stocks[:n]
    except Exception as e:
        print(f"Error loading from stock_universe: {e}")
        # Final fallback to Nifty 50 only if all else fails
        return get_all_nifty50()[:n]

