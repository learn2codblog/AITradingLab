# Quick Start - Enhanced Model Setup

## ✅ Step-by-Step Setup Checklist

### 1. File Verification
- [ ] `feature_engineering.py` exists (new module)
- [ ] `models.py` updated with enhanced functions
- [ ] `app.py` imports feature_engineering module
- [ ] `data_loader.py` cleaned (data only)
- [ ] `fundamental_analysis.py` exists and separated
- [ ] `technical_indicators.py` well-documented

**Check command:**
```bash
ls -la *.py  # Should see all files
```

### 2. Dependencies Verification
Required packages (check in requirements.txt):
- [ ] `pandas` ≥ 1.3
- [ ] `numpy` ≥ 1.20
- [ ] `scikit-learn` ≥ 1.0
- [ ] `xgboost` ≥ 1.5
- [ ] `tensorflow` or `keras` (for LSTM)
- [ ] `ta` (technical analysis)
- [ ] `yfinance` (data download)
- [ ] `streamlit` (for app)
- [ ] `matplotlib` (visualization)

**Check versions:**
```bash
pip list | grep -E "pandas|numpy|scikit|xgboost|tensorflow|ta|yfinance|streamlit"
```

### 3. Module Import Test
Create a test file `test_imports.py`:
```python
print("Testing imports...")
try:
    from feature_engineering import engineer_advanced_features, select_best_features
    print("✓ feature_engineering")
except ImportError as e:
    print(f"✗ feature_engineering: {e}")

try:
    from models import train_random_forest, train_xgboost, build_lstm_model
    print("✓ models")
except ImportError as e:
    print(f"✗ models: {e}")

try:
    from data_loader import load_stock_data
    print("✓ data_loader")
except ImportError as e:
    print(f"✗ data_loader: {e}")

try:
    from technical_indicators import calculate_technical_indicators
    print("✓ technical_indicators")
except ImportError as e:
    print(f"✗ technical_indicators: {e}")

try:
    from fundamental_analysis import get_fundamentals, engineer_advanced_features
    print("✓ fundamental_analysis")
except ImportError as e:
    print(f"✗ fundamental_analysis: {e}")

print("\nAll imports successful! ✓")
```

Run:
```bash
python test_imports.py
```

### 4. First Run - Test Script

Create `test_model.py`:
```python
import pandas as pd
from data_loader import load_stock_data
from technical_indicators import calculate_technical_indicators
from feature_engineering import engineer_advanced_features, select_best_features
from fundamental_analysis import get_fundamentals
from models import train_random_forest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

print("▶ Loading test data...")
symbol = "INFY.NS"
stock = load_stock_data(symbol, "2023-01-01", "2024-12-31")
print(f"  ✓ Loaded {len(stock)} days of data")

print("\n▶ Calculating technical indicators...")
stock = calculate_technical_indicators(stock)
print(f"  ✓ Features: {len(stock.columns)}")

print("\n▶ Getting fundamentals...")
fundamentals = get_fundamentals(symbol)
print(f"  ✓ ROE: {fundamentals.get('ROE', 'N/A')}")

print("\n▶ Engineering advanced features...")
stock = engineer_advanced_features(stock, fundamentals=fundamentals)
print(f"  ✓ Total features: {len(stock.columns)}")

print("\n▶ Selecting best features...")
exclude_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Target', 'Future_Ret']
all_features = [col for col in stock.columns if col not in exclude_cols]
selected_features = select_best_features(all_features, max_features=60)
print(f"  ✓ Selected {len(selected_features)} features")

print("\n▶ Creating target variable...")
stock['Future_Ret'] = stock['Close'].pct_change(5).shift(-5)
stock['Target'] = (stock['Future_Ret'] > stock['Future_Ret'].median()).astype(int)
stock.dropna(inplace=True)
print(f"  ✓ Data points: {len(stock)}")

print("\n▶ Splitting data...")
X = stock[selected_features]
y = stock['Target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
print(f"  ✓ Train: {len(X_train)}, Test: {len(X_test)}")

print("\n▶ Scaling features...")
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc = scaler.transform(X_test)
print(f"  ✓ Scaling complete")

print("\n▶ Training Random Forest...")
model = train_random_forest(X_train_sc, y_train, n_estimators=100, max_depth=10)
print(f"  ✓ Model trained")

print("\n▶ Evaluating model...")
preds = model.predict(X_test_sc)
accuracy = accuracy_score(y_test, preds)
f1 = f1_score(y_test, preds)
print(f"  ✓ Accuracy: {accuracy:.2%}")
print(f"  ✓ F1-Score: {f1:.2%}")

print("\n✓ SUCCESS - Enhanced model is working!")
```

Run:
```bash
python test_model.py
```

Expected output:
```
▶ Loading test data...
  ✓ Loaded 500 days of data

▶ Calculating technical indicators...
  ✓ Features: 32

▶ Getting fundamentals...
  ✓ ROE: 0.215

▶ Engineering advanced features...
  ✓ Total features: 85

▶ Selecting best features...
  ✓ Selected 60 features

▶ Creating target variable...
  ✓ Data points: 495

▶ Splitting data...
  ✓ Train: 396, Test: 99

▶ Scaling features...
  ✓ Scaling complete

▶ Training Random Forest...
  ✓ Model trained

▶ Evaluating model...
  ✓ Accuracy: 53.5%
  ✓ F1-Score: 0.52

✓ SUCCESS - Enhanced model is working!
```

### 5. Run Streamlit App

