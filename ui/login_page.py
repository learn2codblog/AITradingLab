"""
Login Page UI Component
Provides the complete login interface with multiple authentication options
"""

import streamlit as st
from datetime import datetime
import os
from typing import Optional, Tuple


class LoginPageUI:
    """Manages the login page interface"""
    
    @staticmethod
    def set_page_config():
        """Configure page settings for login"""
        st.set_page_config(
            page_title="AITradingLab - Login",
            page_icon="🚀",
            layout="centered",
            initial_sidebar_state="collapsed"
        )

    @staticmethod
    def apply_login_styles():
        """Apply custom CSS styles for login page"""
        st.markdown("""
        <style>
        /* Hide sidebar on login page */
        [data-testid="collapsedControl"] {
            display: none;
        }
        
        /* Style login container */
        .login-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            padding: 40px;
            color: white;
        }
        
        /* Button styles */
        .login-btn {
            background-color: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        .login-btn:hover {
            background-color: #764ba2;
        }
        
        /* Input field styles */
        .login-input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        
        .login-input:focus {
            border-color: #667eea;
            outline: none;
        }
        
        /* Card styles */
        .login-card {
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
        }
        
        /* Header styles */
        .login-header {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        
        .login-subheader {
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-top: 20px;
        }
        
        /* Error/Success messages */
        .error-box {
            background-color: #fee;
            border-left: 4px solid #f00;
            padding: 12px;
            border-radius: 4px;
            margin: 10px 0;
        }
        
        .success-box {
            background-color: #efe;
            border-left: 4px solid #0f0;
            padding: 12px;
            border-radius: 4px;
            margin: 10px 0;
        }
        
        /* Divider */
        .divider {
            text-align: center;
            color: #999;
            margin: 20px 0;
            position: relative;
        }
        
        .divider::before {
            content: '';
            position: absolute;
            left: 0;
            top: 50%;
            width: 100%;
            height: 1px;
            background: #ddd;
        }
        
        .divider span {
            background: white;
            padding: 0 10px;
            position: relative;
            z-index: 1;
        }
        </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def show_header():
        """Display login page header"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            <div class="login-header">
                <h1>🚀 AITradingLab</h1>
                <p style="color: #666; font-size: 16px;">
                    AI-Powered Trading Platform
                </p>
            </div>
            """, unsafe_allow_html=True)

    @staticmethod
    def show_oauth_login(auth_manager) -> str:
        """Display OAuth login options (Gmail, Microsoft, Yahoo)"""
        st.markdown("### 🔐 Sign In with Email Provider")
        
        col1, col2, col3 = st.columns(3)
        
        # Gmail
        with col1:
            gmail_btn = st.button(
                "📧 Gmail",
                key="oauth_gmail",
                use_container_width=True,
                help="Sign in with Gmail"
            )
            if gmail_btn:
                st.info("""
                ### Gmail Login Setup
                
                **Environment Variables Required:**
                - `GMAIL_CLIENT_ID`
                - `GMAIL_CLIENT_SECRET`
                - `GMAIL_REDIRECT_URI`
                
                Get credentials from [Google Cloud Console](https://console.cloud.google.com/)
                """)
        
        # Microsoft
        with col2:
            microsoft_btn = st.button(
                "🔵 Microsoft",
                key="oauth_microsoft",
                use_container_width=True,
                help="Sign in with Microsoft (Outlook)"
            )
            if microsoft_btn:
                st.info("""
                ### Microsoft (Outlook) Login Setup
                
                **Environment Variables Required:**
                - `MICROSOFT_CLIENT_ID`
                - `MICROSOFT_CLIENT_SECRET`
                - `MICROSOFT_REDIRECT_URI`
                - `MICROSOFT_TENANT_ID` (optional, defaults to 'common')
                
                Get credentials from [Azure Portal](https://portal.azure.com/)
                """)
        
        # Yahoo
        with col3:
            yahoo_btn = st.button(
                "🟣 Yahoo",
                key="oauth_yahoo",
                use_container_width=True,
                help="Sign in with Yahoo"
            )
            if yahoo_btn:
                st.info("""
                ### Yahoo Mail Login Setup
                
                **Environment Variables Required:**
                - `YAHOO_CLIENT_ID`
                - `YAHOO_CLIENT_SECRET`
                - `YAHOO_REDIRECT_URI`
                
                Get credentials from [Yahoo Developer Network](https://developer.yahoo.com/)
                """)
        
        # Return which provider was clicked
        if gmail_btn:
            return "gmail"
        elif microsoft_btn:
            return "microsoft"
        elif yahoo_btn:
            return "yahoo"
        
        return ""

    @staticmethod
    def show_demo_login() -> Tuple[bool, str, str]:
        """Display demo login form"""
        st.markdown("---")
        st.markdown("#### Demo Login (for Testing)")
        
        with st.warning():
            st.markdown("⚠️ **Demo login** is for testing only. Use Gmail OAuth2 in production.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            email = st.text_input(
                "📧 Email",
                value="trader@example.com",
                placeholder="your.email@example.com",
                key="demo_email"
            )
        
        with col2:
            name = st.text_input(
                "👤 Full Name",
                value="Demo Trader",
                placeholder="Your Name",
                key="demo_name"
            )
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        
        with col_btn1:
            demo_login = st.button(
                "✅ Demo Login",
                key="demo_login_btn",
                use_container_width=True,
                help="Login with demo credentials"
            )
        
        return demo_login, email, name

    @staticmethod
    def show_email_login(auth_manager) -> Tuple[bool, str, str, str]:
        """Display email/password login form"""
        st.markdown("---")
        st.markdown("#### 📧 Email Login")
        
        # Tabs for login/register
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.markdown("**Sign in with your email**")
            email = st.text_input(
                "Email",
                placeholder="your.email@example.com",
                key="email_login_email"
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter password",
                key="email_login_password"
            )
            
            login_btn = st.button(
                "🔓 Login with Email",
                key="email_login_btn",
                use_container_width=True,
                help="Login with email and password"
            )
            
            if login_btn:
                if email and password:
                    success, message = auth_manager.login_email_user(email, password)
                    if success:
                        st.success(message)
                        return True, "email_login", email, ""
                    else:
                        st.error(message)
                else:
                    st.error("Please enter email and password")
            
            # Demo credentials hint
            with st.expander("💡 Test Credentials"):
                st.markdown("""
                **Demo Account:**
                - Email: `demo@example.com`
                - Password: `demo123`
                
                **Test Account:**
                - Email: `test@example.com`
                - Password: `test123`
                """)
        
        with tab2:
            st.markdown("**Create a new account**")
            reg_name = st.text_input(
                "Full Name",
                placeholder="Your Name",
                key="email_register_name"
            )
            reg_email = st.text_input(
                "Email",
                placeholder="your.email@example.com",
                key="email_register_email"
            )
            reg_password = st.text_input(
                "Password",
                type="password",
                placeholder="At least 6 characters",
                key="email_register_password"
            )
            reg_confirm = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Confirm password",
                key="email_register_confirm"
            )
            
            register_btn = st.button(
                "✍️ Register Account",
                key="email_register_btn",
                use_container_width=True,
                help="Create a new account"
            )
            
            if register_btn:
                if not (reg_name and reg_email and reg_password and reg_confirm):
                    st.error("All fields are required")
                elif reg_password != reg_confirm:
                    st.error("Passwords do not match")
                elif len(reg_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    success, message = auth_manager.register_email_user(
                        reg_email, reg_password, reg_name
                    )
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
        
        return False, "", "", ""

    @staticmethod
    def show_features_info():
        """Display features information"""
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 📊 Features
            
            - **Advanced Analysis**
              - Stock research & analysis
              - Technical indicators
              - Fundamental metrics
            
            - **Portfolio Tools**
              - Portfolio builder
              - Risk analysis
              - Performance tracking
            """)
        
        with col2:
            st.markdown("""
            ### 🤖 AI & ML
            
            - **Intelligent Insights**
              - AI predictions
              - Market trends
              - Price targets
            
            - **Smart Strategies**
              - Sector screening
              - Strategy builder
              - Backtesting
            """)
        
        st.markdown("---")
        st.markdown(
            "<p style='text-align: center; color: gray; font-size: 12px;'>"
            "© 2026 AITradingLab. All rights reserved. | "
            "<a href='#' style='color: gray;'>Privacy Policy</a> | "
            "<a href='#' style='color: gray;'>Terms of Service</a>"
            "</p>",
            unsafe_allow_html=True
        )

    @staticmethod
    def show_features_info():
        """Display current user session information"""
        from src.auth import AuthManager
        
        auth_manager = AuthManager()
        
        if not auth_manager.is_authenticated():
            return
        
        user_info = auth_manager.get_user_info()
        if not user_info:
            return
        
        st.markdown("---")
        st.markdown("### 👤 User Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if user_info.get('picture'):
                st.image(user_info['picture'], width=100)
        
        with col2:
            st.markdown(f"**Name:** {user_info['name']}")
            st.markdown(f"**Email:** {user_info['email']}")
        
        with col3:
            login_method = user_info.get('login_method', 'unknown').upper()
            st.markdown(f"**Login:** {login_method}")
            st.markdown(f"**Session:** {auth_manager.get_session_duration()}")


def render_login_page(auth_manager) -> bool:
    """
    Render complete login page
    
    Args:
        auth_manager: AuthManager instance
    
    Returns:
        bool: True if login was successful
    """
    # Initialize UI
    login_ui = LoginPageUI()
    login_ui.set_page_config()
    login_ui.apply_login_styles()
    
    # Hide sidebar
    st.set_option('client.showErrorDetails', False)
    
    # Create main layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Header
        login_ui.show_header()
        
        # OAuth login (Gmail, Microsoft, Yahoo)
        oauth_provider = login_ui.show_oauth_login(auth_manager)
        
        # Email login
        email_result = login_ui.show_email_login(auth_manager)
        if email_result[0]:  # If email login returned True
            st.success("✅ Login successful! Redirecting...")
            st.balloons()
            return True
        
        # Demo login
        demo_clicked, email, name = login_ui.show_demo_login()
        
        # Handle demo login
        if demo_clicked:
            if email.strip() and name.strip():
                if auth_manager.create_demo_user(email, name):
                    st.success("✅ Login successful! Redirecting...")
                    st.balloons()
                    return True
            else:
                st.error("❌ Please enter both email and name")
        
        # Features
        login_ui.show_features_info()
    
    return False
