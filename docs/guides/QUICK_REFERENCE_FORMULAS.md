# Quick Reference: Portfolio Scoring Formulas

## Summary Sheet

### 1. FundScore Calculation
```
FundScore = (ROE × 4)_capped at 2.0
          + (RevGrowth + EPSGrowth) × 2_capped at 1.5
          + (ProfitMargin × 3)_capped at 1.0
          - (PE ÷ 50)_capped at 1.0
          - max(Beta - 1.2, 0) × 0.5
          + Sentiment × 0.3

With Safe Defaults (when data unavailable):
  - ROE defaults to 0.0 (neutral)
  - Growth defaults to 0.0 (neutral)
  - Margin defaults to 0.0 (neutral)
  - PE defaults to 20.0 (moderate valuation, not expensive)
  - Beta defaults to 1.0 (market correlation)
  - Sentiment defaults to 0.0 (no bias)

Result: FundScore is typically -1.0 to +3.0
```

### 2. FundNorm (Normalization)
```
FundNorm = min(max((FundScore + 1.0) ÷ 3.0, 0.0), 1.0)

This converts raw score to 0-1 range:
  FundScore -1.0  →  FundNorm 0.0 (Terrible)
  FundScore  0.0  →  FundNorm 0.33 (Average)
  FundScore +1.0  →  FundNorm 0.67 (Good)
  FundScore +2.0  →  FundNorm 1.0 (Excellent)
  FundScore >2.0  →  FundNorm 1.0 (Capped)

IMPORTANT: If FundScore can't be calculated = FundNorm shows "N/A"
```

### 3. TechNorm (Technical Normalization)
```
SMA_align  = 1.0 if (SMA5 > SMA20 > SMA50) else 0.0                [Weight: 1.5]
EMA_cross  = 1.0 if (EMA12 > EMA26) else 0.0                      [Weight: 0.8]
MACD_pos   = 1.0 if (MACD > 0) else 0.0                           [Weight: 0.7]
RSI_score  = min(max((RSI14 - 30) ÷ 40, 0.0), 1.0)               [Weight: 1.0]
             Converts RSI 30-70 range to 0-1
Vol_score  = min(max((VolRatio - 1.0) ÷ 2.0, 0.0), 1.0)          [Weight: 0.5]
             Converts volume above 20-day MA to 0-1

TechNorm = (1.5×SMA_align + 0.8×EMA_cross + 0.7×MACD_pos 
           + 1.0×RSI_score + 0.5×Vol_score) ÷ 4.5

Result: Always 0.0 (Bearish) to 1.0 (Bullish)
```

### 4. Combined Score
```
IF Fundamentals Available (FundScore calculated):
  Combined = 0.60 × TechNorm + 0.40 × FundNorm

IF Fundamentals NOT Available (marked as N/A):
  Combined = 0.75 × TechNorm + 0.25 × FundNorm
  (Uses neutral 0.5 for the missing FundNorm)

Result: 0.0 to 1.0 scale
```

### 5. Recommendations
```
IF Combined >= 0.65:
  Recommendation = "Hold"

ELSE IF Combined >= 0.45:
  Recommendation = "Watch / Partial Hold"

ELSE (Combined < 0.45):
  Recommendation = "Consider Sell"

NOTE: Add " [Limited Fund Data]" suffix if FundScore not available
```

---

## Component Reference

### Fundamental Components
```
Component      | Source      | Ideal Range  | Cap in Formula | Effect of High Value
─────────────────────────────────────────────────────────────────────────────────
ROE            | Company     | > 15%        | 2.0 max        | +0.6 to +2.0
RevenueGrowth  | Company     | 5-20%        | 0.75 max       | +0.15 to +0.75
EPSGrowth      | Company     | 5-20%        | 0.75 max       | +0.15 to +0.75
ProfitMargin   | Company     | 10-20%       | 1.0 max        | +0.3 to +1.0
PE Ratio       | Yahoo Fin   | 15-25        | -1.0 penalty   | -0.3 to -1.0
Beta           | Yahoo Fin   | 0.8-1.2      | -0.5 max       | 0 to -0.5
Sentiment      | News        | -1 to +1     | None           | -0.3 to +0.3
```

