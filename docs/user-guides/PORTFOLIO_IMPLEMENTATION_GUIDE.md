# Portfolio Components Implementation Guide

## 📚 Developer Documentation

This guide explains the internal architecture of the new portfolio features for developers.

---

## 🏗️ Architecture Overview

### Component Hierarchy

```
app_modern.py
└── Portfolio Manager Page
    ├── Tab 1: Build Portfolio
    │   ├── create_portfolio_builder()
    │   ├── create_mobile_responsive_portfolio()
    │   └── show_portfolio_recommendations()
    │
    ├── Tab 2: Advanced Tracker
    │   └── create_advanced_portfolio_builder()
    │
    └── Tab 3: Analysis
        └── Original portfolio analysis code
```

### File Structure
```
ui/
├── portfolio_builder.py (NEW - 380 lines)
│   ├── create_portfolio_builder()
│   ├── create_advanced_portfolio_builder()
│   ├── create_mobile_responsive_portfolio()
│   └── show_portfolio_recommendations()
│
└── styles.py (ENHANCED - +150 lines)
    ├── Responsive CSS media queries
    ├── Dark mode support
    └── Touch optimization
```

---

## 🔧 Core Components

### 1. create_portfolio_builder()

**Location**: `ui/portfolio_builder.py` (Lines 1-120)

**Purpose**: Interactive portfolio allocation builder

**Parameters**: None

**Returns**: Dictionary via st.session_state.portfolio_items

**Session State Used**:
```python
st.session_state.portfolio_items = {
    'INFY.NS': {'allocation': 30},
    'SBIN.NS': {'allocation': 25},
    'TCS.NS': {'allocation': 45}
}
```

**Implementation Details**:

```python
def create_portfolio_builder():
    """
    Interactive portfolio builder with allocation sliders.
    
    Features:
    - Add stocks with symbol input
    - Allocate percentages with sliders (0-100%)
    - Auto-balance to exactly 100%
    - Remove stocks from portfolio
    - Pie chart visualization
    - Save/export portfolio
    
    State Persistence:
    - Uses st.session_state.portfolio_items
    - Persists between page refreshes
    - Resets when user clears cache
    """
```

**Key Functions Inside**:

1. **Add Stock Button**
   ```python
   if st.button("➕ Add Stock"):
       symbol = st.session_state.stock_symbol.strip().upper()
       if symbol and symbol not in portfolio_items:
           portfolio_items[symbol] = {'allocation': 0}
   ```

2. **Allocation Sliders**
   ```python
   allocation = st.slider(
       f"Allocate {symbol}",
       0, 100, portfolio_items[symbol]['allocation']
   )
   portfolio_items[symbol]['allocation'] = allocation
   ```

3. **Auto-Balance Logic**
   ```python
   if st.button("🔄 Auto-Balance to 100%"):
       total = sum(item['allocation'] for item in portfolio_items.values())
       if total > 0:
           for symbol in portfolio_items:
               portfolio_items[symbol]['allocation'] *= 100 / total
   ```

4. **Pie Chart Visualization**
   ```python
   fig = go.Figure(data=[go.Pie(
       labels=symbols,
       values=allocations,
       hole=0  # Full pie, not donut
   )])
   st.plotly_chart(fig, use_container_width=True)
   ```

5. **Save Portfolio**
   ```python
   import json
   portfolio_json = json.dumps(portfolio_items, indent=2)
   st.download_button(
       label="💾 Save Portfolio",
       data=portfolio_json,
       file_name="portfolio.json"
   )
   ```

**Data Flow**:
1. User types symbol → Input field
2. User clicks "Add Stock" → Stored in session_state.portfolio_items
3. User adjusts sliders → Allocation % updated in real-time
4. Pie chart updates → Visualizes new allocation
5. User clicks "Auto-Balance" → Scales all % proportionally
6. User clicks "Save Portfolio" → Downloads JSON file

---

### 2. create_advanced_portfolio_builder()

**Location**: `ui/portfolio_builder.py` (Lines 122-230)

