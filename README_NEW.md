# 🚀 AI Trading Lab PRO+ v2.0

**Professional AI-Powered Trading & Analysis Platform**

A comprehensive stock market analysis platform featuring advanced machine learning, multi-timeframe technical analysis, fundamental analysis with sentiment, portfolio optimization, and sector-wise screening across 500+ stocks.

---

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [Modern UI Features](#modern-ui-features)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

### 📊 Stock Analysis
- **Multi-Timeframe Analysis**: Support & resistance levels across 1-day, weekly, and monthly timeframes
- **Technical Indicators**: 20+ indicators including RSI, MACD, Bollinger Bands, Moving Averages
- **Price Targets**: AI-powered entry, target, and stop-loss calculations
- **Risk Management**: Dynamic position sizing, VaR, CVaR, and risk assessment

### 🤖 Machine Learning
- **Random Forest & XGBoost**: Advanced ML models for price predictions
- **Feature Engineering**: 50+ engineered features for better predictions
- **Backtesting**: Historical performance validation with Sharpe ratio and drawdown analysis
- **Confidence Scoring**: Signal strength assessment for informed decision-making

### 💰 Fundamental Analysis
- **Financial Metrics**: P/E ratio, ROE, profit margins, growth rates
- **News Sentiment**: AI-powered sentiment analysis from news
- **Analyst Ratings**: Target prices and recommendations
- **Sector Comparison**: Compare stocks across industry peers

### 🎯 Smart Screener
- **Sector-wise Screening**: Analyze stocks by sector (Banking, IT, Energy, Pharma, Auto, etc.)
- **Comprehensive Database**: Access to 500+ stocks beyond Nifty 50
- **Batch Analysis**: Screen multiple stocks simultaneously
- **Custom Filters**: Filter by confidence threshold, potential returns, R/R ratio

### 💼 Portfolio Manager
- **Portfolio Optimization**: Mean-variance optimization using modern portfolio theory
- **Correlation Analysis**: Heatmap visualization of portfolio correlations
- **Performance Tracking**: Monitor returns, Sharpe ratio, volatility, drawdowns
- **AI Scoring**: Combined technical and fundamental scoring system

### 🎨 Modern UI
- **Responsive Design**: Works seamlessly on desktop and tablets
- **Interactive Charts**: Plotly-powered interactive visualizations
- **Card-based Layout**: Clean, organized information presentation
- **Gradient Themes**: Beautiful purple gradient design
- **Icon System**: Intuitive icons for quick navigation

---

## 📁 Project Structure

```
AITradingLab/
│
├── 📱 app_modern.py              # New modern UI application (Use this!)
├── app.py                         # Legacy application (deprecated)
│
├── 🎨 ui/                         # UI components and styling
│   ├── __init__.py
│   ├── styles.py                  # CSS styling and themes
│   └── components.py              # Reusable UI components
│
├── 🔧 src/                        # Core backend modules
│   ├── __init__.py
│   ├── config.py                  # Configuration settings
│   ├── data_loader.py             # Data loading utilities
│   ├── technical_indicators.py   # Technical analysis
│   ├── fundamental_analysis.py   # Fundamental analysis
│   ├── feature_engineering.py    # ML feature engineering
│   ├── models.py                  # ML models
│   ├── metrics.py                 # Performance metrics
│   ├── portfolio_optimizer.py    # Portfolio optimization
│   ├── risk_management.py        # Risk management tools
│   ├── price_targets.py           # Price target calculations
│   ├── price_targets_enhanced.py # Enhanced targets with sectors
│   ├── stock_universe.py          # Stock database (500+ stocks)
│   ├── signal_generator.py        # Trading signals
│   ├── backtesting.py             # Backtesting engine
│   └── utils.py                   # Utility functions
│
├── 📚 documentation/              # All documentation files
│   ├── README.md                  # This file
│   ├── QUICK_START.md             # Quick start guide
│   ├── ARCHITECTURE.md            # Architecture overview
│   ├── API_REFERENCE.md           # API documentation
│   ├── ENHANCEMENT_SUMMARY.md     # Enhancement history
│   ├── PORTFOLIO_SCORING_EXPLAINED.md
│   ├── SCORING_SYSTEM_DETAILS.md
│   └── ... (other docs)
│
├── 🧪 tests/                      # Test files
│   └── test_enhanced_model.py
│
├── 📦 assets/                     # Static assets (future use)
│
├── 📄 requirements.txt            # Python dependencies
├── stock_universe_template.csv   # Stock universe CSV template
└── verify_structure.py           # Project structure validator

```

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Step 1: Clone or Download
```bash
cd C:\Project\Code-Base\AI-Project\AITradingLab
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Verify Installation
```bash
python verify_structure.py
```

---

## ⚡ Quick Start

### Running the Modern UI Application

```bash
streamlit run app_modern.py
```

The application will open in your default browser at `http://localhost:8501`

### First Time Setup

1. **Navigate to Settings**: Click on "⚙️ Settings" in the sidebar
2. **Configure Date Range**: Set your preferred analysis date range
3. **Adjust Parameters**: Set confidence thresholds and risk parameters
4. **Start Analyzing**: Go to "📊 Stock Analysis" or "🎯 Smart Screener"

---

## 📖 Usage Guide

### 1️⃣ Stock Analysis

**Analyze individual stocks with comprehensive technical and fundamental analysis**

1. Navigate to "📊 Stock Analysis"
2. Enter stock symbol (e.g., `RELIANCE.NS`, `TCS.NS`)
3. Select analysis type (Complete/Technical Only/Fundamental Only)
4. Click "🔍 Analyze Stock"
5. View:
   - AI Recommendation (Buy/Sell/Hold)
   - Price targets and stop-loss
   - Multi-timeframe support/resistance
   - Interactive charts
   - Risk metrics

### 2️⃣ Smart Screener

**Find trading opportunities across sectors**

1. Navigate to "🎯 Smart Screener"
2. Choose screening mode:
   - **Sector-wise Analysis**: Select a specific sector (Banking, IT, Energy, etc.)
   - **Top N Universe**: Screen top N stocks from universe
3. Set universe size (how many stocks to analyze)
4. Set minimum confidence threshold
5. Click "🔍 Screen Stocks"
6. View results sorted by confidence
7. Download results as CSV

**Available Sectors:**
- Banking (22+ stocks)
- IT (18+ stocks)
- Energy (21+ stocks)
- Pharma (24+ stocks)
- Auto (23+ stocks)
- Metals (16+ stocks)
- FMCG (19+ stocks)
- Financials (17+ stocks)
- Consumer (21+ stocks)
- And more...

### 3️⃣ Portfolio Manager

**Build and optimize your investment portfolio**

1. Navigate to "💼 Portfolio Manager"
2. Enter comma-separated stock symbols
3. Click "📊 Analyze Portfolio"
4. View:
   - Portfolio summary metrics
   - Individual stock performance
   - Correlation heatmap
   - Optimized weights
   - Performance comparison chart

### 4️⃣ Settings

**Configure your preferences**

1. Navigate to "⚙️ Settings"
2. Adjust display preferences
3. Set analysis parameters
4. Manage data and cache

---

## 🎨 Modern UI Features

### Design Elements

- **Gradient Headers**: Beautiful purple gradient headers for visual appeal
- **Card-based Layout**: Information organized in clean cards with shadows
- **Metric Cards**: Large, readable metrics with icons
- **Interactive Charts**: Plotly charts with hover information and zoom
- **Signal Badges**: Color-coded badges for buy/sell/hold signals
- **Progress Indicators**: Real-time progress during analysis
- **Responsive Tables**: Sortable, filterable data tables

### Color Scheme

- **Primary Gradient**: Purple (#667eea to #764ba2)
- **Success/Bullish**: Green shades (#c6f6d5, #22543d)
- **Warning/Neutral**: Yellow/Orange shades (#feebc8, #d69e2e)
- **Danger/Bearish**: Red shades (#fed7d7, #742a2a)
- **Background**: Light gray (#f8f9fa)
- **Cards**: White with shadows

### Typography

- **Headers**: Bold, gradient-filled
- **Metrics**: Large (2rem), bold (700 weight)
- **Body**: Clear, readable sans-serif
- **Icons**: Emoji-based for universal compatibility

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file (optional):

```env
# Data Settings
DEFAULT_START_DATE=2020-01-01
DEFAULT_END_DATE=2026-02-09

# Model Settings
DEFAULT_MODEL=RandomForest
CONFIDENCE_THRESHOLD=0.6

# Risk Management
RISK_PER_TRADE=0.02
MAX_POSITION_SIZE=0.20
```

### Custom Stock Universe

Create `stock_universe.csv` in the root directory:

```csv
Symbol,Sector,Market_Cap,Exchange
RELIANCE.NS,Energy,1500000,NSE
TCS.NS,IT,1200000,NSE
...
```

---

## 📊 API Reference

### Data Loading

```python
from src.data_loader import load_stock_data

# Load stock data
data = load_stock_data("RELIANCE.NS", start_date, end_date)
```

### Technical Analysis

```python
from src.technical_indicators import calculate_technical_indicators

# Calculate indicators
data_with_indicators = calculate_technical_indicators(data)
```

### Fundamental Analysis

```python
from src.fundamental_analysis import get_fundamentals, get_news_sentiment

# Get fundamental data
fundamentals = get_fundamentals("RELIANCE.NS")
sentiment = get_news_sentiment("RELIANCE.NS")
```

### Price Targets

```python
from src.price_targets import calculate_entry_target_prices

# Calculate entry and target prices
targets = calculate_entry_target_prices(stock_data, fundamentals)
```

### Sector Screening

```python
from src.price_targets_enhanced import get_sector_stocks_from_universe

# Get stocks from a sector
banking_stocks = get_sector_stocks_from_universe("Banking", universe_size=50)
```

### Risk Management

```python
from src.risk_management import calculate_risk_metrics, calculate_position_size

# Calculate risk metrics
risk_metrics = calculate_risk_metrics(stock_data)

# Calculate position size
position_size = calculate_position_size(
    portfolio_value=100000,
    risk_per_trade=0.02,
    entry_price=1000,
    stop_loss_price=950
)
```

---

## 🎯 Key Improvements in v2.0

### UI/UX
- ✅ Complete UI redesign with modern card-based layout
- ✅ Gradient theme with purple color scheme
- ✅ Interactive Plotly charts replacing matplotlib
- ✅ Better button placement and spacing
- ✅ Clear navigation with sidebar menu
- ✅ Responsive design for different screen sizes

### Functionality
- ✅ Sector-wise screening beyond Nifty 50 (500+ stocks)
- ✅ Multi-timeframe support/resistance analysis
- ✅ Enhanced AI recommendations with detailed explanations
- ✅ Portfolio optimization with correlation analysis
- ✅ Real-time progress indicators
- ✅ Export results as CSV

### Project Structure
- ✅ Organized documentation in `/documentation`
- ✅ Modular UI components in `/ui`
- ✅ Clear separation of concerns
- ✅ Better naming conventions

---

## 🐛 Troubleshooting

### Issue: Module not found
**Solution**: Make sure you've installed all dependencies
```bash
pip install -r requirements.txt
```

### Issue: Yahoo Finance data error
**Solution**: Check your internet connection and stock symbol format. Use `.NS` suffix for NSE stocks.

### Issue: Plotly charts not showing
**Solution**: Clear browser cache or try a different browser. Plotly requires JavaScript.

### Issue: Slow screening
**Solution**: Reduce universe size or select fewer stocks. Screening 100+ stocks takes time.

---

## 📝 Best Practices

1. **Always verify stock symbols**: Use `.NS` for NSE stocks, `.BO` for BSE
2. **Start with smaller date ranges**: For faster analysis, especially when learning
3. **Use confidence thresholds**: Filter out low-confidence signals (>60% recommended)
4. **Diversify your portfolio**: Don't put all eggs in one basket
5. **Check risk metrics**: Always review VaR, volatility, and drawdown
6. **Backtest strategies**: Validate before live trading
7. **Monitor sector correlations**: Avoid over-concentration in correlated sectors

---

## ⚠️ Disclaimer

This tool is for **educational and informational purposes only**. It is not financial advice. Always:

- Do your own research
- Consult with financial advisors
- Understand the risks involved in trading
- Never invest more than you can afford to lose
- Past performance doesn't guarantee future results

---

## 📧 Support

For issues, questions, or contributions:
- Create an issue in the repository
- Check documentation in `/documentation` folder
- Review code comments for implementation details

---

## 📜 License

© 2026 AI Trading Lab. All rights reserved.

---

## 🙏 Acknowledgments

- **yfinance**: For financial data
- **Streamlit**: For the web framework
- **Plotly**: For interactive visualizations
- **scikit-learn**: For machine learning
- **XGBoost**: For gradient boosting
- **TensorFlow**: For deep learning

---

**Made with ❤️ for traders and investors**

**Happy Trading! 🚀📈**

