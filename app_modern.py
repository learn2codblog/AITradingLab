"""
AI Trading Lab PRO+
Modern UI Application with Enhanced Features
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

# ══════════════════════════════════════════════════════════════════════
# APP CONFIGURATION
# ══════════════════════════════════════════════════════════════════════

# Load app configuration
config_path = os.path.join(os.path.dirname(__file__), 'app_config.json')
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        APP_CONFIG = json.load(f)
except FileNotFoundError:
    # Fallback configuration if file is missing
    APP_CONFIG = {
        "app_name": "AI Trading Lab PRO+",
        "app_display_name": "TradeGenius AI",
        "version": "4.0.0",
        "description": "AI-Powered Trading & Portfolio Analysis Platform with Modern UI & User Profiles",
        "tagline": "🚀 Smart Trading • 🤖 AI-Powered • 📈 Data-Driven Insights",
        "icon": "🚀",
        "copyright_year": "2026"
    }
except Exception as e:
    st.error(f"Error loading app configuration: {e}")
    APP_CONFIG = {"app_name": "AI Trading Lab", "version": "1.0.0", "description": "Trading Platform"}

# ══════════════════════════════════════════════════════════════════════
# AUTHENTICATION - CHECK LOGIN STATUS BEFORE ANYTHING ELSE
# ══════════════════════════════════════════════════════════════════════

from src.auth import AuthManager, create_login_page
from ui.login_page import render_login_page

# OAuth callback handling: exchange authorization code for tokens and create session
try:
    import requests
    from utils.oauth_config import oauth_config
except Exception:
    requests = None
    oauth_config = None

# If the app was redirected back with an auth 'code', handle the exchange before auth checks
try:
    params = st.experimental_get_query_params()
    if params and 'code' in params:
        code = params.get('code')[0]
        provider = params.get('provider', ['gmail'])[0] if params.get('provider') else 'gmail'
        if oauth_config is None or requests is None:
            st.error('OAuth support is not available in this environment.')
        else:
            try:
                data = oauth_config.get_token_request_data(code)
                token_resp = requests.post(oauth_config.token_endpoint, data=data, timeout=15)
                token_resp.raise_for_status()
                token_json = token_resp.json()
                access_token = token_json.get('access_token')
                if not access_token:
                    st.error('OAuth token exchange failed. No access token received.')
                else:
                    headers = {'Authorization': f'Bearer {access_token}'}
                    userinfo = requests.get(oauth_config.user_info_endpoint, headers=headers, timeout=10).json()
                    email = userinfo.get('email')
                    name = userinfo.get('name') or email
                    picture = userinfo.get('picture')
                    # Initialize session and set user
                    auth_manager_temp = AuthManager()
                    auth_manager_temp.initialize_session_state()
                    auth_manager_temp.set_user_session(email=email, name=name, picture=picture, method=provider)
                    # Clear query params and reload
                    try:
                        st.experimental_set_query_params()
                    except Exception:
                        pass
                    # Force immediate rerun to pick up the new session state
                    st.success("✅ Login successful! Redirecting to home page...")
                    st.balloons()
                    import time
                    time.sleep(0.5)
                    st.rerun()
            except Exception as e:
                st.error(f"OAuth callback handling failed: {e}")
except Exception:
    # experimental_get_query_params may not be available in some runtimes
    pass

# Handle Zerodha OAuth callback (request_token) if present in URL
try:
    params = st.experimental_get_query_params()
    if params and 'request_token' in params:
        req_token = params.get('request_token')[0]
        # If an authenticator was stored in session state, complete the flow automatically
        if 'zerodha_authenticator' in st.session_state:
            try:
                auth = st.session_state.zerodha_authenticator
                from src.zerodha_integration import ZerodhaAuthenticator
                result = auth.set_access_token(req_token)
                if 'error' not in result and result.get('success'):
                    st.session_state.zerodha_connected = True
                    st.session_state.zerodha_user_id = result.get('user_id')
                    st.session_state.zerodha_access_token = result.get('access_token')
                    st.success(f"✅ Zerodha connected: {result.get('user_id')}")
                    try:
                        st.experimental_set_query_params()
                    except Exception:
                        pass
                    import time
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error(f"Zerodha authorization failed: {result.get('error', 'unknown')}")
            except Exception as e:
                st.error(f"Error completing Zerodha auth: {e}")
        else:
            st.info("Zerodha request_token found in URL. Please open Account Settings and complete authorization by clicking 'Complete Authorization' or paste the token into the form.")
            try:
                st.experimental_set_query_params()
            except Exception:
                pass
except Exception:
    pass

# Initialize authentication
auth_manager = AuthManager()
auth_manager.initialize_session_state()

# Check if user is authenticated
if not auth_manager.is_authenticated():
    # Render login page
    render_login_page(auth_manager)
    st.stop()

# Check if session is valid (not expired)
if not auth_manager.is_session_valid():
    auth_manager.logout()
    st.warning("⏰ Your session has expired. Please login again.")
    render_login_page(auth_manager)
    st.stop()

# ══════════════════════════════════════════════════════════════════════
# MAIN APPLICATION - USER IS AUTHENTICATED
# ══════════════════════════════════════════════════════════════════════

# Import backend modules
from src.data_loader import load_stock_data
from src.symbol_utils import normalize_symbol
from src.fundamental_analysis import get_fundamentals, get_news_sentiment, get_analyst_ratings, get_stock_news
from src.technical_indicators import calculate_technical_indicators, generate_signals, get_trend
from src.feature_engineering import engineer_advanced_features, select_best_features
from src.metrics import sharpe_ratio, max_drawdown
from src.portfolio_optimizer import optimize_portfolio
from src.price_targets import calculate_entry_target_prices
from src.price_targets_enhanced import (
    calculate_multi_timeframe_levels,
    generate_buy_sell_explanation,
    get_sector_stocks_from_universe,
    get_all_available_sectors,
    get_nifty_top_n
)
# Heavy ML imports are lazily loaded to avoid large startup memory usage.
# Use `load_ml_resources()` to import ML functions on demand.
_ml_resources_loaded = False

def load_ml_resources():
    """Lazily import heavy ML modules and bind names into module globals.
    Call this before using ML/advanced AI functions to avoid loading at startup.
    """
    global _ml_resources_loaded
    if _ml_resources_loaded:
        return

    # Import models and advanced AI functions here (CPU-only packages expected)
    try:
        from src.models import train_random_forest, train_xgboost  # type: ignore
        from src.ml import (
            calculate_advanced_indicators,
            detect_candlestick_patterns,
            detect_chart_patterns,
            detect_market_regime,
            detect_anomalies,
            create_ensemble_prediction,
            generate_ai_analysis,
            predict_with_lstm,
            analyze_news_sentiment,
            calculate_feature_importance,
            calculate_position_size,
            backtest_strategy,
            analyze_sentiment_transformer,
            calculate_supertrend,
            calculate_adx,
            calculate_psar,
            forecast_volatility_garch,
            get_volatility_regime,
            combined_trend_signal,
            predict_with_transformer,
            detect_anomalies_autoencoder,
        )

        # Bind to globals so existing code can use the names directly
        globals().update({
            'train_random_forest': train_random_forest,
            'train_xgboost': train_xgboost,
            'calculate_advanced_indicators': calculate_advanced_indicators,
            'detect_candlestick_patterns': detect_candlestick_patterns,
            'detect_chart_patterns': detect_chart_patterns,
            'detect_market_regime': detect_market_regime,
            'detect_anomalies': detect_anomalies,
            'create_ensemble_prediction': create_ensemble_prediction,
            'generate_ai_analysis': generate_ai_analysis,
            'predict_with_lstm': predict_with_lstm,
            'analyze_news_sentiment': analyze_news_sentiment,
            'calculate_feature_importance': calculate_feature_importance,
            'calculate_position_size': calculate_position_size,
            'backtest_strategy': backtest_strategy,
            'analyze_sentiment_transformer': analyze_sentiment_transformer,
            'calculate_supertrend': calculate_supertrend,
            'calculate_adx': calculate_adx,
            'calculate_psar': calculate_psar,
            'forecast_volatility_garch': forecast_volatility_garch,
            'get_volatility_regime': get_volatility_regime,
            'combined_trend_signal': combined_trend_signal,
            'predict_with_transformer': predict_with_transformer,
            'detect_anomalies_autoencoder': detect_anomalies_autoencoder,
        })

        _ml_resources_loaded = True
    except Exception as e:
        # If lazy import fails, log but allow the app to continue; operations will raise later if used.
        import logging
        logging.getLogger('app_modern').warning(f"Lazy ML import failed: {e}")

from src.risk_management import calculate_risk_metrics, calculate_stop_loss_take_profit
from src.backtester import SimpleBacktester, WalkForwardBacktester, generate_ma_crossover_signals, generate_rsi_signals, generate_macd_signals
from src.email_alerts import EmailAlertConfig, EmailAlertSender, AlertManager
from src.zerodha_integration import ZerodhaAuthenticator, ZerodhaKite, AutomatedTrader, analyze_portfolio

# Import UI modules
from ui.styles import get_custom_css, get_icon_mapping, get_theme_css
from ui.components import (
    create_metric_card,
    create_signal_badge,
    create_info_card,
    create_section_header,
    create_price_chart,
    create_volume_chart,
    create_comparison_chart,
    create_gauge_chart,
    create_heatmap
)
from ui.portfolio_builder import (
    create_portfolio_builder,
    create_advanced_portfolio_builder,
    create_mobile_responsive_portfolio,
    show_portfolio_recommendations
)

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# ══════════════════════════════════════════════════════════════════════
# CACHING FOR PERFORMANCE
# ══════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def load_stock_data_cached(symbol: str, start_date, end_date):
    """Cached stock data loading"""
    try:
        from src.symbol_utils import normalize_symbol
        symbol = normalize_symbol(symbol)
    except Exception:
        pass
    return load_stock_data(symbol, start_date, end_date)

@st.cache_data(ttl=86400, show_spinner=False)  # Cache for 24 hours
def get_fundamentals_cached(symbol: str):
    """Cached fundamentals - changes less frequently"""
    return get_fundamentals(symbol)

@st.cache_data(ttl=3600, show_spinner=False)
def calculate_indicators_cached(_df):
    """Cached indicator calculation - uses _df to avoid hashing issues"""
    df = _df.copy()
    df = calculate_technical_indicators(df)
    # Lazily import advanced indicators to avoid large memory use at startup
    try:
        load_ml_resources()
    except Exception:
        # If loading fails, allow the error to be surfaced when advanced indicators are used
        pass
    df = calculate_advanced_indicators(df)
    return df

@st.cache_data(ttl=3600, show_spinner=False)
def get_news_sentiment_cached(symbol: str):
    """Cached news sentiment"""
    return get_news_sentiment(symbol)

# ══════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ══════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title=APP_CONFIG["app_name"],
    page_icon=APP_CONFIG["icon"],
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://docs.streamlit.io',
        'Report a bug': 'https://github.com/streamlit/streamlit/issues',
        'About': f'# {APP_CONFIG["app_name"]} v{APP_CONFIG["version"]}\n\n{APP_CONFIG["description"]}'
    }
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Initialize dark mode flag if missing
if 'dark_mode_toggle' not in st.session_state:
    st.session_state['dark_mode_toggle'] = False

# Inject theme-specific CSS based on dark mode setting
st.markdown(get_theme_css(st.session_state.get('dark_mode_toggle', False)), unsafe_allow_html=True)

# Get icon mapping
icons = get_icon_mapping()

# ══════════════════════════════════════════════════════════════════════
# TOP BAR - NAVIGATION & SETTINGS
# ══════════════════════════════════════════════════════════════════════

# Create modern header
st.markdown('<div class="header-box">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 5, 2.5])

with col1:
    # Empty column for spacing (removed logo)
    st.markdown("")

with col2:
    st.markdown(f'<h1 class="app-title">💎 {APP_CONFIG["app_display_name"]}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="app-tagline">{APP_CONFIG["tagline"]}</p>', unsafe_allow_html=True)

with col3:
        # Display user info with profile dropdown and theme toggle
        col3_inner1, col3_inner2, col3_inner3 = st.columns([1.2, 0.8, 0.8])
        with col3_inner1:
            user_info = auth_manager.get_user_info()
            if user_info:
                # Create user profile dropdown
                st.markdown(f"""
                <div class='user-info'>
                    <p class='user-name'>👤 {user_info['name']}</p>
                    <p class='user-email'>{user_info['email']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("<div class='user-info'><p class='user-name'>Guest</p></div>", unsafe_allow_html=True)
        
        with col3_inner2:
            # Dark mode toggle
            dark_mode = st.checkbox("🌙", value=st.session_state.get('dark_mode_toggle', False), key="dark_mode_toggle", help="Toggle dark mode")
            if dark_mode != st.session_state.get('dark_mode_toggle', False):
                st.session_state['dark_mode_toggle'] = dark_mode
                st.rerun()
        
        with col3_inner3:
            col_menu1, col_menu2 = st.columns(2)

            with col_menu1:
                if st.button("👤 Profile", use_container_width=True, key="btn_profile", help="View your profile and manage settings"):
                    st.session_state.active_page = "👤 My Profile"
                    st.rerun()

            with col_menu2:
                if st.button("🚪 Logout", use_container_width=True, key="btn_logout", help="Logout from your account"):
                    # Clear all session data including Zerodha
                    auth_manager.logout()
                    # Clear Zerodha connection
                    if 'zerodha_connected' in st.session_state:
                        st.session_state.zerodha_connected = False
                    if 'zerodha_user_id' in st.session_state:
                        del st.session_state.zerodha_user_id
                    if 'zerodha_access_token' in st.session_state:
                        del st.session_state.zerodha_access_token
                    st.success("✅ Logged out successfully!")
                    import time
                    time.sleep(1)
                    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Create modern navigation
st.markdown('<div class="nav-container">', unsafe_allow_html=True)

# Check if Zerodha is connected
zerodha_connected = st.session_state.get('zerodha_connected', False)

# Adjust columns based on Zerodha connection
if zerodha_connected:
    nav_cols = st.columns([1, 1, 1.2, 1, 0.9, 1, 1.5, 1, 1, 1, 1, 0.9])
else:
    nav_cols = st.columns([1, 1, 1.2, 1, 0.9, 1, 1.5, 1, 1, 1, 0.9])

btn_data = [
    (nav_cols[0], "🏠 Home", "nav_home"),
    (nav_cols[1], "📊 Analysis", "nav_analysis"),
    (nav_cols[2], "🤖 AI Deep", "nav_ai"),
    (nav_cols[3], "🎯 Screener", "nav_screener"),
    (nav_cols[4], "📰 News", "nav_news"),
    (nav_cols[5], "🔬 Advanced", "nav_advanced"),
    (nav_cols[6], "🧠 Deep Learning", "nav_deeplearning"),
    (nav_cols[7], "📈 Backtest", "nav_backtest"),
    (nav_cols[8], "💼 Portfolio", "nav_portfolio"),
]

# Add Live Trading button only if Zerodha is connected
if zerodha_connected:
    btn_data.append((nav_cols[9], "🔴 Live Trading", "nav_livetrading"))
    btn_data.append((nav_cols[10], "⚙️ Settings", "nav_settings"))
    btn_data.append((nav_cols[11], "🚪 Logout", "nav_logout"))
else:
    btn_data.append((nav_cols[9], "⚙️ Settings", "nav_settings"))
    btn_data.append((nav_cols[10], "🚪 Logout", "nav_logout"))

button_results = {}
for col, label, key in btn_data:
    with col:
        button_results[key] = st.button(label, use_container_width=True, key=key, help=label)

home_btn = button_results["nav_home"]
analysis_btn = button_results["nav_analysis"]
ai_btn = button_results["nav_ai"]
screener_btn = button_results["nav_screener"]
news_btn = button_results["nav_news"]
advanced_btn = button_results["nav_advanced"]
deeplearning_btn = button_results["nav_deeplearning"]
backtest_btn = button_results["nav_backtest"]
portfolio_btn = button_results["nav_portfolio"]
livetrading_btn = button_results.get("nav_livetrading", False)
settings_btn = button_results["nav_settings"]
logout_btn = button_results["nav_logout"]

st.markdown('</div>', unsafe_allow_html=True)

# Debug: record which nav button was pressed last (helps diagnose click issues)
if 'last_nav_debug' not in st.session_state:
    st.session_state['last_nav_debug'] = None

for k, pressed in button_results.items():
    if pressed:
        st.session_state['last_nav_debug'] = k

# Optionally display debug info (set this to True while troubleshooting)
if True or st.session_state.get('show_nav_debug', False):
    st.info(f"Last nav pressed: {st.session_state.get('last_nav_debug')}")

# Determine active page
if 'active_page' not in st.session_state:
    st.session_state.active_page = "🏠 Home"

if home_btn:
    st.session_state.active_page = "🏠 Home"
    st.rerun()
elif analysis_btn:
    st.session_state.active_page = "📊 Stock Analysis"
    st.rerun()
elif ai_btn:
    st.session_state.active_page = "🤖 AI Deep Analysis"
    st.rerun()
elif screener_btn:
    st.session_state.active_page = "🎯 Smart Screener"
    st.rerun()
elif news_btn:
    st.session_state.active_page = "📰 General News"
    st.rerun()
elif advanced_btn:
    st.session_state.active_page = "🔬 Advanced Indicators"
    st.rerun()
elif deeplearning_btn:
    st.session_state.active_page = "🧠 Deep Learning"
    st.rerun()
elif backtest_btn:
    st.session_state.active_page = "📈 Strategy Backtest"
    st.rerun()
elif portfolio_btn:
    st.session_state.active_page = "💼 Portfolio Manager"
    st.rerun()
elif livetrading_btn:
    st.session_state.active_page = "🔴 Live Trading"
    st.rerun()
elif settings_btn:
    st.session_state.active_page = "⚙️ Settings"
    st.rerun()
elif logout_btn:
    # Handle logout - clear all session data
    auth_manager.logout()
    # Clear Zerodha connection data
    if 'zerodha_connected' in st.session_state:
        st.session_state.zerodha_connected = False
    if 'zerodha_user_id' in st.session_state:
        del st.session_state.zerodha_user_id
    if 'zerodha_access_token' in st.session_state:
        del st.session_state.zerodha_access_token
    if 'zerodha_api_key' in st.session_state:
        del st.session_state.zerodha_api_key
    if 'zerodha_api_secret' in st.session_state:
        del st.session_state.zerodha_api_secret
    st.success("✅ Logged out successfully!")
    st.info("Redirecting to login page...")
    import time
    time.sleep(1)
    st.rerun()

page = st.session_state.active_page

# Settings Bar (collapsible)
with st.expander("⚙️ Analysis Settings", expanded=False):
    settings_col1, settings_col2, settings_col3 = st.columns(3)

    with settings_col1:
        start_date = st.date_input(
            "📅 Start Date",
            value=datetime.now() - timedelta(days=365*3),
            help="Historical data start date"
        )

    with settings_col2:
        end_date = st.date_input(
            "📅 End Date",
            value=datetime.now(),
            help="Historical data end date"
        )

    with settings_col3:
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        st.info("💡 Adjust date range for historical analysis")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# PAGE ROUTING
# ══════════════════════════════════════════════════════════════════════

# Import page handlers directly for conditional rendering
from pages.home import render_home_page
from pages.analysis import render_stock_analysis
from pages.ai import render_ai
from pages.screener import render_smart_screener
from pages.news import render_general_news

try:
    from pages.advanced_indicators import render_advanced_indicators
except Exception as e:
    st.error(f"Error importing advanced_indicators: {e}")
    def render_advanced_indicators():
        st.error("Advanced Indicators page is currently unavailable.")
        
from pages.portfolio import render_portfolio_manager
from pages.deep_learning import render_deep_learning
from pages.backtest import render_strategy_backtest
from pages.profile import render_my_profile
from pages.security import render_security_settings
from pages.account import render_account_settings
from pages.zerodha_portfolio import render_zerodha_portfolio
from pages.zerodha_analyze import render_zerodha_analyze
from pages.zerodha_trade import render_zerodha_trade
from pages.settings import render_settings

# Route to the selected page using conditional rendering
if page == "🏠 Home":
    render_home_page()
elif page == "📊 Stock Analysis":
    render_stock_analysis(start_date, end_date)
elif page == "🤖 AI Deep Analysis":
    render_ai(start_date, end_date)
elif page == "🎯 Smart Screener":
    render_smart_screener()
elif page == "📰 General News":
    render_general_news()
elif page == "🔬 Advanced Indicators":
    render_advanced_indicators()
elif page == "💼 Portfolio Manager":
    render_portfolio_manager()
elif page == "🧠 Deep Learning":
    render_deep_learning()
elif page == "📈 Strategy Backtest":
    render_strategy_backtest()
elif page == "👤 My Profile":
    render_my_profile()
elif page == "🔐 Security Settings":
    render_security_settings()
elif page == "⚙️ Account Settings":
    render_account_settings()
elif page == "📊 Zerodha Portfolio":
    render_zerodha_portfolio()
elif page == "🔬 Zerodha Analyze":
    render_zerodha_analyze()
elif page == "🔁 Zerodha Trade":
    render_zerodha_trade()
elif page == "🔴 Live Trading":
    # Map Live Trading to Zerodha Trade page
    render_zerodha_trade()
elif page == "⚙️ Settings":
    render_settings()
else:
    # Default to home page if page not found
    st.error(f"Page '{page}' not found. Redirecting to Home.")
    render_home_page()

# ══════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #718096; padding: 20px;'>
    <p><strong>Disclaimer:</strong> This tool is for educational purposes only. Always do your own research before making investment decisions.</p>
    <p>Made with ❤️ using Python & Streamlit | © {APP_CONFIG["copyright_year"]}</p>
</div>
""", unsafe_allow_html=True)