**Purpose**: Track real holdings with P&L calculations

**Parameters**: None

**Returns**: Dictionary via st.session_state.advanced_portfolio

**Session State Used**:
```python
st.session_state.advanced_portfolio = {
    'INFY.NS': {
        'quantity': 10,
        'buy_price': 1500,
        'current_price': 1650,
        'notes': 'Quality stock'
    },
    'SBIN.NS': {
        'quantity': 5,
        'buy_price': 400,
        'current_price': 410,
        'notes': 'Banking exposure'
    }
}
```

**Implementation Details**:

```python
def create_advanced_portfolio_builder():
    """
    Track actual holdings with quantity, prices, and P&L.
    
    Features:
    - Add multiple positions with quantities
    - Enter buy prices and current prices
    - Real-time P&L calculation (₹ and %)
    - Position notes for strategy tracking
    - Portfolio-level summary metrics
    - Expandable position details
    
    Calculations:
    - Investment = quantity × buy_price
    - Current Value = quantity × current_price
    - Absolute Gain/Loss = Current Value - Investment
    - Return % = (Gain/Loss / Investment) × 100
    
    Color Coding:
    - Green (🟢): Profits (positive return)
    - Red (🔴): Losses (negative return)
    """
```

**Key Calculations**:

```python
# Per position
investment = quantity * buy_price
current_value = quantity * current_price
absolute_gain = current_value - investment
return_pct = (absolute_gain / investment) * 100 if investment > 0 else 0

# Portfolio totals
total_investment = sum(qty * price for qty, price in positions)
total_current_value = sum(qty * current_price for ...positions)
total_gain_loss = total_current_value - total_investment
portfolio_return = (total_gain_loss / total_investment) * 100
```

**Expandable Sections**:

```python
with st.expander(f"📊 {symbol} - {symbol_return:+.2f}%"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Quantity", f"{quantity} shares")
    with col2:
        st.metric("Buy Price", f"₹{buy_price:.2f}")
    with col3:
        st.metric("Current Price", f"₹{current_price:.2f}")
    
    st.text_area("Notes", value=notes, key=f"notes_{symbol}")
```

**Portfolio Summary**:

```python
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Investment", f"₹{total_investment:,.0f}")
with col2:
    st.metric("Current Value", f"₹{total_current_value:,.0f}")
with col3:
    color = "🟢" if total_gain_loss >= 0 else "🔴"
    st.metric(
        "Gain/Loss",
        f"{color} ₹{total_gain_loss:,.0f}",
        f"{portfolio_return:+.2f}%"
    )
```

**Data Flow**:
1. User adds symbol
2. User enters: quantity, buy_price, current_price
3. System calculates: investment, current_value, gain/loss, return %
4. Data stored in st.session_state.advanced_portfolio
5. Summary metrics calculated and displayed
6. Color-coded indicators (green/red) show profit/loss

---

### 3. create_mobile_responsive_portfolio()

**Location**: `ui/portfolio_builder.py` (Lines 232-290)

**Purpose**: Adapt portfolio display for mobile/desktop

**Parameters**: None

**Returns**: Responsive view (no return value)

**Session State Used**:
```python
# Detects mobile via session state flag
st.session_state.is_mobile = screen_width < 768
```

**Implementation Details**:

```python
def create_mobile_responsive_portfolio():
    """
    Responsive portfolio view adapting to screen size.
    
    Behaviors:
    - Mobile (< 768px): Single column, compact cards
    - Desktop (≥ 768px): Multi-column, full details
    
    Responsive Elements:
    - Font sizes scale down on mobile
    - Columns stack vertically on small screens
    - Charts reduce height percentage
    - Buttons go full-width on mobile
    - Padding/margins reduced on mobile
    """
```

**Mobile Detection**:

```python
# Option 1: Manual detection (requires client-side JS)
is_mobile = st.session_state.get('is_mobile', False)

# Option 2: Check for specific boolean flag
if 'viewport_width' in st.session_state:
    is_mobile = st.session_state.viewport_width < 768
```

**Responsive Layout**:

```python
if is_mobile:
    # Mobile: Stacked layout
    for symbol, data in portfolio_items.items():
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(f"**{symbol}**")
        with col2:
            st.write(f"${data['allocation']}%")
else:
    # Desktop: Multi-column layout
    cols = st.columns(4)
    for i, (symbol, data) in enumerate(portfolio_items.items()):
        with cols[i % 4]:
            st.metric(symbol, f"{data['allocation']}%")
```

**Data Flow**:
1. System detects screen size
2. Stores in st.session_state.is_mobile
3. Component checks flag
4. Renders mobile or desktop layout accordingly

---

### 4. show_portfolio_recommendations()

**Location**: `ui/portfolio_builder.py` (Lines 292-380)

**Purpose**: AI-powered portfolio suggestions

**Parameters**:
```python
def show_portfolio_recommendations(portfolio_items: dict):
```

**Returns**: None (displays UI directly)

**Recommendations Types**:

```python
recommendations = [
    {
        'title': '🔄 Rebalance Portfolio',
        'description': 'Your allocation has drifted...',
        'color': 'blue',
        'severity': 'info'
    },
    {
        'title': '🌍 Diversify Holdings',
        'description': 'Consider adding stocks from...',
        'color': 'blue',
        'severity': 'info'
    },
    {
        'title': '⚠️ Risk Check',
        'description': 'High concentration detected...',
        'color': 'red',
        'severity': 'warning'
    },
    # ... more recommendations
]
```

**Implementation Details**:

```python
def show_portfolio_recommendations(portfolio_items: dict):
    """
    Display AI-powered portfolio improvement recommendations.
    
    Recommendation Categories:
    1. Rebalance: When allocations drift from targets
    2. Diversify: Suggest different sectors
    3. Risk Check: Monitor concentration
    4. Tax Planning: Identify opportunities
    5. Quality: Improve overall quality
    
    Display:
    - 2-column card layout
    - Color-coded boxes (blue/red/green)
    - Expandable for more details
    - Data-driven suggestions
    """
```

**Card Layout**:

```python
cols = st.columns(2)

for i, rec in enumerate(recommendations):
    with cols[i % 2]:
        # Color border based on severity
        if rec['severity'] == 'warning':
            border_color = '#ff6b6b'  # Red
        else:
            border_color = '#4ecdc4'  # Teal
        
        # Custom HTML box
        st.markdown(f"""
        <div style="border-left: 4px solid {border_color}; 
                    padding: 15px; margin: 10px 0;">
            <h4>{rec['title']}</h4>
            <p>{rec['description']}</p>
        </div>
        """, unsafe_allow_html=True)
```

**Logic Examples**:

```python
# Rebalance recommendation
if portfolio_items:
    for symbol, data in portfolio_items.items():
        if abs(data['allocation'] - target_allocation) > 5:
            trigger_rebalance_recommendation()

# Diversify recommendation
num_stocks = len(portfolio_items)
if num_stocks < 5:
    trigger_diversify_recommendation()

# Risk check
concentration = max(data['allocation'] for data in portfolio_items.values())
if concentration > 40:
    trigger_risk_warning()

# Tax planning
position_returns = calculate_returns()
for symbol, return_pct in position_returns.items():
    if return_pct < -2:  # Loss threshold
        trigger_tax_harvest_suggestion(symbol)

# Quality check
quality_metrics = analyze_quality()
if quality_metrics['score'] < 70:
    trigger_quality_improvement_suggestion()
```

**Data Flow**:
1. Portfolio collected from portfolio_items
2. Analyzed against multiple criteria
3. Recommendations generated
4. Displayed in 2-column card layout
5. Color-coded by severity/type

---

## 🎨 CSS & Styling

### Responsive Media Queries Added

**File**: `ui/styles.py` (Lines 252-350+)

**Breakpoints**:

