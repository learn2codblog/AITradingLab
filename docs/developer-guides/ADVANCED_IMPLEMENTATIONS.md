# 🚀 Advanced Implementations - Next Level Features

## 🎯 1. Hyperparameter Optimization with Optuna

### Complete Optuna Implementation

```python
import optuna
from optuna.visualization import plot_optimization_history, plot_param_importances
import pandas as pd
from src.backtester import SimpleBacktester, generate_ma_crossover_signals
from src.data_loader import load_stock_data

class StrategyOptimizer:
    """Optimize trading strategy parameters using Optuna"""
    
    def __init__(self, df: pd.DataFrame, n_trials: int = 50):
        self.df = df
        self.n_trials = n_trials
        self.study = None
        
    def optimize_ma_crossover(self) -> dict:
        """Optimize Moving Average Crossover parameters"""
        
        def objective(trial):
            # Suggest parameters
            fast_ma = trial.suggest_int('fast_ma', 5, 30)
            slow_ma = trial.suggest_int('slow_ma', 30, 100)
            
            # Ensure slow > fast
            if slow_ma <= fast_ma:
                return float('-inf')
            
            try:
                # Generate signals
                signals = generate_ma_crossover_signals(
                    self.df, fast_ma, slow_ma
                )
                
                # Backtest
                backtester = SimpleBacktester()
                result = backtester.backtest(self.df, signals)
                
                # Objective: maximize Sharpe ratio
                return result['sharpe_ratio']
            
            except Exception as e:
                return float('-inf')
        
        # Create study
        self.study = optuna.create_study(direction='maximize')
        self.study.optimize(objective, n_trials=self.n_trials, show_progress_bar=True)
        
        # Get results
        best_trial = self.study.best_trial
        
        return {
            'best_params': best_trial.params,
            'best_sharpe': best_trial.value,
            'n_trials': len(self.study.trials),
            'all_trials': [
                {
                    'params': t.params,
                    'sharpe': t.value
                } for t in self.study.trials
            ]
        }
    
    def optimize_rsi_parameters(self) -> dict:
        """Optimize RSI strategy parameters"""
        from src.backtester import generate_rsi_signals
        
        def objective(trial):
            rsi_period = trial.suggest_int('rsi_period', 7, 28)
            oversold = trial.suggest_int('oversold', 15, 40)
            overbought = trial.suggest_int('overbought', 60, 85)
            
            if overbought <= oversold:
                return float('-inf')
            
            try:
                signals = generate_rsi_signals(
                    self.df, rsi_period, oversold, overbought
                )
                result = SimpleBacktester().backtest(self.df, signals)
                return result['sharpe_ratio']
            except:
                return float('-inf')
        
        self.study = optuna.create_study(direction='maximize')
        self.study.optimize(objective, n_trials=self.n_trials, show_progress_bar=True)
        best_trial = self.study.best_trial
        
        return {
            'best_params': best_trial.params,
            'best_sharpe': best_trial.value
        }
    
    def optimize_custom_strategy(self, strategy_fn, param_ranges: dict) -> dict:
        """
        Optimize any custom strategy
        
        Args:
            strategy_fn: Function that takes df and params dict, returns signals
            param_ranges: Dict like {'param1': (min, max), 'param2': (min, max)}
        """
        
        def objective(trial):
            # Generate params based on ranges
            params = {}
            for param_name, (min_val, max_val) in param_ranges.items():
                if isinstance(min_val, float):
                    params[param_name] = trial.suggest_float(
                        param_name, min_val, max_val
                    )
                else:
                    params[param_name] = trial.suggest_int(
                        param_name, int(min_val), int(max_val)
                    )
            
            try:
                signals = strategy_fn(self.df, params)
                result = SimpleBacktester().backtest(self.df, signals)
                return result['sharpe_ratio']
            except:
                return float('-inf')
        
        self.study = optuna.create_study(direction='maximize')
        self.study.optimize(objective, n_trials=self.n_trials, show_progress_bar=True)
        
        return {
            'best_params': self.study.best_trial.params,
            'best_sharpe': self.study.best_trial.value
        }

# Usage Example
if __name__ == "__main__":
    # Load data
    df = load_stock_data('INFY', '2022-01-01', '2024-01-27')
    
    # Optimize MA Crossover
    optimizer = StrategyOptimizer(df, n_trials=50)
    result = optimizer.optimize_ma_crossover()
    
    print(f"Best Parameters: {result['best_params']}")
    print(f"Best Sharpe Ratio: {result['best_sharpe']:.3f}")
    
    # Use optimized parameters
    best_fast_ma = result['best_params']['fast_ma']
    best_slow_ma = result['best_params']['slow_ma']
    
    signals = generate_ma_crossover_signals(df, best_fast_ma, best_slow_ma)
    backtest_result = SimpleBacktester().backtest(df, signals)
    print(f"Optimized Strategy Sharpe: {backtest_result['sharpe_ratio']:.3f}")
```

