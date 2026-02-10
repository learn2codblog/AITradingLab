# Portfolio Analysis Scoring Explained

## Understanding the Scores

### 1. **FundScore** (Raw Fundamental Score)
This is a **raw, unnormalized score** calculated from company financials:

```
FundScore = 
  + min(ROE × 4, 2.0)                    # Profitability (higher ROE = better)
  + min(Growth × 2, 1.5)                 # Growth (RevGrowth + EPSGrowth, higher = better)
  + min(Margin × 3, 1.0)                 # Profit margin (higher = better)
  - min(PE / 50, 1.0)                    # Valuation penalty (higher PE = worse)
  - max(Beta - 1.2, 0) × 0.5             # Risk penalty (higher beta = worse)
  + Sentiment × 0.3                      # News sentiment bonus
```

**Range**: Usually -1.0 to +3.0 (unbounded)
- Negative FundScore = Poor fundamentals (high PE, low ROE, declining revenue)
- Positive FundScore = Good fundamentals (healthy ROE, growth, margins)

**Example:**
- Stock with ROE=25%, Growth=5%, Margin=15%, PE=20, Beta=1.0, Sentiment=0.5
  - FundScore ≈ 2.0 + 0.7 + 0.45 - 0.4 - 0 + 0.15 = **2.9** (Very Good)

- Stock with ROE=5%, Growth=-2%, Margin=-5%, PE=60, Beta=1.5, Sentiment=-0.5
  - FundScore ≈ 0.2 - 0.08 - 0.15 - 1.2 - 0.25 - 0.15 = **-1.63** (Poor)

---

### 2. **FundNorm** (Normalized Fundamental Score 0-1)
This converts FundScore to a **0-1 scale** for comparison:

```
FundNorm = min(max((FundScore + 1.0) / 3.0, 0.0), 1.0)
```

**Mapping:**
- FundScore = -1.0 → FundNorm = 0.0 (bad)
- FundScore = 0.0 → FundNorm = 0.33 (neutral)
- FundScore = +2.0 → FundNorm = 1.0 (excellent)

**Range**: 0.0 to 1.0

---

### 3. **TechNorm** (Normalized Technical Score 0-1)
This evaluates **price trends and momentum**:

```
TechNorm = (
    + SMA Alignment (1.5 weight)    # Is SMA5 > SMA20 > SMA50?
    + EMA Cross (0.8 weight)        # Is EMA12 > EMA26?
    + MACD Positive (0.7 weight)    # Is MACD > 0?
    + RSI Score (1.0 weight)        # Maps RSI14 [30-70] to [0-1]
    + Volume Score (0.5 weight)     # Is volume above average?
) / 4.5  # Normalize by total weights
```

**Range**: 0.0 to 1.0
- 0.0 = Bearish (all signals negative)
- 0.5 = Neutral (mixed signals)
- 1.0 = Very Bullish (all signals positive)

---

### 4. **Combined Score** (Final Decision Score)
Weighted average of both:

```
Combined = 0.6 × TechNorm + 0.4 × FundNorm
```

**Weights:**
- 60% Technical (short-term trends matter more)
- 40% Fundamental (long-term quality matters less)

**Recommendation Logic:**
- Combined ≥ 0.65 → **Hold** (Good both ways)
- Combined 0.45-0.65 → **Watch / Partial Hold** (Mixed signals)
- Combined < 0.45 → **Consider Sell** (Poor fundamentals or technicals)

---

## Why "Sell" is Being Flagged

### Scenario 1: "Sell" with High TechNorm, Low FundNorm
```
Example:
  TechNorm = 0.95  (Bullish trend)
  FundNorm = 0.10  (Poor fundamentals - high PE, low growth)
  Combined = 0.6 × 0.95 + 0.4 × 0.10 = 0.57 + 0.04 = 0.61 → Hold

But if:
  TechNorm = 0.80  (Moderately bullish)
  FundNorm = 0.15  (Poor fundamentals)
  Combined = 0.6 × 0.80 + 0.4 × 0.15 = 0.48 + 0.06 = 0.54 → Hold (borderline)

If:
  TechNorm = 0.60  (Weak technical)
  FundNorm = 0.15  (Poor fundamentals)
  Combined = 0.6 × 0.60 + 0.4 × 0.15 = 0.36 + 0.06 = 0.42 → SELL
```

**Reason**: Poor fundamentals drag down overall score even if technicals are good.

---

## Why FundScore/FundNorm Might Not Show

### Issue 1: Missing Fundamental Data
If `get_fundamentals(sym)` returns None or incomplete data:
```python
roe = f.get('ROE', 0)  # Defaults to 0 if missing
pe = f.get('PE', 50)   # Defaults to 50 (expensive stock) if missing
```
With default values, FundScore becomes artificially low.

