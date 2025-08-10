#!/usr/bin/env python3
"""
Refresh OAuth tokens using refresh_token without browser authentication.
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, '.')

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = [
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.readonly"
]

CREDENTIALS_DIR = "credentials"
TOKEN_FILES = [
    "oauth_token.json",
    "oauth_token2.json",
    "oauth_token3.json", 
    "oauth_token4.json"
]

def refresh_token(token_file):
    """Refresh OAuth token using refresh_token."""
    
    token_path = os.path.join(CREDENTIALS_DIR, token_file)
    
    if not os.path.exists(token_path):
        print(f"  [ERROR] Token file not found: {token_path}")
        return False
    
    try:
        # Load existing credentials
        with open(token_path, 'r') as f:
            creds_data = json.load(f)
        
        creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
        
        if not creds.refresh_token:
            print(f"  [ERROR] No refresh_token available")
            return False
        
        # Try to refresh
        print(f"  [REFRESHING] Refreshing token...")
        creds.refresh(Request())
        
        # Save the refreshed credentials
        with open(token_path, 'w') as f:
            f.write(creds.to_json())
        
        print(f"  [SUCCESS] Token refreshed successfully!")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if 'invalid_grant' in error_msg:
            print(f"  [ERROR] Refresh token expired or revoked - needs full reauth")
        else:
            print(f"  [ERROR] Error refreshing: {error_msg}")
        return False

def main():
    print("=== OAuth Token Refresh Tool ===\n")
    print("Attempting to refresh tokens using refresh_token (no browser needed)...\n")
    
    success_count = 0
    failed_sets = []
    
    for i, token_file in enumerate(TOKEN_FILES, 1):
        print(f"Set {i} ({token_file}):")
        if refresh_token(token_file):
            success_count += 1
        else:
            failed_sets.append(i)
        print()
    
    print(f"=== Summary ===")
    print(f"Successfully refreshed: {success_count}/{len(TOKEN_FILES)} tokens")
    
    if failed_sets:
        print(f"Failed sets: {failed_sets}")
        print("\nFor failed sets, you'll need to run regenerate_tokens.py for full reauth")
    else:
        print("\n[SUCCESS] All tokens refreshed successfully!")
        print("You can now run the YouTube authentication tests!")

if __name__ == "__main__":
    main()