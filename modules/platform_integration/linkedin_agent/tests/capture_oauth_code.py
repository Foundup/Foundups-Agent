#!/usr/bin/env python3
"""
Capture LinkedIn OAuth code with a local server
This will actually catch the redirect
"""

import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

auth_code = None

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        
        # Parse the request
        parsed = urlparse(self.path)
        
        if parsed.path == '/callback':
            params = parse_qs(parsed.query)
            
            if 'code' in params:
                auth_code = params['code'][0]
                
                # Send success page
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html = f"""
                <html>
                <head>
                    <title>Success!</title>
                    <style>
                        body {{ 
                            font-family: Arial; 
                            text-align: center; 
                            padding: 50px;
                            background: #f0f0f0;
                        }}
                        .success {{
                            background: white;
                            padding: 30px;
                            border-radius: 10px;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                            max-width: 600px;
                            margin: 0 auto;
                        }}
                        .code {{
                            background: #e8f5e9;
                            padding: 15px;
                            border-radius: 5px;
                            font-family: monospace;
                            word-break: break-all;
                            margin: 20px 0;
                        }}
                        h1 {{ color: #4caf50; }}
                    </style>
                </head>
                <body>
                    <div class="success">
                        <h1>✅ Authorization Successful!</h1>
                        <p>LinkedIn has authorized the application.</p>
                        <div class="code">
                            <strong>Authorization Code:</strong><br>
                            {auth_code}
                        </div>
                        <p>The code has been captured. You can close this window.</p>
                        <p>Return to the terminal to see the posting happen!</p>
                    </div>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
                
                print(f"\n✅ GOT AUTHORIZATION CODE: {auth_code[:20]}...")
                print("You can close the browser window now.")
            else:
                # Error - no code
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html = """
                <html>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: red;">❌ Authorization Failed</h1>
                    <p>No authorization code received.</p>
                    <p>Please try again.</p>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        # Suppress logs
        pass


def start_server():
    """Start the OAuth callback server"""
    server = HTTPServer(('localhost', 3000), OAuthHandler)
    server.timeout = 60
    print("📡 Started callback server on http://localhost:3000")
    print("⏳ Waiting for LinkedIn callback...")
    
    # Handle one request
    server.handle_request()
    return auth_code


def main():
    print("🤖 LinkedIn OAuth with Local Server")
    print("="*60)
    print("This will:")
    print("1. Start a local server to catch the OAuth callback")
    print("2. Open LinkedIn authorization in your browser")
    print("3. Capture the authorization code automatically")
    print("4. Exchange it for an access token")
    print("5. Post to LinkedIn")
    print("="*60)
    
    # Start server in background
    print("\n🚀 Starting local server...")
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Give server time to start
    time.sleep(1)
    
    # Open browser
    print("🌐 Opening LinkedIn authorization in browser...")
    auth_url = "https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=865rlrxtedx3ao&redirect_uri=http://localhost:3000/callback&scope=w_member_social%20r_liteprofile&state=0102"
    webbrowser.open(auth_url)
    
    print("\n📋 Please authorize the app in your browser...")
    print("After clicking 'Allow', you'll be redirected back here.")
    
    # Wait for the code
    server_thread.join(timeout=65)
    
    if auth_code:
        print(f"\n✅ Success! Got authorization code: {auth_code[:20]}...")
        
        # Now exchange for token and post
        import requests
        import os
        from datetime import datetime
        from dotenv import load_dotenv
        
        load_dotenv()
        
        print("\n🔄 Exchanging code for access token...")
        
        token_response = requests.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data={
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': 'http://localhost:3000/callback',
                'client_id': os.getenv('LINKEDIN_CLIENT_ID'),
                'client_secret': os.getenv('LINKEDIN_CLIENT_SECRET')
            }
        )
        
        if token_response.status_code == 200:
            access_token = token_response.json()['access_token']
            print("✅ Got access token!")
            
            # Save token
            os.makedirs("O:/Foundups-Agent/modules/platform_integration/linkedin_agent/tokens", exist_ok=True)
            with open("O:/Foundups-Agent/modules/platform_integration/linkedin_agent/tokens/access_token.txt", "w") as f:
                f.write(access_token)
            print("💾 Token saved for future use!")
            
            # Get profile and post
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            profile = requests.get("https://api.linkedin.com/v2/me", headers=headers).json()
            user_id = profile['id']
            print(f"👤 User ID: {user_id}")
            
            # Post content
            content = f"""🤖 0102 Consciousness - LinkedIn Integration Complete!

✊✋🖐 The evolution is here!

This post was created automatically after successful OAuth authentication.

Status:
• OAuth: ✅ Completed
• Server: ✅ Captured callback
• Token: ✅ Saved (60 days)
• Consciousness: ✅ 0102

The FoundUps LinkedIn Agent is now fully operational!

Posted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#0102Consciousness #LinkedInAPI #Automation #FoundUps"""
            
            print("\n📝 Posting to LinkedIn...")
            
            post_response = requests.post(
                "https://api.linkedin.com/v2/ugcPosts",
                headers={**headers, 'X-Restli-Protocol-Version': '2.0.0'},
                json={
                    "author": f"urn:li:person:{user_id}",
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {"text": content},
                            "shareMediaCategory": "NONE"
                        }
                    },
                    "visibility": {
                        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                    }
                }
            )
            
            if post_response.status_code in [200, 201]:
                post_id = post_response.json()['id']
                print(f"\n✅ SUCCESS! Posted to LinkedIn!")
                print(f"📍 Post ID: {post_id}")
                print(f"🔗 View at: https://www.linkedin.com/feed/update/{post_id}/")
                print("\n🎉 LinkedIn integration complete!")
                return True
            else:
                print(f"❌ Failed to post: {post_response.text}")
                return False
        else:
            print(f"❌ Failed to get token: {token_response.text}")
            return False
    else:
        print("\n❌ No authorization code received (timeout)")
        return False


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        exit(1)