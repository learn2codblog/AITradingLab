# AI Coding Agents Guide for AITradingLab

**Version:** 4.1.0 | **Stack:** Streamlit + Supabase + Python ML/DL

## Architecture Overview

This is a **Streamlit-based trading analytics platform** with Supabase persistence. The app uses a **single-entry point** (`app_modern.py`) that handles authentication, then dynamically loads page modules from `pages/`. No multi-page Streamlit structure - navigation is handled via session state.

### Core Components
- **Entry:** `app_modern.py` - Main app with auth check, navigation, OAuth callbacks
- **Pages:** `pages/*.py` - Individual page modules (home, analysis, ai, portfolio, etc.)
- **UI:** `ui/` - Components (login_page, portfolio_builder, styles, components)
- **Backend:** `src/` - Business logic (auth, data loading, ML models, indicators)
- **ML:** `src/ml/` - Specialized ML modules (ensemble, lstm, patterns, sentiment)

### Data Flow
1. User authenticates via `src/auth_supabase.py` → Session state set
2. `app_modern.py` checks auth → Loads navigation → Renders selected page module
3. Page modules call `src/` utilities for data/analysis
4. All persistent data flows through `src/supabase_client.py`
5. Stock data fetched via `yfinance` in `src/data_loader.py` with `.NS` suffix for NSE stocks

## Critical Conventions

### Symbol Normalization
**ALWAYS** use `src/symbol_utils.normalize_symbol()` when accepting user symbol input. Bare symbols (e.g., `INFY`) are auto-converted to `INFY.NS` for NSE. Handles both `.NS` suffix and `NSE:` prefix formats.

### Streamlit Caching Strategy
- `@st.cache_data(ttl=3600)` for stock data/indicators (1h TTL)
- `@st.cache_data(ttl=86400)` for static sector lists (24h TTL)
- `@st.cache_resource` for singleton clients (e.g., `get_supabase_client()`)
- Never cache user-specific data (portfolios, sessions)

### Configuration System
- **App metadata:** `app_config.json` (app name, version, tagline) - loaded in `app_modern.py`
- **Feature settings:** `config.yaml` (indicator periods, ML params, thresholds, persistence flags)
- Use `yaml.safe_load()` to read config, not direct imports

### Supabase Persistence
All user data MUST flow through `src/supabase_client.py` methods:
- User management: `create_user()`, `get_user_by_email()`, `user_exists()`
- Activity logs: `log_activity()`, `log_trading_activity()`
- Portfolios: `save_portfolio()`, `get_user_portfolios()`
- Backtests: `save_backtest_result()`, `get_user_backtest_results()`

**Registration requires SERVICE_ROLE_KEY** (not anon key) to bypass RLS. Standard operations use anon key with RLS policies. Check connection with `is_connected()` before operations.

## Authentication Pattern

```python
# In app_modern.py (always at top before UI renders)
from src.auth_supabase import SupabaseAuthManager as AuthManager
from ui.login_page import render_login_page

auth = AuthManager()
if not st.session_state.get('authenticated'):
    render_login_page(auth)
    st.stop()
```

Pages assume user is authenticated - `st.session_state.user_id` and `st.session_state.user_email` are available.

## ML/Analysis Workflows

### Technical Indicators
Use `src/technical_indicators.calculate_technical_indicators(df)` which adds 30+ indicators to DataFrame in-place:
- Trend: SMA (5/20/50/200), EMA (12/26), MACD, ADX, CCI
- Momentum: RSI (7/14/28), Stochastic, ROC, MFI
- Volatility: ATR, Bollinger Bands, Historical Volatility
- Volume: OBV, Volume MA/Ratio

**Prerequisite:** DataFrame must have OHLCV columns (`Open`, `High`, `Low`, `Close`, `Volume`)

