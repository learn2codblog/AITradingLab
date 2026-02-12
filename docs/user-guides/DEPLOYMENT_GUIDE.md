# 🚀 DEPLOYMENT & GO-LIVE GUIDE

Complete step-by-step guide to deploy AITradingLab to production and start live trading.

---

## 📋 Pre-Deployment Checklist

### System Requirements
```bash
✅ Python 3.8+
✅ 4GB RAM minimum
✅ Internet connection (for data, Zerodha, email)
✅ Valid Zerodha account (free tier available)
✅ Gmail account (for email alerts)
✅ Stable server/laptop/cloud VM
```

### Software Setup
```bash
# 1. Clone/setup project
cd d:\Code-Base\Personal\Trading-AI\AITradingLab

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation
python -c "import tensorflow, backtrader, kiteconnect; print('✅ All dependencies installed')"

# 5. Test imports
python -c "
from src.backtester import SimpleBacktester
from src.zerodha_integration import ZerodhaAuthenticator
from src.email_alerts import EmailAlertManager
from src.advanced_ai import predict_with_transformer
print('✅ All modules import successfully')
"
```

---

## 🔑 Configuration Setup

### 1. Zerodha Authentication

```python
# src/zerodha_integration.py is already configured
# To setup credentials:

from src.zerodha_integration import ZerodhaAuthenticator

# Initialize authenticator
auth = ZerodhaAuthenticator(
    api_key='YOUR_ZERODHA_API_KEY',
    api_secret='YOUR_ZERODHA_API_SECRET'
)

# Get login URL
login_url = auth.get_login_url()
print(f"Visit this URL and login: {login_url}")

# After login, use the request token shown in redirect URL
auth.set_access_token(request_token='YOUR_REQUEST_TOKEN')

# Save session for future use (automatically done)
print("✅ Zerodha authenticated and saved")
```

**Get API Credentials**:
1. Go to https://kite.zerodha.com/
2. Login to your account
3. Go to Settings → API Consultants
4. Create new app or use existing
5. Copy API Key and API Secret

### 2. Gmail Setup

```python
# src/email_alerts.py handles this automatically

from src.email_alerts import EmailAlertConfig

# First time setup
config = EmailAlertConfig()
config.update_gmail_credentials(
    email='your_email@gmail.com',
    password='YOUR_APP_PASSWORD'  # Not regular password!
)
config.add_recipient('recipient@gmail.com')
config.save_config()

print("✅ Gmail configured")
```

**Generate Gmail App Password**:
1. Go to https://myaccount.google.com/security
2. Enable 2-Factor Authentication
3. Create App Password (select Mail, Windows)
4. Use this 16-char password above

### 3. Strategy Configuration

```yaml
# config.yaml - Update with your preferences

strategies:
  ma_crossover:
    enabled: true
    fast_ma: 20
    slow_ma: 50
    symbols: ['NSE:INFY', 'NSE:SBIN', 'NSE:BAJAJFINSV']
  
  mean_reversion:
    enabled: false
    ma_period: 20
    std_mult: 2.0
    symbols: []
  
  momentum:
    enabled: true
    rsi_period: 14
    macd_fast: 12
    macd_slow: 26
    symbols: ['NSE:INFY']

alerts:
  send_email: true
  send_sms: false
  daily_limit: 100
  
backtest:
  min_sharpe: 0.5
  max_drawdown: 0.30
  min_win_rate: 0.40

position_sizing:
  account_size: 100000  # ₹
  risk_per_trade: 0.02  # 2%
  max_position_size: 0.10  # 10% per stock
```

---

## 🏗️ Deployment Architecture

### Option 1: Local Laptop (Simple)
```
┌─────────────────────────────────────┐
│  Your Laptop / Desktop PC           │
├─────────────────────────────────────┤
│ - AITradingLab app running          │
│ - Zerodha connection (live)         │
│ - Gmail alerts (live)               │
│ - ⚠️ Requires laptop always on      │
└─────────────────────────────────────┘
```

### Option 2: Cloud Server (Recommended)
```
┌──────────────────────────────────────┐
│  Cloud Host (AWS EC2 / Azure)       │
├──────────────────────────────────────┤
│ - AITradingLab running 24/7         │
│ - Zerodha connection                │
│ - Gmail alerts                      │
│ - ✅ Always accessible              │
│ - ✅ Low cost (~$5-10/month)        │
└──────────────────────────────────────┘
```

### Option 3: Google Colab (Free)
```python
# Free GPU, always available
# See ADVANCED_IMPLEMENTATIONS.md for Colab setup

# Quick Colab setup:
# 1. Mount Google Drive: from google.colab import drive
# 2. Upload project to Drive
# 3. Run in Colab cells with GPU enabled
# ✅ Free, ✅ Powerful, ⚠️ Needs Drive mounted
```

