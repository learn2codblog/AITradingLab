# Portfolio Scoring System - Visual Guide

## The Complete Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                 PORTFOLIO ANALYSIS START                        │
└─────────────────────────────────────────────────────────────────┘

                            ↓

┌─────────────────────────────────────────────────────────────────┐
│ For Each Stock Enter (5-50 stocks):                             │
│  1. Load price data (OHLCV from yfinance)                      │
│  2. Load fundamental data (if available)                        │
│  3. Calculate 27 technical indicators                           │
└─────────────────────────────────────────────────────────────────┘

                            ↓
            ┌───────────────┴───────────────┐
            ↓                               ↓
    ┌──────────────────┐         ┌──────────────────┐
    │ TECHNICAL TRACK  │         │ FUNDAMENTAL TRACK│
    └──────────────────┘         └──────────────────┘
            ↓                               ↓

    • SMA5 > SMA20? ✓─────┐      • ROE available? ─┐
    • SMA20 > SMA50? ✓──┐ │      • PE available? ─┐│
    • EMA12 > EMA26? ✓──┼─┼─┐    • Growth avail? ──┼┐       NOT AVAILABLE?
    • MACD > 0? ✓────┐  │ │ │    • Beta available? │→ YES OR NO ─┐
    • RSI 30-70? ···─┤  │ │ │    • Sentiment calc ─┘             │
    • Vol > MA? ✓────┼──┘ │ │                                     ↓
    └──────────────────┘   │ │                            FundScore = N/A
              ↓            │ │    FundScore Formula:      FundNorm = N/A
                           │ │    ─────────────────       (Show "N/A")
    TechNorm Calc:         │ │    (ROE×4)                Use: 0.25 for fund norm
    ────────────────       │ │    + (Growth×2)           Weight: 75% Tech
    (Weight each)     ↓    │ │    + (Margin×3)
                           │ │    - (PE/50)
    1.5×SMA_align +   │    │ │    - (Beta-1.2)×0.5
    0.8×EMA_cross +   │    │ │    + Sentiment×0.3
    0.7×MACD_pos  +   │ ┌──┘ │
    1.0×RSI_score +   │ │    │    FundScore
    0.5×Vol_score) /  │ │    ↓    Calc & Normalize
    4.5              │ │   │
        ↓            │ │   │
    TechNorm        │ │   ↓
    (0-1)           │ └──→┘
                    │      ↓
                    │   FundNorm = (FundScore+1)/3
                    │   Clamped to [0, 1]
                    │      ↓
                    └─────→┘
                            ↓
    ┌───────────────────────────────────────────┐
    │ COMBINE SCORES (Decision Point)           │
    ├───────────────────────────────────────────┤
    │                                            │
    │ IF Fundamentals Available:                 │
    │   Combined = 0.60 × TechNorm +            │
    │             0.40 × FundNorm               │
    │                                            │
    │ IF No Fundamentals:                        │
    │   Combined = 0.75 × TechNorm +            │
    │             0.25 × 0.5 (neutral)          │
    │                                            │
    └───────────────────────────────────────────┘
                            ↓
    ┌───────────────────────────────────────────┐
    │ GENERATE RECOMMENDATION                   │
    ├───────────────────────────────────────────┤
    │                                            │
    │ if Combined ≥ 0.65:                        │
    │    Rec = "Hold"                           │
    │                                            │
    │ elif Combined ≥ 0.45:                      │
    │    Rec = "Watch / Partial Hold"           │
    │                                            │
    │ else:                                      │
    │    Rec = "Consider Sell"                  │
    │                                            │
    │ if No Fundamentals:                        │
    │    Add suffix: " [Limited Fund Data]"     │
    │                                            │
    └───────────────────────────────────────────┘
                            ↓
    ┌───────────────────────────────────────────┐
    │ OUTPUT ROW                                │
    ├───────────────────────────────────────────┤
    │ Symbol | FundScore | FundNorm | TechNorm│
    │ -------|-----------|----------|---------|
    │  ABC   |   0.85    |   0.62   |  0.75  │
    │ Comb=0.68 "Hold"                       │
    │                                          │
    │  XYZ   |    N/A    |    N/A   |  0.82  │
    │ Comb=0.62 "Hold [Limited Fund Data]"   │
    │                                          │
    └───────────────────────────────────────────┘
                            ↓
    ┌───────────────────────────────────────────┐
    │ REPEAT FOR REMAINING STOCKS              │
    └───────────────────────────────────────────┘
