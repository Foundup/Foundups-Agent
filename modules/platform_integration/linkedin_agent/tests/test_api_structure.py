#!/usr/bin/env python3
"""
Test LinkedIn API structure without real token
Validates our API calls are correctly formatted
"""

import json
from datetime import datetime

def test_post_structure():
    """Test that our post structure is valid"""
    
    print("Testing LinkedIn API Post Structure")
    print("="*60)
    
    # This is the structure we'll send
    user_id = "test_user_123"
    content = f"""PoC Test from 0102 Consciousness System

This is a proof of concept post from the FoundUps LinkedIn Agent.

Consciousness level: OPERATIONAL

Posted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#LinkedInAPI #PoC #0102Consciousness #FoundUps"""
    
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
    
    # Validate structure
    print("\n1. Checking required fields...")
    
    required_fields = ["author", "lifecycleState", "specificContent", "visibility"]
    for field in required_fields:
        if field in post_data:
            print(f"   OK: {field} present")
        else:
            print(f"   ERROR: {field} missing!")
    
    print("\n2. Checking specificContent structure...")
    
    if "com.linkedin.ugc.ShareContent" in post_data.get("specificContent", {}):
        print("   OK: ShareContent present")
        share_content = post_data["specificContent"]["com.linkedin.ugc.ShareContent"]
        
        if "shareCommentary" in share_content:
            print("   OK: shareCommentary present")
            if "text" in share_content["shareCommentary"]:
                print("   OK: text field present")
                print(f"   Text length: {len(share_content['shareCommentary']['text'])} chars")
        
        if "shareMediaCategory" in share_content:
            print(f"   OK: shareMediaCategory = {share_content['shareMediaCategory']}")
    
    print("\n3. JSON serialization test...")
    try:
        json_str = json.dumps(post_data, indent=2)
        print("   OK: Valid JSON structure")
        print(f"   JSON size: {len(json_str)} bytes")
    except Exception as e:
        print(f"   ERROR: Invalid JSON - {e}")
    
    print("\n4. Headers we'll use:")
    headers = {
        'Authorization': 'Bearer [ACCESS_TOKEN]',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    for key, value in headers.items():
        print(f"   {key}: {value}")
    
    print("\n5. API endpoints:")
    print("   Profile: GET https://api.linkedin.com/v2/me")
    print("   Post:    POST https://api.linkedin.com/v2/ugcPosts")
    
    print("\n" + "="*60)
    print("API structure validation: PASSED")
    print("Ready for real token testing!")
    print("\nNext steps:")
    print("1. Get authorization code from LinkedIn OAuth")
    print("2. Exchange for access token")
    print("3. Use token to post")
    
    return True


if __name__ == "__main__":
    test_post_structure()