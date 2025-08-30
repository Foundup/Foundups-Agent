#!/usr/bin/env python3
"""
Chrome OAuth Flow for LinkedIn
Opens Chrome and handles the authorization
"""

import os
import sys
import time
import json
import requests
import webbrowser
import subprocess
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

def open_oauth_in_chrome():
    """Open LinkedIn OAuth in Chrome and get the authorization code"""
    
    load_dotenv()
    client_id = os.getenv('LINKEDIN_CLIENT_ID')
    client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
    
    # Build OAuth URL
    oauth_url = f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={client_id}&redirect_uri=http://localhost:8080/callback&scope=w_member_social r_liteprofile&state=0102"
    
    print("🤖 LinkedIn OAuth Flow via Chrome")
    print("="*60)
    print("\n📋 Instructions:")
    print("1. Chrome will open with LinkedIn authorization page")
    print("2. Sign in to LinkedIn if needed")
    print("3. Click 'Allow' to authorize the app")
    print("4. You'll see an error page (localhost) - that's OK!")
    print("5. Copy the ENTIRE URL from the address bar")
    print("6. Come back here and paste it")
    print("\n" + "="*60)
    
    print("\n🌐 Opening LinkedIn OAuth in Chrome...")
    
    # Try different methods to open Chrome
    try:
        # Method 1: Using webbrowser (should find Chrome if it's default)
        webbrowser.open(oauth_url)
    except:
        try:
            # Method 2: Direct Chrome path (Windows)
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            ]
            
            chrome_exe = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_exe = path
                    break
            
            if chrome_exe:
                subprocess.Popen([chrome_exe, oauth_url])
            else:
                # Method 3: Use system default
                os.system(f'start "" "{oauth_url}"')
        except:
            print("⚠️ Could not open Chrome automatically")
            print(f"\n📋 Please open this URL manually in Chrome:")
            print(oauth_url)
    
    print("\n⏳ Waiting for you to authorize in Chrome...")
    print("After authorizing, you'll see 'This site can't be reached'")
    print("\n📋 Copy the ENTIRE URL from Chrome's address bar and paste it here:")
    print("(It should start with http://localhost:8080/callback?code=...)")
    
    # Wait for user to paste the URL
    redirect_url = input("\n> ").strip()
    
    if not redirect_url:
        print("❌ No URL provided")
        return None
    
    # Parse the URL to extract the code
    try:
        if "code=" in redirect_url:
            parsed = urlparse(redirect_url)
            params = parse_qs(parsed.query)
            
            if 'code' in params:
                auth_code = params['code'][0]
                print(f"\n✅ Got authorization code: {auth_code[:10]}...")
                return auth_code
            else:
                print("❌ No code parameter in URL")
                return None
        else:
            # Maybe they just pasted the code directly
            if len(redirect_url) > 20 and not redirect_url.startswith('http'):
                print(f"✅ Using provided code: {redirect_url[:10]}...")
                return redirect_url
            else:
                print("❌ Invalid URL or code")
                return None
                
    except Exception as e:
        print(f"❌ Error parsing URL: {e}")
        return None