### Technical Components
```
Component      | Indicator           | Bullish Value | Weight
──────────────────────────────────────────────────────────────
SMA Alignment  | 5 > 20 > 50         | 1.0           | 1.5
EMA Crossover  | EMA12 > EMA26       | 1.0           | 0.8
MACD Positive  | MACD > 0            | 1.0           | 0.7
RSI Momentum   | 50-70 range         | 1.0 at 70     | 1.0
Volume Trend   | Vol > 20d MA        | 1.0 at 3x MA  | 0.5
```

---

## Decision Tree

```
Portfolio Analysis Flow:

┌─────────────────────────────────────────┐
│ Load Stock Data (need ≥ 60 days)       │
├─────────────────────────────────────────┤
│ Calculate Technical Indicators
│ (27 indicators: SMA, EMA, RSI, MACD...)
├─────────────────────────────────────────┤
│ Fetch Fundamentals (ROE, PE, Growth...) │
├─────────────────────────────────────────┤
│ Fundamentals Available? (not all NaN)   │
│    ↙                               ↘
│   YES                              NO
│    ↓                               ↓
│ Calculate FundScore            FundScore = N/A
│    ↓                           FundNorm = "N/A"
│ Normalize to FundNorm (0-1)    Use: 0.75T + 0.25F
│ Use: 0.60T + 0.40F             ↓
│    ↓                        OUTPUT:
│    └──→ Combined Score    ┌─────────────────┐
│        = 0.60×Tech        │ Symbol          │
│        + 0.40×Fund        │ TechNorm = XX   │
│                           │ FundNorm = N/A  │
│ OUTPUT:                    │ Combined = XX   │
│ ┌─────────────────────┐   │ Rec: ...        │
│ │ Symbol              │   │ [Limited Fund]  │
│ │ FundScore = XX      │   └─────────────────┘
│ │ FundNorm = XX       │
│ │ TechNorm = XX       │
│ │ Combined = XX       │
│ │ Recommendation:     │
│ │  ≥0.65: Hold        │
│ │  0.45-0.65: Watch   │
│ │  <0.45: Sell        │
│ └─────────────────────┘
```

---

## Common Scenarios & Their Meanings

### Scenario 1: High Tech, Low Fund (All Fields Populated)
```
FundScore = -0.5  (Poor fundamentals)
FundNorm = 0.17
TechNorm = 0.85   (Strong bullish trend)
Combined = 0.6 × 0.85 + 0.4 × 0.17 = 0.51 + 0.07 = 0.58
Recommendation = "Watch / Partial Hold"

Interpretation:
  ✓ Price is trending up strongly
  ✗ Company fundamentals are weak (expensive, low growth)
  → Opportunity: Buy on pullback when price weakness confirms
  → Risk: If technicals reverse, support from fundamentals is weak
```

### Scenario 2: High Fund, Low Tech (All Fields Populated)
```
FundScore = 2.0   (Excellent fundamentals)
FundNorm = 1.0
TechNorm = 0.35   (Weak/declining trend)
Combined = 0.6 × 0.35 + 0.4 × 1.0 = 0.21 + 0.40 = 0.61
Recommendation = "Watch / Partial Hold"

Interpretation:
  ✓ Company is solid, profitable, growing
  ✗ Price is falling, bearish technical setup
  → Opportunity: Potential value buy (strong company, weak price)
  → Risk: If company health deteriorates, price could fall more
```

### Scenario 3: Both Good, Perfect Combo (All Fields Populated)
```
FundScore = 1.5   (Good fundamentals)
FundNorm = 0.83
TechNorm = 0.80   (Strong bullish trend)
Combined = 0.6 × 0.80 + 0.4 × 0.83 = 0.48 + 0.33 = 0.81
Recommendation = "Hold"

Interpretation:
  ✓ Both fundamentals and technicals align
  ✓ Company is healthy AND price is trending up
  → Opportunity: High confidence entry/hold point
  → Next level: Follow from entry; reduces risk of false breakout
```

### Scenario 4: Limited Fundamental Data (FundNorm = N/A)
```
FundScore = N/A
FundNorm = "N/A"
TechNorm = 0.72
Combined = 0.75 × 0.72 + 0.25 × 0.5 = 0.54 + 0.125 = 0.665
Recommendation = "Hold [Limited Fund Data]"

Interpretation:
  ? Company fundamentals not available on yfinance
  ✓ Price is trending bullishly
  → Means: Use technical signals with extra caution (check company manually)
  → Action: Read news/earnings separately before trading
  → Note: Not a red flag! Many good stocks have missing data
```