---

## 🔗 2. Combining Transformer + Autoencoder + Backtesting

### Ensemble Prediction System

```python
import pandas as pd
import numpy as np
from src.advanced_ai import (
    predict_with_transformer,
    predict_with_lstm,
    detect_anomalies_autoencoder
)
from src.backtester import SimpleBacktester
from src.data_loader import load_stock_data

class EnsembleTradingSystem:
    """Combines multiple ML models for robust signal generation"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.transformer_pred = None
        self.lstm_pred = None
        self.anomalies = None
        
    def generate_ensemble_signal(self, confidence_threshold: float = 60.0) -> dict:
        """
        Generate trading signal from ensemble of models
        
        Returns:
            Dict with combined signal and component analysis
        """
        # 1. Transformer prediction
        print("Running Transformer prediction...")
        self.transformer_pred = predict_with_transformer(self.df)
        
        # 2. LSTM prediction
        print("Running LSTM prediction...")
        self.lstm_pred = predict_with_lstm(self.df)
        
        # 3. Anomaly detection
        print("Detecting anomalies...")
        self.anomalies = detect_anomalies_autoencoder(self.df)
        
        # Combine signals
        signals = self._combine_signals(confidence_threshold)
        
        return {
            'combined_signal': signals['signal'],
            'confidence': signals['confidence'],
            'anomaly_risk': signals['anomaly_risk'],
            'component_analysis': {
                'transformer_trend': self.transformer_pred.get('overall_trend'),
                'lstm_return': self.lstm_pred.get('expected_return'),
                'anomalies_detected': self.anomalies.get('anomalies_detected')
            }
        }
    
    def _combine_signals(self, threshold: float) -> dict:
        """Combine signals from all models"""
        
        # Transformer signal
        transformer_return = self.transformer_pred.get('expected_return', 0)
        transformer_confidence = self.transformer_pred.get('confidence', 0)
        
        # LSTM signal
        lstm_return = self.lstm_pred.get('expected_return', 0)
        lstm_confidence = self.lstm_pred.get('confidence', 0)
        
        # Anomaly check
        anomaly_ratio = self.anomalies.get('anomaly_ratio', 0)
        anomaly_risk = + 0 if anomaly_ratio < 0.05 else 50  # High anomaly = higher risk
        
        # Average expected return
        avg_return = (transformer_return + lstm_return) / 2
        avg_confidence = (transformer_confidence + lstm_confidence) / 2
        
        # Final signal
        if avg_return > 2.5 and avg_confidence > threshold:
            signal = 'STRONG BUY'
        elif avg_return > 1.0 and avg_confidence > threshold * 0.9:
            signal = 'BUY'
        elif avg_return < -2.5 and avg_confidence > threshold:
            signal = 'STRONG SELL'
        elif avg_return < -1.0 and avg_confidence > threshold * 0.9:
            signal = 'SELL'
        else:
            signal = 'HOLD'
        
        return {
            'signal': signal,
            'confidence': avg_confidence,
            'anomaly_risk': anomaly_risk,
            'composite_return': avg_return
        }
    
    def generate_signals_for_backtesting(self) -> pd.Series:
        """
        Create signals series for backtesting
        Uses only Transformer predictions (fastest)
        """
        pred = self.transformer_pred
        
        signals = pd.Series(0, index=self.df.index)
        if pred.get('overall_trend') == 'Bullish':
            signals[-1] = 1
        elif pred.get('overall_trend') == 'Bearish':
            signals[-1] = -1
        
        return signals
    
    def backtest_ensemble(self) -> dict:
        """Backtest using ensemble-generated signals"""
        
        # Generate ensemble signal
        ensemble_signal = self.generate_ensemble_signal()
        
        # Create simple buy-hold signal for backtesting
        signals = pd.Series(0, index=self.df.index)
        if 'BUY' in ensemble_signal['combined_signal']:
            signals = pd.Series(1, index=self.df.index)
        elif 'SELL' in ensemble_signal['combined_signal']:
            signals = pd.Series(-1, index=self.df.index)
        
        # Backtest
        backtester = SimpleBacktester()
        result = backtester.backtest(self.df, signals)
        
        return {
            **result,
            'ensemble_signal': ensemble_signal
        }

# Usage Example
if __name__ == "__main__":
    df = load_stock_data('INFY', '2023-01-01', '2024-01-27')
    
    # Create ensemble system
    ensemble = EnsembleTradingSystem(df)
    
    # Generate signal
    signal = ensemble.generate_ensemble_signal()
    print(f"Combined Signal: {signal['combined_signal']}")
    print(f"Confidence: {signal['confidence']:.1f}%")
    print(f"Anomaly Risk: {signal['anomaly_risk']}")
    
    # Backtest ensemble
    result = ensemble.backtest_ensemble()
    print(f"Sharpe Ratio: {result['sharpe_ratio']:.2f}")
    print(f"Return: {result['total_return_pct']:.2f}%")
```

