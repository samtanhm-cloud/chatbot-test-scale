"""
Autodesk OAuth Authentication for Draftr

Uses Autodesk Identity SDK (IDSDK) OAuth flow to get access tokens
for authenticating Draftr API/automation requests.

Much more secure than session cookies!
"""

import requests
import streamlit as st
from typing import Dict, Optional, Tuple
import base64
import time
from urllib.parse import urlencode


class AutodeskOAuthClient:
    """
    Autodesk OAuth 2.0 authentication client
    
    Uses Autodesk Forge/APS authentication system which is shared
    across all Autodesk products including Draftr.
    """
    
    # Autodesk authentication endpoints
    AUTH_BASE = "https://developer.api.autodesk.com/authentication/v2"
    TOKEN_URL = f"{AUTH_BASE}/token"
    AUTHORIZE_URL = f"{AUTH_BASE}/authorize"
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """
        Initialize Autodesk OAuth client
        
        Args:
            client_id: Autodesk app client ID
            client_secret: Autodesk app client secret
        """
        # Try to load from secrets if not provided
        self.client_id = client_id
        self.client_secret = client_secret
        
        if not self.client_id and hasattr(st, 'secrets'):
            self.client_id = st.secrets.get('AUTODESK_CLIENT_ID')
            self.client_secret = st.secrets.get('AUTODESK_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Autodesk OAuth credentials required. "
                "Add AUTODESK_CLIENT_ID and AUTODESK_CLIENT_SECRET to Streamlit secrets."
            )
        
        # Token storage
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
    
    def get_authorization_url(self, redirect_uri: str, scope: str = "data:read data:write") -> Tuple[str, str]:
        """
        Get authorization URL for OAuth flow
        
        Args:
            redirect_uri: Where to redirect after authorization
            scope: OAuth scopes to request
            
        Returns:
            (authorization_url, state) - URL to redirect user to and state parameter
        """
        import secrets
        state = secrets.token_urlsafe(32)
        
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'scope': scope,
            'state': state
        }
        
        auth_url = f"{self.AUTHORIZE_URL}?{urlencode(params)}"
        return auth_url, state
    
    def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from OAuth callback
            redirect_uri: Same redirect URI used in authorization
            
        Returns:
            Token response with access_token, refresh_token, expires_in
        """
        # Create Basic Auth header
        credentials = f"{self.client_id}:{self.client_secret}"
        b64_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {b64_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri
        }
        
        response = requests.post(self.TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        
        # Store tokens
        self.access_token = token_data['access_token']
        self.refresh_token = token_data.get('refresh_token')
        self.token_expires_at = time.time() + token_data['expires_in']
        
        return token_data
    
    def get_token_with_client_credentials(self, scope: str = "data:read data:write") -> Dict:
        """
        Get access token using client credentials (2-legged OAuth)
        
        This is for server-to-server authentication without user interaction.
        
        Args:
            scope: OAuth scopes to request
            
        Returns:
            Token response with access_token and expires_in
        """
        # Create Basic Auth header
        credentials = f"{self.client_id}:{self.client_secret}"
        b64_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {b64_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'client_credentials',
            'scope': scope
        }
        
        response = requests.post(self.TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        
        # Store token
        self.access_token = token_data['access_token']
        self.token_expires_at = time.time() + token_data['expires_in']
        
        return token_data
    
    def refresh_access_token(self) -> Dict:
        """
        Refresh access token using refresh token
        
        Returns:
            New token response
        """
        if not self.refresh_token:
            raise ValueError("No refresh token available")
        
        # Create Basic Auth header
        credentials = f"{self.client_id}:{self.client_secret}"
        b64_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {b64_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        
        response = requests.post(self.TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        
        # Update tokens
        self.access_token = token_data['access_token']
        if 'refresh_token' in token_data:
            self.refresh_token = token_data['refresh_token']
        self.token_expires_at = time.time() + token_data['expires_in']
        
        return token_data
    
    def get_valid_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary
        
        Returns:
            Valid access token string
        """
        # Check if token exists and is not expired
        if self.access_token and self.token_expires_at:
            # Refresh if expiring in next 5 minutes
            if time.time() < (self.token_expires_at - 300):
                return self.access_token
        
        # Try to refresh if we have a refresh token
        if self.refresh_token:
            try:
                self.refresh_access_token()
                return self.access_token
            except Exception:
                pass
        
        # Fall back to client credentials
        self.get_token_with_client_credentials()
        return self.access_token
    
    def make_authenticated_request(self, url: str, method: str = 'GET', **kwargs) -> requests.Response:
        """
        Make an authenticated request to Autodesk/Draftr API
        
        Args:
            url: API endpoint URL
            method: HTTP method
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response object
        """
        token = self.get_valid_token()
        
        # Add authorization header
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {token}'
        
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        
        return response


# Streamlit integration functions

def setup_autodesk_oauth() -> Optional[AutodeskOAuthClient]:
    """
    Setup Autodesk OAuth client for Streamlit app
    
    Returns:
        Configured OAuth client or None if credentials missing
    """
    try:
        client = AutodeskOAuthClient()
        return client
    except ValueError as e:
        st.error(f"❌ Autodesk OAuth not configured: {e}")
        with st.expander("📋 How to Configure"):
            st.markdown("""
            ### Getting Autodesk OAuth Credentials:
            
            1. Go to [Autodesk Platform Services](https://aps.autodesk.com/)
            2. Create an account or log in
            3. Create a new App
            4. Get your **Client ID** and **Client Secret**
            5. Add to Streamlit secrets:
            
            ```toml
            AUTODESK_CLIENT_ID = "your_client_id"
            AUTODESK_CLIENT_SECRET = "your_client_secret"
            ```
            """)
        return None


def get_autodesk_token_for_draftr() -> Optional[str]:
    """
    Get valid Autodesk access token for Draftr requests
    
    Returns:
        Access token string or None if not available
    """
    try:
        client = AutodeskOAuthClient()
        # Use client credentials (2-legged) for server-to-server
        client.get_token_with_client_credentials(scope="data:read data:write")
        return client.access_token
    except Exception as e:
        st.error(f"❌ Failed to get Autodesk token: {e}")
        return None

