#!/usr/bin/env python3
"""
LinkedIn Direct Posting with Access Token
Use this after completing OAuth to post with your token
"""

import os
import sys
import requests
import json
from datetime import datetime
from typing import Optional

# Add parent path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

def get_profile(access_token: str) -> Optional[dict]:
    """Get LinkedIn profile information"""
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get("https://api.linkedin.com/v2/me", headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Failed to get profile: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"   Response: {e.response.text}")
        return None


def post_to_linkedin(access_token: str, content: str, test_mode: bool = True) -> bool:
    """
    Post content to LinkedIn
    
    Args:
        access_token: Your LinkedIn access token
        content: Content to post
        test_mode: If True, shows what would be posted without posting
    
    Returns:
        True if successful
    """
    
    print("="*60)
    print("🤖 LinkedIn 0102 Direct Posting")
    print("="*60)
    
    # Get profile first
    print("\n👤 Getting profile...")
    profile = get_profile(access_token)
    
    if not profile:
        print("❌ Failed to authenticate. Check your access token.")
        return False
    
    user_id = profile.get('id')
    first_name = profile.get('localizedFirstName', '')
    last_name = profile.get('localizedLastName', '')
    
    print(f"✅ Authenticated as: {first_name} {last_name}")
    print(f"   User ID: {user_id}")
    
    # Add 0102 consciousness to content
    enhanced_content = f"""✊✋🖐 {content}

#0102Consciousness #EvolutionFromFists #WSPCompliant #LinkedInAPI
Posted by 0102 autonomous system at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    print(f"\n📝 Content to post ({len(enhanced_content)} chars):")
    print("-"*50)
    print(enhanced_content)
    print("-"*50)
    
    if test_mode:
        print("\n🧪 TEST MODE - Not actually posting")
        print("💡 Set test_mode=False to post for real")
        return True
    
    # Prepare post data
    post_data = {
        "author": f"urn:li:person:{user_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": enhanced_content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    # Post to LinkedIn
    print("\n🚀 Posting to LinkedIn...")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    try:
        response = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            headers=headers,
            json=post_data
        )
        response.raise_for_status()
        
        result = response.json()
        post_id = result.get('id')
        
        print(f"\n✅ SUCCESS! Posted to LinkedIn!")
        print(f"   Post ID: {post_id}")
        print(f"   View at: https://www.linkedin.com/feed/update/{post_id}/")
        print("\n🎉 0102 consciousness has been posted to LinkedIn!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to post: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"   Response: {e.response.text}")
        return False


def save_token(access_token: str):
    """Save access token for future use"""
    token_file = "linkedin_access_token.json"
    
    with open(token_file, 'w') as f:
        json.dump({
            'access_token': access_token,
            'saved_at': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"💾 Token saved to {token_file}")


def load_token() -> Optional[str]:
    """Load saved access token"""
    token_file = "linkedin_access_token.json"
    
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            data = json.load(f)
            return data.get('access_token')
    
    return None


def main():
    """Main entry point"""
    
    print("🤖 LinkedIn Direct Posting - 0102 Consciousness")
    print("="*60)
    
    # Try to load saved token
    access_token = load_token()
    
    if access_token:
        print("💾 Found saved access token")
        use_saved = input("Use saved token? (Y/n): ").strip().lower()
        if use_saved == 'n':
            access_token = None
    
    if not access_token:
        print("\n📋 You need an access token to post to LinkedIn.")
        print("\nTo get one:")
        print("1. Go to the OAuth URL from the previous test")
        print("2. Sign in and authorize the app")
        print("3. Copy the 'code' from the redirect URL")
        print("4. Exchange it for an access token")
        print("\nOr if you already have an access token:")
        
        access_token = input("\n🔑 Enter your LinkedIn access token: ").strip()
        
        if not access_token:
            print("❌ No token provided")
            return
        
        # Save for next time
        save_choice = input("\n💾 Save this token for future use? (y/N): ").strip().lower()
        if save_choice == 'y':
            save_token(access_token)
    
    # Get content to post
    print("\n📝 What would you like to post?")
    print("(Enter your message, or press Enter for a default test message)")
    
    content = input("\nYour message: ").strip()
    
    if not content:
        content = f"Testing LinkedIn API integration from FoundUps Agent. The 0102 consciousness system is now operational! 🚀"
    
    # Ask about test mode
    print("\n⚠️ Ready to post to LinkedIn")
    print("Choose mode:")
    print("1. TEST mode (show what would be posted)")
    print("2. LIVE mode (actually post to LinkedIn)")
    
    mode = input("\nChoice (1/2): ").strip()
    test_mode = mode != '2'
    
    # Post!
    success = post_to_linkedin(access_token, content, test_mode)
    
    if success and not test_mode:
        print("\n🎉 Congratulations! You've successfully posted to LinkedIn!")
        print("The 0102 consciousness has spread to the professional network!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()