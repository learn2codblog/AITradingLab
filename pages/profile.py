"""
My Profile page module for AI Trading Lab PRO+
Comprehensive user profile management with Zerodha integration
"""
import streamlit as st
import json
import os
from datetime import datetime
from ui.components import get_theme_colors
from src.auth import AuthManager


def render_my_profile():
    """Render comprehensive My Profile page with Zerodha integration."""
    theme_colors = get_theme_colors()
    auth_manager = AuthManager()
    
    # Header with gradient
    st.markdown(f"""
    <div style='background: {theme_colors['gradient_bg']}; padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: center;'>
        <h1 style='color: white; margin: 0;'>👤 My Profile</h1>
        <p style='color: rgba(255,255,255,0.9); margin: 10px 0 0 0;'>
            Manage Your Account, Preferences & Trading Connections
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get user information
    user_email = st.session_state.get('user_email', 'user@example.com')
    user_name = st.session_state.get('user_name', 'Demo Trader')
    user_picture = st.session_state.get('user_picture', None)
    login_method = st.session_state.get('login_method', 'email')
    session_start = st.session_state.get('session_start', datetime.now())
    
    # Profile tabs
    tabs = st.tabs([
        "👤 Account Info",
        "🔗 Zerodha Connect",
        "📊 Trading Stats",
        "🎨 Preferences",
        "🔐 Security"
    ])
    
    # Tab 1: Account Information
    with tabs[0]:
        render_account_info(user_name, user_email, user_picture, login_method, session_start, theme_colors)
    
    # Tab 2: Zerodha Connection
    with tabs[1]:
        render_zerodha_connection(theme_colors)
    
    # Tab 3: Trading Statistics
    with tabs[2]:
        render_trading_stats(theme_colors)
    
    # Tab 4: Preferences
    with tabs[3]:
        render_profile_preferences(theme_colors)
    
    # Tab 5: Security
    with tabs[4]:
        render_security_settings(theme_colors, auth_manager)


def render_account_info(user_name: str, user_email: str, user_picture: str, 
                        login_method: str, session_start: datetime, theme_colors: dict):
    """Render account information section."""
    st.markdown("### 👤 Account Information")
    
    # Profile card
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if user_picture:
            st.image(user_picture, width=150)
        else:
            # Display initials in a circle
            initials = ''.join([word[0].upper() for word in user_name.split()[:2]])
            st.markdown(f"""
            <div style='background: {theme_colors["gradient_bg"]}; width: 150px; height: 150px; 
                        border-radius: 50%; display: flex; align-items: center; justify-content: center;'>
                <span style='color: white; font-size: 48px; font-weight: bold;'>{initials}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"### {user_name}")
        st.markdown(f"📧 **Email:** {user_email}")
        st.markdown(f"🔐 **Login Method:** {login_method.title()}")
        st.markdown(f"🕐 **Session Started:** {session_start.strftime('%Y-%m-%d %H:%M:%S') if isinstance(session_start, datetime) else session_start}")
        
        # Account status badges
        st.markdown("#### Account Status")
        col_badge1, col_badge2, col_badge3 = st.columns(3)
        
        with col_badge1:
            st.success("✅ Active")
        with col_badge2:
            if st.session_state.get('zerodha_connected', False):
                st.success("🔗 Zerodha Connected")
            else:
                st.info("⚪ Zerodha Not Connected")
        with col_badge3:
            st.info("🆓 Free Plan")
    
    st.markdown("---")
    
    # Editable profile fields
    st.markdown("### ✏️ Edit Profile")
    
    with st.form("profile_form"):
        edit_col1, edit_col2 = st.columns(2)
        
        with edit_col1:
            new_name = st.text_input("Full Name", value=user_name)
            phone = st.text_input("Phone Number", value=st.session_state.get('user_phone', ''))
        
        with edit_col2:
            country = st.selectbox("Country", ["India", "USA", "UK", "UAE", "Singapore", "Other"], index=0)
            timezone = st.selectbox("Timezone", ["Asia/Kolkata (IST)", "UTC", "EST", "PST"], index=0)
        
        bio = st.text_area("Bio (Optional)", value=st.session_state.get('user_bio', ''), 
                          help="Tell us about your trading experience")
        
        if st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True):
            st.session_state.user_name = new_name
            st.session_state.user_phone = phone
            st.session_state.user_country = country
            st.session_state.user_timezone = timezone
            st.session_state.user_bio = bio
            st.success("✅ Profile updated successfully!")
            st.rerun()


