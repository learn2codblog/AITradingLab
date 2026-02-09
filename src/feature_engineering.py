# feature_engineering.py
"""
Advanced Feature Engineering Module
Creates comprehensive features combining technical, fundamental, and derived metrics
"""

import pandas as pd
import numpy as np


def engineer_advanced_features(stock: pd.DataFrame, fundamentals: dict = None, index_data: pd.DataFrame = None) -> pd.DataFrame:
    """
    Create advanced features for machine learning models
    
    Feature Categories:
    1. TREND STRENGTH FEATURES
    2. MOMENTUM FEATURES  
    3. VOLATILITY & RISK FEATURES
    4. VOLUME FEATURES
    5. PRICE PATTERN FEATURES
    6. MOVING AVERAGE FEATURES
    7. FUNDAMENTAL RATIO FEATURES
    8. RELATIVE STRENGTH FEATURES
    9. LAGGED FEATURES
    10. INTERACTION FEATURES
    
    Args:
        stock: DataFrame with technical indicators already calculated
        fundamentals: Dict with fundamental metrics
        index_data: Index data for relative calculations
        
    Returns:
        DataFrame with all engineered features
    """
    
    stock = stock.copy()
    
    # ════════════════════════════════════════════════════════════════
    # 1. TREND STRENGTH FEATURES
    # ════════════════════════════════════════════════════════════════
    
    # Moving Average Positions
    stock['Price_vs_SMA5'] = stock['Close'] / stock['SMA5'] - 1
    stock['Price_vs_SMA20'] = stock['Close'] / stock['SMA20'] - 1
    stock['Price_vs_SMA50'] = stock['Close'] / stock['SMA50'] - 1
    stock['Price_vs_SMA200'] = stock['Close'] / stock['SMA200'] - 1
    
    # SMA Position Hierarchy
    stock['SMA_Cross_5_20'] = (stock['SMA5'] > stock['SMA20']).astype(int)
    stock['SMA_Cross_20_50'] = (stock['SMA20'] > stock['SMA50']).astype(int)
    stock['SMA_Cross_50_200'] = (stock['SMA50'] > stock['SMA200']).astype(int)
    stock['Bullish_SMA'] = (stock['SMA5'] > stock['SMA20']) & (stock['SMA20'] > stock['SMA50']) & (stock['SMA50'] > stock['SMA200'])
    stock['Bullish_SMA'] = stock['Bullish_SMA'].astype(int)
    
    # EMA Positioning
    stock['EMA_Cross_12_26'] = (stock['EMA12'] > stock['EMA26']).astype(int)
    stock['Price_vs_EMA12'] = stock['Close'] / stock['EMA12'] - 1
    
    # Distance from moving averages (normalized)
    stock['Dist_Avg_MA'] = (
        (stock['Price_vs_SMA5'] + stock['Price_vs_SMA20'] + stock['Price_vs_SMA50']) / 3
    )
    
    # ════════════════════════════════════════════════════════════════
    # 2. MOMENTUM COMPOSITE FEATURES
    # ════════════════════════════════════════════════════════════════
    
    # RSI Composite Score
    stock['RSI_Avg'] = (stock['RSI7'] + stock['RSI14'] + stock['RSI28']) / 3
    stock['RSI_Extreme'] = (stock['RSI14'] < 30).astype(int) | (stock['RSI14'] > 70).astype(int)
    stock['RSI_Bullish'] = (stock['RSI14'] > 50).astype(int)
    
    # Stochastic Positioning
    stock['Stoch_Avg'] = (stock['Stoch_K'] + stock['Stoch_D']) / 2
    stock['Stoch_Bullish'] = (stock['Stoch_K'] > stock['Stoch_D']).astype(int)
    stock['Stoch_Extreme'] = (stock['Stoch_K'] < 20).astype(int) | (stock['Stoch_K'] > 80).astype(int)
    
    # MACD Features
    stock['MACD_Positive'] = (stock['MACD'] > 0).astype(int)
    stock['MACD_Trend'] = stock['MACD'].rolling(5).mean()
    
    # ADX Strength
    stock['ADX_Bullish'] = (stock['ADX'] > 25).astype(int)
    stock['ADX_Strong'] = (stock['ADX'] > 40).astype(int)
    
    # Composite Momentum Score
    stock['Momentum_Score'] = (
        stock['RSI_Bullish'] * 1.0 +
        stock['Stoch_Bullish'] * 0.8 +
        stock['MACD_Positive'] * 0.8 +
        stock['EMA_Cross_12_26'] * 0.6
    )
    
    # ════════════════════════════════════════════════════════════════
    # 3. VOLATILITY & RISK FEATURES
    # ════════════════════════════════════════════════════════════════
    
    # Volatility Ratios
    stock['Vol_Ratio_20_5'] = stock['Vol_20d'] / (stock['Vol_5d'] + 1e-8)
    stock['Vol_Trend'] = stock['Vol_5d'].rolling(10).mean()
    stock['Vol_Increase'] = stock['Vol_5d'] > stock['Vol_20d']
    stock['Vol_Increase'] = stock['Vol_Increase'].astype(int)
    
    # ATR Positioning
    stock['ATR_Ratio'] = stock['ATR'] / stock['Close']
    stock['High_Low_Ratio'] = (stock['High'] - stock['Low']) / stock['Close']
    
    # Price Spread
    stock['Close_Position'] = (stock['Close'] - stock['Low']) / (stock['High'] - stock['Low'] + 1e-8)
    
    # ════════════════════════════════════════════════════════════════
    # 4. VOLUME FEATURES
    # ════════════════════════════════════════════════════════════════
    
    # Volume Intensity
    stock['Volume_Intensity'] = stock['Volume_Ratio'] - 1  # 0 = average, 1 = double average
    stock['OBV_Trend'] = stock['OBV'].rolling(10).mean()
    stock['OBV_Increasing'] = (stock['OBV'] > stock['OBV'].rolling(10).mean()).astype(int)
    
    # Volume & Price Correlation
    stock['Vol_Price_Surge'] = (stock['Volume_Ratio'] > 1.5) & (stock['Ret_1d'] > 0)
    stock['Vol_Price_Surge'] = stock['Vol_Price_Surge'].astype(int)
    
    # ════════════════════════════════════════════════════════════════
    # 5. PRICE PATTERN FEATURES
    # ════════════════════════════════════════════════════════════════
    
    # Consecutive Up/Down Days
    stock['Daily_Direction'] = (stock['Ret_1d'] > 0).astype(int)
    stock['Consecutive_Ups'] = stock['Daily_Direction'].rolling(5).sum()
    stock['Consecutive_Downs'] = (1 - stock['Daily_Direction']).rolling(5).sum()
    
    # Reversal Patterns
    stock['Gap_Up'] = (stock['Open'] > stock['Close'].shift(1)).astype(int)
    stock['Gap_Down'] = (stock['Open'] < stock['Close'].shift(1)).astype(int)
    
    # Volatility Breakout
    stock['Range_Expansion'] = stock['High_Low_Ratio'] > stock['High_Low_Ratio'].rolling(20).mean()
    stock['Range_Expansion'] = stock['Range_Expansion'].astype(int)
    
    # ════════════════════════════════════════════════════════════════
    # 6. RETURN STATISTICS FEATURES
    # ════════════════════════════════════════════════════════════════
    
    # Multi-period Returns
    stock['Ret_2d'] = stock['Close'].pct_change(2)
    stock['Ret_10d'] = stock['Close'].pct_change(10)
    
    # Return Acceleration
    stock['Ret_Acceleration'] = stock['Ret_5d'] - stock['Ret_5d'].shift(5)
    
    # Volatility of Returns
    stock['Ret_Std_10d'] = stock['Ret_1d'].rolling(10).std()
    stock['Ret_Std_20d'] = stock['Ret_1d'].rolling(20).std()
    
    # ════════════════════════════════════════════════════════════════
    # 7. CORRELATION & RELATIVE FEATURES (if index data provided)
    # ════════════════════════════════════════════════════════════════
    
    if index_data is not None:
        # Ensure index data is aligned
        index_data = index_data.reindex(stock.index).ffill()
        
        # Relative Strength
        stock['Rel_Strength'] = stock['Close'] / index_data['Close']
        stock['Rel_Strength_Trend'] = stock['Rel_Strength'].rolling(20).mean()
        stock['Outperforming'] = (stock['Rel_Strength'] > stock['Rel_Strength'].rolling(20).mean()).astype(int)
        
        # Correlation
        stock['Correlation_10d'] = stock['Ret_1d'].rolling(10).corr(index_data['Close'].pct_change())
        
        # Relative Volatility
        stock['Rel_Vol'] = stock['Vol_5d'] / index_data['Close'].pct_change().rolling(5).std()
        
        # Beta Rolling (already in app.py, adding smoothed version)
        stock['Beta_Rolling'] = stock['Close'].pct_change().rolling(252).cov(
            index_data['Close'].pct_change()
        ) / index_data['Close'].pct_change().rolling(252).var()
        stock['Beta_Smooth'] = stock['Beta_Rolling'].rolling(20).mean()
    
    # ════════════════════════════════════════════════════════════════
    # 8. FUNDAMENTAL FEATURES (if fundamentals provided)
    # ════════════════════════════════════════════════════════════════
    
    if fundamentals:
        # Create time-series features from static fundamentals
        # These will be constant across all rows but useful for screening
        
        roe = fundamentals.get('ROE', 0)
        pe = fundamentals.get('PE', 50)
        profit_margin = fundamentals.get('ProfitMargin', 0)
        revenue_growth = fundamentals.get('RevenueGrowth', 0)
        eps_growth = fundamentals.get('EPSGrowth', 0)
        beta = fundamentals.get('Beta', 1.0)
        div_yield = fundamentals.get('DividendYield', 0)
        
        # Fundamental Quality Score
        stock['Fund_ROE_Score'] = min(max(roe / 0.20, 0), 2)  # 0-2 scale
        stock['Fund_Growth_Score'] = min(max((revenue_growth + eps_growth) / 0.40, 0), 2)
        stock['Fund_Margin_Score'] = min(max(profit_margin / 0.20, 0), 2)
        
        # Valuation Score (inverse of P/E)
        stock['Fund_PE_Score'] = 3 - min(max(pe / 25, 0), 2)  # Higher = cheaper
        
        # Risk Profile
        stock['Fund_Beta_Score'] = 2 - min(max(abs(beta - 1.0) / 0.5, 0), 1)
        stock['Fund_Risk_Score'] = stock['Fund_Beta_Score'] + stock['Vol_5d'].rolling(20).mean() * 5
        
        # Composite Fundamental Score
        stock['Fundamental_Score'] = (
            stock['Fund_ROE_Score'] * 0.30 +
            stock['Fund_Growth_Score'] * 0.30 +
            stock['Fund_Margin_Score'] * 0.20 +
            stock['Fund_PE_Score'] * 0.15 +
            stock['Fund_Beta_Score'] * 0.05
        )
    
    # ════════════════════════════════════════════════════════════════
    # 9. LAGGED FEATURES (for temporal patterns)
    # ════════════════════════════════════════════════════════════════
    
    # Lagged RSI
    for lag in [1, 2, 3]:
        stock[f'RSI14_Lag{lag}'] = stock['RSI14'].shift(lag)
    
    # Lagged Returns
    for lag in [1, 2, 5]:
        stock[f'Ret_Lag{lag}'] = stock['Ret_1d'].shift(lag)
    
    # Lagged Volume Ratio
    for lag in [1, 2]:
        stock[f'Volume_Ratio_Lag{lag}'] = stock['Volume_Ratio'].shift(lag)
    
    # ════════════════════════════════════════════════════════════════
    # 10. INTERACTION FEATURES
    # ════════════════════════════════════════════════════════════════
    
    # Trend × Momentum
    stock['Trend_Momentum'] = stock['Bullish_SMA'] * stock['Momentum_Score']
    
    # Volume × Volatility
    stock['Vol_Vol_Signal'] = stock['Volume_Intensity'] * stock['Vol_5d']
    
    # Price Position × RSI
    stock['Price_RSI_Signal'] = stock['Close_Position'] * (stock['RSI14'] / 100)
    
    # ════════════════════════════════════════════════════════════════
    return stock


