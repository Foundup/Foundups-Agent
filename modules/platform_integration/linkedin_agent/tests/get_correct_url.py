#!/usr/bin/env python3
"""
Get correct LinkedIn OAuth URL
"""

import os
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv('LINKEDIN_CLIENT_ID')
print(f"Client ID from .env: '{client_id}'")
print(f"Length: {len(client_id)}")
print(f"Last char ASCII: {ord(client_id[-1]) if client_id else 'N/A'}")

# Clean the client_id of any hidden characters
client_id_clean = client_id.strip().replace('^', '') if client_id else ''
print(f"\nCleaned Client ID: '{client_id_clean}'")

# Build clean URL
redirect_uri = "http://localhost:8080/callback"
scope = "w_member_social r_liteprofile"

url = f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={client_id_clean}&redirect_uri={redirect_uri}&scope={scope}&state=0102"

print("\n" + "="*60)
print("CLEAN LinkedIn OAuth URL:")
print("="*60)
print(url)
print("="*60)
print("\nCopy and paste this URL into Chrome.")