#!/usr/bin/env python3
"""
Test LinkedIn credentials and find the issue
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv('LINKEDIN_CLIENT_ID')
client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')

print("Testing LinkedIn Configuration")
print("="*60)
print(f"Client ID: {client_id}")
print(f"Client Secret: {client_secret[:20]}..." if client_secret else "MISSING")

# Test different redirect URIs
redirect_uris = [
    "http://localhost:3000/callback",
    "http://localhost:8080/callback", 
    "http://localhost/callback",
    "https://localhost:3000/callback",
    "http://127.0.0.1:3000/callback"
]

print("\nTesting OAuth URLs with different redirect URIs:")
print("-"*60)

for redirect_uri in redirect_uris:
    oauth_url = f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=w_member_social r_liteprofile"
    print(f"\n{redirect_uri}")
    print(f"URL: {oauth_url}")

print("\n" + "="*60)
print("Possible issues:")
print("1. The LinkedIn app might not exist with this client_id")
print("2. The app might be disabled or expired")
print("3. The redirect URI might not be registered in the app")
print("4. The client_id/secret might be incorrect")

print("\nTo fix this, you need to:")
print("1. Go to: https://www.linkedin.com/developers/apps")
print("2. Check if an app exists with client_id: 865rlrxtedx3ao")
print("3. If not, create a new LinkedIn app")
print("4. Add the redirect URI to the app settings")
print("5. Update the .env file with the correct credentials")

print("\nAlternatively, if you have a LinkedIn account that already works,")
print("just give me a valid access token and we can skip OAuth.")