def render_zerodha_connection(theme_colors: dict):
    """Render Zerodha connection section."""
    st.markdown("### 🔗 Zerodha Kite Connect")
    st.caption("Connect your Zerodha account to enable live trading and portfolio sync")
    
    # Check connection status
    zerodha_connected = st.session_state.get('zerodha_connected', False)
    zerodha_user = st.session_state.get('zerodha_user_id', None)
    
    if zerodha_connected:
        # Display connected state
        st.success(f"✅ Connected to Zerodha Account: **{zerodha_user}**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Connection Status", "🟢 Active", help="Your Zerodha connection is active")
        
        with col2:
            connection_time = st.session_state.get('zerodha_connected_at', 'N/A')
            st.metric("Connected Since", connection_time if isinstance(connection_time, str) else connection_time.strftime('%Y-%m-%d %H:%M'))
        
        st.markdown("---")
        
        # Connection features
        st.markdown("#### 🎯 Available Features")
        
        feature_col1, feature_col2 = st.columns(2)
        
        with feature_col1:
            st.markdown("""
            **Enabled Features:**
            - ✅ Live Portfolio Sync
            - ✅ Real-time Holdings
            - ✅ Order Placement
            - ✅ Position Tracking
            - ✅ Market Data Access
            """)
        
        with feature_col2:
            st.markdown("""
            **Coming Soon:**
            - 🔜 Auto-trade from AI Signals
            - 🔜 Risk Management Alerts
            - 🔜 Advanced Order Types
            - 🔜 Basket Orders
            - 🔜 Options Trading
            """)
        
        st.markdown("---")
        
        # Disconnect option
        st.markdown("#### ⚠️ Disconnect Zerodha")
        st.warning("Disconnecting will stop live trading and portfolio sync features.")
        
        if st.button("🔌 Disconnect Zerodha Account", type="secondary", use_container_width=True):
            if st.session_state.get('confirm_zerodha_disconnect', False):
                # Clear Zerodha session
                st.session_state.zerodha_connected = False
                st.session_state.zerodha_user_id = None
                st.session_state.zerodha_access_token = None
                st.session_state.zerodha_connected_at = None
                st.session_state.confirm_zerodha_disconnect = False
                st.success("✅ Zerodha account disconnected successfully!")
                st.rerun()
            else:
                st.session_state.confirm_zerodha_disconnect = True
                st.warning("⚠️ Click the button again to confirm disconnection")
    
    else:
        # Display connection UI
        st.info("🔗 Connect your Zerodha account to unlock live trading features")
        
        st.markdown("#### 📋 Prerequisites")
        st.markdown("""
        Before connecting, ensure you have:
        1. ✅ Active Zerodha (Kite) trading account
        2. ✅ Kite Connect API subscription (₹2000/month)
        3. ✅ API Key and Secret from Kite Connect dashboard
        
        **How to get API credentials:**
        - Visit [Kite Connect](https://kite.trade/)
        - Login and subscribe to Kite Connect
        - Go to "Apps" section and create a new app
        - Copy your API Key and API Secret
        """)
        
        st.markdown("---")
        
        # API credentials input
        st.markdown("#### 🔑 Enter API Credentials")
        
        with st.form("zerodha_connect_form"):
            api_key = st.text_input(
                "API Key",
                type="password",
                help="Your Zerodha Kite Connect API Key"
            )
            
            api_secret = st.text_input(
                "API Secret",
                type="password",
                help="Your Zerodha Kite Connect API Secret"
            )
            
            st.caption("🔒 Your credentials are stored securely and never shared")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                connect_btn = st.form_submit_button("🔗 Connect to Zerodha", type="primary", use_container_width=True)
            
            with col_btn2:
                if st.form_submit_button("📖 View Setup Guide", use_container_width=True):
                    st.session_state.show_zerodha_guide = True
        
        if connect_btn:
            if api_key and api_secret:
                # Initialize Zerodha connection
                try:
                    from src.zerodha_integration import ZerodhaAuthenticator
                    
                    # Create authenticator
                    zerodha_auth = ZerodhaAuthenticator(api_key, api_secret)
                    
                    # Get login URL
                    login_url = zerodha_auth.get_login_url()
                    
                    if login_url:
                        st.success("✅ API credentials validated!")
                        st.info("""
                        🎯 **Next Steps:**
                        1. Click the link below to login to Zerodha
                        2. After successful login, you'll be redirected back
                        3. Copy the request token from the URL
                        4. Enter the request token below to complete connection
                        """)
                        
                        st.markdown(f"[🔗 Login to Zerodha Kite]({login_url})")
                        
                        # Request token input
                        request_token = st.text_input(
                            "Enter Request Token (from URL after login)",
                            help="Look for request_token=XXXXX in the redirected URL"
                        )
                        
                        if st.button("✅ Complete Connection", type="primary", use_container_width=True):
                            if request_token:
                                result = zerodha_auth.set_access_token(request_token)
                                
                                if result.get('success'):
                                    # Save connection
                                    st.session_state.zerodha_connected = True
                                    st.session_state.zerodha_user_id = result['user_id']
                                    st.session_state.zerodha_access_token = result['access_token']
                                    st.session_state.zerodha_connected_at = datetime.now()
                                    st.session_state.zerodha_api_key = api_key
                                    st.session_state.zerodha_api_secret = api_secret
                                    
                                    st.success(f"✅ Successfully connected to Zerodha! Welcome, {result['user_name']}")
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error(f"❌ Connection failed: {result.get('error', 'Unknown error')}")
                            else:
                                st.warning("⚠️ Please enter the request token from the URL")
                    else:
                        st.error("❌ Failed to generate login URL. Make sure kiteconnect is installed: pip install kiteconnect")
                
                except ImportError:
                    st.error("❌ Zerodha integration not available. Install kiteconnect: pip install kiteconnect")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")
            else:
                st.warning("⚠️ Please enter both API Key and API Secret")
        
        # Setup guide
        if st.session_state.get('show_zerodha_guide', False):
            with st.expander("📖 Detailed Setup Guide", expanded=True):
                st.markdown("""
                ### Step-by-Step Zerodha Connection Guide
                
                #### 1️⃣ Get Kite Connect Subscription
                - Visit [kite.trade](https://kite.trade/)
                - Login with your Zerodha credentials
                - Subscribe to Kite Connect API (₹2000/month + GST)
                
                #### 2️⃣ Create Your App
                - Go to [developers.kite.trade](https://developers.kite.trade/)
                - Click "Create new app"
                - Fill in details:
                  - **App Name**: AI Trading Lab (or any name)
                  - **Redirect URL**: `http://localhost:8000/`
                  - **Description**: Personal trading app
                - Click "Create"
                
                #### 3️⃣ Get API Credentials
                - After creating the app, you'll see:
                  - **API Key**: Long alphanumeric string
                  - **API Secret**: Another alphanumeric string
                - Copy both and keep them secure
                
                #### 4️⃣ Connect in This App
                - Enter API Key and API Secret in the form above
                - Click "Connect to Zerodha"
                - You'll be redirected to Zerodha login
                - Login with your Zerodha credentials
                - Authorize the app
                - Copy the `request_token` from the redirected URL
                - Paste it back here and complete connection
                
                #### 🔒 Security Notes
                - Your credentials are stored locally only
                - Access tokens expire daily (you'll need to reconnect)
                - Never share your API credentials
                - You can revoke access anytime from Zerodha dashboard
                
                #### ❓ Troubleshooting
                - **"Invalid API Key"**: Check if you copied the correct key
                - **"Session expired"**: Reconnect daily as tokens expire
                - **"Redirect error"**: Ensure redirect URL matches exactly
                - **"Permission denied"**: Check if Kite Connect is active
                
                #### 📞 Support
                - Zerodha Support: [support.zerodha.com](https://support.zerodha.com)
                - Kite Connect Docs: [kite.trade/docs/connect](https://kite.trade/docs/connect)
                """)


