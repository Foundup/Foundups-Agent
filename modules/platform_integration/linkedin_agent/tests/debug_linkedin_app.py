#!/usr/bin/env python3
"""
Debug LinkedIn app issues
Check if the app (Client ID: 865rlrxtedx3ao) has proper permissions
"""

import requests
import json
import os
from dotenv import load_dotenv

def debug_app_permissions():
    """Debug why the app can't post"""
    
    load_dotenv()
    
    client_id = os.getenv('LINKEDIN_CLIENT_ID', '865rlrxtedx3ao')
    client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
    member_id = os.getenv('LinkedIn_ID', '156137799')
    
    print("🔍 LinkedIn App Debugging")
    print("="*60)
    print(f"Client ID: {client_id}")
    print(f"Member ID: {member_id}")
    
    # Load token
    token_file = "O:/Foundups-Agent/modules/platform_integration/linkedin_agent/tokens/access_token.json"
    
    with open(token_file, 'r') as f:
        token_data = json.load(f)
        access_token = token_data['access_token']
    
    print("✅ Token loaded")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    print("\n📋 Checking app capabilities...")
    
    # Check token introspection (what permissions it has)
    print("\n1. Token permissions check...")
    introspect_response = requests.post(
        "https://www.linkedin.com/oauth/v2/introspectToken",
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data={
            'token': access_token,
            'client_id': client_id,
            'client_secret': client_secret
        }
    )
    
    if introspect_response.status_code == 200:
        token_info = introspect_response.json()
        print(f"   Token active: {token_info.get('active')}")
        print(f"   Scope: {token_info.get('scope')}")
        print(f"   Expires in: {token_info.get('expires_in')} seconds")
        print(f"   Authorized at: {token_info.get('authorized_at')}")
    else:
        print(f"   Could not introspect token: {introspect_response.status_code}")
    
    # Check what member the token belongs to
    print("\n2. Checking token owner...")
    
    # Try different endpoints to identify the token owner
    endpoints = [
        ("/v2/me?projection=(id)", "Profile ID check"),
        ("/v2/userinfo", "UserInfo check"),
    ]
    
    for endpoint, description in endpoints:
        print(f"\n   Trying {description}...")
        response = requests.get(
            f"https://api.linkedin.com{endpoint}",
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            
            # Check if this matches our target member ID
            found_id = data.get('id') or data.get('sub')
            if found_id:
                if str(found_id) == str(member_id):
                    print(f"   ✅ Token belongs to correct member!")
                else:
                    print(f"   ❌ Token belongs to different member: {found_id}")
                    print(f"      Expected: {member_id}")
    
    print("\n3. Checking app verification status...")
    print("   LinkedIn apps need to be verified for production use")
    print("   Unverified apps have limitations:")
    print("   • Can only post from developer's account")
    print("   • Rate limits are lower")
    print("   • Some features are restricted")
    
    print("\n" + "="*60)
    print("DIAGNOSIS:")
    print("-"*60)
    
    print("\n🔴 Possible issues:")
    print("1. App not verified - can only post from app owner's account")
    print("2. Token belongs to different LinkedIn account than 'openstartup'")
    print("3. App needs LinkedIn verification for production use")
    
    print("\n🟢 Solutions:")
    print("1. Use the LinkedIn account that created the app")
    print("2. Verify the app in LinkedIn Developer settings")
    print("3. Create a new LinkedIn app with the 'openstartup' account")
    
    print("\n📋 To check app ownership:")
    print("1. Go to: https://www.linkedin.com/developers/apps")
    print("2. Sign in as 'openstartup'") 
    print("3. Check if app '865rlrxtedx3ao' appears in your apps")
    print("4. If not, the app belongs to a different account")
    
    return False


if __name__ == "__main__":
    debug_app_permissions()