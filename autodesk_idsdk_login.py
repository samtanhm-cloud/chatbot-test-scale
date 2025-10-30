#!/usr/bin/env python3
"""
Autodesk IDSDK Login Script

Run this to perform one-time interactive login and capture OAuth token.
Much better than manual cookie capture!

Usage:
    python3 autodesk_idsdk_login.py

What it does:
1. Opens browser with Autodesk sign-in
2. You log in (SSO/2FA supported!)
3. Captures OAuth token
4. Displays token for saving to Streamlit secrets
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main login flow"""
    print("=" * 70)
    print("🔐 Autodesk IDSDK Login")
    print("=" * 70)
    print()
    
    # Check for Client ID
    print("📋 Checking configuration...")
    
    # Try to load from .streamlit/secrets.toml
    secrets_path = os.path.join(os.path.dirname(__file__), '.streamlit', 'secrets.toml')
    client_id = None
    
    if os.path.exists(secrets_path):
        print(f"   Found secrets file: {secrets_path}")
        try:
            with open(secrets_path, 'r') as f:
                for line in f:
                    if line.strip().startswith('AUTODESK_CLIENT_ID'):
                        client_id = line.split('=')[1].strip().strip('"\'')
                        print(f"   ✅ Client ID found: {client_id[:20]}...")
                        break
        except Exception as e:
            print(f"   ⚠️  Could not read secrets: {e}")
    
    # If not found, prompt user
    if not client_id:
        print()
        print("❌ AUTODESK_CLIENT_ID not found in secrets")
        print()
        print("📋 To get Autodesk Client ID:")
        print("   1. Go to https://aps.autodesk.com/")
        print("   2. Create an app")
        print("   3. Copy your Client ID")
        print("   4. Add to .streamlit/secrets.toml:")
        print('      AUTODESK_CLIENT_ID = "your_client_id"')
        print()
        
        # Prompt for manual entry
        client_id = input("Or enter Client ID now: ").strip()
        
        if not client_id:
            print("❌ No Client ID provided. Exiting.")
            return 1
        
        # Save to secrets
        try:
            os.makedirs(os.path.dirname(secrets_path), exist_ok=True)
            with open(secrets_path, 'a') as f:
                f.write(f'\nAUTODESK_CLIENT_ID = "{client_id}"\n')
            print(f"✅ Saved to {secrets_path}")
        except Exception as e:
            print(f"⚠️  Could not save to secrets: {e}")
    
    print()
    print("=" * 70)
    print("🚀 Starting Login Flow")
    print("=" * 70)
    print()
    print("In a moment, your browser will open with Autodesk sign-in.")
    print("Complete the login (SSO and 2FA are supported!).")
    print()
    input("Press ENTER when ready to start...")
    print()
    
    # Import here so we can set up client_id first
    from autodesk_idsdk_auth import AutodeskIDSDKAuth
    
    # Temporarily set secrets for auth class
    class TempSecrets:
        AUTODESK_CLIENT_ID = client_id
    
    import streamlit as st
    if not hasattr(st, 'secrets'):
        st.secrets = TempSecrets()
    else:
        st.secrets['AUTODESK_CLIENT_ID'] = client_id
    
    try:
        # Perform login
        auth = AutodeskIDSDKAuth()
        token_data = auth.login_interactive()
        
        print()
        print("=" * 70)
        print("✅ LOGIN SUCCESSFUL!")
        print("=" * 70)
        print()
        print(f"📊 Token Details:")
        print(f"   Valid for: {token_data['expires_in']} seconds (~{token_data['expires_in']//60} minutes)")
        print(f"   Token type: {token_data.get('token_type', 'Bearer')}")
        print(f"   Scope: {token_data.get('scope', 'default')}")
        print()
        print("=" * 70)
        print("📋 COPY THIS TO YOUR STREAMLIT SECRETS:")
        print("=" * 70)
        print()
        
        # Generate secrets content
        secrets_content = auth.save_token_to_secrets()
        print(secrets_content)
        
        print()
        print("=" * 70)
        print("💾 Where to Save:")
        print("=" * 70)
        print()
        print("🏠 Local Development:")
        print(f"   → {secrets_path}")
        print()
        print("☁️  Streamlit Cloud:")
        print("   → Go to App Settings → Secrets")
        print("   → Paste the above content")
        print("   → Click Save")
        print()
        print("=" * 70)
        print("🎯 Next Steps:")
        print("=" * 70)
        print()
        print("1. Copy the token section above")
        print("2. Add to secrets (local or cloud)")
        print("3. Run your Draftr automation!")
        print("4. Token will auto-refresh - no manual work needed!")
        print()
        print("✅ Done! You're all set!")
        print()
        
        return 0
        
    except KeyboardInterrupt:
        print()
        print("⚠️  Login cancelled by user")
        return 1
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ LOGIN FAILED")
        print("=" * 70)
        print()
        print(f"Error: {e}")
        print()
        print("🔧 Troubleshooting:")
        print("   1. Check your Client ID is correct")
        print("   2. Make sure you have internet connection")
        print("   3. Try again - browser should open automatically")
        print("   4. Check browser didn't block the popup")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())