---

## 📊 Deployment Steps (Local)

### Step 1: Data Preparation
```python
# scripts/prepare_data.py

import pandas as pd
import yfinance as yf

# Download 3 years of data for each symbol
symbols = ['INFY.NS', 'SBIN.NS', 'BAJAJFINSV.NS']

for symbol in symbols:
    df = yf.download(symbol, progress=False)
    df.to_csv(f'data/{symbol}.csv')
    print(f"✅ Downloaded {symbol}")

print(f"✅ All data ready for backtesting")
```

### Step 2: Backtest & Optimize
```python
# scripts/optimize_strategies.py

from src.backtester import SimpleBacktester, WalkForwardBacktester
from src.advanced_ai import generate_ma_crossover_signals
import optuna
import pandas as pd

# Load data
df = pd.read_csv('data/INFY.NS.csv', index_col='Date', parse_dates=True)

# Optimize MA parameters
def objective(trial):
    fast_ma = trial.suggest_int('fast_ma', 5, 20)
    slow_ma = trial.suggest_int('slow_ma', 30, 100)
    
    signals = generate_ma_crossover_signals(df, fast_ma, slow_ma)
    result = SimpleBacktester().backtest(df, signals)
    
    return result['sharpe_ratio']

study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=50)

print(f"✅ Best parameters: {study.best_params}")
print(f"   Sharpe: {study.best_value:.2f}")

# Save best params
import json
with open('strategies/ma_best_params.json', 'w') as f:
    json.dump(study.best_params, f)
```

### Step 3: Validate Strategy
```python
# scripts/validate_strategy.py

from TESTING_VALIDATION_GUIDE import full_validation_report
from src.advanced_ai import generate_ma_crossover_signals
import pandas as pd

df = pd.read_csv('data/INFY.NS.csv', index_col='Date', parse_dates=True)

best_params = {
    'fast_ma': 20,
    'slow_ma': 50
}

is_approved = full_validation_report(
    df,
    generate_ma_crossover_signals,
    best_params
)

if is_approved:
    print("\n🚀 APPROVED FOR LIVE TRADING")
else:
    print("\n❌ NEEDS MORE OPTIMIZATION")
    exit(1)
```

### Step 4: Configure Live Credentials
```python
# scripts/setup_live.py

from src.zerodha_integration import ZerodhaAuthenticator
from src.email_alerts import EmailAlertConfig

print("=" * 50)
print("LIVE TRADING SETUP")
print("=" * 50)

# Setup Zerodha
print("\n1. Zerodha Configuration")
print("   Get credentials from https://kite.zerodha.com/")
api_key = input("   Enter API Key: ")
api_secret = input("   Enter API Secret: ")

auth = ZerodhaAuthenticator(api_key, api_secret)
login_url = auth.get_login_url()
print(f"   Visit: {login_url}")
request_token = input("   Enter Request Token: ")
auth.set_access_token(request_token)
print("   ✅ Zerodha configured")

# Setup Gmail
print("\n2. Gmail Configuration")
gmail = input("   Enter Gmail address: ")
app_password = input("   Enter 16-char App Password: ")

config = EmailAlertConfig()
config.update_gmail_credentials(gmail, app_password)
config.add_recipient(input("   Alert recipient email: "))
config.save_config()
print("   ✅ Gmail configured")

print("\n" + "=" * 50)
print("✅ READY FOR LIVE TRADING")
print("=" * 50)
```

