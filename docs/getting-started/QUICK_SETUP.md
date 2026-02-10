# ⚡ Quick Setup Guide - AI Trading Lab PRO+ v2.0

**Get started in 5 minutes!**

---

## 📋 Prerequisites

- ✅ Python 3.8 or higher
- ✅ pip package manager
- ✅ Internet connection (for stock data)

---

## 🚀 Setup Steps

### Method 1: Windows Quick Start (Recommended)

**Just double-click:** `START_APP.bat`

That's it! The batch file will:
1. Check Python installation
2. Verify dependencies
3. Launch the application
4. Open in your browser

---

### Method 2: Command Line

#### Step 1: Open PowerShell/Command Prompt
```bash
cd C:\Project\Code-Base\AI-Project\AITradingLab
```

#### Step 2: Install Dependencies (First Time Only)
```bash
pip install -r requirements.txt
```

#### Step 3: Run the App
```bash
# Option A: Using the launcher script
python start.py

# Option B: Direct streamlit command
streamlit run app_modern.py
```

#### Step 4: Access in Browser
The app will automatically open at: `http://localhost:8501`

---

## 🎯 First Time Usage

### 1. Home Page
- Read the feature overview
- Check the quick start guide
- Familiarize yourself with capabilities

### 2. Stock Analysis
1. Click "📊 Stock Analysis" in sidebar
2. Enter a stock symbol: `RELIANCE.NS`
3. Select analysis type: `Complete`
4. Click "🔍 Analyze Stock"
5. View AI recommendations and charts

### 3. Smart Screener
1. Click "🎯 Smart Screener" in sidebar
2. Select screening mode: `Sector-wise Analysis`
3. Choose sector: `Banking` or `IT`
4. Set universe size: `50`
5. Click "🔍 Screen Stocks"
6. Download results as CSV

### 4. Portfolio Manager
1. Click "💼 Portfolio Manager" in sidebar
2. Enter stocks: `RELIANCE.NS, TCS.NS, INFY.NS`
3. Click "📊 Analyze Portfolio"
4. View correlation and optimization

---

## 📊 Stock Symbol Format

### Indian Stocks (NSE)
Use `.NS` suffix:
- RELIANCE.NS
- TCS.NS
- INFY.NS
- HDFCBANK.NS
- ICICIBANK.NS

### Indian Stocks (BSE)
Use `.BO` suffix:
- RELIANCE.BO
- TCS.BO

### US Stocks
No suffix needed:
- AAPL (Apple)
- GOOGL (Google)
- MSFT (Microsoft)

---

## ⚙️ Configuration

### Date Range Settings
1. Go to sidebar
2. Set "Start Date" (default: 3 years ago)
3. Set "End Date" (default: today)

### Analysis Parameters
1. Go to "⚙️ Settings"
2. Adjust confidence threshold
3. Set risk parameters
4. Save preferences

---

## 🎨 UI Navigation

### Sidebar Menu
- **🏠 Home**: Welcome & features
- **📊 Stock Analysis**: Individual stock analysis
- **🎯 Smart Screener**: Sector-wise screening
- **💼 Portfolio Manager**: Portfolio optimization
- **⚙️ Settings**: Configuration & preferences

### Key Features in Each Page

#### Stock Analysis
- ✅ AI Buy/Sell/Hold recommendation
- ✅ Entry price & target calculation
- ✅ Multi-timeframe support/resistance
- ✅ Interactive Plotly charts
- ✅ Risk metrics (VaR, volatility)

#### Smart Screener
- ✅ Sector-wise analysis (15+ sectors)
- ✅ 500+ stock database
- ✅ Confidence filtering
- ✅ Batch processing
- ✅ CSV export

#### Portfolio Manager
- ✅ Multi-stock comparison
- ✅ Correlation heatmap
- ✅ Optimized weights
- ✅ Performance tracking

---

## 🔧 Troubleshooting

### Issue: Dependencies not installed
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Port already in use
**Solution:**
```bash
streamlit run app_modern.py --server.port=8502
```

### Issue: Stock data not loading
**Solution:**
1. Check internet connection
2. Verify stock symbol format (use .NS for NSE)
3. Try a different stock
4. Check if market is open

### Issue: Slow screening
**Solution:**
1. Reduce universe size (50 instead of 200)
2. Select fewer sectors
3. Close other applications
4. Clear cache in Settings

### Issue: Charts not showing
**Solution:**
1. Clear browser cache
2. Try different browser (Chrome recommended)
3. Check JavaScript is enabled
4. Refresh the page (F5)

---

## 💡 Tips for Best Experience

### Performance
1. **Start small**: Analyze 1-2 stocks first
2. **Use cache**: Don't refresh unnecessarily
3. **Limit history**: 1-3 years is usually sufficient
4. **Close unused tabs**: Keep only active analysis

### Analysis
1. **Verify symbols**: Always double-check stock codes
2. **Check dates**: Ensure data range is valid
3. **Read explanations**: AI provides detailed reasoning
4. **Compare sectors**: Cross-sector analysis helps
5. **Use confidence filters**: >60% for quality signals

### Screening
1. **Sector focus**: Analyze one sector at a time
2. **Reasonable universe**: 50-100 stocks is optimal
3. **Export results**: Save CSV for later reference
4. **Review manually**: AI assists, you decide

