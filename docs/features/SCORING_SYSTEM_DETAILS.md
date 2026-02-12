# Portfolio Analysis Scoring System - Complete Guide

## Overview

The portfolio analysis uses a **hybrid rules-based scoring system** combining technical and fundamental analysis. **XGBoost is NOT involved** in portfolio analysis—it's only used in the "Full Analysis" button for ML-based predictions.

---

## 1. FundScore & FundNorm (Fundamental Analysis)

### What is FundScore?

**FundScore** is a **raw, normalized score** calculated from company financial fundamentals:

```
FundScore = (ROE × 4) 
          + (Growth × 2) 
          + (Margin × 3) 
          - (PE / 50) 
          - max(Beta - 1.2, 0) × 0.5 
          + Sentiment × 0.3
```

**Where:**
- **ROE** = Return on Equity (profitability). Higher = better. Capped at 2.0 contribution.
- **Growth** = Revenue Growth + EPS Growth (company expansion). Capped at 1.5 contribution.
- **Margin** = Net Profit Margin (efficiency). Capped at 1.0 contribution.
- **PE** = Price-to-Earnings (valuation). Higher PE penalizes the score (penalty up to -1.0).
- **Beta** = Volatility relative to market. Higher beta incurs penalty (max -0.5).
- **Sentiment** = News sentiment from recent headlines. Range -1 to +1, weighted 0.3.

**Range of FundScore:** Typically -1.0 to +3.0 (unbounded)

**Example Calculations:**

| Company Type | ROE | Growth | Margin | PE | Beta | Sentiment | FundScore | Interpretation |
|---|---|---|---|---|---|---|---|---|
| Healthy Growth | 25% | 5% | 15% | 20 | 1.0 | 0.3 | 2.9 | Excellent |
| Mature Profitable | 18% | 2% | 12% | 25 | 1.2 | 0.1 | 1.8 | Very Good |
| Neutral | 10% | 0% | 8% | 30 | 1.0 | 0.0 | 0.2 | Okay |
| Struggling | 5% | -2% | 5% | 50 | 1.5 | -0.3 | -1.5 | Poor |

### What is FundNorm?

**FundNorm** is the **normalized version** of FundScore, mapped to a 0-1 scale:

```
FundNorm = min(max((FundScore + 1.0) / 3.0, 0.0), 1.0)
```

**How it maps:**

| FundScore | Calculation | FundNorm | Meaning |
|---|---|---|---|
| -1.0 | (-1 + 1) / 3 | 0.00 | Terrible fundamentals |
| 0.0 | (0 + 1) / 3 | 0.33 | Neutral fundamentals |
| 1.0 | (1 + 1) / 3 | 0.67 | Good fundamentals |
| 2.0 | (2 + 1) / 3 | 1.00 | Excellent fundamentals |
| >2.0 | Clamped | 1.00 | Capped at excellent |

**Key Point:** FundNorm is always 0.0 to 1.0, making it comparable with TechNorm.

### Why FundScore/FundNorm Show "N/A"

`FundScore` and `FundNorm` will show **"N/A"** when:

