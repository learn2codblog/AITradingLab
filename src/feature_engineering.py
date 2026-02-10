"""
Feature Engineering Module for TradeGenius AI
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif


def engineer_advanced_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer advanced features for ML models

    Args:
        df: DataFrame with OHLCV and indicators

    Returns:
        DataFrame with additional features
    """
    df = df.copy()

    # ─── PRICE FEATURES ───
    df['Price_Range'] = df['High'] - df['Low']
    df['Price_Range_Pct'] = df['Price_Range'] / df['Close'] * 100
    df['Upper_Shadow'] = df['High'] - df[['Open', 'Close']].max(axis=1)
    df['Lower_Shadow'] = df[['Open', 'Close']].min(axis=1) - df['Low']
    df['Body'] = abs(df['Close'] - df['Open'])
    df['Body_Pct'] = df['Body'] / df['Close'] * 100

    # ─── RETURN FEATURES ───
    for period in [1, 2, 3, 5, 10, 20]:
        df[f'Return_{period}d'] = df['Close'].pct_change(periods=period)

    # ─── VOLATILITY FEATURES ───
    df['Volatility_5d'] = df['Daily_Return'].rolling(5).std() if 'Daily_Return' in df.columns else df['Close'].pct_change().rolling(5).std()
    df['Volatility_10d'] = df['Daily_Return'].rolling(10).std() if 'Daily_Return' in df.columns else df['Close'].pct_change().rolling(10).std()
    df['Volatility_20d'] = df['Daily_Return'].rolling(20).std() if 'Daily_Return' in df.columns else df['Close'].pct_change().rolling(20).std()

    # Annualized volatility
    df['Volatility_Annual'] = df['Volatility_20d'] * np.sqrt(252) if 'Volatility_20d' in df.columns else 0

    # ─── MOVING AVERAGE FEATURES ───
    if 'SMA20' in df.columns:
        df['Distance_SMA20'] = (df['Close'] - df['SMA20']) / df['SMA20'] * 100
    if 'SMA50' in df.columns:
        df['Distance_SMA50'] = (df['Close'] - df['SMA50']) / df['SMA50'] * 100
    if 'SMA200' in df.columns:
        df['Distance_SMA200'] = (df['Close'] - df['SMA200']) / df['SMA200'] * 100

    # ─── CROSSOVER FEATURES ───
    if 'SMA20' in df.columns and 'SMA50' in df.columns:
        df['SMA20_Above_SMA50'] = (df['SMA20'] > df['SMA50']).astype(int)
    if 'SMA50' in df.columns and 'SMA200' in df.columns:
        df['SMA50_Above_SMA200'] = (df['SMA50'] > df['SMA200']).astype(int)
    if 'EMA12' in df.columns and 'EMA26' in df.columns:
        df['EMA12_Above_EMA26'] = (df['EMA12'] > df['EMA26']).astype(int)

    # ─── MOMENTUM FEATURES ───
    if 'RSI14' in df.columns:
        df['RSI_Overbought'] = (df['RSI14'] > 70).astype(int)
        df['RSI_Oversold'] = (df['RSI14'] < 30).astype(int)
        df['RSI_Change'] = df['RSI14'].diff()

    if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
        df['MACD_Above_Signal'] = (df['MACD'] > df['MACD_Signal']).astype(int)
        df['MACD_Positive'] = (df['MACD'] > 0).astype(int)

    # ─── BOLLINGER BAND FEATURES ───
    if 'BB_Upper' in df.columns and 'BB_Lower' in df.columns:
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        df['Above_BB_Upper'] = (df['Close'] > df['BB_Upper']).astype(int)
        df['Below_BB_Lower'] = (df['Close'] < df['BB_Lower']).astype(int)

    # ─── VOLUME FEATURES ───
    df['Volume_Change'] = df['Volume'].pct_change()
    df['Volume_MA5'] = df['Volume'].rolling(5).mean()
    df['Volume_MA20'] = df['Volume'].rolling(20).mean()
    df['Volume_Ratio_5_20'] = df['Volume_MA5'] / df['Volume_MA20']

    # ─── HIGH/LOW FEATURES ───
    df['Days_Since_High_20'] = df['High'].rolling(20).apply(lambda x: 20 - x.argmax() - 1, raw=True)
    df['Days_Since_Low_20'] = df['Low'].rolling(20).apply(lambda x: 20 - x.argmin() - 1, raw=True)

    df['Dist_From_High_20'] = (df['High'].rolling(20).max() - df['Close']) / df['Close'] * 100
    df['Dist_From_Low_20'] = (df['Close'] - df['Low'].rolling(20).min()) / df['Close'] * 100

    # ─── TREND FEATURES ───
    df['Higher_High'] = (df['High'] > df['High'].shift(1)).astype(int)
    df['Higher_Low'] = (df['Low'] > df['Low'].shift(1)).astype(int)
    df['Lower_High'] = (df['High'] < df['High'].shift(1)).astype(int)
    df['Lower_Low'] = (df['Low'] < df['Low'].shift(1)).astype(int)

    # Trend score (price action based: higher highs/lows pattern)
    # Named differently from advanced_ai.py's SMA-based Trend_Score to avoid conflicts
    df['PA_Trend_Score'] = df['Higher_High'] + df['Higher_Low'] - df['Lower_High'] - df['Lower_Low']
    df['PA_Trend_Score_5d'] = df['PA_Trend_Score'].rolling(5).sum()

    # ─── TARGET VARIABLE ───
    # NOTE: Target variables use future data (shift(-1), shift(-5)) and MUST NOT be used as features.
    # They are created here solely for model training labels.
    # The dropna() in prepare_ml_data removes the last row(s) where target is NaN,
    # preventing look-ahead bias during training.
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    df['Target_5d'] = (df['Close'].shift(-5) > df['Close']).astype(int)

    return df