```css
/* Tablet Optimization */
@media (max-width: 768px) {
    h1 { font-size: 1.5rem; }
    h2 { font-size: 1.2rem; }
    .metric-card { padding: 1rem; }
    .chart-container { height: 250px; }
}

/* Mobile Optimization */
@media (max-width: 480px) {
    h1 { font-size: 1.3rem; }
    h2 { font-size: 1.1rem; }
    h3 { font-size: 0.95rem; }
    
    .main-padding { padding: 0.8rem 1rem; }
    .button { 
        padding: 0.5rem;
        min-height: 44px;
    }
    
    .form-input { width: 100%; }
    .chart-container { height: 200px; }
    
    .columns { 
        flex-direction: column;
        width: 100%;
    }
}

/* Desktop Enhancement */
@media (min-width: 1200px) {
    .main-padding { padding: 3rem; }
    .container-max-width { max-width: 1400px; }
}

/* Dark Mode */
@media (prefers-color-scheme: dark) {
    body {
        background-color: #1a1a1e;
        color: #e0e0e0;
    }
    .button {
        background-color: #2d2d3d;
        color: #e0e0e0;
    }
}

/* Touch Devices */
@media (any-hover: none) {
    button, .button {
        min-height: 44px;
        padding: 12px 16px;
    }
}

/* Landscape Mode */
@media (max-height: 600px) {
    .navbar { height: 50px; }
    .chart-container { height: 200px; }
    .form-inputs { padding: 0.5rem; }
}
```

### CSS Classes Used

```css
.metric-card {
    padding: 1.5rem;
    border-radius: 8px;
    background: #f8f9fa;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.allocation-slider {
    padding: 1rem;
    border-left: 4px solid #667eea;
}

.portfolio-pie-chart {
    margin: 2rem auto;
    max-width: 500px;
}

.recommendation-card {
    border-left: 4px solid #667eea;
    padding: 1.5rem;
    margin: 1rem 0;
    border-radius: 4px;
}

.recommendation-card.warning {
    border-left-color: #f56565;
}

.p-l-metric {
    font-weight: bold;
}

.p-l-metric.positive {
    color: #48bb78;
}

.p-l-metric.negative {
    color: #f56565;
}

.touch-button {
    min-height: 44px;
    padding: 12px 16px;
}
```

---

## 🔄 Data Flow Diagram

```
User Interaction
    ↓
st.session_state Updates
    ↓
Component Re-render
    ↓
Display Updated
    ↓
User Sees Result

Example Flow:
─────────────
User types "INFY.NS" in input
    ↓
User clicks "Add Stock"
    ↓
portfolio_items['INFY.NS'] created in session_state
    ↓
Component re-renders with new stock
    ↓
Slider appears for INFY.NS allocation
    ↓
User adjusts slider to 30%
    ↓
allocation updated in session_state
    ↓
Pie chart re-renders with new data
```

---

## 🧪 Testing Notes

### Unit Testing Example

```python
def test_auto_balance():
    portfolio = {
        'INFY.NS': {'allocation': 40},
        'SBIN.NS': {'allocation': 40},
        'TCS.NS': {'allocation': 40}
    }
    
    # Total is 120%, needs balancing
    total = sum(p['allocation'] for p in portfolio.values())
    assert total == 120
    
    # After auto-balance
    for symbol in portfolio:
        portfolio[symbol]['allocation'] *= 100 / total
    
    total = sum(p['allocation'] for p in portfolio.values())
    assert abs(total - 100) < 0.01  # Account for floating point

def test_p_l_calculation():
    position = {
        'quantity': 10,
        'buy_price': 1500,
        'current_price': 1650
    }
    
    investment = position['quantity'] * position['buy_price']
    current_value = position['quantity'] * position['current_price']
    gain_loss = current_value - investment
    return_pct = (gain_loss / investment) * 100
    
    assert investment == 15000
    assert current_value == 16500
    assert gain_loss == 1500
    assert return_pct == 10.0

def test_mobile_responsiveness():
    # Check CSS media queries exist
    with open('ui/styles.py', 'r') as f:
        content = f.read()
        assert '@media (max-width: 480px)' in content
        assert '@media (max-width: 768px)' in content
        assert '@media (min-width: 1200px)' in content
```