### ML Predictions
Ensemble approach using `src/ml/ensemble.create_ensemble_prediction()`:
- Modes: `quick_mode` (5 features, fast), `deep_mode` (20+ features, rigorous)
- Returns: `{'signal': 'BUY'/'SELL'/'HOLD', 'confidence': 0-1, 'models': {...}}`
- Target: 1-day forward price movement prediction
- Models: RandomForest, XGBoost, LogisticRegression, SVM (configurable in ensemble.py)

### Deep Learning (LSTM)
Located in `src/ml/lstm.py` - used for multi-day forecasts with uncertainty quantification:
- Lookback default: 60 days (configurable in `config.yaml`)
- Monte Carlo dropout for prediction intervals
- Model sizes: 'small' (fast), 'medium', 'large' (more accurate)

## Development Commands

```powershell
# First-time setup
pip install -r requirements.txt
python SETUP.py  # Initializes Supabase schema

# Run locally
python app_modern.py
# OR
streamlit run app_modern.py --server.port=8501

# Quick start script (checks deps)
python start.py
```

### Environment Setup
Required `.env` variables (local dev) or platform secrets (Hugging Face):
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...  # Critical for registration
```

Run `python check_env.py` to verify environment configuration.

## Testing Patterns

No formal test suite - manual validation via:
1. `test_sectors.py` - Validates sector screening universe
2. Page-level logging to `tradegenius.log` (see `src/logger.py`)
3. Settings page has "Clear Cache" button for cache invalidation testing

## Common Pitfalls

1. **Module Cache Issues:** Supabase client methods may get stale after code changes. Always use `st.cache_resource` decorator, increment `VERSION` constant when adding methods.

2. **Timezone Handling:** 
   - **yfinance DataFrames:** Remove timezone with `df.index = df.index.tz_localize(None)` - yfinance returns tz-aware, but matplotlib/plotly expect naive timestamps.
   - **NewsProvider timestamps:** Returns timezone-aware UTC datetimes. Always use `datetime.now(timezone.utc)` for comparisons, never `datetime.now()`. Normalize with: `dt.replace(tzinfo=timezone.utc)` if needed.
   - **General rule:** Import `timezone` from datetime and use `datetime.now(timezone.utc)` when comparing with timezone-aware timestamps.

3. **Sector Lists:** Stock universe in `src/stock_universe.py` must match Supabase `stock_universe` table. CSV imports available in `data_management.py` page.

4. **OAuth Flow:** Query params `?code=xxx&provider=gmail` trigger OAuth callback logic at app start. Must happen BEFORE auth check to avoid infinite redirects.

5. **Page Imports:** Pages must NOT import `streamlit` at module level with multi-page patterns - but this codebase uses single-page architecture so safe. Each page has a `render_*_page()` function called from `app_modern.py`.

## Styling & UI

Modern gradient UI system in `ui/styles.py`:
- `get_custom_css()` returns full CSS as string
- No sidebar - top navigation via button grid
- Cards use glassmorphism: `backdrop-filter: blur(10px)`, gradient backgrounds
- Metrics auto-styled via Streamlit's `st.metric()` + CSS overrides

Apply styles in page modules: `st.markdown(get_custom_css(), unsafe_allow_html=True)`

## Key Files for Reference

- **Architecture:** `docs/developer-guides/ARCHITECTURE.md`
- **Features:** `docs/features/` (scoring systems, sector screening)
- **Quick Reference:** `docs/guides/QUICK_REFERENCE.md` (all formulas)
- **Schema:** `docs/SUPABASE_SCHEMA.sql` (database structure)

## Integration Points

- **Yahoo Finance:** All market data via `yfinance` library (symbols must have `.NS` suffix for Indian stocks)
- **Zerodha Kite:** Optional integration in `src/zerodha_integration.py` + pages `zerodha_*.py` (requires API credentials)
- **News:** Multiple providers in `src/news_provider.py` (RSS feeds, web scraping with fallbacks)

---

**When modifying features:** Update both code AND corresponding doc in `docs/features/`. When changing data models, update `docs/SUPABASE_SCHEMA.sql` and increment schema version comments.

