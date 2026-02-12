# 🚀 AI Trading Lab PRO+

An advanced AI-powered stock analysis and portfolio optimization platform combining Machine Learning, Deep Learning, Technical Analysis, Fundamental Analysis, and Multi-Timeframe Analysis.

## 📁 Project Structure

```
AITradingLab/
├── src/                          # Source code modules
│   ├── __init__.py              # Package initialization
│   ├── data_loader.py           # Data fetching and preprocessing
│   ├── feature_engineering.py   # Feature creation and selection
│   ├── fundamental_analysis.py  # Fundamental data & sentiment
│   ├── metrics.py               # Performance metrics
│   ├── models.py                # ML/DL model implementations
│   ├── portfolio_optimizer.py   # Portfolio optimization algorithms
│   ├── price_targets.py         # Price target calculations
│   ├── price_targets_enhanced.py # Enhanced multi-timeframe analysis
│   ├── technical_indicators.py  # Technical indicators
│   └── utils.py                 # Utility functions
│
├── docs/                         # Documentation
│   ├── ARCHITECTURE.md          # System architecture
│   ├── QUICK_START.md           # Quick start guide
│   ├── QUICK_REFERENCE.md       # Quick reference
│   ├── FEATURE_IMPLEMENTATION.md # Feature details
│   ├── SCORING_SYSTEM_DETAILS.md # Scoring system
│   └── ...                      # Additional docs
│
├── tests/                        # Test files
│   └── test_enhanced_model.py   # Main test suite
│
├── app.py                        # Main Streamlit application
├── app_header.py                # Alternative UI layout
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🌟 Features

### Machine Learning & Deep Learning
- **Random Forest** - Ensemble learning for robust predictions
- **XGBoost** - Gradient boosting for high accuracy
- **LSTM Networks** - Sequential pattern recognition
- **Dense Neural Networks** - Deep learning predictions

### Technical Analysis
- 50+ Technical Indicators
- Multi-timeframe analysis (Daily, Weekly, Monthly)
- Support/Resistance levels
- Trend analysis and momentum indicators

### Fundamental Analysis
- Real-time fundamental data
- News sentiment analysis
- Analyst ratings and recommendations
- Financial ratios and metrics

### Portfolio Optimization
- Modern Portfolio Theory (MPT)
- Sharpe Ratio optimization
- Risk-adjusted returns
- Diversification analysis

### Advanced Features
- **Smart Screening** - Sector-based and universe screening
- **Multi-timeframe Signals** - Coordinated buy/sell signals
- **Risk Management** - Stop-loss and take-profit calculations
- **Backtesting** - Historical strategy validation

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd AITradingLab
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
streamlit run app.py
```

### First Run

1. The app will open in your browser at `http://localhost:8501`
2. Enter a stock symbol (e.g., `RELIANCE.NS` for Indian stocks, `AAPL` for US stocks)
3. Configure date range and prediction parameters
4. Click "Run Analysis" to see predictions and insights

## 📊 Usage Examples

### Single Stock Analysis
```python
from src.data_loader import load_stock_data
from src.technical_indicators import calculate_technical_indicators
from src.models import train_random_forest

# Load data
data = load_stock_data("RELIANCE.NS", "2020-01-01", "2024-12-31")

# Calculate indicators
data = calculate_technical_indicators(data)

# Train model and predict
model, scaler, accuracy = train_random_forest(data)
```

### Portfolio Optimization
```python
from src.portfolio_optimizer import optimize_portfolio

symbols = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]
weights = optimize_portfolio(symbols, start_date, end_date)
```

### Multi-Timeframe Analysis
```python
from src.price_targets_enhanced import calculate_multi_timeframe_levels

levels = calculate_multi_timeframe_levels("RELIANCE.NS")
print(f"Daily: {levels['daily']}")
print(f"Weekly: {levels['weekly']}")
print(f"Monthly: {levels['monthly']}")
```

## 🧪 Testing

Run the test suite:
```bash
python tests/test_enhanced_model.py
```

## 📈 Performance Metrics

The system tracks multiple performance metrics:
- **Accuracy** - Prediction accuracy
- **Precision** - True positive rate
- **Recall** - Sensitivity
- **F1 Score** - Harmonic mean of precision and recall
- **Sharpe Ratio** - Risk-adjusted returns
- **Max Drawdown** - Largest peak-to-trough decline

## 🔧 Configuration

### Data Sources
- Yahoo Finance (yfinance) - Price data
- Alpha Vantage - Fundamental data
- News API - Sentiment analysis

### Model Parameters
Edit configuration in `app.py`:
- `future_days` - Prediction horizon
- `confidence_thresh` - Signal confidence threshold
- `model_type` - Choose between RandomForest, XGBoost, LSTM

## 📚 Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and architecture
- [Quick Reference](docs/QUICK_REFERENCE.md) - Command reference
- [Feature Guide](docs/FEATURE_IMPLEMENTATION.md) - Detailed feature documentation
- [Scoring System](docs/SCORING_SYSTEM_DETAILS.md) - How signals are scored

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is for educational and research purposes.

## ⚠️ Disclaimer

This software is for educational purposes only. Do not use it for actual trading without understanding the risks. Past performance does not guarantee future results. Always do your own research and consult with financial advisors.

## 🆘 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the [documentation](docs/)
- Review the [Quick Start Guide](docs/QUICK_START.md)

## 🔄 Version History

### v2.0.0 (Current)
- ✅ Modular project structure
- ✅ Enhanced documentation
- ✅ Improved code organization
- ✅ Better test coverage

### v1.0.0
- Initial release with ML/DL capabilities
- Basic technical and fundamental analysis
- Portfolio optimization

---

Made with ❤️ by AI Trading Lab Team

