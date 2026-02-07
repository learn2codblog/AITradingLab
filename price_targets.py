# price_targets.py
"""
Entry/Target Price Calculation Module
Calculates buy price, target price, stop loss, and R/R ratio based on technical levels
"""

import pandas as pd
import numpy as np
import yfinance as yf


def calculate_support_resistance(stock: pd.DataFrame, lookback: int = 20) -> tuple:
    """
    Calculate support and resistance levels
    
    Args:
        stock: DataFrame with OHLCV data and technical indicators
        lookback: Number of periods to look back
    
    Returns:
        Tuple of (support, resistance)
    """
    latest = stock.iloc[-1]
    
    # Support = lowest low in lookback period
    support = stock['Low'].tail(lookback).min()
    
    # Resistance = highest high in lookback period
    resistance = stock['High'].tail(lookback).max()
    
    # Secondary support/resistance from moving averages
    sma50 = latest.get('SMA50', np.nan)
    sma200 = latest.get('SMA200', np.nan)
    
    return support, resistance, sma50, sma200


def calculate_entry_target_prices(stock: pd.DataFrame, fundamentals: dict = None) -> dict:
    """
    Calculate entry price, target price, and stop loss based on technical analysis
    
    Strategy:
    - Entry: Wait for pullback to support or SMA20 (not chase momentum)
    - Target: Recent resistance or 1.5-2x risk/reward
    - Stop Loss: Below recent support
    
    Args:
        stock: DataFrame with indicators and price data
        fundamentals: Dict with fundamental metrics for weighting
    
    Returns:
        Dict with entry, target, stop_loss, and confidence
    """
    
    latest = stock.iloc[-1]
    current_price = latest['Close']
    
    # Get technical levels
    support, resistance, sma50, sma200 = calculate_support_resistance(stock, lookback=20)
    
    # Entry Price Strategy
    # ─────────────────────
    # If price is above SMA50: Wait for pullback to SMA20 (or first support)
    # If price is below SMA50: Wait for break above SMA20
    
    sma20 = latest.get('SMA20', current_price)
    rsi14 = latest.get('RSI14', 50)
    
    # Entry price = pullback to key support level
    if current_price > sma50 and not pd.isna(sma50):
        # Price above 50-day MA: Enter on pullback to SMA20 or support
        entry_price = max(support, sma20 * 0.98)  # 2% below SMA20
    elif current_price < sma20:
        # Price below 20-day MA: Enter at support or just above SMA20
        entry_price = max(support, sma20 * 0.99)
    else:
        # Price around SMA20-50: Enter at support
        entry_price = support * 0.99
    
    # Target Price Strategy
    # ─────────────────────
    # Use resistance level or calculate based on R/R ratio
    
    # If current price near support: Target first resistance (2:1 R/R)
    # If current price near resistance: Take target at resistance
    
    if current_price > resistance:
        # Price has broken resistance: Target next resistance
        target_price = resistance * 1.05
    else:
        # Normal setup: Target = resistance or 2x risk
        risk = abs(current_price - entry_price)
        target_price = current_price + (risk * 2)  # 2:1 R/R
    
    # Ensure target is above current price
    if target_price <= current_price:
        target_price = current_price * 1.03  # At least 3% target
    
    # Stop Loss
    stop_loss = support * 0.99
    
    # Calculate Risk/Reward Ratio
    if entry_price > 0:
        risk_amount = entry_price - stop_loss
        reward_amount = target_price - entry_price
        if risk_amount > 0:
            rr_ratio = reward_amount / risk_amount
        else:
            rr_ratio = 0
    else:
        rr_ratio = 0
    
    # Confidence Score (how many indicators align)
    confidence_score = 0
    confidence_reasons = []
    
    # Technical Confidence
    if current_price > sma50 and not pd.isna(sma50):
        confidence_score += 0.2
        confidence_reasons.append("Price > SMA50")
    
    if current_price > sma20 and not pd.isna(sma20):
        confidence_score += 0.2
        confidence_reasons.append("Price > SMA20")
    
    if latest.get('EMA12', 0) > latest.get('EMA26', 0):
        confidence_score += 0.2
        confidence_reasons.append("EMA12 > EMA26")
    
    if latest.get('MACD', 0) > 0:
        confidence_score += 0.15
        confidence_reasons.append("MACD Positive")
    
    if 40 < rsi14 < 70:
        confidence_score += 0.15
        confidence_reasons.append("RSI in optimal range")
    elif rsi14 < 30:
        confidence_score += 0.1
        confidence_reasons.append("RSI oversold (reversal)")
    
    # Fundamental Confidence (if available)
    if fundamentals:
        roe = fundamentals.get('ROE', 0)
        pe = fundamentals.get('PE', 50)
        
        if roe and roe > 0.15:
            confidence_score += 0.1
            confidence_reasons.append("Good ROE")
        
        if pe and 15 < pe < 30:
            confidence_score += 0.1
            confidence_reasons.append("Reasonable PE")
    
    # Cap at 1.0
    confidence_score = min(confidence_score, 1.0)
    
    # Strength classification
    if confidence_score >= 0.75:
        strength = "🟢 STRONG BUY"
    elif confidence_score >= 0.60:
        strength = "🟡 BUY"
    elif confidence_score >= 0.45:
        strength = "🟠 WATCH"
    else:
        strength = "🔴 AVOID"
    
    return {
        'Current Price': round(current_price, 2),
        'Entry Price': round(entry_price, 2),
        'Target Price': round(target_price, 2),
        'Stop Loss': round(stop_loss, 2),
        'Risk Amount': round(entry_price - stop_loss, 2),
        'Reward Amount': round(target_price - entry_price, 2),
        'R/R Ratio': round(rr_ratio, 2),
        'Confidence Score': round(confidence_score, 2),
        'Strength': strength,
        'Support (20d)': round(support, 2),
        'Resistance (20d)': round(resistance, 2),
        'SMA20': round(sma20, 2),
        'SMA50': round(sma50, 2) if not pd.isna(sma50) else 'N/A',
        'SMA200': round(sma200, 2) if not pd.isna(sma200) else 'N/A',
        'RSI14': round(rsi14, 2),
        'Confidence Reasons': ', '.join(confidence_reasons)
    }


