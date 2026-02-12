# ❓ FAQ & Troubleshooting Guide

Quick answers to common questions and solutions to common problems.

---

## 🎯 Quick Answers (30 seconds or less)

### Q: Where do I start?
**A**: Read [START_HERE.md](START_HERE.md) (5 min), then pick your path.

### Q: How do I install it?
**A**: 
```bash
pip install -r requirements.txt
python app_modern.py
```

### Q: How do I backtest a strategy?
**A**: See code examples in [QUICK_REFERENCE.md](QUICK_REFERENCE.md) under "Backtesting"

### Q: Will this make money?
**A**: Backtested ≠ live trading. Start small (1 share), monitor daily, scale gradually.

### Q: Is it safe?
**A**: Yes - built-in risk management, stop-losses, position sizing, daily limits.

### Q: Can I use my data?
**A**: Yes - CSV files, yfinance, NSEPy, Zerodha API all work.

### Q: How much does it cost?
**A**: Free software + free Zerodha tier (₹0 brokerage) + $5-10/month cloud (optional).

### Q: How long to go live?
**A**: ~4-8 hours from zero to live trading with validation.

---

## 🐛 Installation & Setup

### Problem: `ModuleNotFoundError: No module named 'tensorflow'`
**Symptoms**: Error when running app or scripts
**Solutions**:
```bash
# 1. Make sure virtual environment is activated
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 2. Reinstall all packages
pip install --upgrade -r requirements.txt

# 3. Check Python version (need 3.8+)
python --version

# 4. Clear cache and retry
pip cache purge
pip install -r requirements.txt
```
**Reference**: [QUICK_SETUP.md](QUICK_SETUP.md) section "Installation"

---

### Problem: `pip install` fails or is slow
**Symptoms**: Installation takes 10+ minutes or shows errors
**Solutions**:
```bash
# 1. Update pip
python -m pip install --upgrade pip

# 2. Use specific Python version (3.9-3.11 recommended)
python3.9 -m pip install -r requirements.txt

# 3. Install without dependencies (troubleshoot)
pip install --no-deps -r requirements.txt

# 4. Use faster index (China, Asia):
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```
**See**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed setup

---

### Problem: `python app_modern.py` doesn't start
**Symptoms**: Command runs but app doesn't open
**Solutions**:
```bash
# 1. Check if Streamlit is installed
python -c "import streamlit; print(streamlit.__version__)"

# 2. Run with verbose output
streamlit run app_modern.py --logger.level=debug

# 3. Access manually
# Default: http://localhost:8501
# Open browser and go there

# 4. Check port already in use
# Kill the process using port 8501 and retry
```
**See**: [QUICK_SETUP.md](QUICK_SETUP.md)

---

## 📊 Data & Backtesting

### Problem: "Not enough data" error in backtesting
**Symptoms**: Strategy fails or returns no signals
**Solutions**:
```python
# Check data length
import pandas as pd
df = pd.read_csv('data/stock.csv')
print(f"Data length: {len(df)} bars")
# Need minimum 252 bars (1 year daily)

# If too short:
# 1. Download more data (2-3 years minimum)
import yfinance as yf
df = yf.download('INFY.NS', period='3y')
df.to_csv('data/INFY.NS.csv')

# 2. Reduce MA periods in strategy
# Instead of fast=20, slow=50 → try fast=5, slow=15
```
**See**: [TESTING_VALIDATION_GUIDE.md](TESTING_VALIDATION_GUIDE.md) section "Data Quality"

---

### Problem: Backtest returns unrealistic results (too good)
**Symptoms**: 100%+ returns or <1% Sharpe ratio
**Solutions**:
```python
# 1. Check for look-ahead bias
# Only use past data in signal generation
# Wrong: use df['Close'].shift(0)  # Today's data
# Right: use df['Close'].shift(1)  # Yesterday's data

# 2. Validate with out-of-sample testing
from src.backtester import WalkForwardBacktester
result = WalkForwardBacktester().backtest_walk_forward(df, strategy, params)
# If OOS Sharpe much lower than in-sample → overfitted

# 3. Use SimpleBacktester instead of custom logic
result = SimpleBacktester().backtest(df, signals)
```
**See**: [TESTING_VALIDATION_GUIDE.md](TESTING_VALIDATION_GUIDE.md) section "Validation"