def get_feature_importance_groups() -> dict:
    """
    Categorize features by type for analysis and interpretation
    
    Returns:
        Dict mapping feature categories to feature lists
    """
    return {
        "Trend": [
            'SMA5', 'SMA20', 'SMA50', 'SMA200',
            'Price_vs_SMA5', 'Price_vs_SMA20', 'Price_vs_SMA50', 'Price_vs_SMA200',
            'SMA_Cross_5_20', 'SMA_Cross_20_50', 'SMA_Cross_50_200',
            'Bullish_SMA', 'EMA_Cross_12_26', 'Dist_Avg_MA'
        ],
        "Momentum": [
            'RSI7', 'RSI14', 'RSI28', 'RSI_Avg', 'RSI_Bullish', 'RSI_Extreme',
            'Stoch_K', 'Stoch_D', 'Stoch_Avg', 'Stoch_Bullish',
            'MACD', 'MACD_Positive', 'ADX', 'CCI',
            'Momentum_Score'
        ],
        "Volatility": [
            'Vol_5d', 'Vol_20d', 'Vol_Ratio_20_5', 'Vol_Trend', 'Vol_Increase',
            'ATR', 'ATR_Ratio', 'High_Low_Ratio', 'Close_Position',
            'Ret_Std_10d', 'Ret_Std_20d'
        ],
        "Volume": [
            'Volume', 'Volume_MA20', 'Volume_Ratio', 'Volume_Intensity',
            'OBV', 'OBV_Trend', 'OBV_Increasing', 'Vol_Price_Surge'
        ],
        "Patterns": [
            'Consecutive_Ups', 'Consecutive_Downs', 'Gap_Up', 'Gap_Down',
            'Range_Expansion', 'Daily_Direction'
        ],
        "Returns": [
            'Ret_1d', 'Ret_2d', 'Ret_5d', 'Ret_10d', 'Ret_20d',
            'Ret_Acceleration', 'Ret_Lag1', 'Ret_Lag2', 'Ret_Lag5'
        ],
        "Relative": [
            'Rel_Strength', 'Rel_Strength_Trend', 'Outperforming',
            'Correlation_10d', 'Rel_Vol', 'Beta_Rolling', 'Beta_Smooth'
        ],
        "Fundamental": [
            'Fund_ROE_Score', 'Fund_Growth_Score', 'Fund_Margin_Score',
            'Fund_PE_Score', 'Fund_Beta_Score', 'Fundamental_Score'
        ],
        "Lagged": [
            'RSI14_Lag1', 'RSI14_Lag2', 'RSI14_Lag3',
            'Volume_Ratio_Lag1', 'Volume_Ratio_Lag2'
        ],
        "Interaction": [
            'Trend_Momentum', 'Vol_Vol_Signal', 'Price_RSI_Signal'
        ]
    }