---

## ☁️ 3. Cloud Deployment for 24/7 Trading

### Google Colab Setup

```python
# Run this in Google Colab for free GPU training

# 1. Install packages
!pip install -q streamlit kiteconnect backtrader optuna arch nsepython

# 2. Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# 3. Copy your app
!cp '/content/drive/My Drive/AITradingLab/app_modern.py' /content/
!cp -r '/content/drive/My Drive/AITradingLab/src' /content/

# 4. Run daily trading script
import schedule
import time
from datetime import datetime

def run_daily_trading():
    """Run trading logic daily"""
    
    from src.data_loader import load_stock_data
    from src.advanced_ai import predict_with_transformer
    from src.email_alerts import AlertManager, EmailAlertConfig
    from src.zerodha_integration import AutomatedTrader, ZerodhaKite
    
    symbols = ['INFY', 'TCS', 'RELIANCE', 'WIPRO']
    
    for symbol in symbols:
        try:
            # Get latest data
            df = load_stock_data(symbol, '2023-01-01', datetime.now().strftime('%Y-%m-%d'))
            
            # Predict
            pred = predict_with_transformer(df)
            
            # Send alert
            config = EmailAlertConfig()
            alert_mgr = AlertManager(config)
            alert_mgr.check_and_alert_signal(
                symbol, 
                {
                    'recommendation': 'BUY' if pred['expected_return'] > 2 else 'SELL',
                    'confidence': pred['confidence']
                },
                df['Close'].iloc[-1]
            )
            
            # Send email summary
            print(f"{symbol}: {pred['overall_trend']}")
        
        except Exception as e:
            print(f"Error for {symbol}: {str(e)}")

# Schedule for daily execution (9:30 AM)
schedule.every().day.at("09:30").do(run_daily_trading)

# Keep running
while True:
    schedule.run_pending()
    time.sleep(60)
```

### AWS Lambda Serverless Setup

