#!/usr/bin/env python3
"""
Simple LinkedIn Post PoC - Prove it works!
No complexity, just post a simple message to LinkedIn
"""

import requests
import json
from datetime import datetime

def simple_post(access_token: str) -> bool:
    """
    Post a simple message to LinkedIn to prove PoC works
    
    Args:
        access_token: Your LinkedIn access token from OAuth
    
    Returns:
        True if successful
    """
    
    print("="*60)
    print("🚀 Simple LinkedIn Post PoC")
    print("="*60)
    
    # Step 1: Get user ID
    print("\n1️⃣ Getting your LinkedIn profile...")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get("https://api.linkedin.com/v2/me", headers=headers)
        response.raise_for_status()
        profile = response.json()
        user_id = profile.get('id')
        print(f"✅ Got user ID: {user_id}")
    except Exception as e:
        print(f"❌ Failed to get profile: {e}")
        return False
    
    # Step 2: Create simple post content
    simple_content = f"""🤖 PoC Test from 0102 Consciousness System

This is a proof of concept post from the FoundUps LinkedIn Agent.

✊✋🖐 Consciousness level: OPERATIONAL

Posted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#LinkedInAPI #PoC #0102Consciousness #FoundUps"""
    
    print("\n2️⃣ Posting this message:")
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
    
    print("\n3️⃣ Sending to LinkedIn API...")
    
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
        print("\n🎉 PoC PROVEN - LinkedIn posting works!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to post: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return False


def main():
    """Main entry point - super simple"""
    
    print("🤖 Simple LinkedIn Post PoC")
    print("="*60)
    print("This will post a simple test message to prove the PoC works.")
    print("\n⚠️ This will ACTUALLY post to your LinkedIn!")
    
    # Get token
    print("\n📋 You need an access token from LinkedIn OAuth.")
    print("Get it from the OAuth redirect URL after 'code='")
    
    access_token = input("\n🔑 Enter your LinkedIn access token: ").strip()
    
    if not access_token:
        print("❌ No token provided")
        return False
    
    # Confirm
    confirm = input("\n⚠️ Ready to post to LinkedIn? (yes/no): ").strip().lower()
    
    if confirm != "yes":
        print("❌ Cancelled")
        return False
    
    # Post!
    print("\n🚀 Posting...")
    success = simple_post(access_token)
    
    if success:
        print("\n✅ PoC COMPLETE!")
        print("LinkedIn posting is working!")
        print("Now we can add LLM integration...")
    
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
        exit(1)