### Scenario 5: Weak Both Ways
```
FundScore = -1.2
FundNorm = 0.0
TechNorm = 0.20
Combined = 0.6 × 0.20 + 0.4 × 0.0 = 0.12
Recommendation = "Consider Sell"

Interpretation:
  ✗ Company fundamentals are poor
  ✗ Price is falling/weak
  → Action: Avoid or exit if holding
  → Only trade: Short-term technical bounce for scalping
```

---

## What Changed in App (Latest Fix)

### Before
- FundScore sometimes showed NaN/missing when data unavailable
- Fundamental data missing → All stocks flagged "Sell" incorrectly

### After
- Safe defaults kick in when data unavailable (default PE=20, not 50)
- FundScore/FundNorm display "N/A" instead of NaN
- System switches to tech-heavy weighting (75% vs 60%) when fund data missing
- Explicit note "[Limited Fund Data]" clarifies why FundNorm is N/A
- Expandable info box explains the scoring on the UI

---

## Testing the Formulas

### Example Stock: INFY.NS (Infosys)

```
Given Data:
  ROE = 20%, RevGrowth = 8%, EPSGrowth = 10%
  ProfitMargin = 14%, PE = 22, Beta = 0.9
  Sentiment = 0.2
  
  SMA5=1800, SMA20=1750, SMA50=1700, SMA200=1600 (✓ aligned)
  EMA12=1780, EMA26=1760 (✓ bullish)
  MACD = +15 (✓ positive)
  RSI14 = 65 (→ score 0.875)
  Vol = 2.5M, VolMA20 = 2.0M (✓ above)

Calculation:

1. FundScore = min(20×4, 2.0) + min((8+10)×2, 1.5) + min(14×3, 1.0) 
             - min(22÷50, 1.0) - max(0.9-1.2, 0)×0.5 + 0.2×0.3
             = 2.0 + 1.5 + 1.0 - 0.44 - 0 + 0.06
             = 4.12 → clamped to 2.0 max components = 3.06 ✓
             
   Actually: 2.0 + 1.5 + 1.0 - 0.44 - 0 + 0.06 = 4.76
   But ROE capped at 2.0, so use: 2.0 + 1.5 + 1.0 - 0.44 - 0 + 0.06 = 4.12
   
   Wait, let me recalculate:
   ROE: min(20×4, 2.0) = min(80, 2.0) = 2.0 ✓
   Growth: min(18×2, 1.5) = min(36, 1.5) = 1.5 ✓
   Margin: min(14×3, 1.0) = min(42, 1.0) = 1.0 ✓
   PE: min(22/50, 1.0) = min(0.44, 1.0) = 0.44 ✓
   Beta: max(0.9-1.2, 0) = max(-0.3, 0) = 0, so 0×0.5 = 0 ✓
   Sentiment: 0.2×0.3 = 0.06 ✓
   
   FundScore = 2.0 + 1.5 + 1.0 - 0.44 - 0 + 0.06 = 4.12

2. FundNorm = min(max((4.12+1.0)/3.0, 0.0), 1.0)
            = min(max(5.12/3.0, 0.0), 1.0)
            = min(max(1.707, 0.0), 1.0)
            = min(1.707, 1.0)
            = 1.0 (Excellent) ✓

3. TechNorm = (1.5×1 + 0.8×1 + 0.7×1 + 1.0×0.875 + 0.5×1.0) / 4.5
            = (1.5 + 0.8 + 0.7 + 0.875 + 0.5) / 4.5
            = 4.375 / 4.5
            = 0.972 (Very bullish) ✓

4. Combined = 0.6 × 0.972 + 0.4 × 1.0
            = 0.5832 + 0.4
            = 0.9832 (Excellent score) ✓

✓ Recommendation = "Hold"
```

---

## Summary

| Metric | Purpose | Range | How Calculated |
|--------|---------|-------|-----------------|
| **FundScore** | Raw fundamental health | -1 to 3 | 6-part formula with ROE, growth, margins |
| **FundNorm** | Normalized fundamentals | 0 to 1 | (FundScore + 1) / 3 |
| **TechNorm** | Normalized technicals | 0 to 1 | Weighted avg of 5 trend indicators |
| **Combined** | Final score | 0 to 1 | 60%TechNorm + 40%FundNorm (or 75/25) |
| **XGBoost** | ML predictions | 0 to 100% | Full Analysis only (NOT portfolio) |

