import os
import logging
from dotenv import load_dotenv
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)

def get_authenticated_service():
    """
    Authenticates the user using OAuth 2.0 and returns a YouTube API service object.
    Handles token loading, refreshing, and the initial authorization flow.
    """
    load_dotenv()
    client_secrets_file = os.getenv('GOOGLE_CLIENT_SECRETS_FILE')
    scopes = os.getenv('YOUTUBE_SCOPES', '').split()
    token_file = os.getenv('OAUTH_TOKEN_FILE', 'credentials/oauth_token.json')

    if not client_secrets_file or not os.path.exists(client_secrets_file):
        logger.error(f"Client secrets file not found at: {client_secrets_file}")
        raise FileNotFoundError(f"Client secrets file not found: {client_secrets_file}")
    if not scopes:
        logger.error("YouTube scopes not defined in .env file.")
        raise ValueError("YOUTUBE_SCOPES must be defined in .env")

    creds = None
    # The file token_file stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists(token_file):
        try:
            creds = google.oauth2.credentials.Credentials.from_authorized_user_file(token_file, scopes)
            logger.info(f"Loaded credentials from {token_file}")
        except Exception as e:
            logger.error(f"Failed to load credentials from {token_file}: {e}")
            # Optionally delete the corrupted token file?
            # os.remove(token_file)


    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Credentials expired, attempting refresh...")
            try:
                creds.refresh(Request())
                logger.info("Credentials refreshed successfully.")
            except Exception as e:
                logger.error(f"Failed to refresh token: {e}. Need to re-authenticate.")
                # Force re-authentication if refresh fails
                creds = None
        else:
            logger.info("No valid credentials found, initiating OAuth flow...")
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, scopes)
            # Specify port 0 to use a random available port, avoid conflicts
            creds = flow.run_local_server(port=0)
            logger.info("OAuth flow completed successfully.")

        # Save the credentials for the next run
        os.makedirs(os.path.dirname(token_file), exist_ok=True)
        try:
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
            logger.info(f"Credentials saved to {token_file}")
        except Exception as e:
             logger.error(f"Failed to save credentials to {token_file}: {e}")


    if not creds:
         logger.critical("Failed to obtain credentials.")
         raise Exception("Could not authenticate with Google.")

    try:
        youtube_service = build('youtube', 'v3', credentials=creds)
        logger.info("YouTube API service built successfully.")
        return youtube_service
    except Exception as e:
        logger.error(f"Failed to build YouTube service: {e}")
        raise

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
