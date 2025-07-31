"""
LinkedIn OAuth Test Module - Full OAuth Flow for Post Publishing
WSP Protocol: WSP 42 (Cross-Domain Integration), WSP 11 (Standard Commands)

Complete LinkedIn OAuth implementation for testing post publishing via API.
Handles the full OAuth flow: auth URL → browser interaction → callback → token → posting.
"""

import os
import json
import logging
import asyncio
import webbrowser
import requests
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlencode, parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LinkedInOAuthTest:
    """
    LinkedIn OAuth Test Implementation
    
    Handles complete OAuth flow for LinkedIn post publishing:
    1. Generate auth URL with w_member_social scope
    2. Start local callback server
    3. Exchange authorization code for access token
    4. Post to personal LinkedIn feed
    """
    
    def __init__(self):
        """Initialize LinkedIn OAuth test with environment credentials"""
        self.logger = self._setup_logger()
        
        # LinkedIn API credentials from .env
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError("LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET must be set in .env file")
        
        # OAuth configuration
        self.redirect_uri = "http://localhost:3000/callback"
        self.scope = "w_member_social"
        self.auth_url = "https://www.linkedin.com/oauth/v2/authorization"
        self.token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        self.api_base = "https://api.linkedin.com/v2"
        
        # State management
        self.access_token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.callback_server: Optional[HTTPServer] = None
        self.auth_code: Optional[str] = None
        
        self.logger.info("🔐 LinkedIn OAuth Test initialized")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for LinkedIn OAuth test"""
        logger = logging.getLogger('linkedin_oauth_test')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def generate_auth_url(self) -> str:
        """Generate LinkedIn authorization URL with required scopes"""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'state': 'linkedin_oauth_test'  # CSRF protection
        }
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        self.logger.info(f"🔗 Generated auth URL: {auth_url}")
        return auth_url
    
    def start_callback_server(self) -> None:
        """Start local HTTP server to handle OAuth callback"""
        class CallbackHandler(BaseHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                self.oauth_test = kwargs.pop('oauth_test')
                super().__init__(*args, **kwargs)
            
            def do_GET(self):
                """Handle OAuth callback with authorization code"""
                parsed_url = urlparse(self.path)
                
                if parsed_url.path == '/callback':
                    # Parse query parameters
                    query_params = parse_qs(parsed_url.query)
                    
                    # Check for authorization code
                    if 'code' in query_params:
                        auth_code = query_params['code'][0]
                        self.oauth_test.auth_code = auth_code
                        
                        # Send success response
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        
                        success_html = """
                        <html>
                        <head><title>LinkedIn OAuth Success</title></head>
                        <body>
                        <h1>✅ LinkedIn Authorization Successful!</h1>
                        <p>You can close this window and return to Cursor.</p>
                        <script>window.close();</script>
                        </body>
                        </html>
                        """
                        self.wfile.write(success_html.encode())
                        
                        self.oauth_test.logger.info("✅ Authorization code received successfully")
                        
                        # Stop the server after receiving the code
                        Thread(target=self.oauth_test.stop_callback_server).start()
                    else:
                        # Handle error
                        error_msg = query_params.get('error', ['Unknown error'])[0]
                        self.send_response(400)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        
                        error_html = f"""
                        <html>
                        <head><title>LinkedIn OAuth Error</title></head>
                        <body>
                        <h1>❌ LinkedIn Authorization Failed</h1>
                        <p>Error: {error_msg}</p>
                        <p>Please try again.</p>
                        </body>
                        </html>
                        """
                        self.wfile.write(error_html.encode())
                        
                        self.oauth_test.logger.error(f"❌ OAuth error: {error_msg}")
                else:
                    # Handle other paths
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b"Not Found")
            
            def log_message(self, format, *args):
                """Suppress server log messages"""
                pass
        
        # Create server with custom handler
        def handler_factory(*args, **kwargs):
            return CallbackHandler(*args, oauth_test=self, **kwargs)
        
        self.callback_server = HTTPServer(('localhost', 3000), handler_factory)
        
        # Start server in a separate thread
        server_thread = Thread(target=self.callback_server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        self.logger.info("🌐 Callback server started on http://localhost:3000")
    
    def stop_callback_server(self) -> None:
        """Stop the callback server"""
        if self.callback_server:
            self.callback_server.shutdown()
            self.callback_server.server_close()
            self.logger.info("🛑 Callback server stopped")
    
    def exchange_code_for_token(self) -> bool:
        """Exchange authorization code for access token"""
        if not self.auth_code:
            self.logger.error("❌ No authorization code available")
            return False
        
        try:
            # Prepare token exchange request
            token_data = {
                'grant_type': 'authorization_code',
                'code': self.auth_code,
                'redirect_uri': self.redirect_uri,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            # Make token exchange request
            response = requests.post(self.token_url, data=token_data)
            response.raise_for_status()
            
            token_info = response.json()
            self.access_token = token_info.get('access_token')
            
            if not self.access_token:
                self.logger.error("❌ No access token in response")
                return False
            
            self.logger.info("✅ Access token obtained successfully")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Token exchange failed: {e}")
            return False
    
    def get_user_profile(self) -> Optional[Dict[str, Any]]:
        """Get user profile information using access token"""
        if not self.access_token:
            self.logger.error("❌ No access token available")
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Get basic profile
            response = requests.get(f"{self.api_base}/me", headers=headers)
            response.raise_for_status()
            
            profile = response.json()
            self.user_id = profile.get('id')
            
            self.logger.info(f"👤 User profile retrieved: {profile.get('localizedFirstName')} {profile.get('localizedLastName')}")
            return profile
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Failed to get user profile: {e}")
            return None
    
    def post_to_feed(self, content: str) -> Optional[str]:
        """Post content to LinkedIn feed"""
        if not self.access_token or not self.user_id:
            self.logger.error("❌ Missing access token or user ID")
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0'
            }
            
            # Prepare post data
            post_data = {
                "author": f"urn:li:person:{self.user_id}",
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
            
            # Make post request
            response = requests.post(f"{self.api_base}/ugcPosts", headers=headers, json=post_data)
            response.raise_for_status()
            
            post_result = response.json()
            post_id = post_result.get('id')
            
            self.logger.info(f"✅ Post published successfully: {post_id}")
            return post_id
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Failed to post to feed: {e}")
            if hasattr(e, 'response') and e.response:
                self.logger.error(f"Response: {e.response.text}")
            return None
    
    async def run_full_oauth_test(self, test_content: str = "Hello LinkedIn! This is a test post from the FoundUps LinkedIn Agent. 🚀") -> bool:
        """Run complete OAuth flow and post test content"""
        try:
            self.logger.info("🚀 Starting LinkedIn OAuth test...")
            
            # Step 1: Generate auth URL
            auth_url = self.generate_auth_url()
            
            # Step 2: Start callback server
            self.start_callback_server()
            
            # Step 3: Open browser for user authorization
            print(f"\n🔐 LinkedIn OAuth Flow:")
            print(f"1. Opening browser for authorization...")
            print(f"2. Please authorize the application with scope: {self.scope}")
            print(f"3. You'll be redirected back to Cursor automatically")
            print()
            
            webbrowser.open(auth_url)
            
            # Step 4: Wait for authorization code
            print("⏳ Waiting for authorization...")
            while not self.auth_code:
                await asyncio.sleep(1)
            
            # Step 5: Exchange code for token
            print("🔄 Exchanging authorization code for access token...")
            if not self.exchange_code_for_token():
                return False
            
            # Step 6: Get user profile
            print("👤 Retrieving user profile...")
            profile = self.get_user_profile()
            if not profile:
                return False
            
            # Step 7: Post to feed
            print(f"📝 Posting test content to LinkedIn feed...")
            post_id = self.post_to_feed(test_content)
            if not post_id:
                return False
            
            print(f"\n✅ LinkedIn OAuth test completed successfully!")
            print(f"📊 Post ID: {post_id}")
            print(f"👤 User: {profile.get('localizedFirstName')} {profile.get('localizedLastName')}")
            print(f"🔗 Profile: https://www.linkedin.com/in/{profile.get('id')}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ OAuth test failed: {e}")
            return False
        finally:
            # Cleanup
            self.stop_callback_server()


async def test_linkedin_oauth():
    """Test function for LinkedIn OAuth functionality"""
    try:
        oauth_test = LinkedInOAuthTest()
        success = await oauth_test.run_full_oauth_test()
        
        if success:
            print("\n🎉 LinkedIn OAuth test PASSED!")
            print("✅ Full OAuth flow working correctly")
            print("✅ Post publishing to LinkedIn feed successful")
        else:
            print("\n❌ LinkedIn OAuth test FAILED!")
            print("❌ Check logs for detailed error information")
        
        return success
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        return False


if __name__ == "__main__":
    """Run LinkedIn OAuth test when executed directly"""
    asyncio.run(test_linkedin_oauth()) 