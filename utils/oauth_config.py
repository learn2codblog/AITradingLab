"""
OAuth Configuration Module
Handles Google OAuth2 setup and configuration
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv


class OAuthConfig:
    """Manage OAuth2 configuration"""
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        self.client_id = os.getenv(
            'GMAIL_CLIENT_ID',
            'your-client-id.apps.googleusercontent.com'
        )
        self.client_secret = os.getenv(
            'GMAIL_CLIENT_SECRET',
            'your-client-secret'
        )
        self.redirect_uri = os.getenv(
            'GMAIL_REDIRECT_URI',
            'http://localhost:8501'
        )
        
        # OAuth2 endpoints
        self.auth_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_endpoint = "https://oauth2.googleapis.com/token"
        self.user_info_endpoint = "https://openidconnect.googleapis.com/v1/userinfo"
        
        # Scopes
        self.scopes = [
            'openid',
            'email',
            'profile'
        ]

    @property
    def is_configured(self) -> bool:
        """Check if OAuth2 is properly configured"""
        return (
            'your-client-id' not in self.client_id and
            'your-client-secret' not in self.client_secret
        )

    def get_auth_url(self) -> str:
        """Generate OAuth2 authorization URL"""
        scope = ' '.join(self.scopes)
        auth_url = (
            f"{self.auth_endpoint}?"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"response_type=code&"
            f"scope={scope}&"
            f"access_type=offline&"
            f"prompt=consent"
        )
        return auth_url

    def get_token_request_data(self, auth_code: str) -> Dict:
        """Get token request data"""
        return {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': auth_code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }

    def get_refresh_token_data(self, refresh_token: str) -> Dict:
        """Get refresh token data"""
        return {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }

    @staticmethod
    def get_config_dict() -> Dict:
        """Get configuration as dictionary"""
        config = OAuthConfig()
        return {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'redirect_uri': config.redirect_uri,
            'auth_endpoint': config.auth_endpoint,
            'token_endpoint': config.token_endpoint,
            'user_info_endpoint': config.user_info_endpoint,
            'scopes': config.scopes,
            'is_configured': config.is_configured
        }

    @staticmethod
    def from_env() -> 'OAuthConfig':
        """Create OAuthConfig from environment variables"""
        return OAuthConfig()


class OAuthHelper:
    """Helper functions for OAuth2 operations"""
    
    @staticmethod
    def validate_oauth_setup() -> bool:
        """Validate OAuth2 setup"""
        config = OAuthConfig()
        return config.is_configured

    @staticmethod
    def get_setup_instructions() -> str:
        """Get OAuth2 setup instructions"""
        instructions = """
        # Gmail OAuth2 Setup Instructions
        
        ## Step 1: Create Google Cloud Project
        1. Go to [Google Cloud Console](https://console.cloud.google.com/)
        2. Create a new project named "AITradingLab"
        3. Select the project
        
        ## Step 2: Enable OAuth 2.0 API
        1. Go to "APIs & Services" > "Library"
        2. Search for "Google+ API"
        3. Click "Enable"
        
        ## Step 3: Create OAuth Credentials
        1. Go to "APIs & Services" > "Credentials"
        2. Click "Create Credentials" > "OAuth 2.0 Client ID"
        3. Select "Web application"
        4. Set Authorized redirect URIs:
           - http://localhost:8501
           - http://localhost:8501/oauth2callback (if needed)
        5. Copy Client ID and Client Secret
        
        ## Step 4: Set Environment Variables
        Create a `.env` file in the project root:
        
        ```
        GMAIL_CLIENT_ID=your-client-id.apps.googleusercontent.com
        GMAIL_CLIENT_SECRET=your-client-secret
        GMAIL_REDIRECT_URI=http://localhost:8501
        ```
        
        ## Step 5: Restart Application
        ```bash
        streamlit run app_modern.py
        ```
        
        ## Testing
        The application includes a demo login for testing without OAuth setup.
        """
        return instructions

    @staticmethod
    def test_oauth_connection() -> bool:
        """Test OAuth2 connection (basic check)"""
        config = OAuthConfig()
        return config.is_configured


# Create default instance
oauth_config = OAuthConfig()