### Step 5: Run Live Trading
```python
# scripts/run_live.py

from src.zerodha_integration import ZerodhaAuthenticator, AutomatedTrader
from src.email_alerts import AlertManager
from src.advanced_ai import generate_ma_crossover_signals
import pandas as pd
import yfinance as yf
import time
from datetime import datetime

# Configuration
SYMBOLS = ['NSE:INFY', 'NSE:SBIN']
CHECK_INTERVAL = 300  # 5 minutes
ACCOUNT_SIZE = 100000
RISK_PER_TRADE = 0.02

# Initialize
auth = ZerodhaAuthenticator()
auth.load_session()  # Load saved credentials
trader = AutomatedTrader(auth.kite, ACCOUNT_SIZE, RISK_PER_TRADE)
alerts = AlertManager()

print("=" * 60)
print("LIVE TRADING STARTED")
print("=" * 60)
print(f"Time: {datetime.now()}")
print(f"Symbols: {SYMBOLS}")
print(f"Account Size: ₹{ACCOUNT_SIZE:,.0f}")
print(f"Risk per trade: {RISK_PER_TRADE*100:.1f}%")
print("=" * 60)

try:
    while True:
        try:
            current_time = datetime.now()
            
            # Check if market is open (9:15 AM - 3:30 PM IST)
            hour = current_time.hour
            minute = current_time.minute
            
            if not (9 <= hour < 15 or (hour == 15 and minute < 30)):
                print(f"{current_time} - Market closed, waiting...")
                time.sleep(CHECK_INTERVAL)
                continue
            
            print(f"\n{current_time} - Checking signals...")
            
            for symbol in SYMBOLS:
                try:
                    # Download latest data (1-month history)
                    symbol_name = symbol.split(':')[1]
                    df = yf.download(
                        f'{symbol_name}.NS',
                        period='1mo',
                        progress=False
                    )
                    
                    # Generate signal
                    signals = generate_ma_crossover_signals(df, 20, 50)
                    latest_signal = signals.iloc[-1]
                    
                    if latest_signal != 0:
                        print(f"\n  {symbol}: Signal = {latest_signal}")
                        
                        # Execute trade
                        result = trader.execute_signal(symbol, latest_signal)
                        
                        if result['success']:
                            print(f"  ✅ Order placed: {result['order_id']}")
                            
                            # Send alert
                            alerts.check_and_alert_signal(
                                symbol,
                                latest_signal,
                                df['Close'].iloc[-1],
                                confidence=80
                            )
                        else:
                            print(f"  ❌ Order failed: {result['reason']}")
                
                except Exception as e:
                    print(f"  ❌ Error for {symbol}: {e}")
            
            print(f"\nNext check in {CHECK_INTERVAL}s...")
            time.sleep(CHECK_INTERVAL)
        
        except KeyboardInterrupt:
            print("\n⚠️  Stopping live trading...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Retrying in 30s...")
            time.sleep(30)

except KeyboardInterrupt:
    print("\n✅ Live trading stopped")
```

---

## 🌐 Deployment on Cloud (AWS EC2)

### Quick AWS Setup

```bash
# 1. Create EC2 instance
# - Ubuntu 20.04 LTS
# - t2.micro (free tier eligible)
# - Storage: 20GB

# 2. Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# 3. Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv git -y

# 4. Clone project
git clone <your-repo-url>
cd AITradingLab

# 5. Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# 6. Install packages
pip install -r requirements.txt

# 7. Setup systemd service (auto-restart on reboot)
sudo tee /etc/systemd/system/aitrading.service > /dev/null <<EOF
[Unit]
Description=AITradingLab
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/AITradingLab
ExecStart=/home/ubuntu/AITradingLab/venv/bin/python scripts/run_live.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 8. Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable aitrading
sudo systemctl start aitrading

# 9. Check status
sudo systemctl status aitrading
sudo journalctl -f -u aitrading  # View logs
```

---

## 📱 Monitoring & Management

### Dashboard Setup
```python
# scripts/monitoring_dashboard.py

import streamlit as st
from src.zerodha_integration import ZerodhaAuthenticator
import pandas as pd

st.set_page_config(page_title="Trading Monitor", layout="wide")

auth = ZerodhaAuthenticator()
auth.load_session()

# Portfolio metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    profile = auth.kite.profile()
    st.metric("Account Balance", f"₹{profile['equity_intraday']:,.0f}")

with col2:
    holdings = auth.kite.holdings()
    st.metric("Total Holdings", len(holdings))

with col3:
    positions = auth.kite.positions()
    st.metric("Open Positions", len(positions['net']))

with col4:
    pnl = sum([h['pnl'] for h in holdings])
    st.metric("P&L Today", f"₹{pnl:,.0f}")

# Detailed table
st.subheader("Holdings")
holdings_df = pd.DataFrame(holdings)
st.dataframe(holdings_df[['tradingsymbol', 'quantity', 'average_price', 'last_price', 'pnl']])

st.subheader("Open Positions")
positions_df = pd.DataFrame(positions['net'])
st.dataframe(positions_df[['tradingsymbol', 'quantity', 'average_price', 'last_price', 'pnl']])

# Refresh every 5 seconds
import time
st.session_state.refresh = time.time()
st.rerun()
```

Run with: `streamlit run scripts/monitoring_dashboard.py`

---

## ⚠️ Risk Management Checklist

Before going live, ensure:

```
✅ Position sizing: Risk ≤ 2% per trade
✅ Stop losses: Always set in Zerodha
✅ Daily limits: Max ₹50,000 loss per day
✅ Position limits: Max 10 open positions
✅ Time limits: Close all positions by 3:20 PM
✅ Capital limits: Keep 20% cash as buffer
✅ Diversification: Max 20% in any single stock
✅ Monitoring: Check every hour during market hours
✅ Backup: Daily backup of logs and configs
✅ Emergency: Have manual close procedure ready
```

---

## 🆘 Troubleshooting