---

### Problem: Can't download stock data
**Symptoms**: `yfinance` fails or returns NaN
**Solutions**:
```python
# 1. Check internet connection
import urllib.request
urllib.request.urlopen('http://www.google.com')  # Should work

# 2. Try different data sources
# yfinance (free, often delays):
import yfinance as yf
df = yf.download('INFY.NS', period='1y')

# NSEPy (direct from NSE India):
from nsetools import Nse
nse = Nse()
df = nse.get_historical_data('INFY', '01-01-2023', '31-12-2023')

# CSV import (your own data):
df = pd.read_csv('data/INFY.csv', index_col='Date', parse_dates=True)

# 3. Check ticker format
# NSE: Use 'INFY.NS' or 'NSE:INFY'
# BSE: Use 'INFY.BO' or 'BSE:INFY'
```
**See**: [ADVANCED_ML_QUICKSTART.md](ADVANCED_ML_QUICKSTART.md) section "Data Sources"

---

## 🤖 Deep Learning & AI

### Problem: Transformer model takes too long to train
**Symptoms**: Model training >10 minutes
**Solutions**:
```python
# 1. Reduce sequence length
result = predict_with_transformer(
    df,
    seq_len=30,  # Instead of 60
    epochs=20,   # Instead of 50
    batch_size=32,
    n_heads=4,   # Instead of 8
    validation_split=0.1
)

# 2. Use GPU (MUCH faster)
import tensorflow as tf
print(tf.config.list_physical_devices('GPU'))
# If empty, GPU not available

# 3. Reduce validation data
validation_split=0.05  # Instead of 0.2

# 4. Use smaller model
n_layers=2  # Instead of 4
d_model=128  # Instead of 256
```
**See**: [ADVANCED_ML_QUICKSTART.md](ADVANCED_ML_QUICKSTART.md) section "Transformer"

---

### Problem: Autoencoder anomaly detection finds nothing
**Symptoms**: No anomalies detected
**Solutions**:
```python
# 1. Check reconstruction error threshold
from src.advanced_ai import detect_anomalies_autoencoder
results = detect_anomalies_autoencoder(df, epochs=50)
print(f"Anomalies found: {len(results)}")

# If 0, check thresholds:
# Automated IQR + percentile thresholding should work
# If not, manually adjust:

# Low detection threshold (more sensitive):
threshold_percentile = 75  # Instead of 90

# High detection threshold (less sensitive):
threshold_percentile = 95  # Instead of 90

# 2. Ensure data has anomalies
# Plot data to see if unusual spikes exist
df['Close'].plot()
# If no obvious spikes, anomaly detector won't find any

# 3. Check epochs and architecture
# May need more training:
detect_anomalies_autoencoder(df, epochs=100)
```
**See**: [ADVANCED_ML_QUICKSTART.md](ADVANCED_ML_QUICKSTART.md) section "Autoencoder"

---

### Problem: LSTM predictions all look the same
**Symptoms**: Predictions don't change, all values similar
**Solutions**:
```python
# 1. Check data normalization
# LSTM needs normalized data (0-1 range)
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
data_normalized = scaler.fit_transform(df['Close'].values.reshape(-1, 1))

# 2. Verify training worked
# Check training loss decreased over epochs
# If loss stayed same → model didn't learn

# 3. Increase model complexity
# More LSTM units → better for complex patterns
model.add(LSTM(128))  # Instead of 50

# 4. More training data
# LSTM needs 500+ samples minimum
if len(df) < 500:
    download_more_data()
```
**See**: [ADVANCED_ML_QUICKSTART.md](ADVANCED_ML_QUICKSTART.md) section "Multi-Step Forecasting"

---

## 📈 Strategy & Signals

### Problem: Strategy generates too many/too few signals
**Symptoms**: 100+ trades per month (too many) or 0 trades (too few)
**Solutions**:

**Too many signals** (=high turnover, high fees):
```python
# 1. Widen moving averages
signals = generate_ma_crossover_signals(df, 
    fast_ma=30,   # Instead of 20
    slow_ma=100   # Instead of 50
)

# 2. Add confirmation indicator
# Use momentum + trend confirmation (see STRATEGY_TEMPLATES.md)

# 3. Add minimum holding period
# Don't trade signals within N days of last trade
```

**Too few signals** (=missed opportunities):
```python
# 1. Tighten moving averages
signals = generate_ma_crossover_signals(df, 
    fast_ma=10,   # Instead of 20
    slow_ma=30    # Instead of 50
)

# 2. Remove confirmation filters
# Use only one indicator instead of two

# 3. Lower thresholds
# RSI > 50 instead of RSI > 60
```

**See**: [STRATEGY_TEMPLATES.md](STRATEGY_TEMPLATES.md) for parameter tuning

---

### Problem: Strategy works in backtesting but fails live
**Symptoms**: Paper trading shows losses, backtesting showed profits
**Solutions**:
```python
# 1. Check for look-ahead bias (most common)
# Backtest code:
signal = df['Close'].shift(0) > sma  # WRONG - uses today's close!
# Fixed code:
signal = df['Close'].shift(1) > sma  # RIGHT - uses yesterday's close

# 2. Validate with walk-forward test
from src.backtester import WalkForwardBacktester
wf_result = WalkForwardBacktester().backtest_walk_forward(df, strategy, params)
# Compare OOS Sharpe to in-sample Sharpe
# If massively different → overfitted

# 3. Check for overfitting
# Run: test_parameter_sensitivity(df, strategy, params)
# Check robustness score > 60%

# 4. Account for trading costs
# Backtester may not include commission
# Real trades: add commission, slippage
commission_per_trade = 20  # ₹20
slippage_per_trade = 10    # ₹10 estimated slippage
```

**See**: [TESTING_VALIDATION_GUIDE.md](TESTING_VALIDATION_GUIDE.md) section "Robustness Testing"

---

## 🔌 Zerodha Integration

### Problem: "ZerodhaAuthenticator: Invalid API credentials"
**Symptoms**: Can't connect to Zerodha, authentication fails
**Solutions**:
```python
# 1. Verify credentials from Zerodha settings
# Go to: https://kite.zerodha.com/settings/api
# Check API Key and API Secret match your code

# 2. Test credentials
from src.zerodha_integration import ZerodhaAuthenticator
auth = ZerodhaAuthenticator(api_key='YOUR_KEY', api_secret='YOUR_SECRET')
profile = auth.kite.profile()
print(profile)  # Should show your name

# 3. Check account active
# Login to Zerodha web
# Verify account shows at kite.zerodha.com

# 4. Regenerate credentials if needed
# Go to Zerodha Sentinel (security) and reset API credentials
```
**See**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) section "Configuration Setup - Zerodha"

---

### Problem: "Session expired" during trading
**Symptoms**: Orders fail with session error after 30+ minutes
**Solutions**:
```python
# 1. Reload session before trading
from src.zerodha_integration import ZerodhaAuthenticator
auth = ZerodhaAuthenticator()
auth.load_session()  # Load saved session

# If session file not found:
# Need to authenticate again (get login token)

# 2. Refresh token periodically
# Add to trading loop:
if time.time() - last_refresh > 3600:  # Every hour
    auth.save_session()
    auth.load_session()

# 3. Check internet connection
import urllib.request
urllib.request.urlopen('http://www.zerodha.com')

# 4. Verify market hours
# Zerodha only works during market hours 9:15 AM - 3:30 PM IST
```
**See**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) section "Troubleshooting - Connection Issues"

---