```python
# Deploy as AWS Lambda function for 24/7 execution
# File: lambda_function.py

import json
import boto3
from src.data_loader import load_stock_data
from src.advanced_ai import predict_with_transformer
from src.email_alerts import AlertManager
from src.zerodha_integration import ZerodhaKite
from datetime import datetime

def lambda_handler(event, context):
    """AWS Lambda entry point"""
    
    symbols = ['INFY', 'TCS', 'RELIANCE']
    results = []
    
    for symbol in symbols:
        try:
            # Load data
            df = load_stock_data(
                symbol, 
                '2023-01-01', 
                datetime.now().strftime('%Y-%m-%d')
            )
            
            # Predict
            pred = predict_with_transformer(df)
            
            # Send alert via SNS
            sns = boto3.client('sns')
            sns.publish(
                TopicArn='arn:aws:sns:region:account:trading-alerts',
                Subject=f'{symbol} Trade Alert',
                Message=json.dumps(pred, indent=2)
            )
            
            results.append({
                'symbol': symbol,
                'trend': pred['overall_trend'],
                'status': 'success'
            })
        
        except Exception as e:
            results.append({
                'symbol': symbol,
                'error': str(e),
                'status': 'failed'
            })
    
    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }

# CloudFormation Template: lambda_serverless.yaml
# This deploys Lambda automatically

AWSTemplateFormatVersion: '2010-09-09'
Description: 'AI Trading Lambda Function'

Resources:
  TradingLambda:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: AITrading
      Runtime: python3.9
      Handler: lambda_function.lambda_handler
      Code:
        ZipFile: |
          # Your lambda_function.py code here
      Timeout: 300
      MemorySize: 1024
      Environment:
        Variables:
          ZERODHA_API_KEY: !Ref ZerodhaAPIKey
          GMAIL_PASSWORD: !Ref GmailPassword
  
  ScheduleRule:
    Type: AWS::Events::Rule
    Properties:
      ScheduleExpression: 'cron(30 9 ? * MON-FRI *)'
      State: ENABLED
      Targets:
        - Arn: !GetAtt TradingLambda.Arn
          RoleArn: !GetAtt LambdaRole.Arn
```

---

## 📱 4. Monitoring with Email Alerts + Live Trading

### Complete Monitoring Dashboard

```python
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from src.zerodha_integration import ZerodhaKite, analyze_portfolio
from src.advanced_ai import predict_with_transformer
from src.email_alerts import AlertManager

def monitoring_dashboard(kite: ZerodhaKite, alert_mgr: AlertManager):
    """Real-time portfolio and alert monitoring"""
    
    st.title("📊 Live Trading Monitor")
    
    # Real-time metrics
    col1, col2, col3, col4 = st.columns(4)
    
    portfolio = analyze_portfolio(kite)
    
    with col1:
        st.metric(
            "Portfolio Value",
            f"₹{portfolio['total_current_value']:,.0f}",
            f"{portfolio['total_return_percent']:+.2f}%"
        )
    
    with col2:
        st.metric(
            "Available Margin",
            f"₹{portfolio['available_margin']:,.0f}",
            f"{portfolio['margin_utilization']:.1f}% used"
        )
    
    with col3:
        st.metric(
            "Total P&L",
            f"₹{portfolio['total_pnl']:,.0f}",
            "Live"
        )
    
    with col4:
        st.metric(
            "Holdings",
            len(portfolio['holdings']),
            f"{len(portfolio['positions'])} positions"
        )
    
    # Holdings table
    st.subheader("Holdings")
    holdings_df = pd.DataFrame(portfolio['holdings'])
    st.dataframe(holdings_df, use_container_width=True)
    
    # Alert history
    st.subheader("Alert History")
    alert_history = alert_mgr.get_alert_history(limit=10)
    if alert_history:
        hist_df = pd.DataFrame(alert_history)
        st.dataframe(hist_df, use_container_width=True)
    
    # Active trades
    st.subheader("Active Positions")
    if portfolio['positions']:
        pos_df = pd.DataFrame(portfolio['positions'])
        st.dataframe(pos_df, use_container_width=True)
    else:
        st.info("No active positions")

# Run monitoring (add to app_modern.py)
if __name__ == "__main__":
    # Initialize
    auth = ZerodhaAuthenticator(api_key, api_secret)
    auth.load_session('.zerodha_session')
    
    kite = ZerodhaKite(auth)
    config = EmailAlertConfig()
    alert_mgr = AlertManager(config)
    
    # Show dashboard
    monitoring_dashboard(kite, alert_mgr)
```

