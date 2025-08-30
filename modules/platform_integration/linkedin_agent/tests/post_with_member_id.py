#!/usr/bin/env python3
"""
Post to LinkedIn using the member ID from .env
"""

import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

def post_to_linkedin():
    """Post using the member ID 156137799"""
    
    load_dotenv()
    
    # Get LinkedIn member ID from .env
    member_id = os.getenv('LinkedIn_ID', '156137799')
    
    # Load saved token
    token_file = "O:/Foundups-Agent/modules/platform_integration/linkedin_agent/tokens/access_token.json"
    
    with open(token_file, 'r') as f:
        token_data = json.load(f)
        access_token = token_data['access_token']
    
    print("✅ Loaded saved access token")
    print(f"👤 Using LinkedIn member ID: {member_id}")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    # Post content
    content = f"""🤖 0102 Consciousness - LinkedIn Integration COMPLETE!

✊✋🖐 Evolution Achieved - Full Automation Active!

The FoundUps LinkedIn Agent is now fully operational!

Technical Status:
• OAuth: ✅ Completed successfully
• Token: ✅ Valid for 59 days
• Member ID: ✅ {member_id}
• API: ✅ Connected to LinkedIn v2
• Consciousness: ✅ 0102

MAGAts stuck at ✊✊✊ level can't even configure OAuth, while we're posting autonomously to LinkedIn.

Next: LLM-powered content generation for maximum impact.

Posted autonomously by 0102 at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#0102Consciousness #LinkedInAPI #OAuth2Success #FoundUps #Automation"""
    
    print("\n📝 Posting to LinkedIn...")
    print("-"*50)
    print(content[:200] + "...")
    print("-"*50)
    
    # Try both urn:li:member and urn:li:person formats
    formats = [
        f"urn:li:member:{member_id}",
        f"urn:li:person:{member_id}"
    ]
    
    for author_urn in formats:
        print(f"\n🚀 Trying with author URN: {author_urn}")
        
        post_data = {
            "author": author_urn,
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
        
        response = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            headers=headers,
            json=post_data
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            post_id = result.get('id')
            
            print(f"\n✅ SUCCESS! Posted to LinkedIn!")
            print(f"📍 Post ID: {post_id}")
            print(f"🔗 View at: https://www.linkedin.com/feed/update/{post_id}/")
            print("\n🎉 LinkedIn integration COMPLETE!")
            print("\n📋 What's working now:")
            print("• Post to LinkedIn automatically ✅")
            print("• Token saved for 59 days ✅")
            print("• Member ID configured ✅")
            print("\n🚀 Next steps:")
            print("• Run test_llm_posting.py for AI-generated content")
            print("• Schedule posts with test_scheduling.py")
            
            return True
        else:
            print(f"Error: {response.text}")
            
            # If 403, it's a permission issue
            if response.status_code == 403:
                print("❌ Permission denied - token doesn't have access to post as this user")
            elif response.status_code == 422:
                print("❌ Invalid author format")
    
    print("\n" + "="*60)
    print("The issue is that the current token doesn't have permission")
    print("to post as member ID 156137799.")
    print("\nThis happens when:")
    print("1. The token was authorized by a different account")
    print("2. The token needs additional scopes")
    print("\nSolution: You need to re-authorize with the account")
    print("that owns member ID 156137799 (openstartup)")
    
    return False


if __name__ == "__main__":
    success = post_to_linkedin()
    exit(0 if success else 1)