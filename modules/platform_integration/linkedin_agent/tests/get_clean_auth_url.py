#!/usr/bin/env python3
"""
Get clean LinkedIn OAuth URL without duplicates
"""

import os
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

# Build clean OAuth URL
params = {
    'response_type': 'code',
    'client_id': os.getenv('LINKEDIN_CLIENT_ID'),
    'redirect_uri': 'http://localhost:8080/callback',
    'scope': 'w_member_social r_liteprofile',
    'state': '0102consciousness'  # Optional state parameter for security
}

base_url = "https://www.linkedin.com/oauth/v2/authorization"
auth_url = f"{base_url}?{urlencode(params)}"

print("="*60)
print("LinkedIn OAuth URL (Clean)")
print("="*60)
print("\nOpen this URL in your browser:")
print("-"*60)
print(auth_url)
print("-"*60)
print("\nAfter authorizing, copy the 'code' parameter from the redirect URL")