```

---

## Score Scales Visual

### FundScore (-1 to +3) → FundNorm (0 to 1)

```
FundScore      -1.0    -0.5    0.0    0.5    1.0    1.5    2.0    2.5    3.0
              ├────────┼────────┼────────┼────────┼────────┼────────┼────────┤
              │◄─Poor──┼─Average─┼─Good──┼─Very Good──┼─Excellent──┴─Capped─┤
              │        │        │       │        │       │        │       │
FundNorm       0.0    0.17    0.33   0.50   0.67   0.83   1.0    1.0    1.0
              ├────────┼────────┼────────┼────────┼────────┼────────┼────────┤
              │ Bad    │       │ Okay  │      │ Good  │    Excellent      │
              
Interpretation:
┌──────────────────────────────────────────────────────────────────┐
│ FundNorm 0.0   → Company is unprofitable, expensive, declining   │
│ FundNorm 0.33  → Company is average, decent quality              │
│ FundNorm 0.67  → Company is good, profitable, decent growth      │
│ FundNorm 1.0   → Company is excellent, all metrics strong        │
└──────────────────────────────────────────────────────────────────┘
```

### TechNorm (0 to 1) 

```
                 0.0        0.25       0.5        0.75       1.0
               ├──────────┼──────────┼──────────┼──────────┤
               │◄─Bearish─┼─Neutral──┼──Bullish─┼─Verybull►│
               │          │          │          │          │
Pattern:       │ Downtrend│ Mixed    │ Uptrend  │Strong up │
               │ All -ve  │ Equal +- │ Most +ve │All +ve   │
               
Interpretation:
┌────────────────────────────────────────────────────────────────┐
│ TechNorm 0.0   → Price falling, all indicators negative         │
│ TechNorm 0.25  → Weak/early decline signal                      │
│ TechNorm 0.5   → Mixed signals, choppy/neutral                  │
│ TechNorm 0.75  → Strong bullish setup, most indicators positive │
│ TechNorm 1.0   → Perfect bullish alignment, very strong trend   │
└────────────────────────────────────────────────────────────────┘
```

### Combined Score (0 to 1) → Recommendations

```
                 0.0        0.45       0.65       1.0
               ├──────────┼──────────┼──────────┤
               │ Sell     │ Watch    │ Hold     │
               │ ◄────────┤──────────┤─────────►│
               │ Weak     │ Mixed    │ Strong   │
               
Zones:
┌────────────────────────────────────────────────────────────────┐
│ 0.00 - 0.45                                                    │
│ "Consider Sell" → Both weak or conflicts heavily               │
│ ◄─────► SELL ZONE (High Risk, Low Upside)                    │
│                                                                │
│ 0.45 - 0.65                                                    │
│ "Watch / Partial Hold" → Mixed signals, requires monitoring    │
│ ◄─────► WATCH ZONE (Neutral, Conflicting)                    │
│                                                                │
│ 0.65 - 1.00                                                    │
│ "Hold" → Both strong or well-balanced                          │
│ ◄─────► HOLD ZONE (Low Risk, Good Upside)                    │
└────────────────────────────────────────────────────────────────┘
```

---

## Decision Matrix: Tech vs Fund

```
                    FundNorm (Fundamental)
                    0.2        0.5        0.8
                   (Poor)    (Okay)    (Good)

TechNorm 0.2        ┌─────────┬─────────┬─────────┐
(Bearish) 0%        │  0.16   │  0.25   │  0.33   │
          ◄─────►   │ SELL    │ SELL    │ WATCH   │
                    │ Weak    │ Tech -  │ Tech -  │
                    │ Both    │ Fund +  │ Fund +  │
                    ├─────────┼─────────┼─────────┤

