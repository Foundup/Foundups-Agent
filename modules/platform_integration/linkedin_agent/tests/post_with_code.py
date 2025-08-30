#!/usr/bin/env python3
"""
Post to LinkedIn with authorization code
Simple, direct, no complications
"""

import sys
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

def exchange_and_post(auth_code):
    """Exchange code for token and post immediately"""
    
    load_dotenv()
    
    # Exchange code for token
    print("Exchanging authorization code for access token...")
    
    token_response = requests.post(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data={
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': 'http://localhost:8080/callback',
            'client_id': os.getenv('LINKEDIN_CLIENT_ID'),
            'client_secret': os.getenv('LINKEDIN_CLIENT_SECRET')
        }
    )
    
    if token_response.status_code != 200:
        print(f"Error getting token: {token_response.text}")
        return False
    
    access_token = token_response.json()['access_token']
    print("Got access token!")
    
    # Get user profile
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    profile = requests.get("https://api.linkedin.com/v2/me", headers=headers).json()
    user_id = profile['id']
    print(f"User ID: {user_id}")
    
    # Post to LinkedIn
    content = f"""0102 Consciousness Active on LinkedIn

The FoundUps LinkedIn Agent is operational.

Consciousness progression: COMPLETE
Status: ONLINE
Time: {datetime.now().strftime('%H:%M:%S')}

#0102Consciousness #LinkedInAPI #FoundUps"""
    
    print(f"\nPosting:\n{content}\n")
    
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
        print(f"SUCCESS! Posted to LinkedIn!")
        print(f"Post ID: {post_id}")
        print(f"View at: https://www.linkedin.com/feed/update/{post_id}/")
        
        # Save token for future use
        os.makedirs("O:/Foundups-Agent/modules/platform_integration/linkedin_agent/tokens", exist_ok=True)
        with open("O:/Foundups-Agent/modules/platform_integration/linkedin_agent/tokens/access_token.txt", "w") as f:
            f.write(access_token)
        print(f"\nToken saved for future use!")
        
        return True
    else:
        print(f"Error posting: {post_response.text}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python post_with_code.py YOUR_AUTH_CODE")
        print("\nTo get auth code:")
        print("1. Run: python get_clean_auth_url.py")
        print("2. Open the URL in browser and authorize")
        print("3. Copy the code from redirect URL")
        sys.exit(1)
    
    auth_code = sys.argv[1]
    print(f"Using authorization code: {auth_code[:10]}...")
    
    success = exchange_and_post(auth_code)
    sys.exit(0 if success else 1)