### Issue 2: Stock Not Found or Delisted
If ticker is invalid, fundamental data APIs return None/zero.

### Issue 3: Insufficient Data
If stock has <60 days of history, calculation fails silently.

---

## Role of XGBoost

XGBoost is **NOT used** in Fundamental/Technical/Portfolio Analysis buttons.

XGBoost is **ONLY used** in the **"Run Full Analysis"** button:

### What XGBoost Does in Full Analysis:
1. **Trains on 60 engineered features** (technical + fundamental + derived)
2. **Predicts future returns** (5-day horizon by default)
3. **Generates trading signals** with confidence scores
4. **Backtests the strategy** vs buy & hold
5. **Shows feature importance** (which features matter most)

### Why XGBoost?
- Captures **non-linear relationships** between features
- Better than simple rules for complex patterns
- Handles 60+ features without overfitting (with regularization)
- Produces **probability scores** (not just binary up/down)

---

## Current Flow

```
┌─────────────────────────────────────────────────────┐
│ Portfolio Analysis (no ML/XGBoost involved)         │
├─────────────────────────────────────────────────────┤
│ For each stock:                                     │
│  1. Get fundamentals (ROE, PE, Growth, etc.)       │
│  2. Calculate FundScore (raw)                      │
│  3. Normalize to FundNorm (0-1)                    │
│  4. Get technical indicators (SMA, RSI, MACD)      │
│  5. Calculate TechNorm (0-1)                       │
│  6. Combine = 0.6×Tech + 0.4×Fund                  │
│  7. Output: FundScore, FundNorm, TechNorm,         │
│     Combined, Recommendation                       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Full Analysis (XGBoost involved)                    │
├─────────────────────────────────────────────────────┤
│ 1. Calculate 27 technical indicators               │
│ 2. Engineer 40+ advanced features                  │
│ 3. Create target (future return > median?)         │
│ 4. Train XGBoost on 60 best features              │
│ 5. Predict probabilities                           │
│ 6. Backtest against buy & hold                     │
│ 7. Show feature importance                         │
└─────────────────────────────────────────────────────┘
```

---

## Fix: Ensure FundScore Calculates

If FundScore is showing None/blank, try:
1. **Check ticker symbols** – make sure they're valid (e.g., "INFY.NS", not typos)
2. **Use longer date range** – ensure enough history (>60 days)
3. **Enable "Allow small dataset"** checkbox if data is limited
4. **Check fundamental API** – yfinance may not have data for all symbols

---

## Recommended Adjustments

### If you want TECHNICAL signals to matter more:
Change weights in `app.py`:
```python
combined = 0.7 * tech_norm + 0.3 * fund_norm  # 70% tech, 30% fund
```

### If you want FUNDAMENTAL quality to matter more:
```python
combined = 0.4 * tech_norm + 0.6 * fund_norm  # 40% tech, 60% fund
```

### If you want HIGHER threshold for "Hold":
```python
if combined >= 0.75:      # Stricter (was 0.65)
    rec = 'Hold'
```

---

## Example: Real-World Interpretation

**Stock: ABC (FundScore=1.5, FundNorm=0.83, TechNorm=0.65, Combined=0.72)**
- ✅ Good fundamentals (ROE, growth, margins)
- ✅ Bullish technical trend
- ✅ **Recommendation: HOLD** (both signals align)

**Stock: XYZ (FundScore=-0.5, FundNorm=0.17, TechNorm=0.80, Combined=0.54)**
- ❌ Poor fundamentals (high PE, declining revenue)
- ✅ Strong bullish technical trend
- ⚠️ **Recommendation: WATCH/PARTIAL HOLD** (conflict signals)
  - *Interpretation*: Price trending up, but company is expensive. Wait for pullback or fundamental improvement.

**Stock: PQR (FundScore=2.2, FundNorm=0.87, TechNorm=0.30, Combined=0.57)**
- ✅ Excellent fundamentals
- ❌ Weak/bearish technical trend
- ⚠️ **Recommendation: WATCH/PARTIAL HOLD** (conflict signals)
  - *Interpretation*: Company is healthy, but price is falling. Could be buying opportunity.

---

## Summary Table

| Metric | Range | Meaning |
|--------|-------|---------|
| **FundScore** | -2 to +3 | Raw fundamental rating (unbounded) |
| **FundNorm** | 0 to 1 | Normalized fundamental (0=bad, 1=excellent) |
| **TechNorm** | 0 to 1 | Normalized technical trend (0=bearish, 1=bullish) |
| **Combined** | 0 to 1 | Final weighted score (0.45=decision point) |
| **Recommendation** | 3 options | Hold / Watch / Sell |

This is a **rules-based system** (no ML), providing **transparency and explainability** for each decision.