---

## 🎯 5. Scaling Strategies Across Multiple Symbols

### Portfolio-Level Strategy Manager

```python
import pandas as pd
from typing import List, Dict
from src.data_loader import load_stock_data
from src.advanced_ai import predict_with_transformer
from src.backtester import SimpleBacktester, generate_ma_crossover_signals

class PortfolioStrategyManager:
    """Manage and run strategies across multiple symbols"""
    
    def __init__(self, symbols: List[str], start_date: str, end_date: str):
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.data_cache = {}
        self.results = {}
        
    def load_all_data(self):
        """Pre-load all symbol data"""
        print(f"Loading data for {len(self.symbols)} symbols...")
        
        for symbol in self.symbols:
            try:
                df = load_stock_data(symbol, self.start_date, self.end_date)
                self.data_cache[symbol] = df
                print(f"✓ {symbol}: {len(df)} rows")
            except Exception as e:
                print(f"✗ {symbol}: {str(e)}")
    
    def run_transformer_signals(self, confidence_threshold: float = 60) -> Dict:
        """Generate Transformer signals for all symbols"""
        
        predictions = {}
        
        for symbol, df in self.data_cache.items():
            try:
                pred = predict_with_transformer(df)
                
                if pred.get('expected_return', 0) > 2 and \
                   pred.get('confidence', 0) > confidence_threshold:
                    signal = 'BUY'
                elif pred.get('expected_return', 0) < -2 and \
                     pred.get('confidence', 0) > confidence_threshold:
                    signal = 'SELL'
                else:
                    signal = 'HOLD'
                
                predictions[symbol] = {
                    'signal': signal,
                    'return_pct': pred.get('expected_return'),
                    'confidence': pred.get('confidence'),
                    '5_day_target': pred.get('predictions', {}).get('5_day', {}).get('price')
                }
            
            except Exception as e:
                predictions[symbol] = {'error': str(e)}
        
        return predictions
    
    def run_backtests(self, strategy_fn=None) -> Dict:
        """Run backtests across all symbols"""
        
        results = {}
        
        for symbol, df in self.data_cache.items():
            try:
                if strategy_fn is None:
                    signals = generate_ma_crossover_signals(df, 20, 50)
                else:
                    signals = strategy_fn(df)
                
                backtester = SimpleBacktester()
                bt_result = backtester.backtest(df, signals)
                
                results[symbol] = {
                    'sharpe': bt_result['sharpe_ratio'],
                    'return_pct': bt_result['total_return_pct'],
                    'max_drawdown': bt_result['max_drawdown_pct'],
                    'win_rate': bt_result['win_rate_pct'],
                    'trades': bt_result['num_trades']
                }
            
            except Exception as e:
                results[symbol] = {'error': str(e)}
        
        return results
    
    def generate_portfolio_report(self) -> pd.DataFrame:
        """Generate summary report for all symbols"""
        
        # Run signals
        signals = self.run_transformer_signals()
        
        # Run backtests
        backtests = self.run_backtests()
        
        # Combine
        report_data = []
        
        for symbol in self.symbols:
            sig = signals.get(symbol, {})
            bt = backtests.get(symbol, {})
            
            report_data.append({
                'Symbol': symbol,
                'Signal': sig.get('signal', 'ERROR'),
                'Confidence': sig.get('confidence', 0),
                'Target': sig.get('5_day_target', 0),
                'Sharpe': bt.get('sharpe', 0),
                'Return%': bt.get('return_pct', 0),
                'Drawdown%': bt.get('max_drawdown', 0),
                'WinRate%': bt.get('win_rate', 0)
            })
        
        report_df = pd.DataFrame(report_data)
        
        # Sort by confidence
        report_df = report_df.sort_values('Confidence', ascending=False)
        
        return report_df

# Usage Example
if __name__ == "__main__":
    # Define watchlist
    nifty_50 = [
        'INFY', 'TCS', 'RELIANCE', 'HDFC', 'YHBANK',
        'ICICIBANK', 'HDFCBANK', 'SBIN', 'AIRTEL', 'BAJAJ-AUTO',
        'MARUTI', 'WIPRO', 'ADANIGREEN', 'HINDALCO', 'SUNPHARMA'
    ]
    
    # Create manager
    manager = PortfolioStrategyManager(
        nifty_50,
        start_date='2023-01-01',
        end_date='2024-01-27'
    )
    
    # Load and analyze
    manager.load_all_data()
    report = manager.generate_portfolio_report()
    
    print(report.to_string())
    
    # Save report
    report.to_csv('trading_signals.csv', index=False)
    print("\n✅ Report saved to trading_signals.csv")
    
    # Recommended actions
    buys = report[report['Signal'] == 'BUY']
    if len(buys) > 0:
        print(f"\n📈 Buy signals for: {', '.join(buys['Symbol'].tolist())}")
```

