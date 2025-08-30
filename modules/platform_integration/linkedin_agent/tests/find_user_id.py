#!/usr/bin/env python3
"""
Find the correct LinkedIn user ID using the current token
Try different API approaches
"""

import requests
import json
import os

def find_user_id():
    """Try different methods to get LinkedIn user ID"""
    
    # Load saved token
    token_file = "O:/Foundups-Agent/modules/platform_integration/linkedin_agent/tokens/access_token.json"
    
    with open(token_file, 'r') as f:
        token_data = json.load(f)
        access_token = token_data['access_token']
    
    print("✅ Loaded saved access token")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    print("\n🔍 Finding user ID with current permissions...")
    
    # Method 1: Try me endpoint with lite projection
    print("\n1. Trying /v2/me with projection=id...")
    response = requests.get(
        "https://api.linkedin.com/v2/me?projection=(id)",
        headers=headers
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Response: {data}")
        if 'id' in data:
            return data['id']
    
    # Method 2: Try without version
    print("\n2. Trying /me without version...")
    response = requests.get(
        "https://api.linkedin.com/me",
        headers=headers
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Response: {data}")
    
    # Method 3: Try to post with a test ID and see error message
    print("\n3. Trying test post to get correct ID format from error...")
    
    test_post = {
        "author": "urn:li:person:test123",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": "Test post"
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
        json=test_post
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code != 201:
        error = response.text
        print(f"   Error: {error}")
        
        # Sometimes the error message reveals the correct user ID format
        if "does not match" in error:
            print("   The error shows we need format: urn:li:person:XXXXX or urn:li:member:XXXXX")
    
    # Method 4: Try shares endpoint (older API)
    print("\n4. Trying /v1/people/~ endpoint...")
    response = requests.get(
        "https://api.linkedin.com/v1/people/~:(id)?format=json",
        headers={'Authorization': f'Bearer {access_token}'}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Response: {data}")
    
    # Method 5: Check if we can use organization ID instead
    print("\n5. Trying organizations endpoint...")
    response = requests.get(
        "https://api.linkedin.com/v2/organizationalEntityAcls?q=roleAssignee",
        headers=headers
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Response: {data}")
    
    print("\n" + "="*60)
    print("Summary:")
    print("The token has 'w_member_social' scope which allows posting")
    print("but not profile access. We need one of these:")
    print("1. Re-authorize with 'profile' or 'r_liteprofile' scope")
    print("2. Use a hardcoded user ID if you know it")
    print("3. Use the organization posting API instead")
    
    return None


def try_hardcoded_post():
    """Try posting with common ID patterns"""
    
    # Load token
    token_file = "O:/Foundups-Agent/modules/platform_integration/linkedin_agent/tokens/access_token.json"
    
    with open(token_file, 'r') as f:
        token_data = json.load(f)
        access_token = token_data['access_token']
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    print("\n🔧 Attempting workaround...")
    print("Since we can't get user ID with current scope,")
    print("you have two options:")
    print("\n1. Re-authorize with profile scope (recommended)")
    print("2. Find your LinkedIn user ID manually:")
    print("   - Go to your LinkedIn profile")
    print("   - Look at the URL")
    print("   - Your ID might be in the URL or page source")
    print("\nOr we can try posting without user ID...")
    
    # Try posting without author field (might default to token owner)
    print("\n📝 Attempting to post without explicit author...")
    
    content = "🤖 0102 Test Post - LinkedIn API Working!"
    
    post_data = {
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
        print("✅ Success! Posted without explicit author!")
        return True
    else:
        print(f"Error: {response.text}")
        return False


if __name__ == "__main__":
    user_id = find_user_id()
    
    if not user_id:
        print("\n❌ Could not find user ID with current permissions")
        try_hardcoded_post()
    else:
        print(f"\n✅ Found user ID: {user_id}")