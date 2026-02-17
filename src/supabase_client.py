"""
Supabase Database Client for AI Trading Lab
Handles user data persistence, Kite credentials, activity logging, and profile management
Production-grade data protection and storage
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple, Any
import hashlib
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from supabase import create_client, Client
except ImportError:
    st.error("Supabase library not installed. Run: pip install -r requirements.txt")
    import sys
    sys.exit(1)


class SupabaseClient:
    """Production-grade Supabase database client for persistent data storage"""
    
    def __init__(self):
        """Initialize Supabase connection"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            st.warning("""
            ⚠️ Supabase credentials not configured.
            Please set environment variables:
            - SUPABASE_URL
            - SUPABASE_ANON_KEY
            - SUPABASE_SERVICE_ROLE_KEY (for registration)
            
            Get these from: https://app.supabase.com/projects
            """)
            self.client = None
            self.service_client = None
        else:
            try:
                self.client: Client = create_client(self.supabase_url, self.supabase_key)
                # Create service client for registration (bypasses RLS)
                if self.service_role_key:
                    self.service_client: Client = create_client(self.supabase_url, self.service_role_key)
                else:
                    self.service_client = None
            except Exception as e:
                st.error(f"Failed to connect to Supabase: {str(e)}")
                self.client = None
                self.service_client = None
    
    def is_connected(self) -> bool:
        """Check if connected to Supabase"""
        return self.client is not None
    
    # ==================== USER MANAGEMENT ====================
    
    def user_exists(self, email: str) -> bool:
        """Check if user exists in database"""
        if not self.is_connected():
            return False
        
        try:
            response = self.client.table('users').select('id').eq('email', email).execute()
            return len(response.data) > 0
        except Exception as e:
            st.error(f"Error checking user existence: {str(e)}")
            return False
    
    def create_user(self, email: str, name: str, password_hash: str, 
                   login_method: str = 'email', picture_url: str = None) -> Optional[Dict]:
        """Create new user in database (uses service role key to bypass RLS)"""
        # Use service client for registration to bypass RLS policies
        client_to_use = self.service_client if self.service_client else self.client
        
        if not client_to_use:
            return None
        
        try:
            user_data = {
                'email': email,
                'name': name,
                'password_hash': password_hash,
                'login_method': login_method,
                'picture_url': picture_url,
                'created_at': datetime.utcnow().isoformat(),
                'last_login': datetime.utcnow().isoformat(),
                'is_active': True
            }
            
            response = client_to_use.table('users').insert(user_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error creating user: {str(e)}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user data by email (uses service role for login/registration)"""
        if not self.is_connected():
            return None
        
        try:
            # Use service client for login/registration (bypass RLS)
            client_to_use = self.service_client if self.service_client else self.client
            response = client_to_use.table('users').select('*').eq('email', email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error fetching user: {str(e)}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user data by ID (uses service role for profile/password operations)"""
        if not self.is_connected():
            return None
        
        try:
            # Use service client for profile/password operations (bypass RLS)
            client_to_use = self.service_client if self.service_client else self.client
            response = client_to_use.table('users').select('*').eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error fetching user by ID: {str(e)}")
            return None
    
    def update_user(self, user_id: str, update_data: Dict) -> Optional[Dict]:
        """Update user data (uses service role to bypass RLS for password changes)"""
        if not self.is_connected():
            return None
        
        try:
            update_data['updated_at'] = datetime.utcnow().isoformat()
            # Use service client for user updates (bypass RLS for password changes)
            client_to_use = self.service_client if self.service_client else self.client
            response = client_to_use.table('users').update(update_data).eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error updating user: {str(e)}")
            return None
    
    def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        if not self.is_connected():
            return False
        
        try:
            self.client.table('users').update({
                'last_login': datetime.utcnow().isoformat()
            }).eq('id', user_id).execute()
            return True
        except Exception as e:
            st.error(f"Error updating last login: {str(e)}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user and related data (for rollback on registration failure)"""
        # Use service client to bypass RLS
        client_to_use = self.service_client if self.service_client else self.client
        
        if not client_to_use:
            return False
        
        try:
            # Delete user (cascade will delete related records)
            response = client_to_use.table('users').delete().eq('id', user_id).execute()
            return True
        except Exception as e:
            print(f"Warning: Failed to delete user during rollback: {str(e)}")
            return False
    
    # ==================== USER PROFILE ====================
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile data"""
        if not self.is_connected():
            return None
        
        try:
            response = self.client.table('user_profiles').select('*').eq('user_id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error fetching profile: {str(e)}")
            return None
    
    def create_or_update_profile(self, user_id: str, profile_data: Dict) -> Optional[Dict]:
        """Create or update user profile"""
        if not self.is_connected():
            return None
        
        try:
            profile_data['user_id'] = user_id
            profile_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Check if profile exists
            existing = self.client.table('user_profiles').select('id').eq('user_id', user_id).execute()
            
            if existing.data:
                # Update existing
                response = self.client.table('user_profiles').update(profile_data).eq('user_id', user_id).execute()
            else:
                # Create new
                profile_data['created_at'] = datetime.utcnow().isoformat()
                response = self.client.table('user_profiles').insert(profile_data).execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error saving profile: {str(e)}")
            return None
    
    # ==================== KITE CREDENTIALS ====================
    
    def store_kite_credentials(self, user_id: str, api_key: str, api_secret: str,
                              access_token: str = None, public_token: str = None) -> bool:
        """Store encrypted Kite API credentials"""
        if not self.is_connected():
            return False
        
        try:
            credentials_data = {
                'user_id': user_id,
                'api_key': api_key,
                'api_secret': api_secret,
                'access_token': access_token,
                'public_token': public_token,
                'is_connected': True,
                'connected_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Check if credentials exist
            existing = self.client.table('kite_credentials').select('id').eq('user_id', user_id).execute()
            
            if existing.data:
                # Update
                response = self.client.table('kite_credentials').update(credentials_data).eq('user_id', user_id).execute()
            else:
                # Create
                response = self.client.table('kite_credentials').insert(credentials_data).execute()
            
            return bool(response.data)
        except Exception as e:
            st.error(f"Error storing Kite credentials: {str(e)}")
            return False
    
    def get_kite_credentials(self, user_id: str) -> Optional[Dict]:
        """Get user's Kite credentials"""
        if not self.is_connected():
            return None
        
        try:
            response = self.client.table('kite_credentials').select('*').eq('user_id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error fetching Kite credentials: {str(e)}")
            return None
    
    def disconnect_kite(self, user_id: str) -> bool:
        """Disconnect Kite account"""
        if not self.is_connected():
            return False
        
        try:
            self.client.table('kite_credentials').update({
                'is_connected': False,
                'access_token': None,
                'disconnected_at': datetime.utcnow().isoformat()
            }).eq('user_id', user_id).execute()
            return True
        except Exception as e:
            st.error(f"Error disconnecting Kite: {str(e)}")
            return False
    
    # ==================== ACTIVITY LOGGING ====================
    
    def log_activity(self, user_id: str, activity_type: str, description: str,
                     action_details: Dict = None, status: str = 'success') -> bool:
        """Log user activity for audit trail (uses service role to bypass RLS)."""
        # Use service client to bypass RLS policies for logging
        client_to_use = self.service_client if self.service_client else self.client

        if not client_to_use:
            return False

        try:
            activity_data = {
                'user_id': user_id,
                'activity_type': activity_type,
                'description': description,
                'action_details': json.dumps(action_details) if action_details else None,
                'status': status,
                'timestamp': datetime.utcnow().isoformat(),
                'ip_address': st.session_state.get('ip_address', 'unknown')
            }

            response = client_to_use.table('activity_logs').insert(activity_data).execute()
            return bool(response.data)
        except Exception as e:
            # Silently fail - don't block operations if logging fails
            print(f"Warning: Failed to log activity: {str(e)}")
            return False

    def log_trading_activity(self, user_id: str, activity_type: str, description: str,
                            symbol: str = None, source: str = None,
                            details: Dict = None, status: str = 'success') -> bool:
        """Log trading-specific activity for reporting (uses service role to bypass RLS)."""
        client_to_use = self.service_client if self.service_client else self.client
        if not client_to_use:
            return False

        try:
            activity_data = {
                'user_id': user_id,
                'activity_type': activity_type,
                'description': description,
                'symbol': symbol,
                'source': source,
                'details': json.dumps(details) if details else None,
                'status': status,
                'timestamp': datetime.utcnow().isoformat(),
                'ip_address': st.session_state.get('ip_address', 'unknown')
            }
            response = client_to_use.table('trading_activity').insert(activity_data).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Warning: Failed to log trading activity: {str(e)}")
            return False

    def get_user_activities(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user's recent activities (uses service role to bypass RLS)."""
        if not self.is_connected():
            return []

        try:
            client_to_use = self.service_client if self.service_client else self.client
            response = client_to_use.table('activity_logs').select('*').eq('user_id', user_id).order(
                'timestamp', desc=True
            ).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            st.error(f"Error fetching activities: {str(e)}")
            return []

    def get_user_trading_activity(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user's trading-specific activity (uses service role to bypass RLS)."""
        if not self.is_connected():
            return []

        try:
            client_to_use = self.service_client if self.service_client else self.client
            response = client_to_use.table('trading_activity').select('*').eq('user_id', user_id).order(
                'timestamp', desc=True
            ).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            st.error(f"Error fetching trading activity: {str(e)}")
            return []

    # ==================== BACKTEST RESULTS ====================

    def save_backtest_result(self, user_id: str, test_name: str, strategy_type: str,
                             symbol: str, result_data: Dict, performance_metrics: Dict) -> Optional[str]:
        """Save a backtest result and return its ID (uses service role to bypass RLS)."""
        client_to_use = self.service_client if self.service_client else self.client
        if not client_to_use:
            return None

        try:
            payload = {
                'user_id': user_id,
                'test_name': test_name,
                'strategy_type': strategy_type,
                'symbol': symbol,
                'result_data': result_data,
                'performance_metrics': performance_metrics,
                'created_at': datetime.utcnow().isoformat()
            }
            response = client_to_use.table('backtest_results').insert(payload).execute()
            if response.data:
                return response.data[0].get('id')
            return None
        except Exception as e:
            st.error(f"Error saving backtest result: {str(e)}")
            return None

    def get_user_backtest_results(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user's backtest results (uses service role to bypass RLS)."""
        if not self.is_connected():
            return []

        try:
            client_to_use = self.service_client if self.service_client else self.client
            response = client_to_use.table('backtest_results').select('*').eq('user_id', user_id).order(
                'created_at', desc=True
            ).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            st.error(f"Error fetching backtest results: {str(e)}")
            return []

    def delete_backtest_result(self, user_id: str, test_name: str) -> bool:
        """Delete backtest results by test name (uses service role to bypass RLS)."""
        client_to_use = self.service_client if self.service_client else self.client
        if not client_to_use:
            return False

        try:
            response = client_to_use.table('backtest_results').delete().eq('user_id', user_id).eq(
                'test_name', test_name
            ).execute()
            return bool(response.data)
        except Exception as e:
            st.error(f"Error deleting backtest result: {str(e)}")
            return False

    def save_backtest_trades(self, user_id: str, backtest_id: str, trades: List[Dict]) -> bool:
        """Save backtest trades linked to a backtest result (uses service role to bypass RLS)."""
        client_to_use = self.service_client if self.service_client else self.client
        if not client_to_use or not trades:
            return False

        try:
            payload = []
            for trade in trades:
                trade_payload = dict(trade)
                trade_payload['user_id'] = user_id
                trade_payload['backtest_id'] = backtest_id
                trade_payload['created_at'] = datetime.utcnow().isoformat()
                payload.append(trade_payload)

            response = client_to_use.table('backtest_trades').insert(payload).execute()
            return bool(response.data)
        except Exception as e:
            st.error(f"Error saving backtest trades: {str(e)}")
            return False

    def get_user_backtest_trades(self, user_id: str, limit: int = 200) -> List[Dict]:
        """Get user's backtest trades (uses service role to bypass RLS)."""
        if not self.is_connected():
            return []

        try:
            client_to_use = self.service_client if self.service_client else self.client
            response = client_to_use.table('backtest_trades').select('*').eq('user_id', user_id).order(
                'entry_time', desc=True
            ).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            st.error(f"Error fetching backtest trades: {str(e)}")
            return []
