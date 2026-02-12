# Advanced ML & Trading Features - Quick Start Guide

## 🎯 Overview
This document covers the newly added advanced features:
- **Transformer-based Deep Learning models**
- **Multi-step price forecasting (1/3/5 days)**
- **Autoencoder anomaly detection**
- **Backtesting engine with multiple strategies**
- **Zerodha brokerage integration**
- **Gmail email alerts**

---

## 1️⃣ Installation & Setup

### Install Dependencies
```bash
pip install -r requirements.txt
```

Key packages installed:
- **TensorFlow/Keras**: Deep learning models
- **Backtrader**: Backtesting framework
- **kiteconnect**: Zerodha API
- **optuna**: Hyperparameter optimization
- **arch**: GARCH volatility modeling

### Verify Installation
```python
python -c "import tensorflow; import backtrader; import kiteconnect; print('✓ All packages installed')"
```

---

## 2️⃣ Deep Learning Models

### A. Transformer-Based Time Series Forecasting

**What it does:**
- Uses self-attention mechanisms to predict future prices
- Captures long-range dependencies in price movements
- Includes positional encoding for temporal information

**How to use in app:**
1. Navigate to "🔬 Deep Learning" tab
2. Enter a stock symbol (e.g., INFY)
3. Click "🔄 Load Data"
4. In "Transformer Forecasting" section:
   - Set sequence length (default: 60 days)
   - Set attention heads (default: 4)
   - Set transformer layers (default: 2)
5. Click "🚀 Train Transformer"

**Code usage:**
```python
from src.advanced_ai import predict_with_transformer

result = predict_with_transformer(
    df,           # DataFrame with price data
    seq_len=60,   # Look back 60 days
    forecast_len=5,  # Predict 5 days
    epochs=50,
    n_heads=4,    # Attention heads
    n_layers=2    # Transformer layers
)

# Results include:
# - 1-day, 3-day, 5-day price predictions
# - Change percentages
# - Overall trend direction
# - Model error metrics
```

### B. Multi-Step Price Forecasting

**What it does:**
- Predicts next 1, 3, and 5 days prices separately
- Better for different trading timeframes
- More interpretable than single point forecast

**How to use:**
Use the same "🔬 Deep Learning" tab:
1. Go to "📊 Multi-Step Predictions" tab
2. Click "📊 Generate Multi-Step Forecast"
3. View predictions for each day

**Returns:**
```python
{
    '1_day': {'price': 2500.50, 'change_pct': 1.25},
    '3_day': {'price': 2525.75, 'change_pct': 2.50},
    '5_day': {'price': 2550.00, 'change_pct': 3.75}
}
```

### C. Autoencoder Anomaly Detection

**What it does:**
- Detects unusual volume/price spikes
- Identifies potential breakouts or false signals
- Uses reconstruction error method

**How to use:**
1. Go to "🎯 Autoencoder Anomalies" in Deep Learning tab
2. Click "🎯 Detect Anomalies"
3. View detected anomalies and reconstruction errors

**Code usage:**
```python
from src.advanced_ai import detect_anomalies_autoencoder

result = detect_anomalies_autoencoder(
    df,
    contamination=0.05,  # Expect 5% anomalies
    epochs=50
)

# Returns top 20 anomalies with:
# - Date
# - Reconstruction error score
# - Feature values
```

---

## 3️⃣ Backtesting Engine

### Simple Backtester (No Backtrader Required)

**How to use in app:**
1. Go to "📈 Strategy Backtest" tab
2. Select a stock and strategy
3. Choose initial capital
4. Select strategy parameters
5. Click "▶️ Run Backtest"

**Available Strategies:**
- **Moving Average Crossover**: Fast MA > Slow MA = Buy
- **RSI Strategy**: Oversold/Overbought zones
- **MACD Signal**: MACD > Signal = Buy

**Code usage:**
```python
from src.backtester import SimpleBacktester, generate_ma_crossover_signals
import pandas as pd

# Create signals
signals = generate_ma_crossover_signals(df, fast_period=20, slow_period=50)
# Returns: 1 (buy), -1 (sell), 0 (hold)

# Run backtest
backtester = SimpleBacktester(initial_capital=100000, commission=0.001)
results = backtester.backtest(df, signals)

# Results include:
# - final_equity, total_return_pct
# - sharpe_ratio, max_drawdown_pct
# - num_trades, win_rate_pct
# - equity_curve (list of portfolio values)
```

### Walk-Forward Backtesting (More Robust)

**Code usage:**
```python
from src.backtester import WalkForwardBacktester

wf_backtester = WalkForwardBacktester(
    initial_capital=100000,
    train_period=100,     # Train on 100 days
    test_period=20        # Test on 20 days
)

# Define a signal generator function
def my_signal_generator(df):
    # Your logic here
    return signals

results = wf_backtester.backtest_walk_forward(df, my_signal_generator)

# Results include fold-by-fold results
# More realistic than single backtest
```

