"""
Settings page module for AI Trading Lab PRO+
Comprehensive configuration and preferences management
"""
import streamlit as st
import json
import os
from datetime import datetime
from ui.components import create_section_header, get_theme_colors


def render_settings():
    """Render comprehensive Settings page with all configuration options."""
    theme_colors = get_theme_colors()
    
    # Header with gradient
    st.markdown(f"""
    <div style='background: {theme_colors['gradient_bg']}; padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: center;'>
        <h1 style='color: white; margin: 0;'>⚙️ Application Settings</h1>
        <p style='color: rgba(255,255,255,0.9); margin: 10px 0 0 0;'>
            Configure Your Trading Platform Preferences & Defaults
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load existing settings
    settings = load_settings()
    
    # Settings tabs
    tabs = st.tabs([
        "👤 User Preferences",
        "🎨 Display Settings", 
        "💰 Trading Defaults",
        "📊 Data & Performance",
        "🔔 Notifications & Alerts",
        "🛡️ Risk Management",
        "💾 Backup & Export"
    ])
    
    # Tab 1: User Preferences
    with tabs[0]:
        render_user_preferences(settings, theme_colors)
    
    # Tab 2: Display Settings
    with tabs[1]:
        render_display_settings(settings, theme_colors)
    
    # Tab 3: Trading Defaults
    with tabs[2]:
        render_trading_defaults(settings, theme_colors)
    
    # Tab 4: Data & Performance
    with tabs[3]:
        render_data_settings(settings, theme_colors)
    
    # Tab 5: Notifications & Alerts
    with tabs[4]:
        render_notification_settings(settings, theme_colors)
    
    # Tab 6: Risk Management
    with tabs[5]:
        render_risk_management(settings, theme_colors)
    
    # Tab 7: Backup & Export
    with tabs[6]:
        render_backup_export(settings, theme_colors)
    
    # Save button (sticky at bottom)
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("💾 Save All Settings", type="primary", use_container_width=True):
            save_settings(settings)
            st.success("✅ Settings saved successfully!")
            st.balloons()
    
    with col2:
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            if st.session_state.get('confirm_reset', False):
                reset_to_defaults()
                st.success("✅ Settings reset to defaults!")
                st.rerun()
            else:
                st.session_state.confirm_reset = True
                st.warning("⚠️ Click again to confirm reset")
    
    with col3:
        if st.button("📋 View Current Config", use_container_width=True):
            with st.expander("Current Configuration", expanded=True):
                st.json(settings)


def render_user_preferences(settings: dict, theme_colors: dict):
    """Render user preferences section."""
    st.markdown("### 👤 Personal Preferences")
    st.caption("Set your default preferences for quick access")
    
    # Default watchlist symbols
    st.markdown("#### 📊 Default Watchlist")
    default_symbols = st.text_area(
        "Favorite Symbols (comma-separated)",
        value=settings.get('default_symbols', 'TCS, INFY, RELIANCE, HDFCBANK, ICICIBANK'),
        help="Symbols that appear by default in analysis screens"
    )
    settings['default_symbols'] = default_symbols
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Default timeframe
        default_timeframe = st.selectbox(
            "⏰ Default Timeframe",
            options=["1 Day", "1 Week", "1 Month", "3 Months", "6 Months", "1 Year", "5 Years"],
            index=["1 Day", "1 Week", "1 Month", "3 Months", "6 Months", "1 Year", "5 Years"].index(
                settings.get('default_timeframe', '6 Months')
            ),
            help="Default time period for charts and analysis"
        )
        settings['default_timeframe'] = default_timeframe
    
    with col2:
        # Default chart type
        default_chart = st.selectbox(
            "📈 Default Chart Type",
            options=["Candlestick", "Line", "Area", "OHLC", "Heikin Ashi"],
            index=["Candlestick", "Line", "Area", "OHLC", "Heikin Ashi"].index(
                settings.get('default_chart', 'Candlestick')
            ),
            help="Preferred chart visualization type"
        )
        settings['default_chart'] = default_chart
    
    # Startup page
    st.markdown("#### 🏠 Startup Preferences")
    col3, col4 = st.columns(2)
    
    with col3:
        startup_page = st.selectbox(
            "Default Landing Page",
            options=["Home", "Analysis", "AI Deep", "Screener", "News", "Portfolio", "Backtest"],
            index=["Home", "Analysis", "AI Deep", "Screener", "News", "Portfolio", "Backtest"].index(
                settings.get('startup_page', 'Home')
            ),
            help="Page to show when app starts"
        )
        settings['startup_page'] = startup_page
    
    with col4:
        auto_refresh = st.checkbox(
            "🔄 Auto-refresh Data on Startup",
            value=settings.get('auto_refresh', True),
            help="Automatically fetch latest data when app starts"
        )
        settings['auto_refresh'] = auto_refresh
    
    # Language and region
    st.markdown("#### 🌐 Region & Format")
    col5, col6 = st.columns(2)
    
    with col5:
        currency_symbol = st.selectbox(
            "Currency Symbol",
            options=["₹ (INR)", "$ (USD)", "€ (EUR)", "£ (GBP)"],
            index=0,
            help="Currency display preference"
        )
        settings['currency_symbol'] = currency_symbol.split()[0]
    
    with col6:
        date_format = st.selectbox(
            "Date Format",
            options=["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"],
            index=["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"].index(
                settings.get('date_format', 'DD/MM/YYYY')
            ),
            help="Date display format"
        )
        settings['date_format'] = date_format


def render_display_settings(settings: dict, theme_colors: dict):
    """Render display and appearance settings."""
    st.markdown("### 🎨 Display & Appearance")
    st.caption("Customize the look and feel of the application")
    
    # Theme settings
    st.markdown("#### 🌓 Theme Settings")
    col1, col2 = st.columns(2)
    
    with col1:
        theme_mode = st.selectbox(
            "Color Theme",
            options=["Auto (System)", "Light Mode", "Dark Mode"],
            index=["Auto (System)", "Light Mode", "Dark Mode"].index(
                settings.get('theme_mode', 'Auto (System)')
            ),
            help="Choose your preferred theme"
        )
        settings['theme_mode'] = theme_mode
        
        # Chart color scheme
        color_scheme = st.selectbox(
            "Chart Color Scheme",
            options=["Default (Purple-Green)", "Classic (Red-Green)", "Blue-Orange", "Monochrome"],
            index=0,
            help="Color palette for charts and indicators"
        )
        settings['color_scheme'] = color_scheme
    
    with col2:
        font_size = st.select_slider(
            "Font Size",
            options=["Small", "Medium", "Large", "Extra Large"],
            value=settings.get('font_size', 'Medium'),
            help="Text size across the application"
        )
        settings['font_size'] = font_size
        
        chart_height = st.slider(
            "Default Chart Height (px)",
            min_value=400,
            max_value=800,
            value=settings.get('chart_height', 600),
            step=50,
            help="Height of chart visualizations"
        )
        settings['chart_height'] = chart_height
    
    # Data display preferences
    st.markdown("#### 📊 Data Display")
    col3, col4 = st.columns(2)
    
    with col3:
        decimal_places = st.slider(
            "Decimal Places",
            min_value=0,
            max_value=4,
            value=settings.get('decimal_places', 2),
            help="Number of decimal places for prices"
        )
        settings['decimal_places'] = decimal_places
        
        show_volume = st.checkbox(
            "📊 Show Volume by Default",
            value=settings.get('show_volume', True),
            help="Display volume bars on charts"
        )
        settings['show_volume'] = show_volume
    
    with col4:
        show_grid = st.checkbox(
            "📐 Show Chart Grid",
            value=settings.get('show_grid', True),
            help="Display grid lines on charts"
        )
        settings['show_grid'] = show_grid
        
        show_crosshair = st.checkbox(
            "➕ Show Crosshair",
            value=settings.get('show_crosshair', True),
            help="Display crosshair cursor on charts"
        )
        settings['show_crosshair'] = show_crosshair
    
    # Table preferences
    st.markdown("#### 📋 Table Settings")
    col5, col6 = st.columns(2)
    
    with col5:
        rows_per_page = st.slider(
            "Rows Per Page",
            min_value=10,
            max_value=100,
            value=settings.get('rows_per_page', 25),
            step=5,
            help="Number of rows in data tables"
        )
        settings['rows_per_page'] = rows_per_page
    
    with col6:
        compact_mode = st.checkbox(
            "📏 Compact Table Mode",
            value=settings.get('compact_mode', False),
            help="Reduce padding in tables for more data"
        )
        settings['compact_mode'] = compact_mode


def render_trading_defaults(settings: dict, theme_colors: dict):
    """Render trading calculation defaults."""
    st.markdown("### 💰 Trading Calculation Defaults")
    st.caption("Default values for trading cost calculations")
    
    st.info("""
    ℹ️ **What are these?**
    These defaults are used across Backtesting, Portfolio Analysis, and Trade Simulation features.
    You can override them in individual screens if needed.
    """)
    
    # Commission and fees
    st.markdown("#### 💵 Brokerage & Fees")
    col1, col2 = st.columns(2)
    
    with col1:
        commission_pct = st.number_input(
            "Commission Rate (%)",
            min_value=0.0,
            max_value=1.0,
            value=settings.get('commission_pct', 0.03),
            step=0.01,
            format="%.3f",
            help="Brokerage commission per trade (e.g., 0.03% for discount brokers)"
        )
        settings['commission_pct'] = commission_pct
        st.caption("💡 Typical: 0.03% (discount), 0.5% (full-service)")
    
    with col2:
        slippage_pct = st.number_input(
            "Slippage (%)",
            min_value=0.0,
            max_value=1.0,
            value=settings.get('slippage_pct', 0.1),
            step=0.05,
            format="%.2f",
            help="Expected price difference between order and execution"
        )
        settings['slippage_pct'] = slippage_pct
        st.caption("💡 Typical: 0.05-0.2% depending on liquidity")
    
    # Tax settings
    st.markdown("#### 📝 Tax Settings")
    col3, col4 = st.columns(2)
    
    with col3:
        stcg_tax = st.number_input(
            "STCG Tax Rate (%)",
            min_value=0.0,
            max_value=50.0,
            value=settings.get('stcg_tax', 15.0),
            step=0.5,
            help="Short Term Capital Gains tax rate"
        )
        settings['stcg_tax'] = stcg_tax
        st.caption("💡 India: 15% for equity")
    
    with col4:
        ltcg_tax = st.number_input(
            "LTCG Tax Rate (%)",
            min_value=0.0,
            max_value=50.0,
            value=settings.get('ltcg_tax', 10.0),
            step=0.5,
            help="Long Term Capital Gains tax rate"
        )
        settings['ltcg_tax'] = ltcg_tax
        st.caption("💡 India: 10% above ₹1L for equity")
    
    # Default position sizing
    st.markdown("#### 📏 Position Sizing Defaults")
    col5, col6 = st.columns(2)
    
    with col5:
        default_position_size = st.slider(
            "Default Position Size (% of Capital)",
            min_value=1,
            max_value=100,
            value=settings.get('default_position_size', 20),
            step=1,
            help="Default size for each position"
        )
        settings['default_position_size'] = default_position_size
        st.caption("💡 Risk management: 5-20% per position")
    
    with col6:
        max_positions = st.slider(
            "Maximum Concurrent Positions",
            min_value=1,
            max_value=20,
            value=settings.get('max_positions', 5),
            step=1,
            help="Maximum number of simultaneous holdings"
        )
        settings['max_positions'] = max_positions
        st.caption("💡 Diversification: 5-10 positions")
    
    # Stop loss defaults
    st.markdown("#### 🛡️ Default Stop Loss & Targets")
    col7, col8 = st.columns(2)
    
    with col7:
        default_stop_loss = st.slider(
            "Default Stop Loss (%)",
            min_value=1,
            max_value=20,
            value=settings.get('default_stop_loss', 5),
            step=1,
            help="Default stop loss percentage"
        )
        settings['default_stop_loss'] = default_stop_loss
    
    with col8:
        default_target = st.slider(
            "Default Target (%)",
            min_value=1,
            max_value=50,
            value=settings.get('default_target', 10),
            step=1,
            help="Default profit target percentage"
        )
        settings['default_target'] = default_target


def render_data_settings(settings: dict, theme_colors: dict):
    """Render data and performance settings."""
    st.markdown("### 📊 Data & Performance Settings")
    st.caption("Configure data sources, caching, and performance options")
    
    # Data sources
    st.markdown("#### 🔌 Data Sources")
    
    primary_source = st.selectbox(
        "Primary Data Provider",
        options=["Yahoo Finance", "NSE India", "BSE India", "Multi-Source"],
        index=["Yahoo Finance", "NSE India", "BSE India", "Multi-Source"].index(
            settings.get('primary_source', 'Yahoo Finance')
        ),
        help="Primary source for stock data"
    )
    settings['primary_source'] = primary_source
    
    fallback_enabled = st.checkbox(
        "🔄 Enable Fallback Sources",
        value=settings.get('fallback_enabled', True),
        help="Use alternate sources if primary fails"
    )
    settings['fallback_enabled'] = fallback_enabled
    
    # Cache settings
    st.markdown("#### 💾 Caching & Storage")
    col1, col2 = st.columns(2)
    
    with col1:
        cache_enabled = st.checkbox(
            "📦 Enable Data Caching",
            value=settings.get('cache_enabled', True),
            help="Cache data locally for faster loading"
        )
        settings['cache_enabled'] = cache_enabled
        
        cache_duration = st.selectbox(
            "Cache Duration",
            options=["5 minutes", "15 minutes", "1 hour", "1 day"],
            index=["5 minutes", "15 minutes", "1 hour", "1 day"].index(
                settings.get('cache_duration', '15 minutes')
            ),
            help="How long to keep cached data"
        )
        settings['cache_duration'] = cache_duration
    
    with col2:
        if st.button("🗑️ Clear Cache Now", use_container_width=True):
            try:
                st.cache_data.clear()
                st.success("✅ Cache cleared successfully!")
            except Exception as e:
                st.error(f"❌ Error clearing cache: {str(e)}")
        
        auto_clear = st.checkbox(
            "🔄 Auto-clear Cache Daily",
            value=settings.get('auto_clear_cache', False),
            help="Automatically clear cache at midnight"
        )
        settings['auto_clear_cache'] = auto_clear
    
    # API settings
    st.markdown("#### 🔑 API Configuration (Optional)")
    st.caption("Add your own API keys for enhanced features")
    
    with st.expander("Alpha Vantage API"):
        alpha_key = st.text_input(
            "Alpha Vantage API Key",
            value=settings.get('alpha_vantage_key', ''),
            type="password",
            help="For US market data and fundamentals"
        )
        settings['alpha_vantage_key'] = alpha_key
        st.caption("[Get free API key](https://www.alphavantage.co/support/#api-key)")
    
    with st.expander("News API"):
        news_key = st.text_input(
            "News API Key",
            value=settings.get('news_api_key', ''),
            type="password",
            help="For enhanced news features"
        )
        settings['news_api_key'] = news_key
        st.caption("[Get free API key](https://newsapi.org/register)")
    
    # Performance settings
    st.markdown("#### ⚡ Performance Options")
    col3, col4 = st.columns(2)
    
    with col3:
        parallel_processing = st.checkbox(
            "🚀 Enable Parallel Processing",
            value=settings.get('parallel_processing', True),
            help="Use multiple CPU cores for faster analysis"
        )
        settings['parallel_processing'] = parallel_processing
    
    with col4:
        preload_data = st.checkbox(
            "📥 Preload Common Symbols",
            value=settings.get('preload_data', False),
            help="Load watchlist data in background on startup"
        )
        settings['preload_data'] = preload_data


def render_notification_settings(settings: dict, theme_colors: dict):
    """Render notification and alert settings."""
    st.markdown("### 🔔 Notifications & Alerts")
    st.caption("Configure how you want to be notified about important events")
    
    # Alert preferences
    st.markdown("#### ⚠️ Alert Notifications")
    
    enable_alerts = st.checkbox(
        "🔔 Enable In-App Alerts",
        value=settings.get('enable_alerts', True),
        help="Show notifications within the application"
    )
    settings['enable_alerts'] = enable_alerts
    
    if enable_alerts:
        st.markdown("**Alert Triggers:**")
        col1, col2 = st.columns(2)
        
        with col1:
            alert_price_change = st.number_input(
                "Price Change Alert (%)",
                min_value=0.0,
                max_value=20.0,
                value=settings.get('alert_price_change', 5.0),
                step=0.5,
                help="Alert when stock moves by this percentage"
            )
            settings['alert_price_change'] = alert_price_change
            
            alert_volume_spike = st.number_input(
                "Volume Spike Alert (x times)",
                min_value=1.0,
                max_value=10.0,
                value=settings.get('alert_volume_spike', 2.0),
                step=0.5,
                help="Alert when volume exceeds average by this multiple"
            )
            settings['alert_volume_spike'] = alert_volume_spike
        
        with col2:
            alert_rsi = st.checkbox(
                "📊 RSI Extreme Alerts",
                value=settings.get('alert_rsi', True),
                help="Alert on RSI < 30 (oversold) or > 70 (overbought)"
            )
            settings['alert_rsi'] = alert_rsi
            
            alert_pattern = st.checkbox(
                "📈 Pattern Detection Alerts",
                value=settings.get('alert_pattern', True),
                help="Alert when key chart patterns are detected"
            )
            settings['alert_pattern'] = alert_pattern
    
    # Email notifications
    st.markdown("#### 📧 Email Notifications (Coming Soon)")
    st.caption("Email alerts for critical events")
    
    email_enabled = st.checkbox(
        "📧 Enable Email Alerts",
        value=settings.get('email_enabled', False),
        help="Send alerts to your email",
        disabled=True  # Feature coming soon
    )
    settings['email_enabled'] = email_enabled
    
    if email_enabled:
        email_address = st.text_input(
            "Email Address",
            value=settings.get('email_address', ''),
            help="Where to send alert emails"
        )
        settings['email_address'] = email_address
    
    # Sound notifications
    st.markdown("#### 🔊 Sound Alerts")
    col3, col4 = st.columns(2)
    
    with col3:
        sound_enabled = st.checkbox(
            "🔊 Enable Sound Alerts",
            value=settings.get('sound_enabled', False),
            help="Play sounds for notifications"
        )
        settings['sound_enabled'] = sound_enabled
    
    with col4:
        if sound_enabled:
            sound_volume = st.slider(
                "Volume",
                min_value=0,
                max_value=100,
                value=settings.get('sound_volume', 50),
                help="Alert sound volume"
            )
            settings['sound_volume'] = sound_volume


def render_risk_management(settings: dict, theme_colors: dict):
    """Render risk management settings."""
    st.markdown("### 🛡️ Risk Management")
    st.caption("Set system-wide risk controls and safeguards")
    
    st.info("""
    ℹ️ **Risk Management Settings**
    These settings help protect your capital by enforcing limits and warnings across the platform.
    """)
    
    # Portfolio risk limits
    st.markdown("#### 📊 Portfolio Risk Limits")
    col1, col2 = st.columns(2)
    
    with col1:
        max_portfolio_risk = st.slider(
            "Maximum Portfolio Risk (%)",
            min_value=1,
            max_value=50,
            value=settings.get('max_portfolio_risk', 20),
            step=1,
            help="Maximum percentage of capital at risk at any time"
        )
        settings['max_portfolio_risk'] = max_portfolio_risk
        st.caption("💡 Conservative: 5-10%, Moderate: 10-20%, Aggressive: 20%+")
        
        max_position_risk = st.slider(
            "Maximum Per-Position Risk (%)",
            min_value=1,
            max_value=25,
            value=settings.get('max_position_risk', 5),
            step=1,
            help="Maximum percentage to risk on a single trade"
        )
        settings['max_position_risk'] = max_position_risk
        st.caption("💡 Recommended: 1-5% per position")
    
    with col2:
        max_correlation = st.slider(
            "Maximum Position Correlation",
            min_value=0.0,
            max_value=1.0,
            value=settings.get('max_correlation', 0.7),
            step=0.05,
            help="Warn if positions are highly correlated"
        )
        settings['max_correlation'] = max_correlation
        st.caption("💡 Lower = better diversification")
        
        max_sector_exposure = st.slider(
            "Maximum Sector Exposure (%)",
            min_value=10,
            max_value=100,
            value=settings.get('max_sector_exposure', 30),
            step=5,
            help="Maximum allocation to any single sector"
        )
        settings['max_sector_exposure'] = max_sector_exposure
        st.caption("💡 Prevents over-concentration")
    
    # Trading limits
    st.markdown("#### 🎯 Trading Limits")
    col3, col4 = st.columns(2)
    
    with col3:
        max_daily_trades = st.number_input(
            "Maximum Daily Trades",
            min_value=1,
            max_value=100,
            value=settings.get('max_daily_trades', 10),
            step=1,
            help="Limit trades per day to prevent overtrading"
        )
        settings['max_daily_trades'] = max_daily_trades
        
        max_daily_loss = st.number_input(
            "Maximum Daily Loss (%)",
            min_value=1,
            max_value=20,
            value=settings.get('max_daily_loss', 5),
            step=1,
            help="Stop trading if daily loss exceeds this"
        )
        settings['max_daily_loss'] = max_daily_loss
    
    with col4:
        min_trade_size = st.number_input(
            "Minimum Trade Size (₹)",
            min_value=100,
            max_value=10000,
            value=settings.get('min_trade_size', 500),
            step=100,
            help="Avoid very small trades with high commission impact"
        )
        settings['min_trade_size'] = min_trade_size
        
        require_stop_loss = st.checkbox(
            "🛡️ Require Stop Loss on All Trades",
            value=settings.get('require_stop_loss', True),
            help="Force stop loss on every position"
        )
        settings['require_stop_loss'] = require_stop_loss
    
    # Risk warnings
    st.markdown("#### ⚠️ Warning Triggers")
    
    warn_high_volatility = st.checkbox(
        "⚠️ Warn on High Volatility Stocks",
        value=settings.get('warn_high_volatility', True),
        help="Show warning when trading highly volatile stocks"
    )
    settings['warn_high_volatility'] = warn_high_volatility
    
    warn_low_liquidity = st.checkbox(
        "⚠️ Warn on Low Liquidity Stocks",
        value=settings.get('warn_low_liquidity', True),
        help="Show warning when trading illiquid stocks"
    )
    settings['warn_low_liquidity'] = warn_low_liquidity


def render_backup_export(settings: dict, theme_colors: dict):
    """Render backup and export settings."""
    st.markdown("### 💾 Backup & Export")
    st.caption("Save your settings and data for backup or transfer")
    
    # Export settings
    st.markdown("#### 📤 Export Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export All Settings", type="primary", use_container_width=True):
            try:
                settings_json = json.dumps(settings, indent=2)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"trading_settings_{timestamp}.json"
                
                st.download_button(
                    label="💾 Download Settings File",
                    data=settings_json,
                    file_name=filename,
                    mime="application/json",
                    use_container_width=True
                )
                st.success("✅ Settings ready for download!")
            except Exception as e:
                st.error(f"❌ Export failed: {str(e)}")
    
    with col2:
        uploaded_file = st.file_uploader(
            "📤 Import Settings",
            type=['json'],
            help="Upload previously exported settings file"
        )
        
        if uploaded_file is not None:
            try:
                imported_settings = json.load(uploaded_file)
                if st.button("✅ Apply Imported Settings", use_container_width=True):
                    save_settings(imported_settings)
                    st.success("✅ Settings imported successfully!")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Import failed: {str(e)}")
    
    # Auto backup
    st.markdown("#### 🔄 Automatic Backup")
    
    auto_backup = st.checkbox(
        "🔄 Enable Auto-Backup",
        value=settings.get('auto_backup', True),
        help="Automatically save settings periodically"
    )
    settings['auto_backup'] = auto_backup
    
    if auto_backup:
        backup_frequency = st.selectbox(
            "Backup Frequency",
            options=["Daily", "Weekly", "Monthly"],
            index=["Daily", "Weekly", "Monthly"].index(
                settings.get('backup_frequency', 'Weekly')
            ),
            help="How often to create automatic backups"
        )
        settings['backup_frequency'] = backup_frequency
    
    # Data management
    st.markdown("#### 🗂️ Data Management")
    
    st.info("""
    📊 **Current Storage Usage:**
    - Settings: < 1 KB
    - Cache: Managed automatically
    - Session data: Cleared on exit
    """)
    
    col3, col4, col5 = st.columns(3)
    
    with col3:
        if st.button("🗑️ Clear All Cache", use_container_width=True):
            try:
                st.cache_data.clear()
                st.success("✅ Cache cleared!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with col4:
        if st.button("🔄 Reset Session", use_container_width=True):
            st.session_state.clear()
            st.success("✅ Session reset!")
            st.rerun()
    
    with col5:
        if st.button("♻️ Full Reset", use_container_width=True):
            if st.session_state.get('confirm_full_reset', False):
                reset_to_defaults()
                st.cache_data.clear()
                st.session_state.clear()
                st.success("✅ Complete reset done!")
                st.rerun()
            else:
                st.session_state.confirm_full_reset = True
                st.warning("⚠️ Click again to confirm")


def load_settings() -> dict:
    """Load settings from session state or create defaults."""
    if 'app_settings' not in st.session_state:
        st.session_state.app_settings = get_default_settings()
    return st.session_state.app_settings


def save_settings(settings: dict):
    """Save settings to session state."""
    st.session_state.app_settings = settings


def get_default_settings() -> dict:
    """Return default settings configuration."""
    return {
        # User preferences
        'default_symbols': 'TCS, INFY, RELIANCE, HDFCBANK, ICICIBANK',
        'default_timeframe': '6 Months',
        'default_chart': 'Candlestick',
        'startup_page': 'Home',
        'auto_refresh': True,
        'currency_symbol': '₹',
        'date_format': 'DD/MM/YYYY',
        
        # Display settings
        'theme_mode': 'Auto (System)',
        'color_scheme': 'Default (Purple-Green)',
        'font_size': 'Medium',
        'chart_height': 600,
        'decimal_places': 2,
        'show_volume': True,
        'show_grid': True,
        'show_crosshair': True,
        'rows_per_page': 25,
        'compact_mode': False,
        
        # Trading defaults
        'commission_pct': 0.03,
        'slippage_pct': 0.1,
        'stcg_tax': 15.0,
        'ltcg_tax': 10.0,
        'default_position_size': 20,
        'max_positions': 5,
        'default_stop_loss': 5,
        'default_target': 10,
        
        # Data settings
        'primary_source': 'Yahoo Finance',
        'fallback_enabled': True,
        'cache_enabled': True,
        'cache_duration': '15 minutes',
        'auto_clear_cache': False,
        'alpha_vantage_key': '',
        'news_api_key': '',
        'parallel_processing': True,
        'preload_data': False,
        
        # Notifications
        'enable_alerts': True,
        'alert_price_change': 5.0,
        'alert_volume_spike': 2.0,
        'alert_rsi': True,
        'alert_pattern': True,
        'email_enabled': False,
        'email_address': '',
        'sound_enabled': False,
        'sound_volume': 50,
        
        # Risk management
        'max_portfolio_risk': 20,
        'max_position_risk': 5,
        'max_correlation': 0.7,
        'max_sector_exposure': 30,
        'max_daily_trades': 10,
        'max_daily_loss': 5,
        'min_trade_size': 500,
        'require_stop_loss': True,
        'warn_high_volatility': True,
        'warn_low_liquidity': True,
        
        # Backup
        'auto_backup': True,
        'backup_frequency': 'Weekly'
    }


def reset_to_defaults():
    """Reset all settings to default values."""
    st.session_state.app_settings = get_default_settings()
    st.session_state.confirm_reset = False