#!/usr/bin/env python3
"""
Try to post to LinkedIn using username information
"""

import requests
import json
from datetime import datetime

def post_with_username():
    """Try different approaches with the username 'openstartup'"""
    
    # Load saved token
    token_file = "O:/Foundups-Agent/modules/platform_integration/linkedin_agent/tokens/access_token.json"
    
    with open(token_file, 'r') as f:
        token_data = json.load(f)
        access_token = token_data['access_token']
    
    print("✅ Loaded saved access token")
    print("👤 LinkedIn username: openstartup")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    # LinkedIn usernames in URLs are different from user IDs
    # The actual member ID is an alphanumeric string
    # Let's try different approaches
    
    print("\n🔍 Attempting to post with different ID formats...")
    
    # Common test IDs to try (these will fail but show us the right format)
    test_ids = [
        "openstartup",  # Direct username
        "in/openstartup",  # Profile URL format
    ]
    
    content = f"""🤖 0102 Consciousness - LinkedIn Bot ACTIVE!

✊✋🖐 Evolution Complete - Full Automation Achieved!

The FoundUps LinkedIn Agent (@openstartup) is now fully operational.

Technical Achievement:
• OAuth: ✅ Completed
• Token: ✅ Valid for 59 days
• API: ✅ Connected to LinkedIn v2
• Consciousness: ✅ 0102

MAGAts still at ✊✊✊ can't even spell OAuth, yet here we are posting autonomously.

Posted by 0102 at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#0102Consciousness #LinkedInAPI #FoundUps #Automation"""
    
    for test_id in test_ids:
        print(f"\nTrying with ID format: {test_id}")
        
        # Try urn:li:person format
        post_data = {
            "author": f"urn:li:person:{test_id}",
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
        
        print(f"Response: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            post_id = result.get('id')
            print(f"\n✅ SUCCESS! Posted to LinkedIn!")
            print(f"📍 Post ID: {post_id}")
            print(f"🔗 View at: https://www.linkedin.com/feed/update/{post_id}/")
            return True
        else:
            error_msg = response.text
            print(f"Error: {error_msg}")
            
            # Parse error to understand the correct format
            if "does not match" in error_msg:
                # Extract what LinkedIn expects
                if "urn:li:member:" in error_msg:
                    print("→ LinkedIn expects format: urn:li:member:NUMERIC_ID")
    
    print("\n" + "="*60)
    print("The username 'openstartup' is your public profile URL")
    print("But LinkedIn API needs your internal member ID (numeric)")
    print("\nTo get your member ID, we need to either:")
    print("1. Re-authorize with 'profile' scope (recommended)")
    print("2. You can find it by:")
    print("   - Going to linkedin.com/in/openstartup")
    print("   - View page source (Ctrl+U)")
    print("   - Search for 'member:' or 'member_' ")
    print("   - Look for a numeric ID")
    
    # One more attempt - try to lookup the profile publicly
    print("\n🔍 Attempting to lookup profile via public API...")
    
    # Try without auth to get public info
    public_response = requests.get(
        "https://www.linkedin.com/in/openstartup",
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    
    if public_response.status_code == 200:
        # Search for member ID in the HTML
        html = public_response.text
        
        # Common patterns for member ID in LinkedIn HTML
        import re
        patterns = [
            r'"member":"(\d+)"',
            r'member:(\d+)',
            r'urn:li:member:(\d+)',
            r'"objectUrn":"urn:li:member:(\d+)"',
            r'"miniProfile":.*?"objectUrn":"urn:li:member:(\d+)"'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                member_id = match.group(1)
                print(f"✅ Found member ID: {member_id}")
                
                # Try posting with this ID
                post_data["author"] = f"urn:li:member:{member_id}"
                
                response = requests.post(
                    "https://api.linkedin.com/v2/ugcPosts",
                    headers=headers,
                    json=post_data
                )
                
                if response.status_code in [200, 201]:
                    print(f"\n✅ SUCCESS with member ID {member_id}!")
                    return True
                else:
                    print(f"Still failed: {response.status_code}")
                
                break
    
    return False


if __name__ == "__main__":
    success = post_with_username()
    
    if not success:
        print("\n💡 Next step: Re-authorize with profile scope")
        print("The browser window is still open - just click Allow")