def get_nifty50_constituents() -> list:
    """
    Get list of Nifty 50 stocks
    
    Returns:
        List of stock symbols in .NS format
    """
    nifty50 = [
        'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS',
        'INFY.NS', 'BAJAJFINSV.NS', 'MARUTI.NS', 'BHARTIARTL.NS', 'WIPRO.NS',
        'POWERGRID.NS', 'AXISBANK.NS', 'LTIM.NS', 'SUNPHARMA.NS', 'HDFC.NS',
        'ASIANPAINT.NS', 'BAJAJ-AUTO.NS', 'ULTRACEMCO.NS', 'DRREDDY.NS', 'NESTLEIND.NS',
        'ADANIGREEN.NS', 'ADANIENT.NS', 'KOTAKBANK.NS', 'LT.NS', 'IDFCFIRSTB.NS',
        'JSWSTEEL.NS', 'BRITANNIA.NS', 'HINDALCO.NS', 'NTPC.NS', 'BPCL.NS',
        'GAIL.NS', 'VBL.NS', 'M&MFIN.NS', 'HCLTECH.NS', 'TATACONSUM.NS',
        'ABBOTINDIA.NS', 'TATAMOTORS.NS', 'EICHERMOT.NS', 'TATAPOWER.NS', 'TECHM.NS',
        'IGL.NS', 'SBICARD.NS', 'SBILIFE.NS', 'TITAN.NS', 'INDIGO.NS',
        'CIPLA.NS', 'MUTHOOTFIN.NS', 'HEROMOTOCORP.NS', 'CHOLAFIN.NS', 'PERSISTENT.NS'
    ]
    return nifty50


def screening_is_buy_signal(entry_targets: dict, current_price: float, margin: float = 0.02) -> bool:
    """
    Determine if stock is a buy based on entry criteria
    
    Buy if:
    - Confidence score >= 0.60
    - Current price is <= entry price (within margin for entry)
    
    Args:
        entry_targets: Dict from calculate_entry_target_prices()
        current_price: Current stock price
        margin: Margin above entry price to consider as "at entry"
    
    Returns:
        True if meets buy criteria
    """
    confidence = entry_targets.get('Confidence Score', 0)
    entry_price = entry_targets.get('Entry Price', 0)
    
    # Buy if decent confidence and price near entry
    if confidence >= 0.60 and current_price <= entry_price * (1 + margin):
        return True
    
    return False