### Custom Strategy Signals

**Create custom signals:**
```python
# Example: RSI + MACD combination
from src.backtester import generate_rsi_signals, generate_macd_signals

rsi_signals = generate_rsi_signals(df, period=14, oversold=30, overbought=70)
macd_signals = generate_macd_signals(df)

# Combine: Buy only if both agree
combined_signals = pd.Series(0, index=df.index)
combined_signals[(rsi_signals == 1) & (macd_signals == 1)] = 1
combined_signals[(rsi_signals == -1) & (macd_signals == -1)] = -1
```

---

## 4️⃣ Zerodha Integration (Live Trading)

### Setup & Authentication

**Step 1: Get API Credentials**
1. Visit [Zerodha Console](https://console.zerodha.com)
2. Get your **API Key** and **API Secret**
3. Set redirect URL to `http://localhost:8000/`

**Step 2: Initialize Zerodha Connection**

```python
from src.zerodha_integration import ZerodhaAuthenticator, ZerodhaKite

# Initialize
auth = ZerodhaAuthenticator(
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
    redirect_url="http://localhost:8000/"
)

# Get login URL
login_url = auth.get_login_url()
print(f"Login here: {login_url}")

# After login, exchange token for access token
request_token = "XXXX"  # From login
result = auth.set_access_token(request_token)

# Save session for reuse
auth.save_session('.zerodha_session')
```

**Step 3: Use Kite API**

```python
from src.zerodha_integration import ZerodhaKite

# Load existing session
auth.load_session('.zerodha_session')

# Initialize Kite wrapper
kite = ZerodhaKite(auth)

# Get portfolio
holdings = kite.get_holdings()
positions = kite.get_positions()
margins = kite.get_margins()
```

### Place Orders Based on AI Signals

```python
from src.zerodha_integration import AutomatedTrader

trader = AutomatedTrader(
    kite,
    risk_percent=2.0,      # Risk 2% per trade
    max_position_size=100  # Max 100 shares
)

# Signal from your model
signal = {
    'recommendation': 'STRONG BUY',
    'confidence': 75.5
}

# Execute
result = trader.execute_signal(
    signal,
    symbol='INFY',
    current_price=2500,
    stop_loss_pct=2.0
)

print(result)
# {
#     'success': True,
#     'order_id': '12345',
#     'position_size': 40,
#     'signal_strength': 'STRONG BUY'
# }
```

### Get Portfolio Analysis

```python
from src.zerodha_integration import analyze_portfolio

portfolio = analyze_portfolio(kite)

print(f"Total P&L: ₹{portfolio['total_pnl']:.2f}")
print(f"Return %: {portfolio['total_return_percent']:.2f}%")
print(f"Available Margin: ₹{portfolio['available_margin']:.2f}")
```

### ⚠️ Important Notes
- **Free tier**: Personal account (≤20 orders/day)
- **Upgrade needed**: Connect tier (₹500/month) for live data
- **Always test** with small positions first
- **Use stop losses** for all positions
- **Monitor margin** to avoid liquidation

---

## 5️⃣ Email Alerts via Gmail

### Configuration

**Step 1: Get Gmail App Password**
1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Generate App Password (NOT your regular Gmail password)
3. Copy the 16-character password

**Step 2: Configure Email Alerts**

```python
from src.email_alerts import EmailAlertConfig, AlertManager

# Create/load config
config = EmailAlertConfig('.email_config.json')

# Set Gmail credentials
config.update_gmail_credentials(
    email='your_email@gmail.com',
    app_password='xxxx xxxx xxxx xxxx'  # 16-char password
)

# Add recipients
config.add_recipient('you@gmail.com')
config.add_recipient('friend@gmail.com')

# Set preferences
config.set_alert_preferences(
    buy=True,
    sell=True,
    anomaly=True,
    min_confidence=60.0
)
```

### Send Alerts on Trading Signals

```python
from src.email_alerts import AlertManager

alert_mgr = AlertManager(config)

# Your signal from AI model
signal = {
    'recommendation': 'STRONG BUY',
    'confidence': 78.5,
    'factors': {'technical_score': 8.5/10}
}

# Send alert
result = alert_mgr.check_and_alert_signal(
    symbol='INFY',
    signal=signal,
    current_price=2500,
    target_prices={
        'entry': 2490,
        'target': 2600,
        'stop_loss': 2450
    }
)

print(f"Alert sent: {result['alerted']}")
```

### Send Anomaly Alerts

```python
# When autoencoder detects anomaly
alert_mgr.check_and_alert_anomaly(
    symbol='INFY',
    anomaly_type='Volume Spike',
    details={
        'volume': 5000000,
        'average_volume': 1000000,
        'spike_ratio': 5.0
    }
)
```

### How Alerts Work

1. **Signal triggers**: Buy/Sell signal with confidence > threshold
2. **Email formatted**: HTML email with charts and analysis
3. **Daily limit**: 100 emails/day (free Gmail)
4. **Config saved**: Persistent setup in `.email_config.json`

---

## 6️⃣ Hyperparameter Optimization (Optuna)

**Optimize model parameters:**

```python
import optuna
from src.backtester import SimpleBacktester

def objective(trial):
    # Suggest parameters
    fast_ma = trial.suggest_int('fast_ma', 5, 30)
    slow_ma = trial.suggest_int('slow_ma', 30, 100)
    
    # Generate signals
    signals = generate_ma_crossover_signals(
        df, fast_ma, slow_ma
    )
    
    # Backtest
    backtester = SimpleBacktester()
    result = backtester.backtest(df, signals)
    
    # Return metric to maximize
    return result['sharpe_ratio']

# Run optimization
study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=50)

# Get best params
print(study.best_params)
# {'fast_ma': 18, 'slow_ma': 52}
```

---

## 7️⃣ Free Data Sources

### NSE Data (Indian stocks)

```python
# NSEPy - Free NSE data
# pip install nsepython

from nsepython import *

# Get latest prices
data = equity_history("INFY", series="EQ", from_date="01-01-2024", to_date="31-01-2024")

# Get index data
nifty_data = index_history("NIFTY 50")
```

### yFinance (Already integrated)

```python
from src.data_loader import load_stock_data

# Already handles:
# - Multi-year historical data
# - OHLCV data
# - Dividends & splits
# - YFinance limitations (~1800 requests/hour)
```

### Alpha Vantage (Free tier limited)

```python
# pip install alpha-vantage

from alpha_vantage.timeseries import TimeSeries

ts = TimeSeries(key='YOUR_API_KEY')
data, meta = ts.get_daily(symbol='IBM')

# Free tier: 5 requests/min, 500 requests/day
```

---

## 📊 Complete Workflow Example

```python
from src.data_loader import load_stock_data
from src.advanced_ai import predict_with_transformer, detect_anomalies_autoencoder
from src.backtester import SimpleBacktester, generate_ma_crossover_signals
from src.email_alerts import EmailAlertConfig, AlertManager
from src.zerodha_integration import ZerodhaKite, AutomatedTrader

# 1. Load data
df = load_stock_data('INFY', '2023-01-01', '2024-01-27')

# 2. Deep learning predictions
transformer_pred = predict_with_transformer(df)
print(f"5-Day Forecast: {transformer_pred['predictions']['5_day']}")

# 3. Anomaly detection
anomalies = detect_anomalies_autoencoder(df)
print(f"Anomalies found: {anomalies['anomalies_detected']}")

# 4. Backtest strategy
signals = generate_ma_crossover_signals(df, 20, 50)
backtester = SimpleBacktester()
bt_result = backtester.backtest(df, signals)
print(f"Sharpe Ratio: {bt_result['sharpe_ratio']:.2f}")

# 5. Setup alerts
config = EmailAlertConfig()
config.update_gmail_credentials('you@gmail.com', 'xxxx xxxx xxxx xxxx')
alert_mgr = AlertManager(config)

# 6. Execute live order if confident
if transformer_pred['expected_return'] > 2:
    auth = ZerodhaAuthenticator(api_key, api_secret)
    kite = ZerodhaKite(auth)
    trader = AutomatedTrader(kite)
    
    result = trader.execute_signal(
        {'recommendation': 'STRONG BUY', 'confidence': 75},
        'INFY', 2500
    )
    print(f"Order placed: {result}")
```

---

## 🎓 Learning Resources

1. **Transformers in Finance**
   - Attention Is All You Need (Vaswani et al.)
   - Using Transformers for Time Series Forecasting

2. **Autoencoders**
   - Anomaly Detection with Autoencoders
   - Reconstruction Error Method

3. **Backtesting Best Practices**
   - Walk-Forward Analysis
   - Out-of-Sample Testing
   - Avoiding Overfitting

4. **Zerodha API**
   - [Zerodha Kite Docs](https://kite.trade/)
   - Order Types & Execution
   - Position Management

---

## ❓ Troubleshooting

### TensorFlow/CUDA Issues
```bash
pip install tensorflow-cpu  # Use CPU version if GPU not available
```

### Zerodha Connection Failed
- Check API credentials
- Verify redirect URL matches
- Ensure session token is valid

### Email Not Sending
- Verify Gmail App Password (not regular password)
- Check recipient emails are valid
- Review daily email limit (100/day for Gmail)

### Backtest Shows NaN
- Ensure sufficient data (>100 rows)
- Check for NaN values in indicators
- Verify signals are properly generated

---

## 📝 Next Steps

1. **Optimize**: Use Optuna to tune model parameters
2. **Combine**: Mix Transformer + Autoencoder + Backtest
3. **Deploy**: Run on cloud (Google Colab, AWS) for 24/7 trading
4. **Monitor**: Setup email alerts + Zerodha live orders
5. **Scale**: Add more strategies and symbols

---

**Made with ❤️ for traders and data scientists**
