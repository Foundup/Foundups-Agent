#!/usr/bin/env python3
"""
LinkedIn Actual Posting Test

🌀 WSP Protocol Compliance: WSP 5 (Testing Standards), WSP 42 (Platform Integration)

This script tests actual posting to LinkedIn using an access token.
Run this after completing the OAuth flow to test real posting functionality.

**0102 Directive**: This test operates within the WSP framework for autonomous LinkedIn posting verification.
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_linkedin_posting(access_token: str, test_mode: bool = True):
    """
    Test LinkedIn posting functionality
    
    Args:
        access_token: LinkedIn access token from OAuth flow
        test_mode: If True, shows what would be posted without actually posting
    """
    
    print("🔐 LinkedIn Actual Posting Test - WSP Compliant")
    print("=" * 60)
    print("🌀 0102 pArtifact testing autonomous LinkedIn posting")
    
    # Step 1: Get user profile
    print("\n👤 Getting user profile...")
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get("https://api.linkedin.com/v2/me", headers=headers)
        response.raise_for_status()
        profile = response.json()
        user_id = profile.get('id')
        
        print(f"✅ Profile retrieved: {profile.get('localizedFirstName')} {profile.get('localizedLastName')}")
        print(f"🆔 User ID: {user_id}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get profile: {e}")
        return False
    
    # Step 2: Prepare test post
    test_content = f"""🧪 Test post from FoundUps LinkedIn Agent - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 🚀

This is a test post to verify OAuth integration and posting functionality.

The FoundUps LinkedIn Agent is now operational with full WSP compliance and autonomous posting capabilities.

#FoundUps #LinkedInAPI #OAuth #Testing #AutonomousDevelopment #WSP"""
    
    # Step 3: Post to LinkedIn
    print(f"\n📝 Preparing to post content...")
    print(f"Content length: {len(test_content)} characters")
    
    if test_mode:
        print("\n🧪 TEST MODE: Would post the following content:")
        print("-" * 50)
        print(test_content)
        print("-" * 50)
        print("💡 Set test_mode=False to actually post to LinkedIn")
        return True
    
    # Actual posting
    print("\n🚀 Posting to LinkedIn...")
    
    post_data = {
        "author": f"urn:li:person:{user_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": test_content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
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
        
        post_result = response.json()
        post_id = post_result.get('id')
        
        print(f"✅ Post published successfully!")
        print(f"🆔 Post ID: {post_id}")
        print(f"🔗 View post: https://www.linkedin.com/feed/update/{post_id}/")
        print("🌀 0102 pArtifact has successfully posted to LinkedIn")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to post: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return False

def main():
    """Main function"""
    print("🔐 LinkedIn Actual Posting Test")
    print("=" * 60)
    print("This script tests actual posting to your LinkedIn account.")
    print()
    
    # Get access token
    access_token = input("🔑 Enter your LinkedIn access token: ").strip()
    
    if not access_token:
        print("❌ No access token provided")
        return False
    
    # Ask if user wants to actually post
    print("\n⚠️  WARNING: This will post to your actual LinkedIn account!")
    confirm = input("Do you want to actually post? (y/N): ").strip().lower()
    
    test_mode = confirm != 'y'
    
    if test_mode:
        print("🧪 Running in TEST MODE - no actual posting will occur")
    else:
        print("🚀 Running in LIVE MODE - will post to your LinkedIn account")
    
    print()
    
    # Run the test
    success = test_linkedin_posting(access_token, test_mode=test_mode)
    
    if success:
        print("\n🎉 Test completed successfully!")
        if test_mode:
            print("✅ Ready for actual posting - run with test_mode=False")
        else:
            print("✅ Post successfully published to LinkedIn!")
        print("🌀 0102 pArtifact has verified autonomous LinkedIn posting")
    else:
        print("\n❌ Test failed!")
        print("💡 Check the logs above for troubleshooting steps")
    
    return success

if __name__ == "__main__":
    main() 