### Problem: Orders failing to execute
**Symptoms**: `place_order()` returns error
**Solutions**:
```python
# 1. Check order parameters
result = trader.execute_signal('NSE:INFY', signal=1)
# Verify: Symbol format correct (NSE:INFY not just INFY)
# Verify: Signal is 1 (buy), -1 (sell), or 0 (no trade)

# 2. Check funds available
profile = auth.kite.profile()
print(f"Available: {profile['equity_intraday']}")
# If 0, can't trade - need to add margin

# 3. Check position limits
positions = auth.kite.positions()
print(f"Current positions: {len(positions['net'])}")
# Max 10-20 concurrent positions (check Zerodha limits)

# 4. Check quantity minimum
# NSE stocks minimum 1 share (fine)
# Some illiquid stocks may have higher minimums

# 5. Test with simple order first
result = auth.kite.place_order(
    variety='regular',
    exchange='NSE',
    tradingsymbol='INFY',
    transaction_type='BUY',
    quantity=1,
    order_type='MARKET',
    product='MIS'  # Intraday
)
print(result)
```
**See**: [src/zerodha_integration.py](src/zerodha_integration.py) lines 200-250

---

## 📧 Email Alerts

### Problem: Emails not sending
**Symptoms**: No emails received, but code runs without error
**Solutions**:
```python
# 1. Verify Gmail setup
from src.email_alerts import EmailAlertConfig, EmailAlertSender
config = EmailAlertConfig()
print(config.config)  # Check if credentials saved

# If empty, setup:
config.update_gmail_credentials('your_email@gmail.com', 'YOUR_APP_PASSWORD')
config.add_recipient('recipient@gmail.com')
config.save_config()

# 2. Generate App Password correctly
# Go to: https://myaccount.google.com/security
# Enable 2-Step Verification
# Create "App Password" (select Mail, select Windows)
# Use this 16-char password

# Regular Gmail password WON'T WORK
# Must be App Password

# 3. Test email sending
sender = EmailAlertSender(config)
sender.send_signal_alert(
    symbol='NSE:INFY',
    signal=1,
    price=1200,
    confidence=100
)

# 4. Check spam folder
# Emails might go to spam/promotions
# Mark as "Not spam" in Gmail

# 5. Check daily limit
# Gmail free tier: 100 emails/day limit
# If exceeded, emails will be blocked
```
**See**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) section "Configuration Setup - Gmail"

---

### Problem: "Too many alerts" or "Daily limit exceeded"
**Symptoms**: Alerts stop sending mid-day
**Solutions**:
```python
# 1. Check daily limit
from src.email_alerts import AlertManager
alerts = AlertManager()
history = alerts.get_alert_history()
print(f"Alerts sent today: {len(history)}")
# Max 100 per day for free Gmail

# 2. Reduce signal frequency
# Space out trades:
# Current: Buy on every MA crossover
# Better: Buy max once per 30 minutes

# 3. Filter low-confidence signals
# Only alert if confidence > 80%
if confidence > 80:
    alerts.check_and_alert_signal(...)

# 4. Disable non-critical alerts
# Keep trading alerts
# Disable hourly status updates
```
**See**: [src/email_alerts.py](src/email_alerts.py) lines 150-180

---

## ☁️ Cloud & Deployment

### Problem: AWS EC2 instance keeps stopping
**Symptoms**: Trading stops working, need to restart
**Solutions**:
```bash
# 1. Enable auto-restart on reboot
sudo systemctl enable aitrading

# 2. Check service logs
sudo journalctl -u aitrading -n 50  # Last 50 lines

# 3. Monitor memory/CPU
free -h  # Check available memory
df -h    # Check disk space
# If full → instance dies

# 4. Setup CloudWatch monitoring
# In AWS console:
# EC2 → Monitoring → Enable detailed monitoring

# 5. Set up EC2 auto-recovery
# If instance crashes → auto-restart
```
**See**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) section "AWS EC2 Setup"

---

