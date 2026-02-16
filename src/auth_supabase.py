"""
Enhanced Authentication Module with Supabase Integration
Handles persistent user data, sessions, and multi-provider OAuth
"""

import streamlit as st
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import hashlib
import secrets
import logging
from src.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


class SupabaseAuthManager:
    """Enhanced authentication manager with persistent Supabase backend"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.session_timeout = 24 * 3600  # 24 hours in seconds
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def initialize_session_state(self):
        """Initialize Streamlit session state for authentication"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user_id' not in st.session_state:
            st.session_state.user_id = None
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
    
    def register_email_user(self, email: str, password: str, name: str) -> Tuple[bool, str]:
        """Register a new email user in Supabase with transaction-like rollback"""
        if not self.supabase.is_connected():
            return False, "Database connection unavailable"
        
        # Validate input
        if email:
            email = email.strip().lower()
        if name:
            name = name.strip()
        
        if not email or not password or not name:
            return False, "All fields are required"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        # Check if user already exists
        if self.supabase.user_exists(email):
            return False, f"Email {email} already registered"
        
        try:
            # Step 1: Create user
            password_hash = self._hash_password(password)
            user = self.supabase.create_user(
                email=email,
                name=name,
                password_hash=password_hash,
                login_method='email'
            )
            
            if not user or not user.get('id'):
                return False, "Failed to create user account"
            
            user_id = user['id']
            
            # Step 2: Log activity (non-critical, but try)
            try:
                self.supabase.log_activity(
                    user_id=user_id,
                    activity_type='registration',
                    description=f'New user registered: {name}',
                    status='success'
                )
            except Exception as log_error:
                # Log failed but don't rollback
                print(f"Activity logging failed (non-critical): {log_error}")
            
            return True, "Registration successful! Please login."
            
        except Exception as e:
            # If any critical step fails, rollback the user
            if 'user_id' in locals() and user_id:
                self.supabase.delete_user(user_id)
            return False, f"Registration failed: {str(e)}"
    
    def login_email_user(self, email: str, password: str) -> Tuple[bool, str]:
        """Login with email and password using Supabase"""
        if not self.supabase.is_connected():
            return False, "Database connection unavailable"
        
        if not email or not password:
            return False, "Email and password required"
        
        email = email.strip().lower()
        
        # Get user from database
        user = self.supabase.get_user_by_email(email)
        
        if not user:
            return False, "Email not found"
        
        # Verify password
        password_hash = self._hash_password(password)
        if user['password_hash'] != password_hash:
            return False, "Incorrect password"
        
        if not user.get('is_active', True):
            return False, "Account is inactive. Please contact support."
        
        # Update last login
        self.supabase.update_last_login(user['id'])
        
        # Set session
        self.set_user_session(
            user_id=user['id'],
            email=email,
            name=user['name'],
            picture=user.get('picture_url'),
            method='email'
        )
        
        # Log activity
        self.supabase.log_activity(
            user_id=user['id'],
            activity_type='login',
            description='User logged in with email/password',
            status='success'
        )
        
        return True, "Login successful"
    
    def login_oauth_user(self, email: str, name: str, picture_url: str = None,
                        provider: str = 'google') -> Tuple[bool, str]:
        """Login/Register user via OAuth provider"""
        if not self.supabase.is_connected():
            return False, "Database connection unavailable"
        
        if not email or not name:
            return False, "Email and name required"
        
        email = email.strip().lower()
        name = name.strip()
        
        # Check if user exists
        user = self.supabase.get_user_by_email(email)
        
        if not user:
            # Create new user for OAuth
            user = self.supabase.create_user(
                email=email,
                name=name,
                password_hash=None,  # No password for OAuth
                login_method=provider,
                picture_url=picture_url
            )
            
            if not user:
                return False, f"Failed to create {provider} account"
            
            # Log activity
            self.supabase.log_activity(
                user_id=user['id'],
                activity_type='oauth_registration',
                description=f'New user registered via {provider}',
                status='success'
            )
        else:
            # Update last login
            self.supabase.update_last_login(user['id'])
            
            # Log activity
            self.supabase.log_activity(
                user_id=user['id'],
                activity_type='login',
                description=f'User logged in via {provider}',
                status='success'
            )
        
        # Set session
        self.set_user_session(
            user_id=user['id'],
            email=email,
            name=user.get('name', name),
            picture=picture_url or user.get('picture_url'),
            method=provider
        )
        
        return True, "Login successful"
    
    def set_user_session(self, user_id: str, email: str, name: str,
                        picture: str = None, method: str = 'email'):
        """Set user session after successful authentication"""
        st.session_state.authenticated = True
        st.session_state.user_id = user_id
        st.session_state.user_email = email
        st.session_state.user_name = name
        st.session_state.user_picture = picture
        st.session_state.session_start = datetime.now()
        st.session_state.login_method = method
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False) and st.session_state.get('user_id') is not None
    
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
        if self.is_authenticated():
            user_id = st.session_state.get('user_id')
            if user_id and self.supabase.is_connected():
                # Log logout activity
                self.supabase.log_activity(
                    user_id=user_id,
                    activity_type='logout',
                    description='User logged out',
                    status='success'
                )
        
        st.session_state.authenticated = False
        st.session_state.user_id = None
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
            'user_id': st.session_state.user_id,
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
    
    def get_user_from_db(self, user_id: str) -> Optional[Dict]:
        """Get user data from Supabase"""
        if not self.supabase.is_connected():
            return None
        
        return self.supabase.get_user_by_id(user_id)
    
    def update_user_profile(self, user_id: str, name: str = None, 
                           picture_url: str = None) -> Tuple[bool, str]:
        """Update user profile information"""
        if not self.supabase.is_connected():
            return False, "Database connection unavailable"
        
        if not user_id:
            return False, "User not authenticated"
        
        update_data = {}
        if name:
            update_data['name'] = name.strip()
        if picture_url:
            update_data['picture_url'] = picture_url
        
        if not update_data:
            return False, "No data to update"
        
        user = self.supabase.update_user(user_id, update_data)
        
        if user:
            # Update session
            if 'name' in update_data:
                st.session_state.user_name = update_data['name']
            if 'picture_url' in update_data:
                st.session_state.user_picture = update_data['picture_url']
            
            # Log activity
            self.supabase.log_activity(
                user_id=user_id,
                activity_type='profile_update',
                description='User updated profile',
                status='success'
            )
            
            return True, "Profile updated successfully"
        
        return False, "Failed to update profile"
    
    def change_password(self, user_id: str, old_password: str,
                       new_password: str) -> Tuple[bool, str]:
        """Change user password"""
        if not self.supabase.is_connected():
            return False, "Database connection unavailable"
        
        if not user_id or not old_password or not new_password:
            return False, "All fields are required"
        
        if len(new_password) < 6:
            return False, "New password must be at least 6 characters"
        
        if old_password == new_password:
            return False, "New password must be different from old password"
        
        # Get user from database
        user = self.supabase.get_user_by_id(user_id)
        
        if not user:
            return False, "User not found"
        
        # Verify old password
        old_hash = self._hash_password(old_password)
        if user['password_hash'] != old_hash:
            return False, "Current password is incorrect"
        
        # Update password
        new_hash = self._hash_password(new_password)
        result = self.supabase.update_user(user_id, {'password_hash': new_hash})
        
        if result:
            # Log activity
            self.supabase.log_activity(
                user_id=user_id,
                activity_type='password_change',
                description='User changed password',
                status='success'
            )
            return True, "Password changed successfully"
        
        return False, "Failed to change password"
    
    def delete_account(self, user_id: str, password: str) -> Tuple[bool, str]:
        """Delete user account"""
        if not self.supabase.is_connected():
            return False, "Database connection unavailable"
        
        if not user_id or not password:
            return False, "Password is required"
        
        # Get user from database
        user = self.supabase.get_user_by_id(user_id)
        
        if not user:
            return False, "User not found"
        
        # Verify password
        password_hash = self._hash_password(password)
        if user['password_hash'] != password_hash:
            return False, "Password is incorrect"
        
        # Log deletion
        self.supabase.log_activity(
            user_id=user_id,
            activity_type='account_deletion',
            description='User deleted their account',
            status='success'
        )
        
        # Note: Actual deletion would be handled by Supabase's user management
        # For now, we mark the account as inactive
        self.supabase.update_user(user_id, {'is_active': False})
        
        # Logout
        self.logout()
        
        return True, "Account deleted successfully"
    
    def get_user_activities(self, user_id: str, limit: int = 20) -> list:
        """Get user's recent activities"""
        if not self.supabase.is_connected():
            return []
        
        return self.supabase.get_user_activities(user_id, limit)
    
    def log_activity(self, activity_type: str, description: str,
                    action_details: Dict = None, status: str = 'success'):
        """Log user activity"""
        user_id = st.session_state.get('user_id')
        if user_id and self.supabase.is_connected():
            self.supabase.log_activity(
                user_id=user_id,
                activity_type=activity_type,
                description=description,
                action_details=action_details,
                status=status
            )


# Backward compatibility - keep old AuthManager class
class AuthManager(SupabaseAuthManager):
    """Backward compatible with old AuthManager"""
    pass
