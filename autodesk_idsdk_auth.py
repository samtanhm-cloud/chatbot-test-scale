"""
Autodesk Identity SDK (IDSDK) Authentication

Uses Autodesk's official IDSDK for OAuth login flow with SSO/2FA support.
Much better than manual cookie capture!

Flow:
1. idsdk_login() - Launches browser for user login
2. Wait for IDSDK_EVENT_LOGIN_COMPLETE
3. idsdk_get_token() - Get OAuth access token
4. Use token for all Draftr/Autodesk API requests
"""

import subprocess
import json
import time
from typing import Optional, Dict
import streamlit as st


class AutodeskIDSDKAuth:
    """
    Autodesk Identity SDK authentication wrapper
    
    Provides OAuth token management using IDSDK's native login flow.
    Handles SSO, 2FA, and token refresh automatically.
    """
    
    def __init__(self):
        """Initialize IDSDK authentication"""
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.user_info = None
    
    def login_interactive(self) -> Dict:
        """
        Perform interactive login using IDSDK
        
        This will:
        1. Launch browser with Autodesk sign-in page
        2. Wait for user to complete login (SSO/2FA handled)
        3. Capture OAuth token when login completes
        
        Returns:
            Token data with access_token, refresh_token, expires_in
        """
        # This would call the actual IDSDK C/C++ library
        # For Python, we can use the Autodesk Identity REST API
        # which provides the same functionality
        
        print("🔐 Starting Autodesk login flow...")
        print("   Browser will open for authentication")
        print("   Please complete login (SSO/2FA will work)")
        
        # Use Autodesk's OAuth flow
        # This is equivalent to idsdk_login() but in Python
        token_data = self._oauth_device_flow()
        
        # Store tokens
        self.access_token = token_data['access_token']
        self.refresh_token = token_data.get('refresh_token')
        self.token_expires_at = time.time() + token_data['expires_in']
        
        print("✅ Login complete!")
        print(f"   Token expires in: {token_data['expires_in']} seconds")
        
        return token_data
    
    def _oauth_device_flow(self) -> Dict:
        """
        Implement OAuth device flow for interactive login
        
        Similar to idsdk_login() - launches browser for user authentication
        """
        import requests
        import webbrowser
        
        # Autodesk OAuth endpoints
        device_url = "https://developer.api.autodesk.com/authentication/v2/authorize/device"
        token_url = "https://developer.api.autodesk.com/authentication/v2/token"
        
        # Get client credentials from secrets
        if not hasattr(st, 'secrets') or 'AUTODESK_CLIENT_ID' not in st.secrets:
            raise ValueError("AUTODESK_CLIENT_ID not found in secrets")
        
        client_id = st.secrets['AUTODESK_CLIENT_ID']
        
        # Step 1: Request device code
        device_response = requests.post(
            device_url,
            data={
                'client_id': client_id,
                'scope': 'data:read data:write user:read'
            }
        )
        device_response.raise_for_status()
        device_data = device_response.json()
        
        # Step 2: Display user code and open browser
        print(f"\n📋 User Code: {device_data['user_code']}")
        print(f"🔗 Verification URL: {device_data['verification_uri']}")
        print(f"\n⏱️  You have {device_data['expires_in']} seconds to complete login")
        
        # Open browser automatically
        verification_url = device_data['verification_uri_complete']
        webbrowser.open(verification_url)
        print(f"\n🌐 Browser opened: {verification_url}")
        print("   Please complete login in the browser...")
        
        # Step 3: Poll for token
        device_code = device_data['device_code']
        interval = device_data['interval']
        expires_at = time.time() + device_data['expires_in']
        
        while time.time() < expires_at:
            time.sleep(interval)
            
            token_response = requests.post(
                token_url,
                data={
                    'client_id': client_id,
                    'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
                    'device_code': device_code
                }
            )
            
            if token_response.status_code == 200:
                # Success! User completed login
                return token_response.json()
            elif token_response.status_code == 400:
                error = token_response.json().get('error')
                if error == 'authorization_pending':
                    # Still waiting for user
                    print(".", end="", flush=True)
                    continue
                elif error == 'slow_down':
                    # Increase polling interval
                    interval += 5
                    continue
                else:
                    raise Exception(f"Login failed: {error}")
        
        raise TimeoutError("Login timeout - user did not complete authentication")
    
    def get_token(self) -> Optional[str]:
        """
        Get current access token (equivalent to idsdk_get_token())
        
        Returns:
            Access token string or None if not logged in
        """
        if not self.access_token:
            print("❌ No token available - user not logged in")
            print("   Call login_interactive() first")
            return None
        
        # Check if token is expired
        if self.token_expires_at and time.time() >= self.token_expires_at:
            print("⚠️  Token expired, refreshing...")
            self.refresh_token_if_needed()
        
        return self.access_token
    
    def refresh_token_if_needed(self) -> bool:
        """
        Refresh access token if expired
        
        Returns:
            True if refresh successful, False otherwise
        """
        if not self.refresh_token:
            print("❌ No refresh token available")
            return False
        
        try:
            import requests
            
            token_url = "https://developer.api.autodesk.com/authentication/v2/token"
            client_id = st.secrets['AUTODESK_CLIENT_ID']
            client_secret = st.secrets.get('AUTODESK_CLIENT_SECRET', '')
            
            response = requests.post(
                token_url,
                data={
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'grant_type': 'refresh_token',
                    'refresh_token': self.refresh_token
                }
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                if 'refresh_token' in token_data:
                    self.refresh_token = token_data['refresh_token']
                self.token_expires_at = time.time() + token_data['expires_in']
                print("✅ Token refreshed successfully")
                return True
            else:
                print(f"❌ Token refresh failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Token refresh error: {e}")
            return False
    
    def is_logged_in(self) -> bool:
        """
        Check if user is currently logged in with valid token
        
        Returns:
            True if logged in with valid token
        """
        if not self.access_token:
            return False
        
        if self.token_expires_at and time.time() >= self.token_expires_at:
            # Try to refresh
            return self.refresh_token_if_needed()
        
        return True
    
    def save_token_to_secrets(self) -> str:
        """
        Generate token data for saving to Streamlit secrets
        
        Returns:
            Formatted string to add to secrets.toml
        """
        if not self.access_token:
            raise ValueError("No token to save - login first")
        
        token_data = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_at': self.token_expires_at
        }
        
        secrets_content = f"""
# Autodesk OAuth Token (from IDSDK login)
# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
# Expires: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.token_expires_at)) if self.token_expires_at else 'Unknown'}

AUTODESK_ACCESS_TOKEN = "{self.access_token}"
AUTODESK_REFRESH_TOKEN = "{self.refresh_token or ''}"
AUTODESK_TOKEN_EXPIRES_AT = {int(self.token_expires_at) if self.token_expires_at else 0}
"""
        return secrets_content.strip()


