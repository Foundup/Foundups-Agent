#!/usr/bin/env python3
"""
OAuth Flow Tool - Generate Fresh YouTube API Tokens

Usage:
    python tools/oauth_flow.py --client credentials/client_secret4.json --out credentials/oauth_token4.json
    
Features:
- Generates fresh OAuth tokens with proper structure
- Saves tokens in correct format for FoundUps Agent
- Supports YouTube API scopes
"""

import argparse
import json
import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Default YouTube API scopes
DEFAULT_SCOPES = [
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.readonly"
]

def generate_oauth_token(client_secrets_file: str, output_file: str, scopes: list = None):
    """
    Generate a fresh OAuth token using the provided client secrets.
    
    Args:
        client_secrets_file: Path to client secrets JSON file
        output_file: Path where to save the OAuth token
        scopes: List of OAuth scopes (defaults to YouTube scopes)
    """
    if scopes is None:
        scopes = DEFAULT_SCOPES
        
    print(f"🔑 Generating OAuth token...")
    print(f"📁 Client secrets: {client_secrets_file}")
    print(f"📄 Output file: {output_file}")
    print(f"🎯 Scopes: {scopes}")
    
    # Check if client secrets file exists
    if not os.path.exists(client_secrets_file):
        print(f"❌ Error: Client secrets file not found: {client_secrets_file}")
        return False
        
    try:
        # Read client secrets to determine the correct redirect URI port
        with open(client_secrets_file, 'r') as f:
            secrets_data = json.load(f)
            
        # Extract redirect URI port from client secrets
        redirect_uris = secrets_data.get('web', {}).get('redirect_uris', [])
        redirect_port = 8080  # Default port
        
        if redirect_uris:
            # Parse port from first redirect URI (e.g., "http://localhost:8080/")
            import urllib.parse
            parsed = urllib.parse.urlparse(redirect_uris[0])
            if parsed.port:
                redirect_port = parsed.port
                print(f"🌐 Using redirect port from client secrets: {redirect_port}")
            else:
                print(f"🌐 Using default redirect port: {redirect_port}")
        
        # Create OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
        
        # Run the OAuth flow with the correct port
        print(f"🌐 Starting OAuth flow (browser will open at http://localhost:{redirect_port})...")
        credentials = flow.run_local_server(port=redirect_port)
        
        # Create output directory if needed
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Save credentials in proper format
        with open(output_file, 'w') as f:
            f.write(credentials.to_json())
            
        print(f"✅ OAuth token saved successfully to: {output_file}")
        
        # Verify the structure
        with open(output_file, 'r') as f:
            token_data = json.load(f)
            
        required_keys = ['token', 'refresh_token', 'client_id', 'client_secret']
        missing_keys = [key for key in required_keys if key not in token_data]
        
        if missing_keys:
            print(f"⚠️ Warning: Generated token missing keys: {missing_keys}")
            return False
        else:
            print("✅ Token structure validated - all required keys present")
            print(f"🔑 Token expires: {token_data.get('expiry', 'Unknown')}")
            return True
            
    except Exception as e:
        print(f"❌ Error generating OAuth token: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Generate fresh OAuth tokens for YouTube API')
    parser.add_argument('--client', required=True, help='Path to client secrets JSON file')
    parser.add_argument('--out', required=True, help='Output path for OAuth token file')
    parser.add_argument('--scopes', nargs='+', default=DEFAULT_SCOPES, 
                       help='OAuth scopes (space-separated)')
    
    args = parser.parse_args()
    
    success = generate_oauth_token(args.client, args.out, args.scopes)
    
    if success:
        print("🎉 OAuth token generation completed successfully!")
        sys.exit(0)
    else:
        print("💥 OAuth token generation failed!")
        sys.exit(1)

if __name__ == '__main__':
    main() 