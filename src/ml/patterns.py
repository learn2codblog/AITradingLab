"""
Pattern Recognition Module for TradeGenius AI
==============================================
Includes:
- Candlestick Pattern Detection
- Chart Pattern Recognition
- Trend Analysis
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


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