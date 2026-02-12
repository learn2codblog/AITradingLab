# 🧪 Testing & Validation Guide

Complete guide to testing, validating, and certifying trading strategies before live deployment.

---

## 1️⃣ Pre-Backtest Checklist

### Code Quality
```python
# ✅ Always do this FIRST

# 1. Syntax validation
python -m py_compile src/backtester.py
python -m py_compile src/your_strategy.py

# 2. Import validation
python -c "from src.backtester import SimpleBacktester; print('OK')"

# 3. Data validation
import pandas as pd
df = pd.read_csv('data/stock.csv')
assert len(df) > 0, "Empty data"
assert 'Close' in df.columns, "Missing Close"
assert 'High' in df.columns, "Missing High"
assert 'Low' in df.columns, "Missing Low"
assert 'Volume' in df.columns, "Missing Volume"
```

### Data Quality
```python
# Check for gaps and NaNs
print(f"Missing values:\n{df.isnull().sum()}")
print(f"Date gaps: {df.index.diff().max()}")  # Should be 1 day

# Check price sanity
assert (df['High'] >= df['Low']).all(), "High < Low error"
assert (df['Close'] >= df['Low']).all(), "Close < Low error"
assert (df['Volume'] > 0).all(), "Zero volume"

# Sufficient history
assert len(df) >= 252, "Need at least 1 year of data"
```

---

## 2️⃣ Backtesting Validation

### In-Sample Testing (Full History)

```python
from src.backtester import SimpleBacktester
from src.advanced_ai import generate_ma_crossover_signals

# Load complete data
df = pd.read_csv('data/AAPL.csv', index_col='Date', parse_dates=True)
df = df.sort_index()

# Generate signals
params = {'fast_ma': 20, 'slow_ma': 50}
signals = generate_ma_crossover_signals(df, params['fast_ma'], params['slow_ma'])

# Backtest
backtester = SimpleBacktester()
result = backtester.backtest(df, signals)

# ✅ Validate results
print("=" * 50)
print("IN-SAMPLE BACKTEST RESULTS")
print("=" * 50)
print(f"Sharpe Ratio:     {result['sharpe_ratio']:.2f}")
print(f"Max Drawdown:     {result['max_drawdown']:.2%}")
print(f"Win Rate:         {result['win_rate']:.2%}")
print(f"Total Return:     {result['total_return']:.2%}")
print(f"Profit Factor:    {result['profit_factor']:.2f}")
print(f"Avg Trade:        {result['avg_trade_return']:.2%}")
print("=" * 50)

# ✅ Validation checks
assert result['sharpe_ratio'] > 1.0, "Sharpe < 1.0 (risky)"
assert result['max_drawdown'] < 0.30, "Drawdown > 30% (high risk)"
assert result['win_rate'] > 0.40, "Win rate < 40% (too many losses)"
assert result['profit_factor'] > 1.0, "Profit factor < 1 (loses money)"
assert result['total_return'] > 0.05, "Return < 5% (too low)"

print("✅ All in-sample checks PASSED!")
```

### Out-of-Sample Testing (Walk-Forward)

```python
from src.backtester import WalkForwardBacktester

# Walk-forward backtest
wf_backtester = WalkForwardBacktester(
    test_size=252,      # 1-year test windows
    train_size=502      # 2-year training windows
)

results = wf_backtester.backtest_walk_forward(
    df,
    generate_ma_crossover_signals,
    {'fast_ma': 20, 'slow_ma': 50}
)

print("=" * 50)
print("WALK-FORWARD BACKTEST RESULTS")
print("=" * 50)
print(f"Avg Sharpe (OOS): {results['avg_sharpe']:.2f}")
print(f"Std Sharpe:       {results['std_sharpe']:.2f}")
print(f"Consistency:      {results['consistency_score']:.2%}")
print(f"Total OOS Return: {results['total_oos_return']:.2%}")
print("=" * 50)

# ✅ Out-of-sample must be better than random
assert results['avg_sharpe'] > 0.5, "OOS Sharpe too low"
assert results['consistency_score'] > 0.60, "Inconsistent across folds"

print("✅ Walk-forward validation PASSED!")
```

---

## 3️⃣ Statistical Validation

### Performance Stability Test

