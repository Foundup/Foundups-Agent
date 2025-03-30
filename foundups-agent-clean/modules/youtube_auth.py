import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from dotenv import load_dotenv
from google.auth.transport.requests import Request
import logging

logger = logging.getLogger(__name__)

def get_authenticated_service():
    """
    Authenticates the user using OAuth 2.0 and returns a YouTube API service object.
    Handles token loading, refreshing, and the initial authorization flow.
    """
    load_dotenv()
    client_secrets_file = os.getenv('GOOGLE_CLIENT_SECRETS_FILE')
    scopes = os.getenv('YOUTUBE_SCOPES', '').split()
    token_file = os.getenv('OAUTH_TOKEN_FILE')
    api_key = os.getenv('YOUTUBE_API_KEY')
    api_key2 = os.getenv('YOUTUBE_API_KEY2')

    if not client_secrets_file or not os.path.exists(client_secrets_file):
        logger.error(f"Client secrets file not found at: {client_secrets_file}")
        raise FileNotFoundError(f"Client secrets file not found: {client_secrets_file}")
    if not scopes:
        logger.error("YouTube scopes not defined in .env file.")
        raise ValueError("YOUTUBE_SCOPES must be defined in .env")
    if not token_file:
        logger.error("OAUTH_TOKEN_FILE not defined in .env file.")
        raise ValueError("OAUTH_TOKEN_FILE must be defined in .env")

    creds = None
    # The file token_file stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists(token_file):
        try:
            creds = google.oauth2.credentials.Credentials.from_authorized_user_file(token_file, scopes)
            logger.info(f"Loaded credentials from {token_file}")
        except Exception as e:
            logger.error(f"Failed to load credentials from {token_file}: {e}")

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
        # Try with first API key
        youtube_service = build('youtube', 'v3', credentials=creds, developerKey=api_key)
        logger.info("YouTube API service built successfully with primary API key.")
        return youtube_service
    except Exception as e:
        logger.warning(f"Failed to build service with primary API key: {e}")
        try:
            # Try with second API key
            youtube_service = build('youtube', 'v3', credentials=creds, developerKey=api_key2)
            logger.info("YouTube API service built successfully with secondary API key.")
            return youtube_service
        except Exception as e:
            logger.error(f"Failed to build YouTube service with both API keys: {e}")
            raise 