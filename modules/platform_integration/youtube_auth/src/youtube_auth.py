import os
import logging
from dotenv import load_dotenv
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# Load environment variables once when the module is imported
load_dotenv()

def get_credentials_for_index(index):
    """
    Get credentials for a specific index (1-4).
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
    Implements multi-client OAuth fallback for quota management.
    
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

    # Determine which credential sets to try
    if token_index is not None:
        # Use specific token index (convert from 0-based to 1-based)
        indices_to_try = [token_index + 1]
        logger.info(f"🎯 Using specific credential set {token_index + 1}")
    else:
        # Try all credential sets in sequence
        indices_to_try = range(1, 5)
        logger.info("🔄 Trying all credential sets in sequence")
    
    for index in indices_to_try:
        logger.info(f"🔑 Attempting authentication with credential set {index}")
        creds_data = get_credentials_for_index(index)
        if not creds_data:
            logger.warning(f"⚠️ No credential data found for set {index}")
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

        # Handle credential refresh or new authentication
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info(f"🔄 Credentials expired for set {index}, attempting refresh...")
                try:
                    creds.refresh(Request())
                    logger.info(f"✅ Credentials refreshed successfully for set {index}")
                except Exception as e:
                    logger.error(f"❌ Failed to refresh token for set {index}: {e}")
                    # Continue to next credential set instead of trying OAuth flow
                    continue
            else:
                if creds and creds.expired and not creds.refresh_token:
                    logger.warning(f"⚠️ Credentials expired for set {index} but no refresh token available")
                else:
                    logger.info(f"🆕 No valid credentials found for set {index}, initiating OAuth flow...")
                
                try:
                    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                        client_secrets_file, scopes)
                    creds = flow.run_local_server(port=0)
                    logger.info(f"✅ OAuth flow completed successfully for set {index}")
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
                if test_response.get('items'):
                    logger.info(f"✅ Service validation successful for set {index}")
                    return youtube_service
                else:
                    logger.warning(f"⚠️ Service built but no channel data returned for set {index}")
                    continue
            except Exception as test_e:
                logger.warning(f"⚠️ Service built but validation failed for set {index}: {test_e}")
                # Still return the service as it might work for other operations
                return youtube_service
                
        except HttpError as e:
            if 'quotaExceeded' in str(e) or 'quota' in str(e).lower():
                logger.warning(f"📊 Quota exceeded for credential set {index}, trying next set...")
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
    raise Exception("Could not authenticate with any Google credential set.")

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
