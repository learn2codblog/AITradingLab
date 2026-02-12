# 📚 Strategy Templates Library

Complete ready-to-use trading strategy templates with full explanations and usage examples.

---

## 1️⃣ Mean Reversion Strategy

### Concept
Buy when price falls below moving average (mean reversion), sell on recovery.

```python
def mean_reversion_strategy(df: pd.DataFrame, params: dict) -> pd.Series:
    """
    Mean Reversion Strategy
    
    Buy: Price < MA(20) - 2*STD
    Sell: Price > MA(20)
    """
    
    ma_period = params.get('ma_period', 20)
    std_multiplier = params.get('std_mult', 2.0)
    
    sma = df['Close'].rolling(ma_period).mean()
    std = df['Close'].rolling(ma_period).std()
    
    upper_band = sma + (std_multiplier * std)
    lower_band = sma - (std_multiplier * std)
    
    signals = pd.Series(0, index=df.index)
    signals[df['Close'] < lower_band] = 1      # Buy signal
    signals[df['Close'] > upper_band] = -1     # Sell signal
    
    return signals

# Test parameters
best_params = {
    'ma_period': 20,
    'std_mult': 2.0
}

signals = mean_reversion_strategy(df, best_params)
```

**Best For**: Range-bound markets  
**Avoid**: Strong trending markets  
**Optimization Target**: Win rate, Sharpe ratio  

---

## 2️⃣ Momentum + Confirmation Strategy

### Concept
Use momentum (RSI) + trend confirmation (MACD) for robust signals.

```python
def momentum_confirmation_strategy(df: pd.DataFrame, params: dict) -> pd.Series:
    """
    Momentum + MACD Confirmation
    
    Buy: RSI > 50 AND MACD > Signal
    Sell: RSI < 50 AND MACD < Signal
    """
    
    rsi_period = params.get('rsi_period', 14)
    macd_fast = params.get('macd_fast', 12)
    macd_slow = params.get('macd_slow', 26)
    macd_signal = params.get('macd_signal', 9)
    rsi_threshold = params.get('rsi_threshold', 50)
    
    # RSI
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(rsi_period).mean()
    loss = -delta.where(delta < 0, 0).rolling(rsi_period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    # MACD
    ema_fast = df['Close'].ewm(span=macd_fast).mean()
    ema_slow = df['Close'].ewm(span=macd_slow).mean()
    macd = ema_fast - ema_slow
    macd_signal_line = macd.ewm(span=macd_signal).mean()
    
    # Signals
    signals = pd.Series(0, index=df.index)
    
    # Buy: RSI bullish + MACD confirmed
    buy_condition = (rsi > rsi_threshold) & (macd > macd_signal_line)
    signals[buy_condition] = 1
    
    # Sell: RSI bearish + MACD confirmed
    sell_condition = (rsi < (100 - rsi_threshold)) & (macd < macd_signal_line)
    signals[sell_condition] = -1
    
    return signals

# Optimization parameters
best_params = {
    'rsi_period': 14,
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,
    'rsi_threshold': 50
}
```

**Best For**: Trending markets  
**Avoid**: Choppy sideways  
**Optimization Target**: Sharpe ratio, drawdown  

---

## 3️⃣ Breakout Strategy

### Concept
Buy on breakout above resistance, sell on support break.

```python
def breakout_strategy(df: pd.DataFrame, params: dict) -> pd.Series:
    """
    Breakout Strategy using Donchian Channels
    
    Buy: Close > 20-day high
    Sell: Close < 20-day low
    """
    
    lookback = params.get('lookback', 20)
    entry_offset = params.get('entry_offset', 0)  # ATR-based offset
    
    high_20 = df['High'].rolling(lookback).max()
    low_20 = df['Low'].rolling(lookback).min()
    
    signals = pd.Series(0, index=df.index)
    
    # Breakout buy signal
    signals[df['Close'] > high_20 * (1 + entry_offset)] = 1
    
    # Support break signal
    signals[df['Close'] < low_20 * (1 - entry_offset)] = -1
    
    return signals

# Parameters
best_params = {
    'lookback': 20,
    'entry_offset': 0.002  # 0.2% above high
}
```

**Best For**: Volatile, trending stocks  
**Avoid**: Low volatility stocks  
**Optimization Target**: Returns, win rate  

---

## 4️⃣ Machine Learning + Technical Hybrid