### Connection Issues
```python
# Test Zerodha connection
from src.zerodha_integration import ZerodhaAuthenticator

auth = ZerodhaAuthenticator()
try:
    auth.load_session()
    profile = auth.kite.profile()
    print(f"✅ Connected as {profile['user_name']}")
except Exception as e:
    print(f"❌ Connection error: {e}")
    print("   - Check internet connection")
    print("   - Check API credentials")
    print("   - Verify session token not expired")
```

### Email Not Sending
```python
from src.email_alerts import EmailAlertConfig, EmailAlertSender

config = EmailAlertConfig()
sender = EmailAlertSender(config)

try:
    sender.send_signal_alert(
        symbol='NSE:INFY',
        signal=1,
        price=1200,
        confidence=80
    )
    print("✅ Email sent successfully")
except Exception as e:
    print(f"❌ Email error: {e}")
    print("   - Check Gmail credentials")
    print("   - Verify 'Less secure app access' enabled")
    print("   - Check recipient email valid")
```

### Strategy Not Generating Signals
```python
# Debug signal generation
from src.advanced_ai import generate_ma_crossover_signals
import pandas as pd
import yfinance as yf

df = yf.download('INFY.NS', period='1mo')
signals = generate_ma_crossover_signals(df, 20, 50)

print(f"Total signals: {(signals != 0).sum()}")
print(f"Buy signals: {(signals == 1).sum()}")
print(f"Sell signals: {(signals == -1).sum()}")
print(f"Last signal: {signals.iloc[-1]}")

# Check MA values
import numpy as np
sma_20 = df['Close'].rolling(20).mean()
sma_50 = df['Close'].rolling(50).mean()
print(f"\nCurrent price: {df['Close'].iloc[-1]:.2f}")
print(f"SMA 20: {sma_20.iloc[-1]:.2f}")
print(f"SMA 50: {sma_50.iloc[-1]:.2f}")
```

---

## 📊 Production Monitoring

### Logging Setup
```python
# src/logger.py - Already configured
# All logs go to: logs/trading_<date>.log

import logging

logger = logging.getLogger('AITradingLab')

# All events logged:
# - Signal generation
# - Order execution
# - Email alerts
# - Errors and exceptions
# - Daily P&L

# View logs:
tail -f logs/trading_*.log
```

### Daily Report Example
```
================================
TRADING REPORT - 2024-01-15
================================

Market Hours: 9:15 AM - 3:30 PM IST
Signals Generated: 5
Orders Placed: 4
Orders Successful: 3
Orders Failed: 1

Symbols Traded:
- NSE:INFY  (1 buy, 0 sell)
- NSE:SBIN  (1 buy, 1 sell)
- NSE:BAJAJFINSV (1 sell, 0 buy)

Daily P&L: +₹2,450 (+2.45%)

Email Alerts: 4 sent successfully

Errors: None

Next trading day: 2024-01-16
================================
```

---

## 🎯 Success Metrics

Track these while live trading:

```python
# scripts/track_metrics.py

import json
from datetime import datetime

def log_daily_metrics(date, trades, pnl, sharpe, win_rate):
    """Log daily metrics for analysis"""
    
    metrics = {
        'date': str(date),
        'trades': trades,
        'pnl': pnl,
        'sharpe': sharpe,
        'win_rate': win_rate,
        'timestamp': str(datetime.now())
    }
    
    with open('metrics/live_metrics.jsonl', 'a') as f:
        f.write(json.dumps(metrics) + '\n')

# Target metrics (rolling 30-day average):
# ✅ Win rate: > 45%
# ✅ Sharpe ratio: > 1.0
# ✅ Avg P&L per trade: > ₹1,000
# ✅ Max drawdown: < 15%
# ✅ Recovery factor: > 2.0
```

---

## ✅ Final Go-Live Checklist

```
[ ] ✅ All backtests passed
[ ] ✅ Walk-forward validation passed
[ ] ✅ Parameter sensitivity tested
[ ] ✅ Market regime testing passed
[ ] ✅ Zerodha credentials configured
[ ] ✅ Gmail alerts tested
[ ] ✅ Position sizing calculated
[ ] ✅ Stop losses defined
[ ] ✅ Risk management rules set
[ ] ✅ Monitoring dashboard ready
[ ] ✅ Logging configured
[ ] ✅ Emergency procedures documented
[ ] ✅ Capital allocated (starting small)
[ ] ✅ Daily report setup
[ ] ✅ Team/family notified (if applicable)

🚀 APPROVED FOR LIVE TRADING 🚀
```

---

**🎯 You are now ready to deploy AITradingLab live! Start small (1-2 shares per trade), monitor closely, and scale gradually based on results.**

**Questions? Check QUICK_REFERENCE.md or TESTING_VALIDATION_GUIDE.md**