def select_best_features(df: pd.DataFrame, target_col: str = 'Target', k: int = 20) -> list:
    """
    Select best features using statistical tests

    Args:
        df: DataFrame with features
        target_col: Target column name
        k: Number of features to select

    Returns:
        List of selected feature names
    """
    # Drop non-numeric and target columns
    exclude_cols = [target_col, 'Target', 'Target_5d', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    feature_cols = [col for col in df.columns if col not in exclude_cols and df[col].dtype in ['float64', 'int64']]

    # Prepare data
    df_clean = df[feature_cols + [target_col]].dropna()

    if len(df_clean) < 100:
        return feature_cols[:k]

    X = df_clean[feature_cols]
    y = df_clean[target_col]

    # Handle infinite values
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.mean())

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Select best features
    k = min(k, len(feature_cols))
    selector = SelectKBest(score_func=f_classif, k=k)

    try:
        selector.fit(X_scaled, y)
        selected_indices = selector.get_support(indices=True)
        selected_features = [feature_cols[i] for i in selected_indices]
        return selected_features
    except Exception as e:
        print(f"Feature selection error: {e}")
        return feature_cols[:k]


def prepare_ml_data(df: pd.DataFrame, target_col: str = 'Target', test_size: float = 0.2):
    """
    Prepare data for ML training

    Args:
        df: DataFrame with features
        target_col: Target column name
        test_size: Fraction of data for testing

    Returns:
        X_train, X_test, y_train, y_test, feature_names
    """
    from sklearn.model_selection import train_test_split

    # Get feature columns
    exclude_cols = [target_col, 'Target', 'Target_5d', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume',
                   'Dividends', 'Stock_Splits']
    feature_cols = [col for col in df.columns if col not in exclude_cols and df[col].dtype in ['float64', 'int64']]

    # Clean data
    df_clean = df[feature_cols + [target_col]].dropna()

    if len(df_clean) < 50:
        return None, None, None, None, []

    X = df_clean[feature_cols]
    y = df_clean[target_col]

    # Handle infinite values
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.mean())

    # Split data (time-series aware - no shuffle)
    split_idx = int(len(X) * (1 - test_size))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, X_test_scaled, y_train.values, y_test.values, feature_cols