TechNorm 0.5        │  0.30   │  0.50   │  0.70   │
(Neutral) 50%       │ WATCH   │ WATCH   │ HOLD    │
          ◄─────►   │ Tech -  │ Mixed   │ Tech +  │
                    │ Fund -  │ Balanced│ Fund +  │
                    ├─────────┼─────────┼─────────┤

TechNorm 0.8        │  0.44   │  0.65   │  0.85   │
(Bullish) 100%      │ SELL    │ HOLD    │ HOLD    │
          ◄─────►   │ Fund -  │ Both +  │ Both ++│
                    │ Tech +  │ Balanced│ Strong  │
                    └─────────┴─────────┴─────────┘

Legend:
┌──────────────────────────────────────────────────┐
│ 0.00-0.45 = SELL (Dark Red)      ██ "Avoid"    │
│ 0.45-0.65 = WATCH (Yellow)       ██ "Caution"  │
│ 0.65-1.00 = HOLD (Green)         ██ "Go"       │
│                                                 │
│ [LimitedFundData] = Tech-heavy (75% weight)     │
└──────────────────────────────────────────────────┘
```

---

## Real-World Example: INFY.NS vs BADSTOCK.NS

### Stock 1: INFY.NS (Good Company, Good Tech)

```
┌────────────────────────────────────┐
│ FUNDAMENTAL                        │
├────────────────────────────────────┤
│ ROE      : 25% → +2.0              │
│ Growth   : 8%  → +0.8              │
│ Margin   : 15% → +0.45             │
│ PE       : 22  → -0.44             │
│ Beta     : 0.9 → +0.0              │
│ Sentiment: 0.3 → +0.09             │
│ ────────────────────────────────── │
│ FundScore: 2.7 (capped components) │
│ FundNorm : 1.0 (Excellent)         │
└────────────────────────────────────┘
          ↓
    ┌─────────────┐
    │  COMBINE    │ 0.6 × 0.90 + 0.4 × 1.0
    │             │ = 0.54 + 0.40 = 0.94
    │  = 0.94     │
    │ [HOLD] ✅   │
    └─────────────┘
          ↑
┌────────────────────────────────────┐
│ TECHNICAL                          │
├────────────────────────────────────┤
│ SMA Align (5>20>50): ✓ → 1.5       │
│ EMA Cross (12>26)  : ✓ → 0.8      │
│ MACD Positive      : ✓ → 0.7      │
│ RSI14 (65)         : ✓ → 0.87     │
│ Volume Ratio (2.5x): ✓ → 0.75     │
│ ────────────────────────────────── │
│ TechNorm: 0.90 (Very Bullish)      │
│ (Total 4.57 / 4.5 = 1.0 capped)    │
└────────────────────────────────────┘

RECOMMENDATION: ✅ HOLD (Excellent Signal)
Confidence: Very High (Both metrics agree)
Action: Safe to buy/hold long-term
Risk: Low (strong company, good momentum)
```

### Stock 2: BADSTOCK.NS (Poor Company, Any Tech)

```
┌────────────────────────────────────┐
│ FUNDAMENTAL                        │
├────────────────────────────────────┤
│ ROE      : 3%   → +0.12            │
│ Growth   : -5%  → -0.20            │
│ Margin   : 2%   → +0.06            │
│ PE       : 45   → -0.90            │
│ Beta     : 1.8  → -0.40            │
│ Sentiment:-0.5  → -0.15            │
│ ────────────────────────────────── │
│ FundScore: -1.47 (Bad Company)     │
│ FundNorm : 0.0  (Terrible)         │
└────────────────────────────────────┘
          ↓
    ┌─────────────┐
    │  COMBINE    │ 0.6 × 0.60 + 0.4 × 0.0
    │             │ = 0.36 + 0.00 = 0.36
    │  = 0.36     │
    │ [SELL] ❌   │
    └─────────────┘
          ↑
┌────────────────────────────────────┐
│ TECHNICAL                          │
├────────────────────────────────────┤
│ SMA Align (5<20>50): ✗ → 0.0      │
│ EMA Cross (12<26)  : ✗ → 0.0      │
│ MACD Positive      : ✗ → 0.0      │
│ RSI14 (28)         : ✗ → 0.0      │
│ Volume Ratio (0.8x): ✗ → 0.0      │
│ ────────────────────────────────── │
│ TechNorm: 0.60 (Weak/Declining)    │
│ Even with OK technicals, fund bad  │
└────────────────────────────────────┘