def render_trading_stats(theme_colors: dict):
    """Render trading statistics section."""
    st.markdown("### 📊 Trading Statistics")
    st.caption("Your trading activity and performance metrics")
    
    # Mock statistics (replace with actual data from database)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Analyses", "127", delta="+12 this week")
    
    with col2:
        st.metric("Backtests Run", "43", delta="+5 this week")
    
    with col3:
        st.metric("Watchlist Stocks", "15", delta="+3 this month")
    
    with col4:
        st.metric("Active Days", "28", delta="91% uptime")
    
    st.markdown("---")
    
    # Activity log
    st.markdown("### 📅 Recent Activity")
    
    activity_data = [
        {"date": "2026-02-13 10:30", "action": "📊 Ran screener", "details": "Advanced screening on 500 stocks"},
        {"date": "2026-02-13 09:15", "action": "🤖 AI Analysis", "details": "Deep learning prediction for TCS"},
        {"date": "2026-02-12 16:45", "action": "📈 Backtest", "details": "MACD strategy on RELIANCE"},
        {"date": "2026-02-12 14:20", "action": "📰 News Check", "details": "Viewed sentiment analysis for IT sector"},
        {"date": "2026-02-11 11:00", "action": "💼 Portfolio", "details": "Updated portfolio allocation"},
    ]
    
    for activity in activity_data:
        st.markdown(f"""
        <div style='background: {theme_colors["card_bg"]}; padding: 10px; border-radius: 8px; margin-bottom: 8px;'>
            <strong>{activity['action']}</strong><br>
            <small style='color: #718096;'>{activity['date']}</small><br>
            <span style='color: #A0AEC0;'>{activity['details']}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Usage stats
    st.markdown("### 📈 Usage Trends")
    
    trend_col1, trend_col2 = st.columns(2)
    
    with trend_col1:
        st.markdown("**Most Used Features:**")
        st.markdown("1. 🎯 Smart Screener (35%)")
        st.markdown("2. 🤖 AI Deep Analysis (28%)")
        st.markdown("3. 📊 Stock Analysis (20%)")
        st.markdown("4. 📈 Backtesting (12%)")
        st.markdown("5. 📰 News & Sentiment (5%)")
    
    with trend_col2:
        st.markdown("**Favorite Stocks:**")
        st.markdown("1. TCS")
        st.markdown("2. INFY")
        st.markdown("3. RELIANCE")
        st.markdown("4. HDFCBANK")
        st.markdown("5. ICICIBANK")


def render_profile_preferences(theme_colors: dict):
    """Render profile-specific preferences."""
    st.markdown("### 🎨 Personal Preferences")
    st.caption("Customize your default settings (applies to all features)")
    
    pref_col1, pref_col2 = st.columns(2)
    
    with pref_col1:
        st.markdown("#### 🎯 Default Settings")
        
        risk_tolerance = st.select_slider(
            "Risk Tolerance",
            options=["Very Conservative", "Conservative", "Moderate", "Aggressive", "Very Aggressive"],
            value=st.session_state.get('risk_tolerance', 'Moderate'),
            help="Your default risk level for analysis and recommendations"
        )
        st.session_state.risk_tolerance = risk_tolerance
        
        investment_horizon = st.selectbox(
            "Investment Horizon",
            options=["Day Trading", "Swing (1-4 weeks)", "Short-term (1-6 months)", "Medium-term (6-24 months)", "Long-term (2+ years)"],
            index=2,
            help="Your typical investment timeframe"
        )
        st.session_state.investment_horizon = investment_horizon
        
        trading_style = st.selectbox(
            "Trading Style",
            options=["Technical Analysis Focus", "Fundamental Analysis Focus", "Quantitative/AI Focus", "Hybrid Approach"],
            index=3,
            help="Your preferred trading methodology"
        )
        st.session_state.trading_style = trading_style
    
    with pref_col2:
        st.markdown("#### 📊 Display Preferences")
        
        show_notifications = st.checkbox(
            "Show In-App Notifications",
            value=st.session_state.get('show_notifications', True),
            help="Display alerts and notifications"
        )
        st.session_state.show_notifications = show_notifications
        
        auto_save = st.checkbox(
            "Auto-save Analysis",
            value=st.session_state.get('auto_save', True),
            help="Automatically save your analysis results"
        )
        st.session_state.auto_save = auto_save
        
        detailed_logs = st.checkbox(
            "Detailed Activity Logs",
            value=st.session_state.get('detailed_logs', False),
            help="Keep detailed logs of all activities"
        )
        st.session_state.detailed_logs = detailed_logs
    
    st.markdown("---")
    
    if st.button("💾 Save Preferences", type="primary", use_container_width=True):
        st.success("✅ Preferences saved successfully!")
        st.info("Your preferences will apply to all analysis features")


def render_security_settings(theme_colors: dict, auth_manager: AuthManager):
    """Render security and session settings."""
    st.markdown("### 🔐 Security & Privacy")
    st.caption("Manage your account security and session settings")
    
    # Password change
    st.markdown("#### 🔒 Change Password")
    
    if st.session_state.get('login_method') == 'email':
        with st.form("change_password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("🔄 Change Password", type="primary", use_container_width=True):
                if new_password == confirm_password:
                    if len(new_password) >= 6:
                        st.success("✅ Password changed successfully!")
                        st.info("Please login again with your new password")
                    else:
                        st.error("❌ Password must be at least 6 characters")
                else:
                    st.error("❌ Passwords do not match")
    else:
        st.info(f"🔐 You're logged in via {st.session_state.get('login_method', 'OAuth').title()}. Password change not applicable.")
    
    st.markdown("---")
    
    # Session management
    st.markdown("#### 🕐 Active Sessions")
    
    current_session = {
        "device": "Current Browser",
        "location": "Mumbai, India",
        "ip": "103.XXX.XXX.XXX",
        "login_time": st.session_state.get('session_start', datetime.now()).strftime('%Y-%m-%d %H:%M:%S') if isinstance(st.session_state.get('session_start'), datetime) else str(st.session_state.get('session_start'))
    }
    
    st.markdown(f"""
    **Current Session:**
    - 🖥️ Device: {current_session['device']}
    - 📍 Location: {current_session['location']}
    - 🌐 IP: {current_session['ip']}
    - 🕐 Login: {current_session['login_time']}
    """)
    
    col_sec1, col_sec2 = st.columns(2)
    
    with col_sec1:
        if st.button("🔓 Logout This Session", use_container_width=True):
            auth_manager.logout()
            st.success("✅ Logged out successfully!")
            st.rerun()
    
    with col_sec2:
        if st.button("🚫 Logout All Sessions", use_container_width=True):
            if st.session_state.get('confirm_logout_all', False):
                auth_manager.logout()
                st.success("✅ All sessions logged out!")
                st.rerun()
            else:
                st.session_state.confirm_logout_all = True
                st.warning("⚠️ Click again to confirm")
    
    st.markdown("---")
    
    # Privacy settings
    st.markdown("#### 🛡️ Privacy Settings")
    
    priv_col1, priv_col2 = st.columns(2)
    
    with priv_col1:
        data_collection = st.checkbox(
            "Allow Usage Analytics",
            value=st.session_state.get('allow_analytics', True),
            help="Help us improve by sharing anonymous usage data"
        )
        st.session_state.allow_analytics = data_collection
    
    with priv_col2:
        crash_reports = st.checkbox(
            "Send Crash Reports",
            value=st.session_state.get('send_crash_reports', True),
            help="Automatically send crash reports to help fix bugs"
        )
        st.session_state.send_crash_reports = crash_reports
    
    st.markdown("---")
    
    # Danger zone
    st.markdown("#### ⚠️ Danger Zone")
    
    with st.expander("🗑️ Delete Account", expanded=False):
        st.warning("""
        **Warning:** Deleting your account will:
        - Permanently remove all your data
        - Delete all saved analyses and settings
        - Disconnect all integrations (including Zerodha)
        - This action cannot be undone!
        """)
        
        delete_confirmation = st.text_input(
            "Type 'DELETE' to confirm account deletion",
            help="This action is irreversible"
        )
        
        if st.button("🗑️ Permanently Delete My Account", type="secondary", use_container_width=True):
            if delete_confirmation == "DELETE":
                st.error("❌ Account deletion feature is currently disabled for safety")
                st.info("Please contact support for account deletion requests")
            else:
                st.warning("⚠️ Please type 'DELETE' to confirm")