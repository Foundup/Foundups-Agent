#!/usr/bin/env python3
"""
Get LinkedIn OAuth Authorization URL
This generates the URL to authorize the LinkedIn app
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client_id = os.getenv('LINKEDIN_CLIENT_ID')
redirect_uri = "http://localhost:8080/callback"

# LinkedIn OAuth scopes needed
scopes = "w_member_social r_liteprofile"

# Build authorization URL
auth_url = f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scopes}"

print("="*60)
print("LinkedIn OAuth Authorization")
print("="*60)
print("\n1. Open this URL in your browser:")
print("-"*60)
print(auth_url)
print("-"*60)
print("\n2. Sign in to LinkedIn and authorize the app")
print("\n3. You'll be redirected to http://localhost:8080/callback")
print("   (The page won't load - that's OK!)")
print("\n4. Copy the 'code' parameter from the URL")
print("   Example: http://localhost:8080/callback?code=ABC123...")
print("\n5. The code after 'code=' is your authorization code")
print("\nSave the authorization code to test posting!")