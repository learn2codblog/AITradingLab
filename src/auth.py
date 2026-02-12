"""
Authentication Module for AITradingLab
Handles user login/logout with Gmail, Microsoft Outlook, Yahoo OAuth2 and Email/Password support
"""

import streamlit as st
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import hashlib
import secrets


class AuthManager:
    """Manage user authentication and sessions"""
    
    def __init__(self):
        self.users_file = "user_sessions.json"
        self.users_db_file = "users.json"
        self.session_timeout = 24 * 3600  # 24 hours in seconds
        self._init_users_db()
        
    def _init_users_db(self):
        """Initialize user database if it doesn't exist"""
        if not os.path.exists(self.users_db_file):
            # Create a default demo user
            users = {
                "demo@example.com": {
                    "password_hash": self._hash_password("demo123"),
                    "name": "Demo Trader",
                    "created_at": datetime.now().isoformat()
                },
                "test@example.com": {
                    "password_hash": self._hash_password("test123"),
                    "name": "Test User",
                    "created_at": datetime.now().isoformat()
                }
            }
            self._save_users_db(users)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _load_users_db(self) -> Dict:
        """Load users from database"""
        try:
            if os.path.exists(self.users_db_file):
                with open(self.users_db_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            st.error(f"Error loading users database: {str(e)}")
        return {}
    
    def _save_users_db(self, users: Dict):
        """Save users to database"""
        try:
            with open(self.users_db_file, 'w') as f:
                json.dump(users, f, indent=2)
        except Exception as e:
            st.error(f"Error saving users database: {str(e)}")
        
    def initialize_session_state(self):
        """Initialize Streamlit session state for authentication"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user_email' not in st.session_state:
            st.session_state.user_email = None
        if 'user_name' not in st.session_state:
            st.session_state.user_name = None
        if 'user_picture' not in st.session_state:
            st.session_state.user_picture = None
        if 'session_start' not in st.session_state:
            st.session_state.session_start = None
        if 'login_method' not in st.session_state:
            st.session_state.login_method = None

    def get_gmail_auth_url(self) -> str:
        """Generate Gmail OAuth2 authorization URL"""
        client_id = os.getenv('GMAIL_CLIENT_ID', 'your-client-id.apps.googleusercontent.com')
        redirect_uri = os.getenv('GMAIL_REDIRECT_URI', 'http://localhost:8501')
        scope = 'openid email profile'
        
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope={scope}"
        )
        return auth_url
    
    def get_microsoft_auth_url(self) -> str:
        """Generate Microsoft (Outlook) OAuth2 authorization URL"""
        client_id = os.getenv('MICROSOFT_CLIENT_ID', 'your-client-id')
        redirect_uri = os.getenv('MICROSOFT_REDIRECT_URI', 'http://localhost:8501')
        scope = 'openid email profile'
        tenant_id = os.getenv('MICROSOFT_TENANT_ID', 'common')
        
        auth_url = (
            f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize?"
            f"client_id={client_id}&"
            f"response_type=code&"
            f"redirect_uri={redirect_uri}&"
            f"scope={scope}&"
            f"response_mode=query"
        )
        return auth_url
    
    def get_yahoo_auth_url(self) -> str:
        """Generate Yahoo OAuth2 authorization URL"""
        client_id = os.getenv('YAHOO_CLIENT_ID', 'your-client-id')
        redirect_uri = os.getenv('YAHOO_REDIRECT_URI', 'http://localhost:8501')
        scope = 'openid email'
        
        auth_url = (
            f"https://api.login.yahoo.com/oauth2/request_auth?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"scope={scope}&"
            f"response_type=code"
        )
        return auth_url
    
    def get_auth_url(self, provider: str = "gmail") -> str:
        """Generate OAuth2 authorization URL for specified provider"""
        if provider == "microsoft":
            return self.get_microsoft_auth_url()
        elif provider == "yahoo":
            return self.get_yahoo_auth_url()
        else:
            return self.get_gmail_auth_url()

    def create_demo_user(self, email: str, name: str, picture: str = None) -> bool:
        """Create a demo user session (for testing without OAuth)"""
        try:
            st.session_state.authenticated = True
            st.session_state.user_email = email
            st.session_state.user_name = name
            st.session_state.user_picture = picture
            st.session_state.session_start = datetime.now()
            st.session_state.login_method = "demo"
            return True
        except Exception as e:
            st.error(f"Error creating demo session: {str(e)}")
            return False
    
    def register_email_user(self, email: str, password: str, name: str) -> Tuple[bool, str]:
        """Register a new email user"""
        # Validate input
        if not email or not password or not name:
            return False, "All fields are required"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        # Check if email already exists
        users = self._load_users_db()
        if email.lower() in users:
            return False, f"Email {email} already registered"
        
        # Create new user
        users[email.lower()] = {
            "password_hash": self._hash_password(password),
            "name": name,
            "created_at": datetime.now().isoformat()
        }
        
        self._save_users_db(users)
        return True, "Registration successful! Please login."
    
    def login_email_user(self, email: str, password: str) -> Tuple[bool, str]:
        """Login with email and password"""
        if not email or not password:
            return False, "Email and password required"
        
        users = self._load_users_db()
        
        if email.lower() not in users:
            return False, "Email not found"
        
        user_data = users[email.lower()]
        password_hash = self._hash_password(password)
        
        if user_data['password_hash'] != password_hash:
            return False, "Incorrect password"
        
        # Set session
        self.set_user_session(
            email=email,
            name=user_data['name'],
            method="email"
        )
        
        return True, "Login successful"

    def set_user_session(self, email: str, name: str, picture: str = None, method: str = "gmail"):
        """Set user session after successful authentication"""
        st.session_state.authenticated = True
        st.session_state.user_email = email
        st.session_state.user_name = name
        st.session_state.user_picture = picture
        st.session_state.session_start = datetime.now()
        st.session_state.login_method = method

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)

    def is_session_valid(self) -> bool:
        """Check if session is still valid"""
        if not self.is_authenticated():
            return False
        
        session_start = st.session_state.get('session_start')
        if session_start is None:
            return False
        
        elapsed = (datetime.now() - session_start).total_seconds()
        return elapsed < self.session_timeout

    def logout(self):
        """Logout user and clear session"""
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.session_state.user_name = None
        st.session_state.user_picture = None
        st.session_state.session_start = None
        st.session_state.login_method = None

    def get_user_info(self) -> Optional[Dict]:
        """Get current user information"""
        if not self.is_authenticated():
            return None
        
        return {
            'email': st.session_state.user_email,
            'name': st.session_state.user_name,
            'picture': st.session_state.user_picture,
            'login_method': st.session_state.login_method,
            'session_start': st.session_state.session_start
        }

    def get_session_duration(self) -> str:
        """Get formatted session duration"""
        if not self.is_authenticated():
            return "Not logged in"
        
        session_start = st.session_state.get('session_start')
        if session_start is None:
            return "Unknown"
        
        elapsed = datetime.now() - session_start
        hours = elapsed.seconds // 3600
        minutes = (elapsed.seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"


def create_login_page() -> bool:
    """
    Create and display the login page
    Returns True if login/logout action was taken
    """
    auth_manager = AuthManager()
    auth_manager.initialize_session_state()
    
    # Check if already authenticated
    if auth_manager.is_authenticated() and auth_manager.is_session_valid():
        return False
    elif auth_manager.is_authenticated() and not auth_manager.is_session_valid():
        # Session expired
        auth_manager.logout()
        st.warning("Session expired. Please login again.")
    
    # Create login interface
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center;'>🚀 AITradingLab</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>AI-Powered Trading Platform</h3>", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        
        st.markdown("### 🔐 Sign In to Continue")
        
        # Gmail Login Button
        st.markdown("#### Gmail Sign In")
        col_gmail1, col_gmail2, col_gmail3 = st.columns([0.5, 1, 0.5])
        with col_gmail2:
            gmail_clicked = st.button(
                "🔗 Sign in with Gmail",
                key="gmail_login",
                use_container_width=True,
                help="Sign in using your Gmail account"
            )
            
            if gmail_clicked:
                st.info(
                    "📧 **Gmail Login**\n\n"
                    "To enable Gmail login:\n\n"
                    "1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)\n"
                    "2. Enable OAuth 2.0\n"
                    "3. Set environment variables:\n"
                    "   - `GMAIL_CLIENT_ID`\n"
                    "   - `GMAIL_CLIENT_SECRET`\n"
                    "   - `GMAIL_REDIRECT_URI`\n"
                    "4. Or use **Demo Login** below for testing"
                )
                st.info("Click the button below to test with Demo Login")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Demo/Test Login
        st.markdown("#### Demo Login (for Testing)")
        st.warning(
            "⚠️ Demo login is for testing only. "
            "In production, use Gmail OAuth2."
        )
        
        col_demo1, col_demo2 = st.columns(2)
        
        with col_demo1:
            test_email = st.text_input(
                "Email",
                value="user@example.com",
                placeholder="your.email@gmail.com",
                key="demo_email"
            )
        
        with col_demo2:
            test_name = st.text_input(
                "Full Name",
                value="Demo User",
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
        
        with col_btn3:
            pass
        
        if demo_login:
            if test_email and test_name:
                if auth_manager.create_demo_user(test_email, test_name):
                    st.success("✅ Demo login successful!")
                    st.balloons()
                    return True
            else:
                st.error("Please enter both email and name")
        
        # Info section
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("""
        ### 📋 About AITradingLab
        
        **Features:**
        - 📊 Advanced Stock Analysis
        - 🤖 AI-Powered Predictions
        - 💼 Portfolio Management
        - 📱 Mobile Responsive
        - 🎯 Trading Strategies
        
        **Get Started:**
        1. Sign in with Gmail or Demo credentials
        2. Build your portfolio
        3. Analyze stocks with AI
        4. Execute trades
        """)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>© 2026 AITradingLab. All rights reserved.</p>", 
                   unsafe_allow_html=True)
    
    return False


def display_user_header():
    """Display user info in header"""
    auth_manager = AuthManager()
    auth_manager.initialize_session_state()
    
    if not auth_manager.is_authenticated():
        return
    
    user_info = auth_manager.get_user_info()
    if not user_info:
        return
    
    # Create header with user info
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.markdown(f"**👤 Logged in as:** {user_info['name']} ({user_info['email']})")
        st.caption(f"Session: {auth_manager.get_session_duration()}")
    
    with col3:
        if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
            auth_manager.logout()
            st.success("✅ Logged out successfully")
            st.rerun()


def require_login(func):
    """Decorator to require login for a page"""
    def wrapper(*args, **kwargs):
        auth_manager = AuthManager()
        auth_manager.initialize_session_state()
        
        if not auth_manager.is_authenticated():
            create_login_page()
            st.stop()
        
        if not auth_manager.is_session_valid():
            auth_manager.logout()
            st.warning("Session expired. Please login again.")
            create_login_page()
            st.stop()
        
        return func(*args, **kwargs)
    
    return wrapper


# Initialize auth manager
auth_manager = AuthManager()
auth_manager.initialize_session_state()