### Manual Testing Checklist

```
✅ Add stock to portfolio
✅ Remove stock from portfolio
✅ Allocate percentages
✅ Auto-balance functionality
✅ Pie chart renders and updates
✅ Advanced tracker quantities
✅ Buy price entry
✅ Current price updates
✅ P&L calculation accuracy
✅ Notes on positions
✅ Portfolio summary metrics
✅ Recommendations display
✅ Mobile layout < 480px
✅ Tablet layout 480-768px
✅ Desktop layout > 768px
✅ Touch button sizing
✅ Dark mode rendering
✅ Chart responsiveness
```

---

## 🚀 Extension Points

### To Add New Features

**1. Add Another Recommendation Type**

```python
# In show_portfolio_recommendations()
if calculate_sharpe_ratio(portfolio) < 1.0:
    recommendations.append({
        'title': '📈 Improve Risk-Adjusted Returns',
        'description': 'Sharpe ratio is below 1.0...',
        'color': 'orange'
    })
```

**2. Add Portfolio Persistence**

```python
# Save to file
import json
with open('my_portfolio.json', 'w') as f:
    json.dump(st.session_state.advanced_portfolio, f)

# Load from file
with open('my_portfolio.json', 'r') as f:
    portfolio = json.load(f)
    st.session_state.advanced_portfolio = portfolio
```

**3. Integrate with Database**

```python
import sqlite3

def save_portfolio_to_db(portfolio, user_id):
    conn = sqlite3.connect('portfolios.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO portfolios (user_id, data)
        VALUES (?, ?)
    ''', (user_id, json.dumps(portfolio)))
    conn.commit()
```

**4. Add Real-Time Price Updates**

```python
def update_portfolio_prices(portfolio):
    for symbol in portfolio.keys():
        price = get_price_from_zerodha(symbol)  # Your data source
        portfolio[symbol]['current_price'] = price
    return portfolio
```

**5. Portfolio Export to PDF**

```python
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

def export_to_pdf(portfolio):
    doc = SimpleDocTemplate("portfolio_report.pdf", pagesize=letter)
    # Add tables, charts, etc.
    doc.build(elements)
```

---

## 📋 Integration Checklist

```
Portfolio Builder Integration:
✅ Import in app_modern.py
✅ Call in Portfolio Manager tab
✅ Session state initialized
✅ No naming conflicts
✅ Tests passing

Advanced Tracker Integration:
✅ Import in app_modern.py
✅ Call in Portfolio Manager tab
✅ Session state initialized
✅ P&L calculations verified
✅ Tests passing

Mobile Responsiveness:
✅ CSS media queries added
✅ Responsive components used
✅ Touch buttons sized correctly (44px)
✅ Tested on 3 device sizes
✅ Dark mode tested

Recommendations System:
✅ Rules configured
✅ Display logic implemented
✅ Color coding applied
✅ Tested with sample data

Documentation:
✅ User guide written
✅ Developer guide written
✅ Code examples provided
✅ Testing procedures documented
```

---

## 🐛 Known Limitations & Future Work

### Current Limitations
```
1. No database persistence
   → Solution: Add SQLite/PostgreSQL integration
   
2. No real-time price updates
   → Solution: Add Zerodha API polling
   
3. Session resets on browser refresh
   → Solution: Use st.cache_data or file persistence
   
4. No portfolio comparison
   → Solution: Add compare view
   
5. Manual price updates only
   → Solution: Add scheduled price sync
```

### Future Enhancements
```
✓ Cloud sync across devices
✓ AI portfolio optimization suggestions
✓ Risk analysis dashboard
✓ Tax optimization recommendations
✓ Portfolio backtesting
✓ Dividend tracking
✓ Rebalancing automation
✓ Mobile app version
```

---

## 📞 Support

For questions on implementation:
- See `ui/portfolio_builder.py` for function docstrings
- Check `ui/styles.py` for CSS details
- Review `app_modern.py` for integration pattern
- Refer to Streamlit docs: https://docs.streamlit.io/

---

**Happy Coding! 🚀**

