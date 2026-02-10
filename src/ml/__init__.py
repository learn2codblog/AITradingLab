"""
ML Modules Package for TradeGenius AI
=====================================
Modular ML components for trading analysis and prediction.

This package contains specialized modules for:
- Technical indicators and trend analysis
- Pattern recognition (candlestick and chart patterns)
- LSTM deep learning for price prediction
- Sentiment analysis from news and text
- Ensemble ML models for prediction aggregation
- Volatility forecasting and regime detection
- Risk management and position sizing
- Anomaly detection for market alerts
- Market regime detection and comprehensive analysis
- Transformer-based forecasting

All modules are designed for lazy loading to optimize memory usage.
"""

from .indicators import *
from .patterns import *
from .lstm import *
from .sentiment import *
from .ensemble import *
from .volatility import *
from .risk import *
from .anomaly import *
from .market_analysis import *

__all__ = [
    # Indicators
    'calculate_advanced_indicators',
    'calculate_atr',
    'calculate_supertrend',
    'calculate_adx',
    'calculate_psar',
    'combined_trend_signal',

    # Patterns
    'detect_candlestick_patterns',
    'detect_chart_patterns',

    # LSTM
    'prepare_lstm_data',
    'build_lstm_model',
    'prepare_lstm_features',
    'predict_with_lstm',

    # Sentiment
    'analyze_sentiment_simple',
    'analyze_sentiment_transformer',
    'analyze_sentiment_batch',
    'analyze_news_sentiment',

    # Ensemble
    'create_ensemble_prediction',

    # Volatility
    'forecast_volatility_garch',
    'get_volatility_regime',

    # Risk
    'calculate_position_size',
    'backtest_strategy',
    'calculate_feature_importance',

    # Anomaly
    'detect_anomalies_autoencoder',
    'detect_anomalies',

    # Market Analysis
    'detect_market_regime',
    'calculate_technical_score',
    'generate_ai_recommendation',
    'generate_ai_analysis',
    'get_positional_encoding',
    'build_transformer_model',
    'predict_with_transformer'
]

__version__ = "2.1.0"