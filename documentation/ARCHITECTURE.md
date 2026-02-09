# Code Architecture: Fundamental vs Technical Analysis

## Overview
This document outlines the separation between Fundamental Analysis and Technical Analysis in the AI Trading Lab PRO+ system.

---

## 1. FUNDAMENTAL ANALYSIS (`fundamental_analysis.py`)

**Purpose:** Assess a company's intrinsic value and long-term health using financial metrics and market data.

**Key Functions:**

### `get_fundamentals(ticker: str) -> dict`
Retrieves core financial metrics:
- **ROE** (Return on Equity): Profitability relative to shareholders' equity
- **P/E Ratio**: Current valuation metric (Price-to-Earnings)
- **Profit Margin**: Net profit as % of revenue (profitability efficiency)
- **Revenue Growth**: Year-over-year growth rate (expansion)
- **Market Cap**: Total market value of the company
- **Sector**: Industry classification
- **Beta**: Volatility relative to market benchmark
- **EPS Growth**: Earnings per share growth rate
- **Dividend Yield**: Annual dividend as % of stock price
- **Debt-to-Equity Ratio**: Financial leverage measure
- **Current/Quick Ratios**: Short-term liquidity indicators

### `get_news_sentiment(ticker: str, num_news: int = 20) -> float`
Sentiment analysis of recent news articles:
- Keyword-based sentiment extraction
- Counts positive words (up, gain, growth, bull) vs negative words (down, loss, decline, bear)
- Returns average sentiment score across articles
- Use Case: Qualitative market perception gauge

### `get_analyst_ratings(ticker: str) -> dict`
Analyst consensus data:
- Target price estimates
- Number of analyst opinions
- Recommendation consensus (Buy/Hold/Sell)
- Use Case: Institutional expectations & price targets

### `get_quality_metrics(ticker: str) -> dict`
Financial health indicators:
- **ROA** (Return on Assets): Overall asset efficiency
- **Operating Margin**: Operational efficiency
- **Payout Ratio**: Dividend stability
- **Asset Turnover**: Revenue generation per asset dollar
- **Debt Ratio**: Overall leverage

---

## 2. TECHNICAL ANALYSIS (`technical_indicators.py`)

**Purpose:** Identify short-term price patterns and momentum using historical price and volume data.

**Key Function:**

### `calculate_technical_indicators(stock: pd.DataFrame) -> pd.DataFrame`

#### A. TREND INDICATORS (Direction of price movement)
| Indicator | Period(s) | Purpose |
|-----------|-----------|---------|
| **SMA** (Simple Moving Average) | 5, 20, 50, 200 | Support/resistance, trend direction |
| **EMA** (Exponential Moving Average) | 12, 26 | Recent price emphasis |
| **MACD** | 12/26/9 | Trend change & momentum |
| **ADX** (Average Directional Index) | 14 | Trend strength measurement |
| **CCI** (Commodity Channel Index) | 20 | Overbought/oversold detection |

#### B. MOMENTUM INDICATORS (Speed of price change)
| Indicator | Period(s) | Purpose |
|-----------|-----------|---------|
| **RSI** (Relative Strength Index) | 7, 14, 28 | Overbought (>70) / Oversold (<30) |
| **Stochastic** (%K, %D) | 14 | Momentum oscillation |

#### C. VOLATILITY INDICATORS (Price spread magnitude)
| Indicator | Period(s) | Purpose |
|-----------|-----------|---------|
| **ATR** (Average True Range) | 14 | Price volatility magnitude |
| **Vol_5d, Vol_20d** | 5, 20 | Rolling standard deviation |

#### D. VOLUME INDICATORS (Volume patterns)
| Indicator | Purpose |
|-----------|---------|
| **OBV** (On-Balance Volume) | Cumulative volume analysis |
| **Volume_MA20** | 20-day average volume |
| **Volume_Ratio** | Current vs average volume |

#### E. RETURNS (Price change metrics)
| Metric | Period | Purpose |
|--------|--------|---------|
| **Ret_1d** | 1 day | Daily returns |
| **Ret_5d** | 5 days | Weekly returns |
| **Ret_20d** | 20 days | Monthly returns |