### Problem: App crashes on cloud after 1-2 hours
**Symptoms**: Cloud app works then becomes unreachable
**Solutions**:
```bash
# 1. Check memory leak
ps aux | grep python  # See all Python processes
# Multiple processes? Kill duplicates:
killall python3

# 2. Check disk space
df -h /
# If >95% full → delete old logs
rm -rf logs/trading_*.log  # Keep only last week

# 3. Set memory limit for process
# Edit /etc/systemd/system/aitrading.service:
MemoryLimit=1G  # Crash if uses >1GB

# 4. Add restart policy
# Add to service file:
Restart=on-failure
RestartSec=30

# 5. Enable swap (if needed)
sudo dd if=/dev/zero of=/swapfile bs=1G count=2
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 🔍 General Debugging

### Problem: Application runs but gives no signals
**Symptoms**: App starts, but no buy/sell signals
**Solutions**:
```python
# 1. Verify data is loaded
print(df.head())
print(f"Data shape: {df.shape}")
print(f"Date range: {df.index[0]} to {df.index[-1]}")

# 2. Test signal generation manually
signals = generate_ma_crossover_signals(df, 20, 50)
print(signals.describe())
print(f"Buy signals: {(signals == 1).sum()}")
print(f"Sell signals: {(signals == -1).sum()}")

# 3. Check MA values
sma_20 = df['Close'].rolling(20).mean()
print(f"Last price: {df['Close'].iloc[-1]:.2f}")
print(f"SMA 20: {sma_20.iloc[-1]:.2f}")
print(f"SMA 50: {df['Close'].rolling(50).mean().iloc[-1]:.2f}")

# 4. Verify parameters
params = {'fast_ma': 20, 'slow_ma': 50}
print(f"Parameters: {params}")

# 5. Check if enough historical data
if len(df) < 50:
    print("ERROR: Need at least 50 bars for SMA50")
```

---

## 📞 Where to Get Help

| Issue | First Check | Then Read |
|-------|------------|-----------|
| **Installation** | Terminal output | [QUICK_SETUP.md](QUICK_SETUP.md) |
| **Backtesting** | Test data length | [TESTING_VALIDATION_GUIDE.md](TESTING_VALIDATION_GUIDE.md) |
| **Strategies** | Check parameters | [STRATEGY_TEMPLATES.md](STRATEGY_TEMPLATES.md) |
| **Deep Learning** | Check data shape | [ADVANCED_ML_QUICKSTART.md](ADVANCED_ML_QUICKSTART.md) |
| **Zerodha** | Verify credentials | [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) |
| **Email** | Check Gmail config | [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) |
| **Cloud** | Check logs | [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) AWS section |
| **General** | See index | [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) |

---

## ✅ Pre-Flight Checklist

Before going live, verify:

```
Installation:
[ ] ✅ pip install -r requirements.txt completed
[ ] ✅ python app_modern.py runs without errors
[ ] ✅ All imports work

Data:
[ ] ✅ Have 2+ years of data
[ ] ✅ Data has no NaN values
[ ] ✅ Data format: Date, Open, High, Low, Close, Volume

Backtest:
[ ] ✅ Strategy tested with SimpleBacktester
[ ] ✅ Sharpe ratio > 0.5
[ ] ✅ Win rate > 40%
[ ] ✅ Walk-forward OOS Sharpe > 0.3

Configuration:
[ ] ✅ Zerodha credentials working
[ ] ✅ Gmail alerts tested
[ ] ✅ Position sizing calculated
[ ] ✅ Stop-loss and take-profit configured

Risk Management:
[ ] ✅ Daily loss limit set
[ ] ✅ Position size limiter active
[ ] ✅ Time-based position close (3:20 PM)
[ ] ✅ Emergency manual close procedure ready

Deployment:
[ ] ✅ Monitoring dashboard setup
[ ] ✅ Logging configured
[ ] ✅ Backup/recovery plan ready
[ ] ✅ Team/family notified

🚀 READY FOR LIVE TRADING
```

---

## 🎯 Remember

- **Small losses teach big lessons** - Start with 1-2 shares
- **Consistency beats perfection** - 2% monthly is great
- **Monitor daily** - Don't set and forget
- **Scale gradually** - 1 symbol → 3 → 10 over months
- **Keep learning** - Review trades, patterns, mistakes
- **Have fun!** - This is exciting stuff

**You've got this! 🚀**

