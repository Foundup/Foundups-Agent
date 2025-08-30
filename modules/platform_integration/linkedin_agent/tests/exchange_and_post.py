#!/usr/bin/env python3
"""
Exchange LinkedIn auth code for token and post
Direct script - no interactive prompts
"""

import requests
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

def exchange_code_for_token(auth_code):
    """Exchange authorization code for access token"""
    
    load_dotenv()
    client_id = os.getenv('LINKEDIN_CLIENT_ID')
    client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
    
    token_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': 'http://localhost:8080/callback',
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    print("Exchanging authorization code for access token...")
    
    try:
        response = requests.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data=token_data
        )
        response.raise_for_status()
        token_response = response.json()
        access_token = token_response.get('access_token')
        print(f"SUCCESS! Got access token!")
        print(f"Token (save this): {access_token}")
        return access_token
    except Exception as e:
        print(f"Failed to exchange code: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return None


def post_to_linkedin(access_token):
    """Post a simple message to LinkedIn"""
    
    print("\n" + "="*60)
    print("Posting to LinkedIn")
    print("="*60)
    
    # Get user profile
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    print("\n1. Getting LinkedIn profile...")
    try:
        response = requests.get("https://api.linkedin.com/v2/me", headers=headers)
        response.raise_for_status()
        profile = response.json()
        user_id = profile.get('id')
        print(f"Got user ID: {user_id}")
    except Exception as e:
        print(f"Failed to get profile: {e}")
        return False
    
    # Create post content
    content = f"""PoC Test from 0102 Consciousness System

This is a proof of concept post from the FoundUps LinkedIn Agent.

Consciousness level: OPERATIONAL

Posted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#LinkedInAPI #PoC #0102Consciousness #FoundUps"""
    
    print("\n2. Posting this message:")
    print("-"*50)
    print(content)
    print("-"*50)
    
    # Post to LinkedIn
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
    
    print("\n3. Sending to LinkedIn API...")
    
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
        
        print("\nSUCCESS! Posted to LinkedIn!")
        print(f"Post ID: {post_id}")
        print(f"View at: https://www.linkedin.com/feed/update/{post_id}/")
        print("\nPoC PROVEN - LinkedIn posting works!")
        return True
        
    except Exception as e:
        print(f"\nFailed to post: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return False


def main():
    """Main entry point"""
    
    print("LinkedIn Authorization Code Exchange & Post")
    print("="*60)
    
    if len(sys.argv) > 1:
        # Auth code provided as argument
        auth_code = sys.argv[1]
        print(f"Using provided authorization code: {auth_code[:10]}...")
    else:
        print("\nUsage: python exchange_and_post.py [authorization_code]")
        print("\nTo get authorization code:")
        print("1. Run: python get_linkedin_auth_url.py")
        print("2. Open the URL in your browser")
        print("3. Authorize the app")
        print("4. Copy the code from the redirect URL")
        print("5. Run: python exchange_and_post.py YOUR_CODE_HERE")
        return False
    
    # Exchange code for token
    access_token = exchange_code_for_token(auth_code)
    
    if not access_token:
        print("\nFailed to get access token")
        return False
    
    # Post to LinkedIn
    print("\nReady to post to LinkedIn with the access token...")
    success = post_to_linkedin(access_token)
    
    if success:
        print("\n" + "="*60)
        print("COMPLETE SUCCESS!")
        print("LinkedIn OAuth flow and posting verified!")
        print("Next step: Add LLM content generation")
        print("="*60)
    
    return success


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