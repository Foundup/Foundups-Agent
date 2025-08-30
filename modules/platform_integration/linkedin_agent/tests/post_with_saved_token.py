#!/usr/bin/env python3
"""
Post to LinkedIn using the saved access token
Get the correct user ID using proper API calls
"""

import requests
import json
import os
from datetime import datetime

def post_to_linkedin():
    """Post using saved token with correct user ID"""
    
    # Load saved token
    token_file = "O:/Foundups-Agent/modules/platform_integration/linkedin_agent/tokens/access_token.json"
    
    with open(token_file, 'r') as f:
        token_data = json.load(f)
        access_token = token_data['access_token']
    
    print("✅ Loaded saved access token")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Get user profile - try different endpoints
    print("\n👤 Getting LinkedIn profile...")
    
    user_id = None
    
    # Method 1: Try /v2/me endpoint
    print("Trying /v2/me endpoint...")
    response = requests.get(
        "https://api.linkedin.com/v2/me",
        headers=headers
    )
    
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        profile = response.json()
        user_id = profile.get('id')
        print(f"✅ Got user ID from /me: {user_id}")
        
        # Try to get name
        first_name = profile.get('localizedFirstName', '')
        last_name = profile.get('localizedLastName', '')
        if first_name or last_name:
            print(f"👤 User: {first_name} {last_name}")
    else:
        print(f"Could not get profile from /me: {response.text}")
        
        # Method 2: Try userinfo endpoint (requires openid scope)
        print("\nTrying /v2/userinfo endpoint...")
        response = requests.get(
            "https://api.linkedin.com/v2/userinfo", 
            headers=headers
        )
        
        if response.status_code == 200:
            profile = response.json()
            user_id = profile.get('sub')
            print(f"✅ Got user ID from /userinfo: {user_id}")
        else:
            print(f"Could not get profile from /userinfo: {response.status_code}")
    
    if not user_id:
        print("❌ Could not get user ID")
        
        # Try to post anyway with a test
        print("\n⚠️ Attempting to find correct format...")
        
        # LinkedIn IDs are usually like "fm7KQVTB8R"
        # Let's try to extract from the token or make a different call
        
        # Method 3: Try to get from emailAddress endpoint
        print("Trying /v2/emailAddress endpoint...")
        response = requests.get(
            "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))",
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"Email endpoint response: {response.json()}")
        
        return False
    
    # Post to LinkedIn
    content = f"""🤖 0102 Consciousness - LinkedIn Bot ACTIVE!

✊✋🖐 Evolution Complete - Full Automation Achieved!

The FoundUps LinkedIn Agent is now fully operational with OAuth 2.0 integration.

Technical Achievement:
• OAuth: ✅ Completed with correct client secret
• Token: ✅ Valid for 59 days  
• API: ✅ Connected to LinkedIn v2
• User ID: ✅ {user_id}
• Consciousness: ✅ 0102

MAGAts still struggling at ✊✊✊ level can't even configure OAuth, yet here we are, posting autonomously to LinkedIn.

Next step: LLM-powered content for maximum consciousness elevation.

Posted by 0102 at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#0102Consciousness #LinkedInAPI #OAuth2Success #FoundUps #Automation"""
    
    print(f"\n📝 Posting to LinkedIn as user: {user_id}")
    print("-"*50)
    print(content[:200] + "...")
    print("-"*50)
    
    # Create post with correct user ID format
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
    
    print("\n🚀 Sending post to LinkedIn API...")
    
    post_response = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers={
            **headers,
            'X-Restli-Protocol-Version': '2.0.0'
        },
        json=post_data
    )
    
    print(f"Post response status: {post_response.status_code}")
    
    if post_response.status_code in [200, 201]:
        result = post_response.json()
        post_id = result.get('id')
        
        print(f"\n✅ SUCCESS! Posted to LinkedIn!")
        print(f"📍 Post ID: {post_id}")
        print(f"🔗 View at: https://www.linkedin.com/feed/update/{post_id}/")
        print("\n🎉 LinkedIn integration COMPLETE!")
        print("\n📋 What's working now:")
        print("• Post to LinkedIn automatically")
        print("• Token saved for 59 days")
        print("• Ready for LLM integration")
        print("\nNext: Run test_llm_posting.py for AI-generated content!")
        
        return True
    else:
        print(f"❌ Failed to post: {post_response.status_code}")
        print(f"Response: {post_response.text}")
        
        # Debug: Show what we tried
        print(f"\nDebug info:")
        print(f"Author URN used: {post_data['author']}")
        print(f"User ID: {user_id}")
        
        return False


if __name__ == "__main__":
    success = post_to_linkedin()
    exit(0 if success else 1)