```python
import numpy as np
from scipy import stats

def validate_strategy_stability(df, signals, params=None):
    """Test if strategy performance is stable across time periods"""
    
    # Split into 4 quarters
    quarter_len = len(df) // 4
    quarter_results = []
    
    for i in range(4):
        start = i * quarter_len
        end = (i + 1) * quarter_len if i < 3 else len(df)
        
        quarter_df = df.iloc[start:end]
        quarter_signals = signals.iloc[start:end]
        
        result = SimpleBacktester().backtest(quarter_df, quarter_signals)
        quarter_results.append(result['sharpe_ratio'])
    
    # ✅ Check consistency
    mean_sharpe = np.mean(quarter_results)
    std_sharpe = np.std(quarter_results)
    cv = std_sharpe / mean_sharpe if mean_sharpe > 0 else float('inf')
    
    print(f"\nQuarter Sharpe Ratios: {[f'{s:.2f}' for s in quarter_results]}")
    print(f"Mean: {mean_sharpe:.2f}, Std: {std_sharpe:.2f}, CV: {cv:.2f}")
    
    # CV < 0.5 = consistent
    if cv < 0.5:
        print("✅ Consistent performance across quarters")
        return True
    else:
        print("❌ Inconsistent - strategy may be overfitted")
        return False

# Test
signals = generate_ma_crossover_signals(df, 20, 50)
is_stable = validate_strategy_stability(df, signals)
```

### Drawdown Analysis

```python
def analyze_drawdowns(df, signals):
    """Analyze maximum drawdown, recovery time, and frequency"""
    
    backtester = SimpleBacktester()
    result = backtester.backtest(df, signals)
    
    # Calculate drawdown over time
    equity_curve = result['equity_curve']
    running_max = equity_curve.cummax()
    drawdown = (equity_curve - running_max) / running_max
    
    # Statistics
    max_dd = drawdown.min()
    avg_dd = drawdown[drawdown < 0].mean() if (drawdown < 0).any() else 0
    
    # Recovery time
    dd_periods = (drawdown < 0).sum()
    
    print(f"Max Drawdown:     {max_dd:.2%}")
    print(f"Avg Drawdown:     {avg_dd:.2%}")
    print(f"Drawdown Days:    {dd_periods}")
    print(f"Recovery Need:    {-max_dd * equity_curve.iloc[-1] / (1 + max_dd):.0f}%")
    
    # ✅ Validation
    assert max_dd > -0.50, "Max DD too extreme (>50%)"
    
    return {
        'max_dd': max_dd,
        'avg_dd': avg_dd,
        'dd_periods': dd_periods
    }
```

---

## 4️⃣ Risk Metrics Validation

### Sharpe Ratio Interpretation
```python
def validate_sharpe_ratio(sharpe_ratio):
    """
    ✅ Good:   > 1.0 (excess return per unit risk)
    ⚠️  Fair:   0.5-1.0 (acceptable)
    ❌ Poor:   < 0.5 (high risk relative to return)
    """
    if sharpe_ratio > 1.5:
        return "⭐⭐⭐ Excellent", True
    elif sharpe_ratio > 1.0:
        return "⭐⭐ Good", True
    elif sharpe_ratio > 0.5:
        return "⭐ Fair", False
    else:
        return "❌ Poor", False
```

### Sortino Ratio (Focus on Downside)
```python
def calculate_sortino_ratio(returns, rf_rate=0.02):
    """Sharpe but only penalizes downside volatility"""
    
    excess_returns = returns - rf_rate / 252
    downside = returns[returns < 0].std()
    
    sortino = excess_returns.mean() / downside * np.sqrt(252)
    
    # ✅ Sortino > 1.0 is good
    return sortino

# Example
daily_returns = df['Close'].pct_change()
sortino = calculate_sortino_ratio(daily_returns)
print(f"Sortino Ratio: {sortino:.2f}")
```

### Risk-Adjusted Return (Calmar Ratio)
```python
def calculate_calmar_ratio(returns, max_drawdown):
    """Annual return / maximum drawdown"""
    
    annual_return = returns.sum() * 252
    calmar = annual_return / abs(max_drawdown) if max_drawdown < 0 else 0
    
    # ✅ Calmar > 2.0 is excellent
    return calmar
```

---

## 5️⃣ Robustness Testing

### Parameter Sensitivity Test