def select_best_features(feature_names: list, max_features: int = 50) -> list:
    """
    Select top features based on trading logic priority
    
    Args:
        feature_names: List of all available feature names
        max_features: Maximum number of features to return
        
    Returns:
        Prioritized list of features
    """
    
    # Priority order for trading signals
    priority_features = [
        # High Priority: Core signals
        'Bullish_SMA', 'SMA_Cross_5_20', 'SMA_Cross_20_50',
        'Momentum_Score', 'RSI14', 'MACD', 'ADX',
        'Volume_Intensity', 'Close_Position',
        
        # Medium Priority: Supporting signals
        'Price_vs_SMA20', 'Price_vs_SMA50',
        'Stoch_K', 'Stoch_D', 'EMA_Cross_12_26',
        'Vol_5d', 'ATR_Ratio', 'OBV_Increasing',
        'Outperforming', 'Ret_5d',
        
        # Lower Priority: Additional context
        'Price_vs_SMA5', 'RSI_Avg', 'Vol_20d',
        'Consecutive_Ups', 'Ret_Acceleration',
        'RSI14_Lag1', 'Ret_Lag1',
    ]
    
    # Filter for features that exist in the data
    selected = [f for f in priority_features if f in feature_names]
    
    # Add remaining features if needed
    remaining = [f for f in feature_names if f not in selected]
    selected.extend(remaining)
    
    return selected[:max_features]
