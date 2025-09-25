#!/usr/bin/env python3
"""
Automatic Token Refresh Script
Refreshes YouTube OAuth tokens before they expire to prevent authentication failures.

This script should be run periodically (e.g., daily via cron/scheduler) to:
1. Check all credential sets for expiring tokens
2. Refresh tokens that will expire within the next hour
3. Save refreshed tokens back to disk

WSP Compliance: WSP 84 (Code Memory Verification) - Enhancing existing youtube_auth module
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta, timezone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, project_root)
os.chdir(project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def refresh_credential_set(index: int, force_refresh: bool = False) -> dict:
    """
    Refresh a single credential set if needed.

    Args:
        index: Credential set number (1 or 10)
        force_refresh: Force refresh even if token isn't expiring soon

    Returns:
        Status dict with result information
    """
    # Only sets 1 and 10 are active
    if index not in [1, 10]:
        return {'status': 'skipped', 'reason': 'Inactive set'}

    # Determine file paths
    if index == 1:
        secret_file = 'credentials/client_secret.json'
        token_file = 'credentials/oauth_token.json'
        set_name = "UnDaoDu (Set 1)"
    else:
        secret_file = f'credentials/client_secret{index}.json'
        token_file = f'credentials/oauth_token{index}.json'
        set_name = f"Foundups (Set {index})"

    logger.info(f"Checking {set_name}...")

    # Check if files exist
    if not os.path.exists(secret_file):
        logger.warning(f"Missing client secret for {set_name}")
        return {'status': 'error', 'reason': 'Missing client secret'}

    if not os.path.exists(token_file):
        logger.warning(f"No token file for {set_name} - needs initial authorization")
        return {'status': 'error', 'reason': 'No token file'}

    try:
        # Load existing credentials
        creds = Credentials.from_authorized_user_file(token_file,
            ['https://www.googleapis.com/auth/youtube.force-ssl',
             'https://www.googleapis.com/auth/youtube.readonly'])

        # Check if refresh is needed
        needs_refresh = False
        refresh_reason = None

        if not creds.valid:
            if creds.expired:
                needs_refresh = True
                refresh_reason = "Token expired"
            else:
                needs_refresh = True
                refresh_reason = "Token invalid"
        elif creds.expiry:
            # Check if expiring soon (within 1 hour)
            # Ensure both datetimes are timezone-aware
            now = datetime.now(timezone.utc)
            expiry = creds.expiry
            if expiry.tzinfo is None:
                # Make expiry timezone-aware if it isn't already
                expiry = expiry.replace(tzinfo=timezone.utc)
            time_until_expiry = expiry - now
            hours_until_expiry = time_until_expiry.total_seconds() / 3600

            if hours_until_expiry < 1 or force_refresh:
                needs_refresh = True
                refresh_reason = f"Token expiring in {hours_until_expiry:.1f} hours"
            else:
                logger.info(f"  ✅ Token valid for {hours_until_expiry:.1f} more hours")

        if needs_refresh and creds.refresh_token:
            logger.info(f"  🔄 Refreshing token: {refresh_reason}")

            try:
                # Perform the refresh
                creds.refresh(Request())

                # Save the refreshed token
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())

                # Log new expiry
                if creds.expiry:
                    new_expiry = creds.expiry
                    now = datetime.now(timezone.utc)
                    if new_expiry.tzinfo is None:
                        new_expiry = new_expiry.replace(tzinfo=timezone.utc)
                    hours_valid = (new_expiry - now).total_seconds() / 3600
                    logger.info(f"  ✅ Token refreshed! Valid for {hours_valid:.1f} hours")
                    logger.info(f"     New expiry: {new_expiry.isoformat()}")

                # Test the refreshed credentials
                youtube = build('youtube', 'v3', credentials=creds)
                response = youtube.channels().list(part='snippet', mine=True).execute()

                if response.get('items'):
                    channel_name = response['items'][0]['snippet']['title']
                    logger.info(f"  📺 Verified access to: {channel_name}")
                    return {
                        'status': 'refreshed',
                        'channel': channel_name,
                        'expiry': creds.expiry.isoformat() if creds.expiry else None
                    }

            except HttpError as e:
                if 'quotaExceeded' in str(e):
                    logger.warning(f"  ⚠️ Quota exceeded during verification, but token should be valid")
                    return {'status': 'refreshed', 'note': 'Quota exceeded during test'}
                else:
                    logger.error(f"  ❌ API error during refresh: {e}")
                    return {'status': 'error', 'reason': f'API error: {e}'}

            except Exception as e:
                error_msg = str(e)
                if 'invalid_grant' in error_msg:
                    if 'Token has been expired or revoked' in error_msg:
                        logger.error(f"  ❌ Refresh token expired or revoked!")
                        logger.info(f"     Fix: python modules/platform_integration/youtube_auth/scripts/authorize_set{index}.py")
                        return {'status': 'error', 'reason': 'Token revoked - needs reauthorization'}
                    else:
                        logger.error(f"  ❌ Invalid grant: {error_msg}")
                        return {'status': 'error', 'reason': 'Invalid grant'}
                else:
                    logger.error(f"  ❌ Refresh failed: {e}")
                    return {'status': 'error', 'reason': str(e)}

        elif needs_refresh and not creds.refresh_token:
            logger.error(f"  ❌ Token needs refresh but no refresh token available")
            logger.info(f"     Fix: python modules/platform_integration/youtube_auth/scripts/authorize_set{index}.py")
            return {'status': 'error', 'reason': 'No refresh token'}

        else:
            return {'status': 'valid', 'hours_remaining': hours_until_expiry if 'hours_until_expiry' in locals() else None}

    except Exception as e:
        logger.error(f"  ❌ Error loading credentials: {e}")
        return {'status': 'error', 'reason': str(e)}

def main():
    """Main function to refresh all active credential sets."""
    logger.info("=" * 60)
    logger.info("AUTOMATIC TOKEN REFRESH")
    logger.info("=" * 60)

    # Track results
    results = {}
    refresh_count = 0
    error_count = 0

    # Check both active sets (1 and 10)
    for set_index in [1, 10]:
        result = refresh_credential_set(set_index)
        results[set_index] = result

        if result['status'] == 'refreshed':
            refresh_count += 1
        elif result['status'] == 'error':
            error_count += 1

    # Summary
    logger.info("=" * 60)
    logger.info("SUMMARY")
    logger.info(f"  Tokens refreshed: {refresh_count}")
    logger.info(f"  Errors: {error_count}")
    logger.info(f"  Sets checked: {len(results)}")

    # Detailed status
    for set_index, result in results.items():
        set_name = "UnDaoDu" if set_index == 1 else "Foundups"
        status = result['status']

        if status == 'refreshed':
            logger.info(f"  Set {set_index} ({set_name}): ✅ Refreshed")
        elif status == 'valid':
            hours = result.get('hours_remaining', 0)
            logger.info(f"  Set {set_index} ({set_name}): ✅ Valid ({hours:.1f}h remaining)")
        elif status == 'error':
            reason = result.get('reason', 'Unknown error')
            logger.info(f"  Set {set_index} ({set_name}): ❌ {reason}")

    logger.info("=" * 60)

    # Return success if at least one token is valid or was refreshed
    valid_count = sum(1 for r in results.values() if r['status'] in ['valid', 'refreshed'])
    return 0 if valid_count > 0 else 1

if __name__ == "__main__":
    sys.exit(main())