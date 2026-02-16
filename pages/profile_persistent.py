"""
Enhanced My Profile page module with persistent Supabase backend
Comprehensive user profile management with data persistence and Zerodha integration
"""
import streamlit as st
import json
from datetime import datetime
from ui.components import get_theme_colors
from src.auth_supabase import SupabaseAuthManager
from src.supabase_client import get_supabase_client


def render_my_profile():
    """Render comprehensive My Profile page with persistent data storage."""
    theme_colors = get_theme_colors()
    auth_manager = SupabaseAuthManager()
    supabase = get_supabase_client()
    
    # Get current user
    user_info = auth_manager.get_user_info()
    if not user_info:
        st.error("❌ User not authenticated")
        return
    
    user_id = user_info['user_id']
    user_email = user_info['email']
    user_name = user_info['name']
    user_picture = user_info['picture']
    
    # Extract gradient to avoid f-string issues
    gradient_bg = theme_colors.get('gradient_bg', 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)')
    
    # Header with gradient
    st.markdown(f"""
    <div style='background: {gradient_bg}; padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: center;'>
        <h1 style='color: white; margin: 0;'>👤 My Profile</h1>
        <p style='color: rgba(255,255,255,0.9); margin: 10px 0 0 0;'>
            Manage Your Account, Preferences & Trading Connections
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Profile tabs
    tabs = st.tabs([
        "👤 Account Info",
        "🔗 Zerodha Connect",
        "📊 Trading Stats",
        "🎨 Preferences",
        "🔐 Security",
        "📋 Activity Log"
    ])
    
    # Tab 1: Account Information
    with tabs[0]:
        render_account_info(user_id, user_name, user_email, user_picture, 
                          auth_manager, supabase, theme_colors)
    
    # Tab 2: Zerodha Connection
    with tabs[1]:
        render_zerodha_connection(user_id, supabase, theme_colors)
    
    # Tab 3: Trading Statistics
    with tabs[2]:
        render_trading_stats(user_id, supabase, theme_colors)
    
    # Tab 4: Preferences
    with tabs[3]:
        render_profile_preferences(user_id, supabase, theme_colors)
    
    # Tab 5: Security
    with tabs[4]:
        render_security_settings(user_id, auth_manager, theme_colors)
    
    # Tab 6: Activity Log
    with tabs[5]:
        render_activity_log(user_id, supabase, theme_colors)


def render_account_info(user_id: str, user_name: str, user_email: str,
                       user_picture: str, auth_manager: SupabaseAuthManager,
                       supabase, theme_colors: dict):
    """Render account information section with persistent updates."""
    st.markdown("### 👤 Account Information")
    
    gradient_bg = theme_colors.get('gradient_bg', 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)')
    
    # Profile card
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if user_picture:
            st.image(user_picture, width=150)
        else:
            initials = ''.join([word[0].upper() for word in user_name.split()[:2]])
            st.markdown(f"""
            <div style='background: {gradient_bg}; width: 150px; height: 150px; 
                        border-radius: 50%; display: flex; align-items: center; justify-content: center;'>
                <span style='color: white; font-size: 48px; font-weight: bold;'>{initials}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"### {user_name}")
        st.markdown(f"📧 **Email:** {user_email}")
        st.markdown(f"🔐 **Login Method:** {st.session_state.get('login_method', 'email').title()}")
        st.markdown(f"🕐 **Session Started:** {st.session_state.get('session_start', 'Unknown')}")
        st.markdown(f"⏱️ **Session Duration:** {auth_manager.get_session_duration()}")
    
    # Account status badges
    st.markdown("#### Account Status")
    col_badge1, col_badge2, col_badge3 = st.columns(3)
    
    with col_badge1:
        st.markdown("""
        <div style='background: #E8F5E9; padding: 15px; border-radius: 8px; text-align: center;'>
            <h4 style='color: #2E7D32; margin: 0;'>✅ Verified</h4>
            <p style='color: #558B2F; margin: 5px 0 0 0; font-size: 14px;'>Account verified</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_badge2:
        kite_creds = supabase.get_kite_credentials(user_id) if supabase.is_connected() else None
        status_text = "🔗 Connected" if kite_creds and kite_creds.get('is_connected') else "❌ Not Connected"
        color = "#E8F5E9" if kite_creds and kite_creds.get('is_connected') else "#FFEBEE"
        text_color = "#2E7D32" if kite_creds and kite_creds.get('is_connected') else "#C62828"
        
        st.markdown(f"""
        <div style='background: {color}; padding: 15px; border-radius: 8px; text-align: center;'>
            <h4 style='color: {text_color}; margin: 0;'>{status_text}</h4>
            <p style='color: {text_color}; margin: 5px 0 0 0; font-size: 14px;'>Zerodha status</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_badge3:
        st.markdown("""
        <div style='background: #E3F2FD; padding: 15px; border-radius: 8px; text-align: center;'>
            <h4 style='color: #1565C0; margin: 0;'>📊 Active</h4>
            <p style='color: #1565C0; margin: 5px 0 0 0; font-size: 14px;'>Trading active</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Edit profile section
    st.markdown("#### Edit Profile")
    
    col_edit1, col_edit2 = st.columns(2)
    
    with col_edit1:
        new_name = st.text_input("Full Name", value=user_name, key="edit_name")
    
    with col_edit2:
        picture_url = st.text_input("Profile Picture URL", value=user_picture or "", key="edit_picture")
    
    if st.button("💾 Save Changes", key="save_profile"):
        success, message = auth_manager.update_user_profile(
            user_id,
            name=new_name,
            picture_url=picture_url
        )
        
        if success:
            st.success(f"✅ {message}")
            st.rerun()
        else:
            st.error(f"❌ {message}")


def render_zerodha_connection(user_id: str, supabase, theme_colors: dict):
    """Render Zerodha connection setup with persistent credentials."""
    st.markdown("### 🔗 Zerodha Connect")
    
    card_bg = theme_colors.get('card_bg', '#f8f9fa')
    text_color = theme_colors.get('text', '#FFFFFF')
    
    kite_creds = supabase.get_kite_credentials(user_id) if supabase.is_connected() else None
    is_connected = kite_creds and kite_creds.get('is_connected', False) if kite_creds else False
    
    # Connection status
    if is_connected:
        st.success(f"✅ Connected as: {kite_creds.get('api_key', 'Unknown')[:10]}...")
        
        if st.button("🔌 Disconnect", key="disconnect_kite"):
            if supabase.disconnect_kite(user_id):
                st.success("✅ Disconnected from Zerodha")
                supabase.log_activity(
                    user_id,
                    'kite_disconnected',
                    'Disconnected from Zerodha',
                )
                st.rerun()
            else:
                st.error("❌ Failed to disconnect")
    else:
        st.info("Not connected to Zerodha yet")
        
        st.markdown("#### 1️⃣ Enter API Credentials")
        col1, col2 = st.columns(2)
        
        with col1:
            api_key = st.text_input("API Key", type="password", key="kite_api_key")
        
        with col2:
            api_secret = st.text_input("API Secret", type="password", key="kite_api_secret")
        
        st.markdown("#### 2️⃣ Complete OAuth Flow")
        st.info("""
        1. Click below to get your request token
        2. Complete the authorization on Zerodha
        3. Enter the request token here
        """)
        
        if st.button("🔗 Get Authorization URL"):
            # Store credentials temporarily and show OAuth URL
            st.session_state.temp_kite_key = api_key
            st.session_state.temp_kite_secret = api_secret
            # In production, generate actual OAuth URL
            st.info("Visit: https://kite.zerodha.com/api/login (This is a placeholder)")
        
        oauth_token = st.text_input("Request Token", type="password", key="oauth_token")
        
        if st.button("✅ Complete Connection"):
            if api_key and api_secret and oauth_token:
                # Store credentials in Supabase
                if supabase.store_kite_credentials(
                    user_id,
                    api_key,
                    api_secret,
                    access_token=oauth_token
                ):
                    st.success("✅ Successfully connected to Zerodha!")
                    supabase.log_activity(
                        user_id,
                        'kite_connected',
                        'Connected to Zerodha with OAuth',
                        {'oauth_token': oauth_token[:10] + '...'},
                    )
                    st.rerun()
                else:
                    st.error("❌ Failed to save credentials")
            else:
                st.warning("⚠️ Please fill all fields")


def render_trading_stats(user_id: str, supabase, theme_colors: dict):
    """Render trading statistics from persistent data."""
    st.markdown("### 📊 Trading Statistics")
    
    # Get backtesting history
    backtest_results = supabase.get_user_backtest_results(user_id, limit=10)
    
    if not backtest_results:
        st.info("📊 No backtest results yet. Start backtesting to see stats here!")
        return
    
    # Summary metrics
    total_backtests = len(backtest_results)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Backtests", total_backtests)
    
    with col2:
        st.metric("Last Test", backtest_results[0]['created_at'][:10] if backtest_results else "N/A")
    
    with col3:
        st.metric("Active Symbols", len(set(b.get('symbol') for b in backtest_results if b.get('symbol'))))
    
    with col4:
        st.metric("Strategies Used", len(set(b.get('strategy_type') for b in backtest_results if b.get('strategy_type'))))
    
    # Recent backtest results
    st.markdown("#### Recent Backtest Results")
    
    for result in backtest_results[:5]:
        with st.expander(f"📈 {result.get('test_name', 'Unnamed Test')} - {result['created_at'][:10]}"):
            # Parse JSON data
            try:
                result_data = json.loads(result.get('result_data', '{}'))
                metrics = json.loads(result.get('performance_metrics', '{}'))
                
                col_m1, col_m2, col_m3 = st.columns(3)
                
                with col_m1:
                    st.metric("Total Return", f"{metrics.get('total_return', 'N/A')}%")
                
                with col_m2:
                    st.metric("Sharpe Ratio", f"{metrics.get('sharpe_ratio', 'N/A'):.2f}")
                
                with col_m3:
                    st.metric("Max Drawdown", f"{metrics.get('max_drawdown', 'N/A')}%")
                
                st.write(f"**Strategy:** {result.get('strategy_type', 'N/A')}")
                st.write(f"**Symbol:** {result.get('symbol', 'N/A')}")
            except:
                st.write(result.get('test_name', 'Unnamed Test'))


def render_profile_preferences(user_id: str, supabase, theme_colors: dict):
    """Render user preferences with persistent storage."""
    st.markdown("### 🎨 Preferences")
    
    # Load existing settings
    existing_settings = supabase.get_user_settings(user_id) if supabase.is_connected() else {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Trading Preferences")
        risk_tolerance = st.selectbox(
            "Risk Tolerance",
            ["Conservative", "Moderate", "Aggressive"],
            index=1,
            key="risk_tolerance"
        )
        
        investment_horizon = st.selectbox(
            "Investment Horizon",
            ["Short (1-3 months)", "Medium (3-12 months)", "Long (1+ years)"],
            index=1,
            key="investment_horizon"
        )
    
    with col2:
        st.markdown("#### Display Preferences")
        dark_mode = st.checkbox("Dark Mode", value=True, key="dark_mode")
        notifications = st.checkbox("Enable Notifications", value=True, key="notifications")
    
    st.markdown("#### Additional Settings")
    initial_capital = st.number_input(
        "Initial Capital (₹)",
        min_value=0.0,
        step=1000.0,
        key="initial_capital"
    )
    
    trading_experience = st.selectbox(
        "Trading Experience",
        ["Beginner", "Intermediate", "Advanced"],
        index=0,
        key="trading_experience"
    )
    
    if st.button("💾 Save Preferences"):
        settings = {
            'risk_tolerance': risk_tolerance,
            'investment_horizon': investment_horizon,
            'dark_mode': dark_mode,
            'notifications': notifications,
            'initial_capital': initial_capital,
            'trading_experience': trading_experience
        }
        
        if supabase.save_user_settings(user_id, settings):
            st.success("✅ Preferences saved successfully")
            supabase.log_activity(
                user_id,
                'preferences_updated',
                'User updated preferences',
                action_details=settings
            )
        else:
            st.error("❌ Failed to save preferences")


def render_security_settings(user_id: str, auth_manager: SupabaseAuthManager, theme_colors: dict):
    """Render security settings."""
    st.markdown("### 🔐 Security Settings")
    
    tab1, tab2, tab3 = st.tabs(["🔑 Password", "🛡️ Sessions", "⚠️ Danger Zone"])
    
    with tab1:
        st.markdown("#### Change Password")
        
        old_password = st.text_input("Current Password", type="password", key="old_pwd")
        new_password = st.text_input("New Password", type="password", key="new_pwd")
        confirm_password = st.text_input("Confirm New Password", type="password", key="confirm_pwd")
        
        if st.button("🔄 Change Password"):
            if new_password != confirm_password:
                st.error("❌ Passwords don't match")
            else:
                success, message = auth_manager.change_password(user_id, old_password, new_password)
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")
    
    with tab2:
        st.markdown("#### Active Sessions")
        st.info(f"🕐 Current session duration: {auth_manager.get_session_duration()}")
        
        if st.button("🚪 Logout from All Devices"):
            st.warning("⚠️ This will log you out from all devices")
            auth_manager.logout()
            st.rerun()
    
    with tab3:
        st.markdown("#### Delete Account")
        st.warning("⚠️ This action cannot be undone!")
        
        if st.checkbox("I understand the consequences", key="understand_deletion"):
            password = st.text_input("Enter password to confirm", type="password", key="delete_pwd")
            
            if st.button("🗑️ Delete My Account", key="delete_account"):
                success, message = auth_manager.delete_account(user_id, password)
                if success:
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")


def render_activity_log(user_id: str, supabase, theme_colors: dict):
    """Render user activity log."""
    st.markdown("### 📋 Activity Log")
    
    activities = supabase.get_user_activities(user_id, limit=50) if supabase.is_connected() else []
    
    if not activities:
        st.info("📋 No activities yet")
        return
    
    # Activity type to emoji mapping
    activity_emoji = {
        'login': '🔐',
        'logout': '🚪',
        'profile_update': '👤',
        'password_change': '🔑',
        'settings_change': '⚙️',
        'kite_connected': '🔗',
        'kite_disconnected': '❌',
        'backtest_created': '📈',
        'portfolio_created': '📊',
        'registration': '✨'
    }
    
    for activity in activities:
        emoji = activity_emoji.get(activity.get('activity_type', 'unknown'), '📝')
        timestamp = activity.get('timestamp', 'Unknown')
        status_color = "🟢" if activity.get('status') == 'success' else "🔴"
        
        st.markdown(f"""
        {emoji} **{activity.get('description', 'Unknown activity')}**  
        {status_color} {activity.get('status', 'unknown')} | {timestamp[:19]}
        """)