### Portfolio
1. **Diversify**: Mix sectors and market caps
2. **Check correlation**: Avoid over-correlation
3. **Optimize weights**: Use MPT optimization
4. **Monitor risk**: Watch volatility and drawdown

---

## 📚 Learning Resources

### Documentation
- **README.md**: Comprehensive guide
- **RESTRUCTURING_V2.md**: Project structure details
- **Other docs**: In `documentation/` folder

### Code Examples
```python
# Example: Load and analyze stock
from src.data_loader import load_stock_data
from src.technical_indicators import calculate_technical_indicators

data = load_stock_data("RELIANCE.NS", "2023-01-01", "2026-02-09")
data = calculate_technical_indicators(data)
```

### In-App Help
- Hover over `?` icons for tooltips
- Check expandable sections
- Read info cards on each page

---

## 🎯 Quick Reference

### Keyboard Shortcuts (Streamlit)
- `Ctrl + R` or `F5`: Refresh page
- `Ctrl + K`: Clear cache
- `Ctrl + C`: Stop server (in terminal)

### Common Tasks
| Task | Steps |
|------|-------|
| Analyze stock | Stock Analysis → Enter symbol → Click Analyze |
| Screen sector | Smart Screener → Select sector → Screen |
| Build portfolio | Portfolio Manager → Enter symbols → Analyze |
| Change settings | Settings → Adjust → Apply |
| Clear cache | Settings → Clear Cache |

### Data Refresh
- **Stock prices**: Real-time (with slight delay)
- **Fundamentals**: Quarterly updates
- **News sentiment**: Daily updates
- **Cache TTL**: 1 hour

---

## 📊 Sample Workflows

### Workflow 1: Find New Opportunities
1. Go to Smart Screener
2. Select sector (e.g., "Banking")
3. Set confidence >70%
4. Screen stocks
5. Note top 3 buy signals
6. Analyze each individually in Stock Analysis
7. Add best ones to Portfolio Manager

### Workflow 2: Portfolio Review
1. List your current holdings
2. Go to Portfolio Manager
3. Enter all symbols
4. Check correlation matrix
5. Review optimized weights
6. Rebalance if needed

### Workflow 3: Deep Dive Analysis
1. Pick a stock
2. Stock Analysis → Complete analysis
3. Review all sections:
   - Price overview
   - AI recommendation
   - Charts (Price, Volume, Indicators)
   - Multi-timeframe levels
   - Fundamentals
   - Risk metrics
4. Make informed decision

---

## 🎨 UI Features Guide

### Metric Cards
Large cards with icons showing key metrics:
- 💰 Prices
- 📊 Ratios
- 📈 Returns
- ⚠️ Risk

### Signal Badges
Color-coded indicators:
- 🟢 Green: Bullish/Buy
- 🔴 Red: Bearish/Sell
- 🟡 Yellow: Neutral/Hold

### Interactive Charts
Plotly features:
- **Zoom**: Click and drag
- **Pan**: Shift + drag
- **Hover**: See exact values
- **Export**: Camera icon to save

### Progress Indicators
Real-time feedback:
- Loading spinners
- Progress bars with %
- Status messages

---

## 🆘 Getting Help

### In-App
1. Check info cards (blue boxes)
2. Read tooltips (hover over `?`)
3. Expand "More Details" sections

### Documentation
1. README.md - Full guide
2. RESTRUCTURING_V2.md - Structure
3. Code comments - Implementation details

### Debugging
1. Check browser console (F12)
2. Look at terminal output
3. Enable debug mode in Settings

---

## ✅ Post-Setup Checklist

- [ ] Application launches successfully
- [ ] Browser opens at localhost:8501
- [ ] Home page loads with cards
- [ ] Can navigate between pages
- [ ] Stock analysis works for one symbol
- [ ] Charts display properly (interactive)
- [ ] Screener returns results
- [ ] Portfolio analysis completes
- [ ] Can export CSV from screener
- [ ] Settings page accessible

If all checked ✅, you're ready to go!

---

## 🚀 Next Steps

1. **Explore**: Try different features
2. **Learn**: Read documentation
3. **Experiment**: Test various stocks and sectors
4. **Optimize**: Fine-tune parameters
5. **Trade**: Apply insights (carefully!)

---

## ⚠️ Important Notes

### Before Trading
- ✅ This is a tool, not financial advice
- ✅ Always do your own research
- ✅ Understand the risks
- ✅ Start with paper trading
- ✅ Consult financial advisors

### Data Disclaimer
- Data from Yahoo Finance (free tier)
- May have delays or inaccuracies
- Not suitable for HFT or day trading
- Best for swing/position trading

### Performance
- First load may be slow (data fetching)
- Subsequent loads are cached
- Screening 100+ stocks takes time
- Optimize by using smaller datasets

---

## 🎉 You're All Set!

**Ready to start trading smarter with AI!**

For more details, check:
- `documentation/README.md` - Full documentation
- `documentation/RESTRUCTURING_V2.md` - Project structure

**Happy Trading! 🚀📈**

---

**Version**: 2.0  
**Last Updated**: February 9, 2026  
**Platform**: Windows / Cross-platform

