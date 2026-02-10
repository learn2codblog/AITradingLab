"""
Price Targets Module for TradeGenius AI
"""

import numpy as np
import pandas as pd


def calculate_entry_target_prices(df: pd.DataFrame, fundamentals: dict = None) -> dict:
    """
    Calculate entry, target, and stop-loss prices

    Args:
        df: DataFrame with OHLCV and indicators
        fundamentals: Fundamental data (optional)

    Returns:
        Dict with price levels and analysis
    """
    if len(df) < 20:
        return {
            'Current Price': df['Close'].iloc[-1] if len(df) > 0 else 0,
            'Entry Price': 0,
            'Target Price': 0,
            'Stop Loss': 0,
            'R/R Ratio': 0,
            'Confidence Score': 0,
            'Strength': 'Weak'
        }

    current_price = df['Close'].iloc[-1]

    # Calculate support and resistance
    recent = df.tail(20)
    support = recent['Low'].min()
    resistance = recent['High'].max()

    # ATR for volatility
    atr = df.get('ATR14', pd.Series([0])).iloc[-1]
    if atr == 0:
        high_low = df['High'] - df['Low']
        atr = high_low.tail(14).mean()

    # Trend analysis
    sma20 = df.get('SMA20', df['Close'].rolling(20).mean()).iloc[-1]
    sma50 = df.get('SMA50', df['Close'].rolling(50).mean()).iloc[-1]

    # RSI
    rsi = df.get('RSI14', pd.Series([50])).iloc[-1]

    # Determine bias
    bullish_score = 0
    bearish_score = 0

    if current_price > sma20:
        bullish_score += 1
    else:
        bearish_score += 1

    if current_price > sma50:
        bullish_score += 1
    else:
        bearish_score += 1

    if sma20 > sma50:
        bullish_score += 1
    else:
        bearish_score += 1

    # RSI interpretation: momentum-based, not contrarian
    # RSI < 30 means bearish momentum (oversold is a warning, not a buy signal by itself)
    # RSI > 70 means bullish momentum but overbought risk
    if rsi < 30:
        bearish_score += 0.5  # Oversold = bearish momentum (potential reversal needs confirmation)
    elif rsi > 70:
        bearish_score += 0.5  # Overbought = risk of pullback
    elif rsi > 50:
        bullish_score += 0.5  # Bullish momentum
    else:
        bearish_score += 0.5  # Bearish momentum

    # Fundamental overlay
    if fundamentals:
        pe = fundamentals.get('PE', 0)
        roe = fundamentals.get('ROE', 0)

        if pe and 0 < pe < 25:
            bullish_score += 1
        elif pe > 40:
            bearish_score += 1

        if roe and roe > 0.15:
            bullish_score += 1

    # Calculate prices based on bias
    is_bullish = bullish_score > bearish_score

    # Calculate the range to understand price context
    price_range = resistance - support
    atr_pct = (atr / current_price) * 100 if current_price > 0 else 2

    if is_bullish:
        # Entry: Look for a pullback entry - use a more meaningful discount
        # Entry should be between support and current price, favoring a dip
        pullback_discount = max(0.02, min(0.05, atr_pct / 100))  # 2-5% pullback based on volatility
        ideal_entry = current_price * (1 - pullback_discount)

        # Entry is the higher of support level or the ideal pullback entry
        # But NOT the same as current price - we want a meaningful entry point
        entry_price = max(support * 1.01, min(ideal_entry, current_price * 0.97))

        # If entry is too close to current price (within 0.5%), push it lower
        if abs(entry_price - current_price) / current_price < 0.005:
            entry_price = current_price * 0.975

        # Target based on resistance and ATR
        target_price = max(resistance * 1.02, current_price + 2.5 * atr)

        # Stop loss below support
        stop_loss = min(support * 0.97, entry_price - 2 * atr)
    else:
        # Bearish bias - entry should be at a slight premium (short entry) or wait
        # For long positions in bearish market, look for deeper discount
        pullback_discount = max(0.03, min(0.08, atr_pct / 100 * 1.5))  # Larger discount for bearish
        entry_price = current_price * (1 - pullback_discount)

        # Ensure entry is above support
        entry_price = max(support * 1.02, entry_price)

        # If still too close to current price
        if abs(entry_price - current_price) / current_price < 0.005:
            entry_price = current_price * 0.96

        # Lower target for bearish
        target_price = current_price + 1.5 * atr

        # Tighter stop for bearish
        stop_loss = entry_price - 1.5 * atr

    # Risk/Reward ratio
    risk = entry_price - stop_loss
    reward = target_price - entry_price

    if risk > 0:
        rr_ratio = reward / risk
    else:
        rr_ratio = 0

    # Confidence score
    total_signals = bullish_score + bearish_score
    if total_signals > 0:
        confidence = max(bullish_score, bearish_score) / total_signals
    else:
        confidence = 0.5

    # Adjust confidence based on R/R
    if rr_ratio >= 2:
        confidence *= 1.1
    elif rr_ratio < 1:
        confidence *= 0.8

    confidence = min(confidence, 0.95)

    # Strength
    if confidence >= 0.75 and rr_ratio >= 2:
        strength = 'Strong'
    elif confidence >= 0.6 and rr_ratio >= 1.5:
        strength = 'Moderate'
    else:
        strength = 'Weak'

    # Build confidence reasons
    confidence_reasons = []
    if current_price > sma20:
        confidence_reasons.append("✅ Price above SMA20 (short-term bullish)")
    else:
        confidence_reasons.append("❌ Price below SMA20 (short-term bearish)")

    if current_price > sma50:
        confidence_reasons.append("✅ Price above SMA50 (medium-term bullish)")
    else:
        confidence_reasons.append("❌ Price below SMA50 (medium-term bearish)")

    if sma20 > sma50:
        confidence_reasons.append("✅ SMA20 > SMA50 (golden cross zone)")
    else:
        confidence_reasons.append("❌ SMA20 < SMA50 (death cross zone)")

    if rsi < 30:
        confidence_reasons.append("✅ RSI oversold - potential bounce")
    elif rsi > 70:
        confidence_reasons.append("⚠️ RSI overbought - potential pullback")
    else:
        confidence_reasons.append(f"ℹ️ RSI at {rsi:.0f} - neutral zone")

    if rr_ratio >= 2:
        confidence_reasons.append(f"✅ Excellent R/R ratio: {rr_ratio:.1f}:1")
    elif rr_ratio >= 1.5:
        confidence_reasons.append(f"ℹ️ Good R/R ratio: {rr_ratio:.1f}:1")
    else:
        confidence_reasons.append(f"⚠️ Low R/R ratio: {rr_ratio:.1f}:1")

    confidence_reasons_text = "\n".join(confidence_reasons)

    return {
        'Current Price': round(current_price, 2),
        'Entry Price': round(entry_price, 2),
        'Target Price': round(target_price, 2),
        'Stop Loss': round(stop_loss, 2),
        'R/R Ratio': round(rr_ratio, 2),
        'Confidence Score': round(confidence, 2),
        'Strength': strength,
        'Bias': 'Bullish' if is_bullish else 'Bearish',
        'Support': round(support, 2),
        'Resistance': round(resistance, 2),
        'ATR': round(atr, 2),
        'Confidence Reasons': confidence_reasons_text
    }