### Concept
Use ML for prediction + technical indicators for confirmation.

```python
def ml_technical_hybrid(df: pd.DataFrame, ml_prediction: dict, 
                       params: dict) -> pd.Series:
    """
    Combine ML predictions with technical confirmation
    
    Buy: ML bullish + RSI not overbought + Price > EMA
    Sell: ML bearish + RSI not oversold + Price < EMA
    """
    
    # ML signal
    ml_trend = ml_prediction.get('overall_trend', 'Neutral')
    ml_confidence = ml_prediction.get('confidence', 0)
    
    # Technical indicators
    ema_period = params.get('ema_period', 20)
    rsi_period = params.get('rsi_period', 14)
    confidence_threshold = params.get('conf_threshold', 60)
    
    ema = df['Close'].ewm(span=ema_period).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(rsi_period).mean()
    loss = -delta.where(delta < 0, 0).rolling(rsi_period).mean()
    rsi = 100 - (100 / (1 + (gain / loss)))
    
    # Generate signals
    signals = pd.Series(0, index=df.index)
    
    if ml_trend == 'Bullish' and ml_confidence > confidence_threshold:
        # Confirm: Price > EMA and RSI < 70
        signals[(df['Close'] > ema) & (rsi < 70)] = 1
    
    elif ml_trend == 'Bearish' and ml_confidence > confidence_threshold:
        # Confirm: Price < EMA and RSI > 30
        signals[(df['Close'] < ema) & (rsi > 30)] = -1
    
    return signals
```

**Best For**: Stable, predictable stocks  
**Avoid**: Unpredictable markets  
**Optimization Target**: Sharpe, ML accuracy  

---

## 5️⃣ Volatility-Based Position Sizing

### Concept
Adjust position size based on volatility (lower vol = larger positions).

```python
def volatility_adjusted_signals(df: pd.DataFrame, 
                               base_signals: pd.Series,
                               params: dict) -> pd.Series:
    """
    Adjust signal strength by volatility regime
    
    Low vol: Full position (1 = buy 100 shares)
    High vol: Half position (0.5 = buy 50 shares)
    """
    
    vol_period = params.get('vol_period', 20)
    vol_threshold_low = params.get('vol_low', 0.01)
    vol_threshold_high = params.get('vol_high', 0.03)
    
    returns = df['Close'].pct_change()
    volatility = returns.rolling(vol_period).std()
    
    # Normalize volatility (0 = low vol, 1 = high vol)
    vol_norm = (volatility - volatility.min()) / (volatility.max() - volatility.min())
    
    # Position sizing multiplier (0.5 to 1.0)
    position_multiplier = 1.0 - (vol_norm * 0.5)
    
    # Adjust signals
    adjusted_signals = base_signals * position_multiplier
    
    return adjusted_signals
```

**Usage**:
```python
# Get base signals from any strategy
signals = mean_reversion_strategy(df, params)

# Adjust for volatility
adjusted_signals = volatility_adjusted_signals(df, signals, vol_params)
```

---

## 6️⃣ Multi-Timeframe Confirmation

### Concept
Confirm signals across multiple timeframes (daily + weekly).

```python
def multi_timeframe_strategy(df_daily: pd.DataFrame, 
                            df_weekly: pd.DataFrame,
                            params: dict) -> pd.Series:
    """
    Multi-timeframe confirmation
    
    Buy: Daily BUY signal + Weekly uptrend
    Sell: Daily SELL signal + Weekly downtrend
    """
    
    # Daily signals (MA crossover)
    daily_signals = generate_ma_crossover_signals(
        df_daily, 
        params['fast_ma'], 
        params['slow_ma']
    )
    
    # Weekly signals (smoothed)
    weekly_signals = generate_ma_crossover_signals(
        df_weekly,
        params['weekly_fast'],
        params['weekly_slow']
    )
    
    # Combine: Daily signal confirmed by weekly trend
    combined_signals = pd.Series(0, index=df_daily.index)
    
    # Buy: Daily BUY + Weekly uptrend
    combined_signals[
        (daily_signals == 1) & (weekly_signals.iloc[-1] == 1)
    ] = 1
    
    # Sell: Daily SELL + Weekly downtrend
    combined_signals[
        (daily_signals == -1) & (weekly_signals.iloc[-1] == -1)
    ] = -1
    
    return combined_signals
```