---

## 3. COMPLEMENTARY MODULES

### `data_loader.py` (Data Infrastructure)
- `load_stock_data()`: Downloads OHLCV data from Yahoo Finance
- Handles data cleaning and formatting
- Foundation for all indicator calculations

### `metrics.py` (Performance Evaluation)
- `sharpe_ratio()`: Risk-adjusted returns metric
- `max_drawdown()`: Largest peak-to-trough decline
- `sortino_ratio()`: Downside volatility focus
- `backtest_strategy()`: Historical performance testing

### `models.py` (Predictive Models)
- `train_random_forest()`: Ensemble classification model
- `train_xgboost()`: Gradient boosting classifier
- `build_lstm_model()`: Deep learning time series model

### `portfolio_optimizer.py` (Portfolio Construction)
- `optimize_portfolio()`: Minimum volatility portfolio allocation
- `portfolio_volatility()`: Risk calculation

---

## 4. WORKFLOW INTEGRATION IN `app.py`

```
1. DATA LOADING
   └─ load_stock_data() → OHLCV DataFrame

2. FUNDAMENTAL ANALYSIS (Long-term view)
   ├─ get_fundamentals() → Financial metrics
   ├─ get_news_sentiment() → Market sentiment
   └─ get_analyst_ratings() → Consensus targets

3. TECHNICAL ANALYSIS (Short-term view)
   └─ calculate_technical_indicators() → 27+ indicators

4. FEATURE ENGINEERING
   ├─ Combine fundamental metrics
   ├─ Combine technical indicators
   ├─ Calculate relative returns vs benchmark
   └─ Apply rolling statistics

5. MODEL TRAINING
   ├─ RandomForest / XGBoost classification
   └─ LSTM for sequence prediction

6. BACKTESTING & EVALUATION
   ├─ backtest_strategy() → Performance metrics
   ├─ sharpe_ratio() → Risk-adjusted returns
   ├─ max_drawdown() → Risk measurement
   └─ confusion_matrix / classification_report

7. PORTFOLIO OPTIMIZATION
   └─ optimize_portfolio() → Optimal allocations
```

---

## 5. KEY DIFFERENCES SUMMARY

| Aspect | Fundamental Analysis | Technical Analysis |
|--------|---------------------|-------------------|
| **Time Horizon** | Long-term (months/years) | Short-term (days/weeks) |
| **Data Source** | Financial statements, news | Price & volume history |
| **Focus** | Company value & health | Price patterns & momentum |
| **Indicators** | P/E, ROE, growth rates | SMA, RSI, MACD, volatility |
| **Update Frequency** | Quarterly/Annually | Continuously (daily/intraday) |
| **Use Case** | Position sizing, sector selection | Entry/exit timing, risk management |
| **Predictability** | Medium/Low | Medium/High (short-term) |
| **Module** | `fundamental_analysis.py` | `technical_indicators.py` |

---

## 6. RECOMMENDED USAGE

### When to Use FUNDAMENTAL ANALYSIS:
- Stock selection & screening
- Long-term position decisions
- Sector/industry allocation
- Valuation assessment
- Risk/reward planning

### When to Use TECHNICAL ANALYSIS:
- Trade timing (entry/exit points)
- Stop-loss placement
- Trend confirmation
- Support/resistance identification
- Short-term momentum trades

### HYBRID STRATEGY (Recommended):
1. **Screen stocks using fundamentals** (quality, growth, valuation)
2. **Rank candidates by technical trend** (uptrend vs downtrend)
3. **Time entry with technical signals** (RSI, MACD crossover)
4. **Manage position with volatility indicators** (ATR stops)
5. **Monitor sentiment** for reversal signals

---

## 7. FEATURE CATEGORIES FOR ML MODELS

### Fundamental Features:
- ROE, P/E, Profit Margin, Revenue Growth, Beta, Debt-to-Equity

### Technical Features:
- SMA200, RSI14, MACD, ADX, ATR, Volume_Ratio, Returns, Volatility

### Relative Features:
- Beta_Rolling, Relative_Strength, Index_Correlation

### Target Variable:
- Binary classification: Future_Ret > median (1) or ≤ median (0)