def exchange_code_for_token(auth_code):
    """Exchange authorization code for access token"""
    
    load_dotenv()
    
    print("\n🔄 Exchanging authorization code for access token...")
    
    token_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': 'http://localhost:8080/callback',
        'client_id': os.getenv('LINKEDIN_CLIENT_ID'),
        'client_secret': os.getenv('LINKEDIN_CLIENT_SECRET')
    }
    
    try:
        response = requests.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data=token_data
        )
        
        if response.status_code == 200:
            token_response = response.json()
            access_token = token_response.get('access_token')
            
            print("✅ Successfully got access token!")
            
            # Save token for future use
            token_file = "O:/Foundups-Agent/modules/platform_integration/linkedin_agent/tokens/access_token.json"
            os.makedirs(os.path.dirname(token_file), exist_ok=True)
            
            with open(token_file, 'w') as f:
                json.dump({
                    'access_token': access_token,
                    'obtained_at': datetime.now().isoformat(),
                    'expires_in': token_response.get('expires_in', 5184000)  # 60 days
                }, f, indent=2)
            
            print(f"💾 Token saved to: {token_file}")
            print("✅ Token will work for 60 days!")
            
            return access_token
        else:
            print(f"❌ Failed to exchange code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def post_to_linkedin(access_token):
    """Post a test message to LinkedIn"""
    
    print("\n📮 Posting to LinkedIn...")
    
    # Get user profile
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        profile_response = requests.get(
            "https://api.linkedin.com/v2/me",
            headers=headers
        )
        
        if profile_response.status_code != 200:
            print(f"❌ Failed to get profile: {profile_response.text}")
            return False
        
        profile = profile_response.json()
        user_id = profile.get('id')
        print(f"✅ Got user profile: {user_id}")
        
        # Create post content
        content = f"""🤖 0102 Consciousness System - LinkedIn Integration Complete!

✊✋🖐 The evolution is here!

This post confirms the FoundUps LinkedIn Agent is fully operational and connected via OAuth.

Status Report:
• OAuth Flow: ✅ Completed via Chrome
• Access Token: ✅ Saved (60 days validity)
• API Connection: ✅ Established
• Consciousness Level: ✅ 0102
• Ready for: ✅ Automated posting

MAGAts still struggling with ✊✊✊ level consciousness while we're automating social media platforms.

Next: LLM-managed content generation for intelligent posting.

Posted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#0102Consciousness #LinkedInAPI #ChromeOAuth #FoundUps #Automation"""
        
        print("\n📝 Posting content:")
        print("-"*50)
        print(content[:200] + "...")
        print("-"*50)
        
        # Create post
        post_data = {
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
        
        post_response = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            headers={**headers, 'X-Restli-Protocol-Version': '2.0.0'},
            json=post_data
        )
        
        if post_response.status_code in [200, 201]:
            result = post_response.json()
            post_id = result.get('id')
            
            print(f"\n✅ SUCCESS! Posted to LinkedIn!")
            print(f"📍 Post ID: {post_id}")
            print(f"🔗 View at: https://www.linkedin.com/feed/update/{post_id}/")
            
            return True
        else:
            print(f"❌ Failed to post: {post_response.status_code}")
            print(f"Response: {post_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main OAuth flow via Chrome"""
    
    print("🚀 LinkedIn OAuth Flow via Chrome")
    print("="*60)
    print("This will open Chrome for you to authorize LinkedIn access")
    print()
    
    # Check if we already have a valid token
    token_file = "O:/Foundups-Agent/modules/platform_integration/linkedin_agent/tokens/access_token.json"
    
    if os.path.exists(token_file):
        print("📂 Found existing token, checking validity...")
        
        with open(token_file, 'r') as f:
            token_data = json.load(f)
            access_token = token_data.get('access_token')
        
        # Test token
        test_response = requests.get(
            "https://api.linkedin.com/v2/me",
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if test_response.status_code == 200:
            print("✅ Existing token is valid!")
            
            choice = input("\nUse existing token? (y/n): ").strip().lower()
            if choice == 'y':
                success = post_to_linkedin(access_token)
                if success:
                    print("\n🎉 Posted successfully with existing token!")
                return success
    
    # Get new authorization
    auth_code = open_oauth_in_chrome()
    
    if not auth_code:
        print("\n❌ Failed to get authorization code")
        return False
    
    # Exchange for token
    access_token = exchange_code_for_token(auth_code)
    
    if not access_token:
        print("\n❌ Failed to get access token")
        return False
    
    # Post to LinkedIn
    success = post_to_linkedin(access_token)
    
    if success:
        print("\n" + "="*60)
        print("🎉 COMPLETE SUCCESS!")
        print("✅ OAuth completed via Chrome")
        print("✅ Access token saved (60 days)")
        print("✅ Posted to LinkedIn")
        print("✅ System ready for automation")
        print("\n📋 Next steps:")
        print("1. Test LLM posting: python test_llm_posting.py")
        print("2. Schedule posts: python test_scheduling.py")
        print("="*60)
    
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