```python
def test_parameter_sensitivity(df, strategy_func, base_params, 
                               sensitivity_range=0.2):
    """Test how sensitive strategy is to parameter changes"""
    
    results = {}
    
    for param_name in base_params:
        base_value = base_params[param_name]
        
        # Test ±20% variations
        variations = [
            base_value * (1 - sensitivity_range),
            base_value,
            base_value * (1 + sensitivity_range)
        ]
        
        sharpes = []
        for variant_value in variations:
            test_params = base_params.copy()
            test_params[param_name] = variant_value
            
            signals = strategy_func(df, test_params)
            result = SimpleBacktester().backtest(df, signals)
            sharpes.append(result['sharpe_ratio'])
        
        # Check if sensitive
        volatility = np.std(sharpes)
        results[param_name] = {
            'sharpes': sharpes,
            'volatility': volatility,
            'robust': volatility < 0.3  # < 0.3 = robust
        }
    
    print("\nPARAMETER SENSITIVITY:")
    for param, result in results.items():
        status = "✅ Robust" if result['robust'] else "❌ Sensitive"
        print(f"{param:15} Volatility: {result['volatility']:.3f} {status}")
    
    return results

# Test
sensitivity = test_parameter_sensitivity(
    df,
    generate_ma_crossover_signals,
    {'fast_ma': 20, 'slow_ma': 50}
)
```

### Market Regime Test

```python
def test_across_market_regimes(df, signals):
    """Test strategy in bull, bear, and sideways markets"""
    
    # Identify regimes using 200-day MA
    sma_200 = df['Close'].rolling(200).mean()
    
    bull = df['Close'] > sma_200
    bear = df['Close'] < sma_200
    sideways = ~bull & ~bear
    
    # Backtest each regime
    regimes = {
        'Bull': (bull, df[bull]),
        'Bear': (bear, df[bear]),
        'Sideways': (sideways, df[sideways])
    }
    
    print("\nPERFORMANCE BY MARKET REGIME:")
    for regime_name, (mask, regime_df) in regimes.items():
        if len(regime_df) < 20:
            continue
        
        regime_signals = signals[mask]
        result = SimpleBacktester().backtest(regime_df, regime_signals)
        
        print(f"{regime_name:10} Sharpe: {result['sharpe_ratio']:6.2f} "
              f"Return: {result['total_return']:7.2%} "
              f"Win Rate: {result['win_rate']:6.2%}")
```

---

## 6️⃣ Live Paper Trading Test

### Simulated Live Trading
```python
def paper_trade_backtest(df, signals, max_lookback=60):
    """
    Simulate live trading where you only use past data
    (prevents look-ahead bias)
    """
    
    equity = 100000
    position = 0
    trades = []
    
    for i in range(max_lookback, len(df)):
        # Only use data up to today
        current_price = df['Close'].iloc[i]
        signal = signals.iloc[i]
        
        if signal == 1 and position == 0:
            # Buy signal
            shares = equity * 0.95 / current_price  # 95% of capital
            position = shares
            entry_price = current_price
            trades.append({'entry': i, 'price': current_price})
            
        elif signal == -1 and position > 0:
            # Sell signal
            exit_price = current_price
            pnl = (exit_price - entry_price) * position
            equity += pnl
            position = 0
            trades[-1]['exit'] = i
            trades[-1]['pnl'] = pnl
    
    # Metrics
    total_trades = len([t for t in trades if 'exit' in t])
    winning_trades = len([t for t in trades if t.get('pnl', 0) > 0])
    
    return {
        'final_equity': equity,
        'total_return': (equity - 100000) / 100000,
        'total_trades': total_trades,
        'win_rate': winning_trades / total_trades if total_trades > 0 else 0
    }

# Test
paper_results = paper_trade_backtest(df, signals)
print(f"Paper Trade Return: {paper_results['total_return']:.2%}")
print(f"Paper Trade Win Rate: {paper_results['win_rate']:.2%}")
```

---

## 7️⃣ Full Validation Checklist

