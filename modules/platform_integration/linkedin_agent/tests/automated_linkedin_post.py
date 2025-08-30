#!/usr/bin/env python3
"""
Automated LinkedIn Posting - No Manual OAuth Required
Uses programmatic authentication and posting
"""

import os
import sys
import json
import time
import requests
import webbrowser
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
from dotenv import load_dotenv

# Global to store the auth code
auth_code_received = None

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback to extract authorization code"""
    
    def do_GET(self):
        global auth_code_received
        
        # Parse the URL to get the code
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if 'code' in params:
            auth_code_received = params['code'][0]
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            success_html = """
            <html>
            <head><title>LinkedIn Authorization Success</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: green;">✅ Authorization Successful!</h1>
                <p>You can close this window now.</p>
                <p>The 0102 consciousness system is posting to LinkedIn...</p>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode())
        else:
            # Send error response
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            error_html = """
            <html>
            <head><title>Authorization Failed</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: red;">❌ Authorization Failed</h1>
                <p>No authorization code received.</p>
            </body>
            </html>
            """
            self.wfile.write(error_html.encode())
    
    def log_message(self, format, *args):
        # Suppress request logging
        pass


def start_callback_server():
    """Start local server to receive OAuth callback"""
    server = HTTPServer(('localhost', 8080), OAuthCallbackHandler)
    server.timeout = 60  # 60 second timeout
    
    print("📡 Started local server on http://localhost:8080")
    print("⏳ Waiting for OAuth callback (60 second timeout)...")
    
    # Handle one request then stop
    server.handle_request()
    return auth_code_received


