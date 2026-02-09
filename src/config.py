"""
Configuration settings for AI Trading Lab
"""

# API Keys (Set these as environment variables)
ALPHA_VANTAGE_API_KEY = "your_alpha_vantage_key"
NEWS_API_KEY = "your_news_api_key"

# Data Settings
DEFAULT_START_DATE = "2020-01-01"
DEFAULT_TICKER = "RELIANCE.NS"
DEFAULT_BENCHMARK = "^NSEI"

# Model Settings
RANDOM_FOREST_PARAMS = {
    'n_estimators': 100,
    'max_depth': 10,
    'random_state': 42
}

XGBOOST_PARAMS = {
    'n_estimators': 100,
    'learning_rate': 0.1,
    'max_depth': 5,
    'random_state': 42
}

LSTM_PARAMS = {
    'units': 50,
    'dropout': 0.2,
    'epochs': 50,
    'batch_size': 32
}

# Feature Engineering
TECHNICAL_INDICATORS = [
    'SMA_20', 'SMA_50', 'EMA_12', 'EMA_26',
    'RSI', 'MACD', 'BB_upper', 'BB_lower',
    'Volume_SMA', 'ATR'
]

# Risk Management
MAX_POSITION_SIZE = 0.2  # 20% per position
STOP_LOSS_PCT = 0.05     # 5% stop loss
TAKE_PROFIT_PCT = 0.15   # 15% take profit

# Screening
CONFIDENCE_THRESHOLD = 0.6
MIN_VOLUME = 100000

# Portfolio Optimization
RISK_FREE_RATE = 0.05    # 5% annual risk-free rate
TARGET_RETURN = 0.15     # 15% target return

# UI Settings
PAGE_TITLE = "AI Trading Lab PRO+"
PAGE_ICON = "🚀"
LAYOUT = "wide"