```python
def full_validation_report(df, strategy_func, params):
    """Generate complete validation report"""
    
    print("\n" + "="*60)
    print("FULL STRATEGY VALIDATION REPORT")
    print("="*60)
    
    # 1. Data Check
    print("\n1️⃣  DATA VALIDATION")
    assert len(df) >= 252, "❌ Insufficient data (need 1+ year)"
    assert df['Close'].isnull().sum() == 0, "❌ Missing Close prices"
    print("✅ Data valid")
    
    # 2. Strategy Signals
    print("\n2️⃣  SIGNAL GENERATION")
    signals = strategy_func(df, params)
    signal_count = (signals != 0).sum()
    print(f"✅ Generated {signal_count} signals ({signal_count/len(df)*100:.1f}% of bars)")
    
    # 3. In-Sample Backtest
    print("\n3️⃣  IN-SAMPLE BACKTEST")
    result = SimpleBacktester().backtest(df, signals)
    print(f"   Sharpe: {result['sharpe_ratio']:.2f}")
    print(f"   Return: {result['total_return']:.2%}")
    print(f"   Drawdown: {result['max_drawdown']:.2%}")
    print(f"   Win Rate: {result['win_rate']:.2%}")
    
    in_sample_pass = (result['sharpe_ratio'] > 0.5 and 
                      result['win_rate'] > 0.40)
    print(f"   {'✅' if in_sample_pass else '❌'} In-sample check")
    
    # 4. Out-of-Sample
    print("\n4️⃣  OUT-OF-SAMPLE VALIDATION")
    wf = WalkForwardBacktester()
    wf_result = wf.backtest_walk_forward(df, strategy_func, params)
    print(f"   OOS Sharpe: {wf_result['avg_sharpe']:.2f}")
    oos_pass = wf_result['avg_sharpe'] > 0.3
    print(f"   {'✅' if oos_pass else '❌'} OOS check")
    
    # 5. Parameter Sensitivity
    print("\n5️⃣  PARAMETER SENSITIVITY")
    sensitivity = test_parameter_sensitivity(df, strategy_func, params)
    robust_params = sum(1 for p in sensitivity.values() if p['robust'])
    print(f"   Robust parameters: {robust_params}/{len(params)}")
    
    # 6. Market Regimes
    print("\n6️⃣  MARKET REGIME TEST")
    test_across_market_regimes(df, signals)
    
    # 7. Final Verdict
    print("\n" + "="*60)
    all_pass = in_sample_pass and oos_pass and robust_params == len(params)
    if all_pass:
        print("✅✅✅ STRATEGY APPROVED FOR LIVE TRADING ✅✅✅")
    else:
        print("❌ STRATEGY NEEDS IMPROVEMENT")
    print("="*60 + "\n")
    
    return all_pass

# Run full validation
is_approved = full_validation_report(
    df,
    generate_ma_crossover_signals,
    {'fast_ma': 20, 'slow_ma': 50}
)
```

---

## 8️⃣ Integration Checklist

Before going live, verify ALL of these:

```python
# Checklist
checks = {
    "✅ Data has 2+ years": len(df) >= 504,
    "✅ No NaN values": df.isnull().sum().sum() == 0,
    "✅ Sharpe > 0.5": result['sharpe_ratio'] > 0.5,
    "✅ Win rate > 40%": result['win_rate'] > 0.40,
    "✅ Drawdown < 30%": result['max_drawdown'] < -0.30,
    "✅ OOS Sharpe > 0.3": oos_result['avg_sharpe'] > 0.3,
    "✅ Robust parameters": sensitivity_pass,
    "✅ Works in multiple regimes": regime_test_pass,
    "✅ Consistent quarterly": stability_pass,
    "✅ Profit factor > 1.5": result['profit_factor'] > 1.5
}

all_passed = all(checks.values())

for check, result in checks.items():
    print(f"{check:35} {'✅' if result else '❌'}")

if all_passed:
    print("\n🚀 READY FOR LIVE TRADING")
else:
    print("\n⚠️  MORE OPTIMIZATION NEEDED")
```

---

## 🎯 Common Pitfalls & How to Avoid Them

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| **Overfitting** | Good in-sample, bad OOS | Use walk-forward test |
| **Look-ahead Bias** | Too good to be true | Use only past data |
| **Insufficient Data** | < 252 bars | Get 2-3 years minimum |
| **Data Snooping** | Optimizing too much | Use OOS test |
| **Survivorship Bias** | Only using winners | Include delisted stocks |
| **Parameter Drift** | Works then stops | Test sensitivity |
| **Black Swan Risk** | Extreme drawdown | Stress test market crashes |

---

**Remember: A strategy that passes all tests has a 70-80% chance of working live.
A strategy that fails tests has <5% chance of working live.**

🚀 **Test thoroughly, trade with confidence!**

