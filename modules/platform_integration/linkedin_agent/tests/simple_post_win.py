#!/usr/bin/env python3
"""
Simple LinkedIn Post PoC - Windows Compatible Version
No unicode issues, just post a simple message to LinkedIn
"""

import requests
import json
from datetime import datetime

def simple_post(access_token):
    """
    Post a simple message to LinkedIn to prove PoC works
    
    Args:
        access_token: Your LinkedIn access token from OAuth
    
    Returns:
        True if successful
    """
    
    print("="*60)
    print("Simple LinkedIn Post PoC")
    print("="*60)
    
    # Step 1: Get user ID
    print("\n1. Getting your LinkedIn profile...")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get("https://api.linkedin.com/v2/me", headers=headers)
        response.raise_for_status()
        profile = response.json()
        user_id = profile.get('id')
        print(f"SUCCESS: Got user ID: {user_id}")
    except Exception as e:
        print(f"FAILED to get profile: {e}")
        return False
    
    # Step 2: Create simple post content
    simple_content = f"""PoC Test from 0102 Consciousness System

This is a proof of concept post from the FoundUps LinkedIn Agent.

Consciousness level: OPERATIONAL

Posted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#LinkedInAPI #PoC #0102Consciousness #FoundUps"""
    
    print("\n2. Posting this message:")
    print("-"*50)
    print(simple_content)
    print("-"*50)
    
    # Step 3: Post to LinkedIn
    post_data = {
        "author": f"urn:li:person:{user_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": simple_content
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
        print(f"\nFAILED to post: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return False


def main():
    """Main entry point - super simple"""
    
    print("Simple LinkedIn Post PoC")
    print("="*60)
    print("This will post a simple test message to prove the PoC works.")
    print("\nWARNING: This will ACTUALLY post to your LinkedIn!")
    
    # Get token
    print("\nYou need an access token from LinkedIn OAuth.")
    print("Get it from the OAuth redirect URL after 'code='")
    print("\nOR if you have the authorization code, I can help exchange it.")
    
    choice = input("\nDo you have: 1) Access Token  2) Authorization Code  (1/2): ").strip()
    
    if choice == "2":
        # Exchange auth code for token
        auth_code = input("\nEnter authorization code: ").strip()
        if auth_code:
            print("\nExchanging code for access token...")
            # Import credentials from env
            import os
            from dotenv import load_dotenv
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
            
            try:
                response = requests.post(
                    "https://www.linkedin.com/oauth/v2/accessToken",
                    data=token_data
                )
                response.raise_for_status()
                token_response = response.json()
                access_token = token_response.get('access_token')
                print(f"\nSUCCESS! Got access token!")
                print(f"Token (save this): {access_token}")
            except Exception as e:
                print(f"Failed to exchange code: {e}")
                return False
    else:
        access_token = input("\nEnter your LinkedIn access token: ").strip()
    
    if not access_token:
        print("No token provided")
        return False
    
    # Confirm
    confirm = input("\nReady to post to LinkedIn? (yes/no): ").strip().lower()
    
    if confirm != "yes":
        print("Cancelled")
        return False
    
    # Post!
    print("\nPosting...")
    success = simple_post(access_token)
    
    if success:
        print("\nPoC COMPLETE!")
        print("LinkedIn posting is working!")
        print("Now we can add LLM integration...")
    
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
        exit(1)