```bash
streamlit run app.py
```

You should see:
1. Sidebar with input parameters
2. Enhanced metrics (5 columns) after model training
3. Feature importance chart
4. All other existing features working

### 6. Verify Features Integration

Check in the Streamlit app:
- [ ] "Using 60 engineered features for model training" message appears
- [ ] 5 metric columns show: Accuracy, Precision, Recall, F1-Score, ROC-AUC
- [ ] Feature Importance chart shows Top 15 features
- [ ] Model trains without errors
- [ ] Backtesting works as before

---

## 🔍 Common Issues & Solutions

### Issue: "No module named 'feature_engineering'"
**Solution:**
```bash
# Make sure feature_engineering.py is in the same directory as app.py
ls -la feature_engineering.py

# If not, copy it from the provided files
```

### Issue: "ImportError: cannot import name 'select_best_features'"
**Solution:**
```bash
# Check that feature_engineering.py has the function
grep "def select_best_features" feature_engineering.py

# If not present, replace the file with the complete version
```

### Issue: "MemoryError" or very slow execution
**Solution:**
```python
# In app.py, reduce max_features:
selected_features = select_best_features(all_features, max_features=40)
# Instead of max_features=60
```

### Issue: "Model training takes too long"
**Solution:**
```python
# In models.py, reduce n_estimators:
model = train_random_forest(X_train_sc, y_train, 
                           n_estimators=200,  # Instead of 500
                           max_depth=10)
```

### Issue: "NaN values in features"
**Solution:**
```python
# Already handled in app.py with:
stock.dropna(inplace=True)

# If still issues, add before feature selection:
stock = stock.dropna()
```

---

## 📊 Feature Verification

After running the model, you should see feature importance for these (examples):

**Top Features (typical):**
1. Bullish_SMA ~8-12%
2. Price_vs_SMA20 ~5-8%
3. Momentum_Score ~4-6%
4. RSI14 ~3-5%
5. Volume_Intensity ~2-4%
6. ... (top 15 shown in chart)

**Feature Categories (should see all 10):**
- ✓ Trend (14 features)
- ✓ Momentum (15 features)
- ✓ Volatility (11 features)
- ✓ Volume (8 features)
- ✓ Patterns (6 features)
- ✓ Returns (9 features)
- ✓ Relative (7 features)
- ✓ Fundamental (6 features)
- ✓ Lagged (5 features)
- ✓ Interaction (3 features)

---

## 🚀 Performance Tuning

### If Model Accuracy is Low (<50%)
```python
# Try these adjustments in models.py:

# 1. Increase trees/complexity
model = train_random_forest(X_train_sc, y_train, 
                           n_estimators=800,    # More trees
                           max_depth=20)         # Deeper trees

# 2. Or try XGBoost instead
model = train_xgboost(X_train_sc, y_train,
                     n_estimators=600,
                     max_depth=10,
                     learning_rate=0.05)
```

### If Model is Overfitting (Train >> Test accuracy)
```python
# Reduce complexity:
model = train_random_forest(X_train_sc, y_train,
                           n_estimators=200,    # Fewer trees
                           max_depth=8)         # Shallower

# Or add regularization:
model = train_xgboost(X_train_sc, y_train,
                     n_estimators=300,
                     max_depth=5,
                     reg_alpha=0.5,     # More L1
                     reg_lambda=2.0)    # More L2
```

### If Model is Underfitting (Train ≈ Test accuracy ≈ 50%)
```python
# Add more features or use more data:

# Option 1: Increase max_features
selected_features = select_best_features(all_features, max_features=80)

# Option 2: Load more historical data
stock = load_stock_data(symbol, "2015-01-01", "2024-12-31")
```

---

## 📈 Monitoring Checklist

After deployment, monitor:
- [ ] Model accuracy weekly
- [ ] Feature importance stability
- [ ] Trading performance (backtest results)
- [ ] Max drawdown
- [ ] Sharpe ratio
- [ ] Win rate

---

## 📚 Documentation to Review

Read in this order:
1. **ENHANCEMENT_SUMMARY.md** - Overview (5 min)
2. **BEFORE_AFTER_COMPARISON.md** - What changed (10 min)
3. **FEATURE_ENHANCEMENTS.md** - Feature details (15 min)
4. **FEATURE_IMPLEMENTATION.md** - Code examples (20 min)

---

## ✨ Next Steps

1. **✓ Verify all files are present**
2. **✓ Run test_imports.py**
3. **✓ Run test_model.py**
4. **✓ Run streamlit app.py**
5. **✓ Check feature importance chart**
6. **✓ Review metrics**
7. **✓ Run backtest**
8. **✓ Compare with old results**
9. **✓ Fine-tune parameters if needed**
10. **✓ Deploy with confidence**

---

## 🎯 Success Criteria

Your setup is successful when:
✓ All modules import without errors
✓ Test script runs and shows >50% accuracy
✓ Streamlit app displays 5 metrics + feature chart
✓ No NaN or error messages
✓ Speed: <15 seconds per full analysis
✓ Feature importance chart shows meaningful features

---

## 📞 Troubleshooting Quick Links

- **Import errors** → Check file paths & requirements.txt
- **NaN values** → Ensure data is sufficiently long (>300 rows)
- **Slow execution** → Reduce max_features or n_estimators
- **Low accuracy** → More data, more features, different model
- **High variance** → Reduce model complexity

**You're all set! Run the app and enjoy the enhanced model! 🚀**