---

## 7️⃣ Risk-Management Enhanced Strategy

### Concept
Include stop-loss and take-profit management in signals.

```python
class RiskManagedStrategy:
    """Strategy with built-in risk management"""
    
    def __init__(self, df: pd.DataFrame, params: dict):
        self.df = df
        self.params = params
        self.positions = []
        
    def generate_signals_with_risks(self) -> pd.Series:
        """
        Generate signals with stop-loss and take-profit
        
        Returns: Signals with embedded risk levels
        """
        
        stop_loss_pct = self.params.get('stop_loss', 2.0)
        take_profit_pct = self.params.get('take_profit', 5.0)
        
        # Get base signals
        signals = generate_ma_crossover_signals(
            self.df,
            self.params['fast_ma'],
            self.params['slow_ma']
        )
        
        # Calculate SL/TP levels
        risk_signals = pd.DataFrame({
            'signal': signals,
            'entry_price': self.df['Close'],
            'stop_loss': self.df['Close'] * (1 - stop_loss_pct / 100),
            'take_profit': self.df['Close'] * (1 + take_profit_pct / 100),
            'risk_reward_ratio': take_profit_pct / stop_loss_pct
        })
        
        return risk_signals
    
    def backtest_with_risk(self) -> dict:
        """Backtest with risk management rules"""
        
        risk_data = self.generate_signals_with_risks()
        
        # Track stopped-out positions
        stopped_out = 0
        take_profits = 0
        
        for i in range(1, len(risk_data)):
            prev_signal = risk_data['signal'].iloc[i-1]
            
            if prev_signal == 1:  # Long position
                # Check stop loss
                if self.df['Low'].iloc[i] < risk_data['stop_loss'].iloc[i-1]:
                    stopped_out += 1
                
                # Check take profit
                elif self.df['High'].iloc[i] > risk_data['take_profit'].iloc[i-1]:
                    take_profits += 1
        
        return {
            'stopped_out': stopped_out,
            'take_profits': take_profits,
            'avg_rr_ratio': risk_data['risk_reward_ratio'].mean()
        }
```

---

## 🏆 Best Strategy for Each Market Type

| Market Type | Strategy | Why | Win Rate |
|-------------|----------|-----|----------|
| **Trending** | Momentum + MACD | Follows trend | 55-65% |
| **Range-Bound** | Mean Reversion | Buys dips | 60-70% |
| **Breakout** | Breakout | Captures moves | 45-55% |
| **Low Vol** | Position Sizing | Maximizes positions | Depends |
| **All** | Multi-Timeframe | Confirms signals | 50-60% |

---

## 🚀 Template Optimization Guide

```python
from src.backtester import SimpleBacktester
import optuna

def optimize_strategy(df, strategy_func, param_ranges):
    """Generic optimization for any strategy"""
    
    def objective(trial):
        # Build parameters
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
        
        # Generate signals
        signals = strategy_func(df, params)
        
        # Backtest
        result = SimpleBacktester().backtest(df, signals)
        
        return result['sharpe_ratio']
    
    # Optimize
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=50)
    
    return study.best_params

# Optimize mean reversion
best_params = optimize_strategy(
    df,
    mean_reversion_strategy,
    {
        'ma_period': (10, 50),
        'std_mult': (1.0, 3.0)
    }
)

print(f"Best params: {best_params}")
```

---

## 📊 Quick Reference: Parameters to Optimize

| Strategy | Parameter | Range | Impact |
|----------|-----------|-------|--------|
| MA Crossover | fast_period | 5-30 | Win rate |
| | slow_period | 30-100 | Drawdown |
| RSI | period | 7-28 | Frequency |
| | oversold | 15-40 | False signals |
| | overbought | 60-85 | False signals |
| Breakout | lookback | 10-50 | Sensitivity |
| | offset | 0-5% | False breakouts |
| Volatility | threshold | varies | Position size |

---

## 🎯 Implementation Steps

1. **Choose Strategy**: Based on market conditions
2. **Load Data**: 2-3 years minimum
3. **Backtest**: Verify strategy works
4. **Optimize**: Find best parameters
5. **Walk-Forward**: Confirm robustness
6. **Paper Trade**: Test live signals
7. **Live Trade**: Start small (1-2 shares)

---

**Pick a template, optimize it, backtest it, and start trading! 🚀**