---

## 🔄 Complete Automated Trading Loop

```python
# automated_trader.py - Run this 24/7

import time
import schedule
from datetime import datetime
from portfolio_manager import PortfolioStrategyManager
from src.zerodha_integration import ZerodhaKite, AutomatedTrader
from src.email_alerts import AlertManager

class FullAutomatedTrader:
    """Complete end-to-end automated trading system"""
    
    def __init__(self, symbols: list, kite: ZerodhaKite, alert_mgr: AlertManager):
        self.symbols = symbols
        self.kite = kite
        self.alert_mgr = alert_mgr
        self.trader = AutomatedTrader(kite)
        
    def run_daily_strategy(self):
        """Execute full trading loop daily"""
        
        print(f"\n{'='*50}")
        print(f"Running Trading Strategy - {datetime.now()}")
        print(f"{'='*50}")
        
        # Generate signals/backtests
        manager = PortfolioStrategyManager(
            self.symbols,
            start_date=datetime.now().strftime('%Y-01-01'),
            end_date=datetime.now().strftime('%Y-%m-%d')
        )
        
        manager.load_all_data()
        report = manager.generate_portfolio_report()
        
        # Execute trades on BUY signals
        buy_signals = report[report['Signal'] == 'BUY']
        
        for _, row in buy_signals.iterrows():
            symbol = row['Symbol']
            confidence = row['Confidence']
            target = row['Target']
            
            # Place order
            result = self.trader.execute_signal(
                {
                    'recommendation': 'STRONG BUY',
                    'confidence': confidence
                },
                symbol=symbol,
                current_price=self.kite.get_holdings()[0]['last_price']
            )
            
            if result.get('success'):
                print(f"✅ Order placed for {symbol}")
                
                # Send alert
                self.alert_mgr.check_and_alert_signal(
                    symbol,
                    {'recommendation': 'BUY', 'confidence': confidence},
                    row['Target']
                )
            
            time.sleep(1)  # Anti-throttle
        
        print("\n✅ Daily strategy run complete!")

# Scheduler
if __name__ == "__main__":
    # Setup
    auth = ZerodhaAuthenticator(api_key, api_secret)
    auth.load_session()
    
    kite = ZerodhaKite(auth)
    config = EmailAlertConfig()
    alert_mgr = AlertManager(config)
    
    # Create trader
    trader = FullAutomatedTrader(
        symbols=['INFY', 'TCS', 'RELIANCE'],
        kite=kite,
        alert_mgr=alert_mgr
    )
    
    # Schedule: Run at 9:35 AM (after market open)
    schedule.every().day.at("09:35").do(trader.run_daily_strategy)
    
    # Keep running
    print("🚀 Automated trader started. Waiting for scheduled time...")
    while True:
        schedule.run_pending()
        time.sleep(60)
```

---

## 📝 Quick Implementation Checklist

- [ ] **Optuna**: Setup hyperparameter tuning for your strategies
- [ ] **Ensemble**: Combine Transformer + Autoencoder predictions
- [ ] **Cloud**: Deploy to Colab or AWS Lambda
- [ ] **Monitoring**: Setup email alerts + live dashboard
- [ ] **Portfolio**: Extend to 10-20 symbol watchlist
- [ ] **Automation**: Run daily trading loop

---

**Ready for production-grade AI trading! 🚀**