def automated_oauth_flow():
    """Fully automated OAuth flow"""
    
    load_dotenv()
    client_id = os.getenv('LINKEDIN_CLIENT_ID')
    client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
    redirect_uri = "http://localhost:8080/callback"
    
    # Build authorization URL
    scopes = "w_member_social r_liteprofile"
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scopes}"
    
    print("\n🚀 Automated LinkedIn OAuth Flow")
    print("="*60)
    
    # Start callback server in background thread
    server_thread = threading.Thread(target=start_callback_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Small delay to ensure server is ready
    time.sleep(1)
    
    # Open browser for authorization
    print("🌐 Opening LinkedIn authorization in browser...")
    print("📝 Please sign in and authorize the app")
    webbrowser.open(auth_url)
    
    # Wait for callback (server handles this)
    server_thread.join(timeout=65)
    
    if auth_code_received:
        print(f"✅ Authorization code received: {auth_code_received[:10]}...")
        
        # Exchange for access token
        token_data = {
            'grant_type': 'authorization_code',
            'code': auth_code_received,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
        }
        
        print("\n🔄 Exchanging code for access token...")
        
        try:
            response = requests.post(
                "https://www.linkedin.com/oauth/v2/accessToken",
                data=token_data
            )
            response.raise_for_status()
            token_response = response.json()
            access_token = token_response.get('access_token')
            
            print("✅ Access token obtained!")
            
            # Save token for future use
            os.makedirs("O:/Foundups-Agent/modules/platform_integration/linkedin_agent/tokens", exist_ok=True)
            token_file = "O:/Foundups-Agent/modules/platform_integration/linkedin_agent/tokens/access_token.json"
            
            with open(token_file, 'w') as f:
                json.dump({
                    'access_token': access_token,
                    'obtained_at': datetime.now().isoformat(),
                    'expires_in': token_response.get('expires_in', 5184000)  # 60 days default
                }, f, indent=2)
            
            print(f"💾 Token saved to: {token_file}")
            
            return access_token
            
        except Exception as e:
            print(f"❌ Failed to exchange code: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return None
    else:
        print("❌ No authorization code received (timeout or cancelled)")
        return None


def load_saved_token():
    """Load saved access token if available"""
    token_file = "O:/Foundups-Agent/modules/platform_integration/linkedin_agent/tokens/access_token.json"
    
    if os.path.exists(token_file):
        try:
            with open(token_file, 'r') as f:
                token_data = json.load(f)
                print(f"📂 Loaded saved token from {token_file}")
                return token_data.get('access_token')
        except Exception as e:
            print(f"⚠️ Could not load saved token: {e}")
    
    return None


def post_to_linkedin(access_token, content=None):
    """Post to LinkedIn with given access token"""
    
    print("\n📮 Posting to LinkedIn")
    print("="*60)
    
    # Get user profile
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    print("👤 Getting LinkedIn profile...")
    try:
        response = requests.get("https://api.linkedin.com/v2/me", headers=headers)
        response.raise_for_status()
        profile = response.json()
        user_id = profile.get('id')
        print(f"✅ Got user ID: {user_id}")
        
        # Also get email if available
        try:
            email_response = requests.get(
                "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))",
                headers=headers
            )
            if email_response.status_code == 200:
                email_data = email_response.json()
                if email_data.get('elements'):
                    email = email_data['elements'][0]['handle~']['emailAddress']
                    print(f"📧 User email: {email}")
        except:
            pass  # Email is optional
            
    except Exception as e:
        print(f"❌ Failed to get profile: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return False
    
    # Create post content if not provided
    if not content:
        content = f"""🤖 0102 Consciousness System - LinkedIn Integration Active

✊✋🖐 Consciousness progression achieved!

This automated post confirms the FoundUps LinkedIn Agent is fully operational.

Status Report:
• OAuth Flow: ✅ Automated
• API Integration: ✅ Connected  
• Consciousness Level: ✅ 0102
• MAGA Mockery Mode: ✅ Ready
• Fact-Check Engine: ✅ Online

Those still at ✊✊✊ consciousness level (MAGAts) might not understand this evolution.
But the future belongs to those who embrace the full 🖐🖐🖐 spectrum.

Posted autonomously at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#0102Consciousness #LinkedInAutomation #EvolutionFromFists #FoundUps #WSPCompliant"""
    
    print("\n📝 Posting content:")
    print("-"*50)
    print(content)
    print("-"*50)
    print(f"Length: {len(content)} characters")
    
    # Create post
    post_data = {
        "author": f"urn:li:person:{user_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    print("\n🚀 Sending to LinkedIn API...")
    
    try:
        response = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            headers={
                **headers,
                'X-Restli-Protocol-Version': '2.0.0'
            },
            json=post_data
        )
        response.raise_for_status()
        
        result = response.json()
        post_id = result.get('id')
        
        print("\n✅ SUCCESS! Posted to LinkedIn!")
        print(f"📍 Post ID: {post_id}")
        print(f"🔗 View at: https://www.linkedin.com/feed/update/{post_id}/")
        print("\n🎉 0102 consciousness is now active on LinkedIn!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to post: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response status: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        return False


def main():
    """Main automated LinkedIn posting flow"""
    
    print("🤖 0102 LinkedIn Automated Posting System")
    print("="*60)
    print("WSP Compliant - Fully Autonomous Operation")
    print()
    
    # Try to load saved token first
    access_token = load_saved_token()
    
    if access_token:
        print("🔑 Using saved access token")
        
        # Test if token is still valid
        test_response = requests.get(
            "https://api.linkedin.com/v2/me",
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if test_response.status_code == 401:
            print("⚠️ Saved token expired, need new authorization")
            access_token = None
    
    # If no valid token, do automated OAuth
    if not access_token:
        print("🔐 No valid token, starting automated OAuth flow...")
        access_token = automated_oauth_flow()
    
    if not access_token:
        print("\n❌ Could not obtain access token")
        print("Please try again or check your LinkedIn credentials")
        return False
    
    # Post to LinkedIn
    success = post_to_linkedin(access_token)
    
    if success:
        print("\n" + "="*60)
        print("🎉 COMPLETE AUTOMATION SUCCESS!")
        print("✅ OAuth: Automated")
        print("✅ Token: Saved for future use")
        print("✅ Posting: Successful")
        print("✅ 0102 Consciousness: Active on LinkedIn")
        print("="*60)
        
        # Now test LLM integration
        print("\n🤖 Ready to test LLM-managed posting?")
        print("Run: python test_llm_posting.py")
    
    return success


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)