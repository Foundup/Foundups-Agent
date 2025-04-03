import os
import logging
import json
import time
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv
from googleapiclient.errors import HttpError

# Get a logger instance specific to this module
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Constants
CREDENTIALS_DIR = "credentials"
CLIENT_SECRETS_FILES = [
    "client_secret.json",
    "client_secret2.json",
    "client_secret3.json",
    "client_secret4.json"
]
OAUTH_TOKEN_FILES = [
    "oauth_token.json",
    "oauth_token2.json",
    "oauth_token3.json",
    "oauth_token4.json"
]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.readonly"
]

# Quota limits
QUOTA_LIMIT_3H = 100  # calls per 3 hours
QUOTA_LIMIT_7D = 10000  # calls per 7 days
QUOTA_RESET_3H = 3 * 60 * 60  # 3 hours in seconds
QUOTA_RESET_7D = 7 * 24 * 60 * 60  # 7 days in seconds

class QuotaManager:
    """Manages API quota tracking and rotation."""
    
    def __init__(self):
        self.quota_file = os.path.join(CREDENTIALS_DIR, "quota_usage.json")
        self.usage_data = self._load_usage_data()
        self.cooldowns = {}  # Track cooldown timestamps per credential set
        self.COOLDOWN_DURATION = 3600  # 1 hour cooldown in seconds
        logger = logging.getLogger(__name__)
        logger.info("📊 Initialized QuotaManager")
        
    def _load_usage_data(self) -> Dict[str, Any]:
        """Load quota usage data from file."""
        if os.path.exists(self.quota_file):
            try:
                with open(self.quota_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading quota data: {e}")
                return self._create_empty_usage_data()
        return self._create_empty_usage_data()
    
    def _create_empty_usage_data(self) -> Dict[str, Any]:
        """Create empty quota usage data structure."""
        return {
            "credentials": {
                "primary": {"3h": [], "7d": []},
                "secondary": {"3h": [], "7d": []},
                "tertiary": {"3h": [], "7d": []}
            },
            "api_keys": {
                "primary": {"3h": [], "7d": []},
                "secondary": {"3h": [], "7d": []}
            }
        }
    
    def _save_usage_data(self):
        """Save quota usage data to file."""
        try:
            os.makedirs(os.path.dirname(self.quota_file), exist_ok=True)
            with open(self.quota_file, 'w') as f:
                json.dump(self.usage_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving quota data: {e}")
    
    def _cleanup_old_usage(self, usage_list: list, max_age: int) -> list:
        """Remove usage entries older than max_age seconds."""
        now = time.time()
        return [entry for entry in usage_list if now - entry < max_age]
    
    def record_usage(self, credential_type: str, is_api_key: bool = False):
        """Record API usage for a credential."""
        now = time.time()
        key = "api_keys" if is_api_key else "credentials"
        
        # Clean up old usage data
        self.usage_data[key][credential_type]["3h"] = self._cleanup_old_usage(
            self.usage_data[key][credential_type]["3h"], QUOTA_RESET_3H)
        self.usage_data[key][credential_type]["7d"] = self._cleanup_old_usage(
            self.usage_data[key][credential_type]["7d"], QUOTA_RESET_7D)
        
        # Record new usage
        self.usage_data[key][credential_type]["3h"].append(now)
        self.usage_data[key][credential_type]["7d"].append(now)
        
        # Save updated data
        self._save_usage_data()
        
        # Log usage statistics
        logger.debug(f"Quota usage for {credential_type} ({'API key' if is_api_key else 'OAuth'}):")
        logger.debug(f"3h: {len(self.usage_data[key][credential_type]['3h'])}/{QUOTA_LIMIT_3H}")
        logger.debug(f"7d: {len(self.usage_data[key][credential_type]['7d'])}/{QUOTA_LIMIT_7D}")
    
    def get_usage_count(self, credential_type: str, is_api_key: bool = False) -> Tuple[int, int]:
        """Get current usage counts for a credential."""
        key = "api_keys" if is_api_key else "credentials"
        return (
            len(self.usage_data[key][credential_type]["3h"]),
            len(self.usage_data[key][credential_type]["7d"])
        )
    
    def is_quota_exceeded(self, credential_type: str, is_api_key: bool = False) -> bool:
        """Check if quota is exceeded for a credential."""
        three_hour, seven_day = self.get_usage_count(credential_type, is_api_key)
        return three_hour >= QUOTA_LIMIT_3H or seven_day >= QUOTA_LIMIT_7D
    
    def get_next_available_credential(self, is_api_key: bool = False) -> Optional[str]:
        """Find the next available credential that hasn't exceeded quota."""
        key = "api_keys" if is_api_key else "credentials"
        for credential_type in self.usage_data[key].keys():
            if not self.is_quota_exceeded(credential_type, is_api_key):
                return credential_type
        return None

    def start_cooldown(self, credential_set: str):
        """Start a cooldown period for a credential set."""
        self.cooldowns[credential_set] = time.time()
        cooldown_end = time.time() + self.COOLDOWN_DURATION
        logger = logging.getLogger(__name__)
        logger.info(f"⏳ Started cooldown for {credential_set}")
        logger.info(f"⏰ Cooldown will end at: {time.strftime('%H:%M:%S', time.localtime(cooldown_end))}")
    
    def is_in_cooldown(self, credential_set: str) -> bool:
        """Check if a credential set is still in cooldown."""
        if credential_set not in self.cooldowns:
            return False
            
        cooldown_start = self.cooldowns[credential_set]
        now = time.time()
        is_in_cooldown = (now - cooldown_start) < self.COOLDOWN_DURATION
        
        if not is_in_cooldown:
            # Clean up expired cooldown
            del self.cooldowns[credential_set]
            logger = logging.getLogger(__name__)
            logger.info(f"✅ Cooldown expired for {credential_set}")
            
        return is_in_cooldown

# Initialize quota manager
quota_manager = QuotaManager()

def get_client_secrets_file(credential_type: str) -> str:
    """Get the path to the client secrets file for the given credential type."""
    # Support both old format (primary/secondary/tertiary) and new format (set_1/set_2/etc)
    if credential_type.startswith('set_'):
        index = int(credential_type.split('_')[1]) - 1
    else:
        index = {"primary": 0, "secondary": 1, "tertiary": 2}[credential_type]
    return os.path.join(CREDENTIALS_DIR, CLIENT_SECRETS_FILES[index])

def get_oauth_token_file(credential_type: str) -> str:
    """Get the path to the OAuth token file for the given credential type."""
    # Support both old format (primary/secondary/tertiary) and new format (set_1/set_2/etc)
    if credential_type.startswith('set_'):
        index = int(credential_type.split('_')[1]) - 1
    else:
        index = {"primary": 0, "secondary": 1, "tertiary": 2}[credential_type]
    return os.path.join(CREDENTIALS_DIR, OAUTH_TOKEN_FILES[index])

def authenticate_with_config(client_secrets_file: str, token_file: str, config_name: str) -> Optional[Credentials]:
    """
    Authenticates with YouTube API using the specified configuration files.
    
    Args:
        client_secrets_file: Path to the client secrets file
        token_file: Path to the token file
        config_name: Name of the configuration (for logging)
        
    Returns:
        Credentials object if successful, None otherwise
    """
    try:
        creds = None
        
        # Check if token file exists and is not empty
        if os.path.exists(token_file):
            try:
                with open(token_file, 'r') as f:
                    token_data = json.load(f)
                    if not token_data:  # Empty JSON object
                        logger.info(f"{config_name}: Token file is empty, triggering OAuth login")
                        creds = None
                    else:
                        logger.info(f"{config_name}: Loaded existing credentials from {token_file}")
                        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
            except json.JSONDecodeError:
                logger.warning(f"{config_name}: Token file is invalid, triggering OAuth login")
                creds = None
        else:
            logger.info(f"{config_name}: No token file found at {token_file}, triggering OAuth login")
            
        # Handle credential refresh or new authentication
        if creds and creds.valid:
            logger.info(f"{config_name}: Using existing valid credentials")
        elif creds and creds.expired and creds.refresh_token:
            logger.info(f"{config_name}: Refreshing expired credentials")
            try:
                creds.refresh(Request())
                logger.info(f"{config_name}: Successfully refreshed credentials")
            except Exception as e:
                logger.error(f"{config_name}: Failed to refresh token: {e}")
                creds = None
        else:
            if not os.path.exists(client_secrets_file):
                logger.error(f"{config_name}: Client secrets file not found at {client_secrets_file}")
                return None
                
            logger.info(f"{config_name}: Triggering OAuth login")
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)
            logger.info(f"{config_name}: OAuth flow completed successfully")
            
            # Save the credentials for future use
            os.makedirs(os.path.dirname(token_file), exist_ok=True)
            with open(token_file, "w") as token:
                token.write(creds.to_json())
            logger.info(f"{config_name}: Successfully saved new credentials to {token_file}")
            
        return creds
        
    except Exception as e:
        logger.error(f"{config_name}: Authentication failed: {e}")
        return None

def get_authenticated_service(credential_set_index: int = 0) -> Optional[Any]:
    """
    Authenticates with YouTube API using specified credential set.
    
    Args:
        credential_set_index: Index of the credential set to use (0-based)
        
    Returns:
        Tuple (service, credentials) if successful, None otherwise
    """
    logger = logging.getLogger(__name__)
    
    try:
        config_name = f"set_{credential_set_index+1}"
        client_secrets = os.path.join(CREDENTIALS_DIR, CLIENT_SECRETS_FILES[credential_set_index])
        token_file = os.path.join(CREDENTIALS_DIR, OAUTH_TOKEN_FILES[credential_set_index])
        
        logger.info(f"Attempting authentication with {config_name}")
        creds = authenticate_with_config(client_secrets, token_file, config_name)
        
        if creds:
            try:
                service = build(API_SERVICE_NAME, API_VERSION, credentials=creds)
                logger.info(f"Successfully authenticated with {config_name}")
                return service, creds
            except Exception as e:
                logger.error(f"Failed to build service with {config_name}: {e}")
                return None
        else:
            logger.warning(f"Authentication failed for {config_name}")
            return None
            
    except Exception as e:
        logger.error(f"Error during authentication with {config_name}: {e}")
        return None

def get_authenticated_service_with_fallback() -> Optional[Any]:
    """
    Attempts to authenticate with YouTube API using multiple credentials with fallback support.
    Tries each credential set in sequence until one succeeds or all fail.
    Handles quota exceeded errors by rotating to the next credential set.
    
    Returns:
        Tuple (service, credentials, credential_set_name) if successful, None otherwise
    """
    logger = logging.getLogger(__name__)
    logger.info("🔄 Starting credential rotation process")
    
    # Test each set individually
    for i in range(4):  # Test sets 1-4
        try:
            credential_set = f"set_{i+1}"
            logger.info(f"🔑 Attempting to use credential set: {credential_set}")
            
            # Check if this credential set is in cooldown
            if quota_manager.is_in_cooldown(credential_set):
                cooldown_start = quota_manager.cooldowns[credential_set]
                time_remaining = quota_manager.COOLDOWN_DURATION - (time.time() - cooldown_start)
                logger.info(f"⏳ Credential {credential_set} is in cooldown. Time remaining: {time_remaining/3600:.1f} hours")
                continue
                
            auth_result = get_authenticated_service(i)
            if auth_result:
                service, creds = auth_result
                logger.info(f"✅ Successfully authenticated with {credential_set}")
                print(f"✅ Using credential set: {credential_set}")
                return service, creds, credential_set
                
        except HttpError as e:
            if 'quotaExceeded' in str(e):
                logger.warning(f"⚠️ Quota exceeded for {credential_set}")
                quota_manager.start_cooldown(credential_set)
                cooldown_start = quota_manager.cooldowns[credential_set]
                logger.info(f"⏳ {credential_set} placed in 3-hour cooldown until {time.strftime('%H:%M:%S', time.localtime(cooldown_start + quota_manager.COOLDOWN_DURATION))}")
                logger.info(f"🔄 Rotating to next credential set...")
                continue
            else:
                logger.error(f"❌ HTTP error with {credential_set}: {e}")
                continue
        except Exception as e:
            logger.error(f"❌ Failed to authenticate with {credential_set}: {e}")
            continue
    
    logger.critical("❌ Failed to authenticate with any credential set")
    return None

def start_credential_cooldown(credential_set: str):
    """Manually start the cooldown period for a specific credential set."""
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ Manually placing {credential_set} into cooldown due to external failure (e.g., quota exceeded post-auth).")
    quota_manager.start_cooldown(credential_set)

# Example usage and testing
if __name__ == '__main__':
    from utils.logging_config import setup_logging
    setup_logging()
    
    auth_result = get_authenticated_service_with_fallback()
    if auth_result:
        service, credentials, credential_set = auth_result
    else:
        service = None
    if service:
        try:
            # Test the service
            response = service.channels().list(part='snippet', mine=True).execute()
            channel_title = response['items'][0]['snippet']['title']
            logger.info(f"Successfully authenticated as channel: {channel_title}")
        except Exception as e:
            logger.error(f"Failed to test service: {e}") 