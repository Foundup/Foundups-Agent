import os
import logging
from dotenv import load_dotenv
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from modules.platform_integration.youtube_auth.src.quota_monitor import QuotaMonitor

logger = logging.getLogger(__name__)

# Initialize quota monitor
quota_monitor = QuotaMonitor()

# Load environment variables once when the module is imported
load_dotenv()

def get_credentials_for_index(index):
    """
    Get credentials for a specific index (1-5).
    Returns tuple of (client_secrets_file, token_file) or None if not found.
    """
    client_secrets = os.getenv(f'GOOGLE_CLIENT_SECRETS_FILE_{index}')
    token_file = os.getenv(f'OAUTH_TOKEN_FILE_{index}')
    
    if not client_secrets or not token_file:
        return None
        
    if not os.path.exists(client_secrets):
        logger.error(f"Client secrets file not found at: {client_secrets}")
        return None
        
    return client_secrets, token_file

def get_authenticated_service(token_index=None):
    """
    Authenticates the user using OAuth 2.0 and returns a YouTube API service object.
    Handles token loading, refreshing, and the initial authorization flow.
    Implements multi-client OAuth fallback for quota management with auto-rotation.
    
    Args:
        token_index: Optional specific token index to use (0-3). If None, tries all.
    """
    scopes_str = os.getenv('YOUTUBE_SCOPES', '').strip()
    
    if not scopes_str:
        logger.error("YouTube scopes not defined in .env file.")
        raise ValueError("YOUTUBE_SCOPES must be defined in .env")
        
    scopes = scopes_str.split()
    
    if not scopes:
        logger.error("YouTube scopes is empty in .env file.")
        raise ValueError("YOUTUBE_SCOPES must be defined in .env")

    # Track quota-exhausted sets persistently
    if not hasattr(get_authenticated_service, 'exhausted_sets'):
        get_authenticated_service.exhausted_sets = set()
    if not hasattr(get_authenticated_service, 'last_reset'):
        import time
        get_authenticated_service.last_reset = time.time()
    
    # Reset exhausted sets daily (quotas reset at midnight PT)
    import time
    current_time = time.time()
    if current_time - get_authenticated_service.last_reset > 86400:  # 24 hours
        logger.info("🔄 Daily reset: Clearing exhausted credential sets")
        get_authenticated_service.exhausted_sets.clear()
        get_authenticated_service.last_reset = current_time

    # Determine which credential sets to try
    if token_index is not None:
        # Use specific token index (already 1-based from caller)
        indices_to_try = [token_index]
        logger.info(f"🎯 Using specific credential set {token_index}")
    else:
        # Auto-rotation: Only use available credential sets (dynamic detection)
        from modules.platform_integration.youtube_auth.src.quota_monitor import get_available_credential_sets
        all_sets = get_available_credential_sets()  # Only configured sets (1, 10)
        available_sets = [s for s in all_sets if s not in get_authenticated_service.exhausted_sets]
        
        if not available_sets:
            # All exhausted - try all again (quotas might have reset)
            logger.warning("⚠️ All credential sets exhausted, retrying all...")
            get_authenticated_service.exhausted_sets.clear()
            available_sets = all_sets
        
        indices_to_try = available_sets
        logger.info(f"🔄 Auto-rotating through sets: {indices_to_try} (Exhausted: {get_authenticated_service.exhausted_sets})")
    
    for index in indices_to_try:
        logger.info(f"🔑 Attempting authentication with credential set {index}")
        creds_data = get_credentials_for_index(index)
        if not creds_data:
            # This should not happen with dynamic detection, but log it as debug instead of warning
            logger.debug(f"🔍 Credential set {index} not configured or files missing")
            continue
            
        client_secrets_file, token_file = creds_data
        creds = None

        # Try to load existing credentials
        if os.path.exists(token_file):
            try:
                creds = google.oauth2.credentials.Credentials.from_authorized_user_file(token_file, scopes)
                logger.info(f"Loaded credentials from {token_file}")
            except Exception as e:
                logger.error(f"Failed to load credentials from {token_file}: {e}")
                # If loading fails, skip to the next credential set
                continue

        # Proactive token refresh - refresh if expiring within 10 minutes
        if creds and creds.valid and creds.expiry:
            from datetime import datetime, timedelta, timezone
            # Handle both timezone-aware and naive datetimes
            if creds.expiry.tzinfo is None:
                # If expiry is naive, assume UTC
                time_until_expiry = creds.expiry - datetime.now()
            else:
                # If expiry is aware, use aware comparison
                time_until_expiry = creds.expiry - datetime.now(timezone.utc)
            if time_until_expiry < timedelta(minutes=10):
                logger.info(f"🔄 Token expiring in {time_until_expiry.seconds // 60} minutes for set {index}, proactively refreshing...")
                try:
                    creds.refresh(Request())
                    logger.info(f"✅ Proactive refresh successful for set {index} (new expiry: {creds.expiry})")
                    # Save the refreshed credentials
                    try:
                        with open(token_file, 'w') as token:
                            token.write(creds.to_json())
                        logger.info(f"💾 Refreshed credentials saved for set {index}")
                    except Exception as save_e:
                        logger.warning(f"⚠️ Could not save refreshed credentials: {save_e}")
                except Exception as refresh_e:
                    logger.warning(f"⚠️ Proactive refresh failed for set {index}: {refresh_e}")
                    # Mark as invalid to trigger normal refresh flow
                    creds = None

        # Handle credential refresh or new authentication
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info(f"🔄 Credentials expired for set {index}, attempting refresh...")
                try:
                    creds.refresh(Request())
                    logger.info(f"✅ Credentials refreshed successfully for set {index}")
                    # Log the new expiration time
                    if creds.expiry:
                        logger.info(f"📅 New token expires at: {creds.expiry} (valid for ~1 hour)")
                except Exception as e:
                    error_msg = str(e)
                    # Better error distinction
                    if 'invalid_grant' in error_msg:
                        if 'Token has been expired or revoked' in error_msg:
                            # Try to distinguish between expired and revoked
                            if 'revoked' in error_msg.lower():
                                logger.error(f"🚫 Token has been REVOKED for set {index} - user action required")
                                logger.info(f"ℹ️ To fix: Run 'python modules/platform_integration/youtube_auth/scripts/authorize_set{index}.py'")
                            else:
                                logger.error(f"⏰ Refresh token EXPIRED for set {index} (tokens last 6 months if unused)")
                                logger.info(f"ℹ️ To fix: Run 'python modules/platform_integration/youtube_auth/scripts/authorize_set{index}.py'")
                        else:
                            logger.error(f"❌ Invalid grant error for set {index}: {error_msg}")
                    else:
                        logger.error(f"❌ Failed to refresh token for set {index}: {e}")

                    # Continue to next credential set instead of trying OAuth flow
                    continue
            else:
                if creds and creds.expired and not creds.refresh_token:
                    logger.warning(f"⚠️ Credentials expired for set {index} but no refresh token available")
                    logger.info(f"ℹ️ To fix: Run 'python modules/platform_integration/youtube_auth/scripts/authorize_set{index}.py'")
                else:
                    logger.info(f"🆕 No valid credentials found for set {index}, initiating OAuth flow...")

                try:
                    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                        client_secrets_file, scopes)
                    creds = flow.run_local_server(port=0)
                    logger.info(f"✅ OAuth flow completed successfully for set {index}")
                    if creds.expiry:
                        logger.info(f"📅 Token expires at: {creds.expiry}")
                except Exception as e:
                    logger.error(f"❌ OAuth flow failed for set {index}: {e}")
                    continue

            # Save the credentials with improved error handling
            if creds:
                try:
                    os.makedirs(os.path.dirname(token_file), exist_ok=True)
                    with open(token_file, 'w') as token:
                        token.write(creds.to_json())
                    logger.info(f"💾 Credentials saved to {token_file}")
                except Exception as e:
                    logger.error(f"❌ Failed to save credentials to {token_file}: {e}")
                    # Don't continue here - we can still use the credentials even if saving fails
                    logger.warning(f"⚠️ Proceeding with unsaved credentials for set {index}")

        if not creds:
            logger.error(f"❌ Failed to obtain credentials for set {index}")
            continue

        try:
            # Try to build service with current credentials
            youtube_service = build('youtube', 'v3', credentials=creds)
            logger.info(f"🎉 YouTube API service built successfully with credential set {index}")
            
            # Test the service with a lightweight call to ensure it's working
            try:
                test_response = youtube_service.channels().list(part='snippet', mine=True).execute()
                # Track the quota usage for this test call
                quota_monitor.track_api_call(index, 'channels.list')
                
                if test_response.get('items'):
                    logger.info(f"✅ Service validation successful for set {index}")
                    # Store the active set for tracking
                    youtube_service._credential_set = index
                    return youtube_service
                else:
                    logger.warning(f"⚠️ Service built but no channel data returned for set {index}")
                    continue
            except Exception as test_e:
                if 'quotaExceeded' in str(test_e):
                    logger.warning(f"📊 Validation failed due to quota for set {index}, marking as exhausted...")
                    get_authenticated_service.exhausted_sets.add(index)
                    continue  # Try next set
                else:
                    # Log full error details for debugging
                    error_msg = str(test_e)
                    if error_msg == str(index):
                        # This is the weird case where just the number is returned
                        logger.warning(f"⚠️ Service built but validation returned credential set number {index} as error")
                    else:
                        logger.warning(f"⚠️ Service built but validation failed for set {index}: {test_e}")
                    # Continue to next credential set instead of returning
                    continue
                
        except HttpError as e:
            if 'quotaExceeded' in str(e) or 'quota' in str(e).lower():
                logger.warning(f"📊 Quota exceeded for credential set {index}, marking as exhausted...")
                get_authenticated_service.exhausted_sets.add(index)
                continue
            else:
                logger.error(f"❌ HTTP error building YouTube service with set {index}: {e}")
                continue
        except Exception as e:
            logger.error(f"❌ Failed to build YouTube service with set {index}: {e}")
            continue

    # If we get here, all credential sets failed
    error_msg = f"💥 All credential sets failed to authenticate (tried {len(indices_to_try)} sets)"
    logger.critical(error_msg)
    logger.critical("🔓 FALLING BACK TO NO-AUTH MODE - Read-only YouTube operations")

    # Return a no-auth YouTube service for read-only operations
    # This allows checking if streams are live without consuming quota
    try:
        youtube_service = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY', None))
        if youtube_service:
            logger.warning("✅ No-auth YouTube service created - Limited to public read-only operations")
            return youtube_service
    except Exception as e:
        logger.error(f"❌ Failed to create no-auth service: {e}")

    # Only raise if we can't even create a no-auth service
    raise Exception("Could not authenticate with any Google credential set and no API key available.")

