"""
Authorize OAuth credential sets 8, 9, and 10 for YouTube API
This script should be run manually to authorize each set with browser authentication
"""

import os
import sys
import argparse

# Add parent directory to path to import youtube_auth module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# YouTube API scopes
SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/youtube.readonly'
]

def authorize_set(set_number):
    """Authorize a single credential set"""
    
    # Build file paths based on set number
    if set_number == 1:
        client_secret_file = f'credentials/client_secret.json'
        token_file = f'credentials/oauth_token.json'
    else:
        client_secret_file = f'credentials/client_secret{set_number}.json'
        token_file = f'credentials/oauth_token{set_number}.json'
    
    print(f"\n{'='*60}")
    print(f"Authorizing Set {set_number}")
    print(f"{'='*60}")
    print(f"Client Secret: {client_secret_file}")
    print(f"Token Output: {token_file}")
    
    # Check if client secret exists
    if not os.path.exists(client_secret_file):
        print(f"❌ Client secret not found: {client_secret_file}")
        print(f"   Please ensure {client_secret_file} exists")
        return False
    
    # Check if token already exists
    if os.path.exists(token_file):
        print(f"⚠️ Warning: Token file already exists: {token_file}")
        print("   This will overwrite the existing token.")
    
    try:
        # Run OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secret_file, SCOPES)
        
        # Use different ports for each set to avoid conflicts
        port = 8080 + set_number
        
        # This will open a browser for authorization
        print(f"\n🌐 Opening browser for authorization on port {port}...")
        print("Please log in with a Google account and authorize the application.")
        print("\n⚠️ IMPORTANT: Each set should use a DIFFERENT Google account")
        print("   to maximize available quota (10,000 units per account per day)")
        
        creds = flow.run_local_server(port=port)
        
        # Save the credentials
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
        
        print(f"✅ Successfully authorized Set {set_number}")
        print(f"💾 Token saved to: {token_file}")
        
        # Test the credentials
        service = build('youtube', 'v3', credentials=creds)
        response = service.channels().list(part='snippet', mine=True).execute()
        if response.get('items'):
            channel = response['items'][0]['snippet']['title']
            print(f"✨ Authenticated as channel: {channel}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to authorize Set {set_number}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to authorize sets 8, 9, and 10"""
    
    parser = argparse.ArgumentParser(
        description='Authorize YouTube API credential sets 8, 9, and 10',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python authorize_sets_8_9_10.py 8      # Authorize set 8
  python authorize_sets_8_9_10.py 9      # Authorize set 9
  python authorize_sets_8_9_10.py 10     # Authorize set 10
  python authorize_sets_8_9_10.py --all  # Authorize all three sets

Note: Each set should use a DIFFERENT Google account for maximum quota.
        """
    )
    
    parser.add_argument('set_number', type=int, nargs='?', 
                        help='Set number to authorize (8, 9, or 10)')
    parser.add_argument('--all', action='store_true',
                        help='Authorize all three sets (8, 9, 10)')
    
    args = parser.parse_args()
    
    # Determine which sets to authorize
    if args.all:
        sets_to_authorize = [8, 9, 10]
    elif args.set_number:
        if args.set_number not in [8, 9, 10]:
            print(f"❌ Invalid set number: {args.set_number}")
            print("   Please specify 8, 9, or 10")
            sys.exit(1)
        sets_to_authorize = [args.set_number]
    else:
        parser.print_help()
        sys.exit(0)
    
    print("YouTube API Authorization for New Credential Sets")
    print("="*60)
    
    successful = []
    failed = []
    
    for set_num in sets_to_authorize:
        if authorize_set(set_num):
            successful.append(set_num)
        else:
            failed.append(set_num)
    
    # Summary
    print("\n" + "="*60)
    print("AUTHORIZATION SUMMARY")
    print("="*60)
    
    if successful:
        print(f"✅ Successfully authorized: {successful}")
    
    if failed:
        print(f"❌ Failed to authorize: {failed}")
    
    # Instructions for next steps
    if successful:
        print("\n📝 Next steps:")
        print("1. The .env file already has entries for sets 8, 9, 10")
        print("2. Update youtube_auth.py to include these sets in rotation:")
        print("   - Add sets 8, 9, 10 to the all_sets list")
        print("3. Test with: python main.py --youtube")
        print("4. Monitor quota usage in memory/quota_usage.json")

if __name__ == "__main__":
    main()