def calculate_fibonacci_levels(df: pd.DataFrame, lookback: int = 100) -> dict:
    """
    Calculate Fibonacci retracement levels

    Args:
        df: DataFrame with OHLCV data
        lookback: Lookback period

    Returns:
        Dict with Fibonacci levels
    """
    recent = df.tail(lookback)

    high = recent['High'].max()
    low = recent['Low'].min()
    diff = high - low

    current_price = df['Close'].iloc[-1]

    # Fibonacci levels
    levels = {
        '0%': high,
        '23.6%': high - 0.236 * diff,
        '38.2%': high - 0.382 * diff,
        '50%': high - 0.5 * diff,
        '61.8%': high - 0.618 * diff,
        '78.6%': high - 0.786 * diff,
        '100%': low
    }

    # Extension levels
    extensions = {
        '-23.6%': high + 0.236 * diff,
        '-38.2%': high + 0.382 * diff,
        '-61.8%': high + 0.618 * diff
    }

    # Find nearest levels
    all_levels = {**levels, **extensions}
    nearest_support = None
    nearest_resistance = None

    for name, level in sorted(all_levels.items(), key=lambda x: x[1], reverse=True):
        if level < current_price and (nearest_support is None or level > nearest_support):
            nearest_support = level
            nearest_support_name = name
        elif level > current_price and (nearest_resistance is None or level < nearest_resistance):
            nearest_resistance = level
            nearest_resistance_name = name

    return {
        'levels': {k: round(v, 2) for k, v in levels.items()},
        'extensions': {k: round(v, 2) for k, v in extensions.items()},
        'current_price': round(current_price, 2),
        'nearest_support': round(nearest_support, 2) if nearest_support else None,
        'nearest_resistance': round(nearest_resistance, 2) if nearest_resistance else None,
        'swing_high': round(high, 2),
        'swing_low': round(low, 2)
    }


def calculate_pivot_points(df: pd.DataFrame) -> dict:
    """
    Calculate pivot points (standard method)

    Args:
        df: DataFrame with OHLCV data

    Returns:
        Dict with pivot levels
    """
    if len(df) < 2:
        return {}

    # Use previous day's data
    prev = df.iloc[-2]
    current_price = df['Close'].iloc[-1]

    high = prev['High']
    low = prev['Low']
    close = prev['Close']

    # Standard pivot point
    pivot = (high + low + close) / 3

    # Support and Resistance levels
    r1 = 2 * pivot - low
    s1 = 2 * pivot - high
    r2 = pivot + (high - low)
    s2 = pivot - (high - low)
    r3 = high + 2 * (pivot - low)
    s3 = low - 2 * (high - pivot)

    return {
        'Pivot': round(pivot, 2),
        'R1': round(r1, 2),
        'R2': round(r2, 2),
        'R3': round(r3, 2),
        'S1': round(s1, 2),
        'S2': round(s2, 2),
        'S3': round(s3, 2),
        'Current Price': round(current_price, 2)
    }