1. **Stock not found in yfinance** (invalid ticker)
2. **Company is delisted or too new** (no historical data)
3. **International stock with missing data** (yfinance doesn't have reliable fundamentals)
4. **Financial data not available** from yfinance for that market

When this happens:
- **FundScore = Not Calculated**
- **FundNorm = Not Calculated**
- **System still runs** using only TechNorm (weighted 75% instead of 40%)
- Recommendation is flagged with **"[Limited Fund Data]"**

This is **NORMAL and NOT an error**. Many stocks (especially international ones) have incomplete fundamental data on yfinance.

---

## 2. TechNorm (Technical Analysis)

### What is TechNorm?

**TechNorm** is a normalized technical score (0-1) based on **price trends and momentum**:

```
Components:
  SMA Alignment    = Is SMA5 > SMA20 > SMA50? (1.0 if yes, 0.0 if no)     [Weight: 1.5]
  EMA Crossover    = Is EMA12 > EMA26? (1.0 if yes, 0.0 if no)           [Weight: 0.8]
  MACD Positive    = Is MACD > 0? (1.0 if yes, 0.0 if no)                [Weight: 0.7]
  RSI Score        = Maps RSI14 from [30-70] range to [0-1]              [Weight: 1.0]
                     (RSI<30=0, RSI=50=0.5, RSI>70=1.0)
  Volume Momentum  = (Current Volume / 20-day Avg Volume - 1) × 0.5      [Weight: 0.5]
                     Maps to [0-1] range

TechNorm = (1.5×SMA + 0.8×EMA + 0.7×MACD + 1.0×RSI + 0.5×Vol) / 4.5
```

**Total Weight Denominator:** 1.5 + 0.8 + 0.7 + 1.0 + 0.5 = 4.5 (normalizes to 0-1 range)

**Interpretation:**

- **TechNorm = 0.0** → Bearish (all trends negative, RSI <30, falling SMAs)
- **TechNorm = 0.5** → Neutral (mixed signals)
- **TechNorm = 1.0** → Very Bullish (all trends positive, RSI >70, rising SMAs)

### Why TechNorm Always Calculates

TechNorm is **ALWAYS available** because it uses only price data (OHLCV), which yfinance provides reliably for all valid stocks.

If `TechNorm = N/A`, it means:
- Stock symbol is invalid
- Insufficient price history (<60 days)
- Data loading failed

---

## 3. Combined Score (Final Decision)

### Formula

```
IF fundamentals available:
    Combined = 0.60 × TechNorm + 0.40 × FundNorm

IF fundamentals NOT available (marked as N/A):
    Combined = 0.75 × TechNorm + 0.25 × FundNorm
```

**Why two formulas?**
- When fundamentals exist, both matter equally: 60% tech (momentum) + 40% fundamental (quality)
- When fundamentals missing, rely more on technical signals: 75% tech + 25% fund (neutral default)

### Recommendation Thresholds

| Combined Score | Recommendation | Interpretation |
|---|---|---|
| ≥ 0.65 | **Hold** | Strong signals both ways; good entry/hold point |
| 0.45-0.65 | **Watch / Partial Hold** | Mixed signals; monitor closely before major moves |
| < 0.45 | **Consider Sell** | Weak or declining signals; risk outweighs upside |

### Real-World Examples

**Example 1: Strong Bull (Fundamentals Available)**
```
Stock: RELIANCE.NS
  FundScore = 1.5  →  FundNorm = 0.83 (Good profitability, reasonable PE)
  TechNorm = 0.95  (SMAs aligned bullishly, RSI near 70, MACD positive)
  Combined = 0.60 × 0.95 + 0.40 × 0.83 = 0.57 + 0.33 = 0.90
  ✅ Recommendation: HOLD (Strong buy/hold signal)
```

**Example 2: Rich Valuation, Bullish Momentum**
```
Stock: TCS.NS
  FundScore = 0.5  →  FundNorm = 0.50 (High PE, moderate growth)
  TechNorm = 0.85  (Bullish trends, but valuations stretched)
  Combined = 0.60 × 0.85 + 0.40 × 0.50 = 0.51 + 0.20 = 0.71
  ✅ Recommendation: HOLD (Technical momentum more important)
```

**Example 3: Good Company, Deteriorating Price**
```
Stock: HDFC.NS
  FundScore = 2.0  →  FundNorm = 1.00 (Excellent balance sheet)
  TechNorm = 0.35  (Bearish trends, RSI <40, SMAs crossed down)
  Combined = 0.60 × 0.35 + 0.40 × 1.00 = 0.21 + 0.40 = 0.61
  ⚠️ Recommendation: WATCH/PARTIAL HOLD (Conflict! Good company, bad trends → possible buying opportunity)
```

**Example 4: No Fundamental Data Available**
```
Stock: SOMESTOCK.NS
  FundScore = N/A  →  FundNorm = N/A (Fundamentals not available)
  TechNorm = 0.70  (Bullish technical trend)
  Combined = 0.75 × 0.70 + 0.25 × 0.5 = 0.525 + 0.125 = 0.65 (using neutral 0.5 for missing fund)
  ⚠️ Recommendation: HOLD [Limited Fund Data] (Based on price trends only)
```

---

## 4. Role of XGBoost

### What is XGBoost?

**XGBoost is a machine learning algorithm** that learns patterns from historical data to make predictions.

### When is XGBoost Used?

**ONLY in the "Run Full Analysis" button**, NOT in Portfolio/Fundamental/Technical analysis.

```
┌─────────────────────────────────────────────┐
│ Portfolio Analysis (NO XGBoost)             │
├─────────────────────────────────────────────┤
│ • Uses fixed rules (FundScore formula)      │
│ • Combines fundamentals + technicals        │
│ • No training/learning involved             │
│ • Results are deterministic/reproducible    │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Full Analysis (WITH XGBoost)                │
├─────────────────────────────────────────────┤
│ • Engineer 60 advanced features             │
│ • Train XGBoost on historical 5-day returns │
│ • Learns non-linear patterns                │
│ • Generates probability predictions         │
│ • Shows feature importance rankings         │
│ • Backtests strategy vs buy & hold          │
└─────────────────────────────────────────────┘
```

### What Does XGBoost Do?

1. **Creates 60 engineered features** from:
   - 27 technical indicators
   - Fundamental metrics
   - Derived/interaction features

2. **Trains on historical data** to predict:
   - Will the stock return >median in the next N days?
   - Outputs probability (0-100%) rather than binary yes/no

3. **Identifies important features**:
   - Shows which indicators matter most for this stock
   - Example: SMA50 importance 5.2%, MACD importance 3.8%, etc.

4. **Backtests the strategy**:
   - Compares model predictions vs actual market performance
   - Shows whether following signals would beat buy & hold

### Why Use XGBoost in Full Analysis?

- **Captures complexity**: Detects non-linear relationships (simple rules miss)
- **Data-driven**: Learns from actual price patterns, not hardcoded rules
- **Probabilistic**: Gives confidence scores, not just binary signals
- **Customizable**: Can adjust to prefer precision vs recall, profit vs risk

---

## 5. Comparison: Portfolio Analysis vs Full Analysis

| Aspect | Portfolio Analysis | Full Analysis |
|---|---|---|
| **Purpose** | Quick multi-stock screening | Deep single-stock analysis |
| **ML Used?** | No (rules-based) | Yes (XGBoost) |
| **Calculation** | FundScore + TechNorm combined | 60 features → XGBoost model |
| **Output** | Buy/Hold/Sell recommendation | Probability score + feature importance + backtest |
| **Speed** | Fast (< 1 sec per stock) | Slow (10-30 sec per stock) |
| **Transparency** | Fully explainable | Model is a "black box" (but shows feature importance) |
| **Best For** | Screening multiple stocks | Detailed analysis of one stock |
| **Uncertainty Handling** | Uses defaults if data missing | Fails if data insufficient |

---

## 6. Troubleshooting

### Q: Why are all FundScore/FundNorm showing "N/A"?

**Answer:** yfinance doesn't have fundamental data for those stocks. This is common for:
- International stocks not well-covered
- Small-cap companies
- Recently IPO'd stocks
- Delisted or merged companies

**Solution:** 
- System will still work using TechNorm (technical trends)
- Try manually checking financials for the company
- Recommendation will be marked "[Limited Fund Data]"

### Q: Why is a bullish stock showing "Consider Sell"?

**Answer:** Two possible reasons:

1. **Poor Fundamentals Outweigh Good Technicals**
   - Stock price is going up (TechNorm = 0.8)
   - But company is expensive/declining (FundNorm = 0.1)
   - Combined = 0.60 × 0.8 + 0.40 × 0.1 = 0.52 ≥ 0.45 = Watch (not Sell)
   - Only shows "Sell" if combined < 0.45

2. **Very Weak Technicals**
   - Even with good fundamentals, if TechNorm < 0.3
   - It could drag combined below 0.45
   - Interpretation: Company is good, but price is falling (potential dip-buy opportunity)

### Q: Should I ignore stocks marked "[Limited Fund Data]"?

**Answer:** No! They can still be good trades. The bracket just means:
- Company metrics couldn't be fetched (data limitation, not company problem)
- Recommendation is based on price trends (TechNorm) only
- With 75% weight on technicals, the signal might actually be STRONGER
- Example: A small-cap growing fast has no fundamentals on yfinance but blazing technical setup = HOLD [Limited Fund Data] is valid

---

## 7. Parameter Reference

### FundScore Components (Weights & Caps)

| Component | Weight | Cap | Effect |
|---|---|---|---|
| ROE | ×4 | 2.0 | Profitability multiplier |
| Growth (Rev+EPS) | ×2 | 1.5 | Expansion potential |
| Margin (Net Profit %) | ×3 | 1.0 | Operational efficiency |
| PE Ratio Penalty | ÷50 | 1.0 | Valuation limiter |
| Beta Excess Risk | ×0.5 | 0.5 max | Volatility penalty |
| Sentiment | ×0.3 | None | News influence (minor) |

### Portfolio Analysis Weighting

| Scenario | Tech Weight | Fund Weight |
|---|---|---|
| Fundamentals Available | 60% | 40% |
| Fundamentals Missing | 75% | 25% (forced neutral) |

### Technical Components (Weights)

| Indicator | Weight | Best Value |
|---|---|---|
| SMA Alignment (5>20>50) | 1.5 | 1.0 (bullish)\`\` |
| EMA Crossover (12>26) | 0.8 | 1.0 (bullish) |
| MACD Positive | 0.7 | 1.0 (bullish) |
| RSI14 Score | 1.0 | 0.8 (50-70 range) |
| Volume Momentum | 0.5 | 1.0 (above average) |
| **Total Denominator** | **4.5** | **Max ≈ 4.5** |

---

## 8. Key Takeaways

1. **FundScore/FundNorm** = Company financial health (0-1 scale after normalization)
2. **TechNorm** = Price momentum and trend (0-1 scale)
3. **Combined** = Weighted blend using 60/40 (or 75/25 if fund data missing)
4. **Recommendations based on Combined score thresholds** (0.65 = Hold, 0.45 = Watch, <0.45 = Sell)
5. **XGBoost is separate** – only used in "Full Analysis" for ML predictions
6. **"N/A" is normal** – doesn't mean "bad stock," just missing fundamentals data
7. **System adjusts weights** when fundamentals unavailable, relying more on technicals

---

## 9. Contact & Questions

For questions about:
- **Specific stocks**: Open the stock chart on TradingView to cross-check signals
- **System behavior**: Run "Full Analysis" to see ML predictions (XGBoost-based)
- **Algorithm tuning**: Modify weights in app.py lines around portfolio_btn section

