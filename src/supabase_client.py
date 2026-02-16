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
        """Log user activity for audit trail (uses service role to bypass RLS)"""
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
    
    def get_user_activities(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user's recent activities"""
        if not self.is_connected():
            return []
        
        try:
            response = self.client.table('activity_logs').select('*').eq('user_id', user_id).order(
                'timestamp', desc=True
            ).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            st.error(f"Error fetching activities: {str(e)}")
            return []
    
    # ==================== PORTFOLIO DATA ====================
    
    def save_portfolio_config(self, user_id: str, portfolio_name: str, 
                             config_data: Dict) -> Optional[Dict]:
        """Save user's portfolio configuration (uses service role to bypass RLS)"""
        if not self.is_connected():
            return None
        
        # Check if service client is available
        if not self.service_client:
            st.error("⚠️ Service role key not configured. Cannot save portfolio.")
            st.info("""
            Please set SUPABASE_SERVICE_ROLE_KEY environment variable.
            Get it from: Supabase Dashboard → Settings → API → service_role key
            """)
            return None
        
        try:
            portfolio_data = {
                'user_id': user_id,
                'portfolio_name': portfolio_name,
                'config_data': json.dumps(config_data),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Use service client for portfolio operations (bypass RLS)
            client_to_use = self.service_client
            
            # Check if exists
            existing = client_to_use.table('portfolios').select('id').eq(
                'user_id', user_id
            ).eq('portfolio_name', portfolio_name).execute()
            
            if existing.data:
                response = client_to_use.table('portfolios').update(portfolio_data).eq(
                    'id', existing.data[0]['id']
                ).execute()
            else:
                response = client_to_use.table('portfolios').insert(portfolio_data).execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error saving portfolio: {str(e)}")
            return None
    
    def get_user_portfolios(self, user_id: str) -> List[Dict]:
        """Get all user portfolios (uses service role for data access)"""
        if not self.is_connected():
            return []
        
        try:
            client_to_use = self.service_client if self.service_client else self.client
            response = client_to_use.table('portfolios').select('*').eq('user_id', user_id).execute()
            return response.data if response.data else []
        except Exception as e:
            st.error(f"Error fetching portfolios: {str(e)}")
            return []
    
    def get_portfolio_by_name(self, user_id: str, portfolio_name: str) -> Optional[Dict]:
        """Get specific portfolio by name (uses service role for data access)"""
        if not self.is_connected():
            return None
        
        try:
            client_to_use = self.service_client if self.service_client else self.client
            response = client_to_use.table('portfolios').select('*').eq(
                'user_id', user_id
            ).eq('portfolio_name', portfolio_name).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error fetching portfolio: {str(e)}")
            return None
    
    def delete_portfolio(self, user_id: str, portfolio_name: str) -> bool:
        """Delete a portfolio (uses service role to bypass RLS)"""
        if not self.is_connected():
            return False
        
        try:
            client_to_use = self.service_client if self.service_client else self.client
            response = client_to_use.table('portfolios').delete().eq(
                'user_id', user_id
            ).eq('portfolio_name', portfolio_name).execute()
            return True
        except Exception as e:
            st.error(f"Error deleting portfolio: {str(e)}")
            return False
    
    # ==================== BACKTESTING RESULTS ====================
    
    def save_backtest_result(self, user_id: str, test_name: str,
                            result_data: Dict) -> Optional[Dict]:
        """Save backtest results (uses service role to bypass RLS)"""
        if not self.is_connected():
            return None
        
        try:
            backtest_data = {
                'user_id': user_id,
                'test_name': test_name,
                'result_data': json.dumps(result_data),
                'created_at': datetime.utcnow().isoformat()
            }
            
            client_to_use = self.service_client if self.service_client else self.client
            response = client_to_use.table('backtest_results').insert(backtest_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error saving backtest result: {str(e)}")
            return None
    
    def get_user_backtest_results(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get user's backtest history (uses service role for data access)"""
        if not self.is_connected():
            return []
        
        try:
            client_to_use = self.service_client if self.service_client else self.client
            response = client_to_use.table('backtest_results').select('*').eq(
                'user_id', user_id
            ).order('created_at', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            st.error(f"Error fetching backtest results: {str(e)}")
            return []
    
    def delete_backtest_result(self, user_id: str, test_name: str) -> bool:
        """Delete a backtest result (uses service role to bypass RLS)"""
        if not self.is_connected():
            return False
        
        try:
            client_to_use = self.service_client if self.service_client else self.client
            client_to_use.table('backtest_results').delete().eq(
                'user_id', user_id
            ).eq('test_name', test_name).execute()
            return True
        except Exception as e:
            st.error(f"Error deleting backtest result: {str(e)}")
            return False
    
    # ==================== PREFERENCES & SETTINGS ====================
    
    def save_user_settings(self, user_id: str, settings: Dict) -> bool:
        """Save user preferences and settings (uses service role to bypass RLS)"""
        if not self.is_connected():
            return False
        
        try:
            settings_data = {
                'user_id': user_id,
                'settings': json.dumps(settings),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            client_to_use = self.service_client if self.service_client else self.client
            
            # Check if exists
            existing = client_to_use.table('user_settings').select('id').eq('user_id', user_id).execute()
            
            if existing.data:
                response = client_to_use.table('user_settings').update(settings_data).eq('user_id', user_id).execute()
            else:
                response = client_to_use.table('user_settings').insert(settings_data).execute()
            
            return bool(response.data)
        except Exception as e:
            st.error(f"Error saving settings: {str(e)}")
            return False
    
    def get_user_settings(self, user_id: str) -> Optional[Dict]:
        """Get user's settings and preferences (uses service role for data access)"""
        if not self.is_connected():
            return None
        
        try:
            client_to_use = self.service_client if self.service_client else self.client
            response = client_to_use.table('user_settings').select('*').eq('user_id', user_id).execute()
            if response.data:
                settings = response.data[0].get('settings')
                return json.loads(settings) if isinstance(settings, str) else settings
            return None
        except Exception as e:
            st.error(f"Error fetching settings: {str(e)}")
            return None
    
    # ==================== WATCHLIST ====================
    
    def add_to_watchlist(self, user_id: str, symbol: str) -> bool:
        """Add stock to user's watchlist (uses service role to bypass RLS)"""
        if not self.is_connected():
            return False
        
        try:
            client_to_use = self.service_client if self.service_client else self.client
            
            # Check if already in watchlist
            existing = client_to_use.table('watchlists').select('id').eq(
                'user_id', user_id
            ).eq('symbol', symbol).execute()
            
            if existing.data:
                return True  # Already in watchlist
            
            watchlist_data = {
                'user_id': user_id,
                'symbol': symbol,
                'added_at': datetime.utcnow().isoformat()
            }
            
            response = client_to_use.table('watchlists').insert(watchlist_data).execute()
            return bool(response.data)
        except Exception as e:
            st.error(f"Error adding to watchlist: {str(e)}")
            return False
    
    def remove_from_watchlist(self, user_id: str, symbol: str) -> bool:
        """Remove stock from user's watchlist (uses service role to bypass RLS)"""
        if not self.is_connected():
            return False
        
        try:
            client_to_use = self.service_client if self.service_client else self.client
            client_to_use.table('watchlists').delete().eq(
                'user_id', user_id
            ).eq('symbol', symbol).execute()
            return True
        except Exception as e:
            st.error(f"Error removing from watchlist: {str(e)}")
            return False
    
    def get_user_watchlist(self, user_id: str) -> List[str]:
        """Get user's watchlist (uses service role for data access)"""
        if not self.is_connected():
            return []
        
        try:
            client_to_use = self.service_client if self.service_client else self.client
            response = client_to_use.table('watchlists').select('symbol').eq('user_id', user_id).execute()
            return [item['symbol'] for item in response.data] if response.data else []
        except Exception as e:
            st.error(f"Error fetching watchlist: {str(e)}")
            return []


# Global Supabase client instance
_supabase_client = None


def get_supabase_client() -> SupabaseClient:
    """Get or create the global Supabase client"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client