RECOMMENDATION: ❌ CONSIDER SELL (Avoid)
Confidence: Very High (Both metrics agree)
Action: Avoid or exit if holding
Risk: High (Bad company, declining trend)
```

---

## The N/A Scenario

### Stock 3: SOMESTOCK.NS (Unknown Fundamentals, Good Tech)

```
┌────────────────────────────────────┐
│ FUNDAMENTAL                        │
├────────────────────────────────────┤
│ yfinance doesn't have:             │
│ ROE      : ??? → defaults 0.0      │
│ Growth   : ??? → defaults 0.0      │
│ Margin   : ??? → defaults 0.0      │
│ PE       : ??? → defaults 20 (mod) │
│ Beta     : ??? → defaults 1.0      │
│ Sentiment: ??? → defaults 0.0      │
│ ────────────────────────────────── │
│ FundScore: -0.4 (All defaults)     │
│ FundNorm : N/A  (Marked unavail)   │
│ [Limited Fund Data] ⚠️              │
└────────────────────────────────────┘
          ↓
    ┌─────────────┐
    │  COMBINE    │ 0.75 × 0.70 + 0.25 × 0.5
    │             │ = 0.525 + 0.125 = 0.65
    │  = 0.65     │
    │ [HOLD] ⚠️    │
    └─────────────┘
          ↑
┌────────────────────────────────────┐
│ TECHNICAL                          │
├────────────────────────────────────┤
│ SMA Align (5>20>50): ✓ → 1.5      │
│ EMA Cross (12>26)  : ✓ → 0.8      │
│ MACD Positive      : ✓ → 0.7      │
│ RSI14 (60)         : ✓ → 0.75     │
│ Volume Ratio (1.5x): ✓ → 0.25     │
│ ────────────────────────────────── │
│ TechNorm: 0.70 (Bullish)           │
│ Good momentum despite low fund data│
└────────────────────────────────────┘

RECOMMENDATION: ⚠️ HOLD [Limited Fund Data]
Interpretation: "Price is trending up, but we don't have 
                 company fundamentals from yfinance"
Confidence: Medium (Based only on technicals)
Action: Use price trend BUT manually verify company health
Risk: Medium (No company health data, but strong price trend)
Solution: Read company news/earnings separately
```

---

## Summary Decision Tree

```
Stock Data Available?
    ├─ NO → "Insufficient data"
    │
    └─ YES (≥60 days price history)
        │
        ├─ Calculate 27 Technical Indicators
        │       ↓
        ├─ Get Fundamentals from yfinance
        │       ↓
        ├─ Fundamentals Found?
        │   ├─ YES (ROE or PE or Growth)
        │   │   ├─ Calculate FundScore
        │   │   ├─ Normalize to FundNorm (0-1)
        │   │   ├─ Use weights: 60% Tech, 40% Fund
        │   │   └─ Display: FundScore, FundNorm (numeric)
        │   │
        │   └─ NO (All NaN, use defaults)
        │       ├─ Use safe defaults (neutral, not punishing)
        │       ├─ Mark fund_available = False
        │       ├─ Use weights: 75% Tech, 25% Fund
        │       └─ Display: FundScore = "N/A", FundNorm = "N/A"
        │
        ├─ Calculate TechNorm (always available if price > 60 days)
        │       ↓
        ├─ Combine Scores
        │   ├─ If fund available: 0.6×Tech + 0.4×Fund
        │   └─ If NOT available:  0.75×Tech + 0.25×0.5
        │
        ├─ Generate Recommendation
        │   ├─ Combined ≥ 0.65 → "Hold"
        │   ├─ Combined 0.45-0.65 → "Watch / Partial Hold"
        │   └─ Combined < 0.45 → "Consider Sell"
        │   (Add " [Limited Fund Data]" if fund not available)
        │
        └─ Output Row to Table
```