# YouTube Comment API Extensions (Per WSP 84 - Enhance existing module)
def list_video_comments(youtube_service, video_id: str, max_results: int = 100):
    """
    List all comment threads for a video.
    Cost: 1 unit per call (returns up to 100 comments)
    """
    try:
        request = youtube_service.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            maxResults=max_results,
            order="relevance"  # or "time" for newest first
        )
        response = request.execute()
        return response.get('items', [])
    except Exception as e:
        logger.error(f"Error fetching comments for video {video_id}: {e}")
        return []

def like_comment(youtube_service, comment_id: str):
    """
    Like a YouTube comment.
    Note: YouTube API doesn't have a direct 'like comment' endpoint.
    We can only rate comments as 'none' or 'spam'.
    For liking, we need to use the video rating system.
    """
    logger.warning("YouTube API doesn't support liking individual comments directly")
    return False

def reply_to_comment(youtube_service, parent_id: str, text: str):
    """
    Reply to a YouTube comment.
    Cost: 50 units per call
    """
    try:
        request = youtube_service.comments().insert(
            part="snippet",
            body={
                "snippet": {
                    "parentId": parent_id,
                    "textOriginal": text
                }
            }
        )
        response = request.execute()
        logger.info(f"✅ Posted reply to comment {parent_id}")
        return response
    except Exception as e:
        logger.error(f"❌ Error replying to comment {parent_id}: {e}")
        return None

def get_latest_video_id(youtube_service, channel_id: str):
    """
    Get the latest video ID from a channel.
    Cost: 1 unit
    """
    try:
        request = youtube_service.search().list(
            part="id",
            channelId=channel_id,
            maxResults=1,
            order="date",
            type="video"
        )
        response = request.execute()
        items = response.get('items', [])
        if items:
            return items[0]['id']['videoId']
        return None
    except Exception as e:
        logger.error(f"Error fetching latest video: {e}")
        return None

# Example usage (for testing purposes, typically called from main.py)
if __name__ == '__main__':
    from utils.logging_config import setup_logging
    setup_logging()
    try:
        service = get_authenticated_service()
        # Test call (optional)
        response = service.channels().list(part='snippet', mine=True).execute()
        logger.info(f"Successfully authenticated as channel: {response['items'][0]['snippet']['title']}")
    except FileNotFoundError:
        logger.error("Setup error: Ensure GOOGLE_CLIENT_SECRETS_FILE points to a valid file.")
    except ValueError as ve:
        logger.error(f"Configuration error: {ve}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