# Streamlit integration functions

def streamlit_idsdk_login() -> Optional[AutodeskIDSDKAuth]:
    """
    Interactive IDSDK login for Streamlit app
    
    Returns:
        Authenticated IDSDK client or None
    """
    auth = AutodeskIDSDKAuth()
    
    st.info("🔐 Starting Autodesk login flow...")
    st.info("   A browser window will open")
    st.info("   Complete login (SSO/2FA supported)")
    
    try:
        with st.spinner("Waiting for login..."):
            token_data = auth.login_interactive()
        
        st.success("✅ Login successful!")
        st.success(f"   Token valid for {token_data['expires_in']} seconds")
        
        # Show token for saving
        with st.expander("📋 Save Token to Secrets"):
            secrets_text = auth.save_token_to_secrets()
            st.code(secrets_text, language="toml")
            st.info("💡 Copy this to .streamlit/secrets.toml (local) or Streamlit Cloud secrets")
        
        return auth
        
    except Exception as e:
        st.error(f"❌ Login failed: {e}")
        return None


def load_token_from_secrets() -> Optional[AutodeskIDSDKAuth]:
    """
    Load saved token from Streamlit secrets
    
    Returns:
        Authenticated IDSDK client or None
    """
    if not hasattr(st, 'secrets'):
        return None
    
    if 'AUTODESK_ACCESS_TOKEN' not in st.secrets:
        return None
    
    auth = AutodeskIDSDKAuth()
    auth.access_token = st.secrets['AUTODESK_ACCESS_TOKEN']
    auth.refresh_token = st.secrets.get('AUTODESK_REFRESH_TOKEN')
    auth.token_expires_at = st.secrets.get('AUTODESK_TOKEN_EXPIRES_AT', 0)
    
    # Check if token is still valid
    if auth.is_logged_in():
        return auth
    else:
        st.warning("⚠️  Saved token expired and could not be refreshed")
        return None

