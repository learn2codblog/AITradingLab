# Quick Reference: Module Structure

## File Organization

```
AI_Trading_Lab_PRO+/
│
├── data_loader.py                    # Market Data Infrastructure
│   └── load_stock_data()             # Download OHLCV data
│
├── fundamental_analysis.py           # Company Valuation & Health
│   ├── get_fundamentals()            # P/E, ROE, margins, growth
│   ├── get_news_sentiment()          # Market sentiment from news
│   ├── get_analyst_ratings()         # Target prices & consensus
│   └── get_quality_metrics()         # Operational efficiency metrics
│
├── technical_indicators.py           # Price & Volume Patterns
│   └── calculate_technical_indicators()
│       ├── Trend: SMA, EMA, MACD, ADX, CCI
│       ├── Momentum: RSI, Stochastic
│       ├── Volatility: ATR, Vol_5d, Vol_20d
│       ├── Volume: OBV, Volume_Ratio
│       └── Returns: Ret_1d, Ret_5d, Ret_20d
│
├── models.py                         # ML/DL Prediction
│   ├── train_random_forest()
│   ├── train_xgboost()
│   └── build_lstm_model()
│
├── metrics.py                        # Performance Evaluation
│   ├── sharpe_ratio()
│   ├── max_drawdown()
│   ├── sortino_ratio()
│   └── backtest_strategy()
│
├── portfolio_optimizer.py            # Asset Allocation
│   └── optimize_portfolio()
│
└── app.py                            # Main Streamlit Application
    └── Integrates all modules
```

## Import Guide

### In your Python scripts, use:

```python
# Data Loading
from data_loader import load_stock_data

# Fundamental Analysis
from fundamental_analysis import (
    get_fundamentals,
    get_news_sentiment,
    get_analyst_ratings,
    get_quality_metrics
)

# Technical Analysis
from technical_indicators import calculate_technical_indicators

# Models & Metrics
from models import train_random_forest, train_xgboost, build_lstm_model
from metrics import sharpe_ratio, max_drawdown, backtest_strategy
from portfolio_optimizer import optimize_portfolio
```

## Indicator Count

| Category | Count | Examples |
|----------|-------|----------|
| **Trend** | 5 | SMA5/20/50/200, EMA12/26, MACD, ADX, CCI |
| **Momentum** | 5 | RSI7/14/28, Stoch_K, Stoch_D |
| **Volatility** | 3 | ATR, Vol_5d, Vol_20d |
| **Volume** | 3 | OBV, Volume_MA20, Volume_Ratio |
| **Returns** | 3 | Ret_1d, Ret_5d, Ret_20d |
| **Fundamental** | 12+ | ROE, P/E, Margins, Growth, Beta, Debt ratios... |
| **Total** | 31+ | Combined indicators for feature engineering |

## Single-Indicator Explanations

### Key Technical Indicators:

**RSI (14)**: 0-100 scale
- <30: Oversold (potential buy)
- >70: Overbought (potential sell)

**MACD**: Moving average convergence
- Positive: Bullish trend
- Negative: Bearish trend
- Crossover: Trend change

**SMA200**: 200-day moving average
- Price above = Uptrend
- Price below = Downtrend

**ATR**: Volatility measure
- Higher = More volatile
- Use for stop-loss sizing

**Volume_Ratio**: Current vs average volume
- >1.0: Above average (stronger move)
- <1.0: Below average (weak move)

### Key Fundamental Metrics:

**P/E Ratio**: Price / Earnings
- <15: Undervalued
- >25: Overvalued
- Growth: Higher P/E acceptable

**ROE**: Net Income / Equity
- >15%: Excellent
- >10%: Good
- <5%: Poor

**Debt-to-Equity**: Financial leverage
- <0.5: Conservative
- 0.5-1.5: Moderate
- >2.0: Risky

**Revenue Growth**: YoY expansion
- >20%: Strong growth
- 10-20%: Good growth
- <5%: Slow growth

## Filter Features Before ML

**Remove columns:** Open, High, Low, Close, Volume, Target, Future_Ret

**Use columns:** All SMA, EMA, RSI, ATR, OBV, Vol, Ret, ROE, P/E, Beta, etc.

Example in code:
```python
features = [col for col in stock.columns 
            if col not in ['Open', 'High', 'Low', 'Close', 
                          'Volume', 'Target', 'Future_Ret']]
X = stock[features]
y = stock['Target']
```
