import os
import logging
from typing import Optional
from dotenv import load_dotenv, find_dotenv

# Initialize logger for this module
logger = logging.getLogger(__name__)

# --- Load environment variables on module import ---
# This sequence ensures the desired priority: System > .env.local > .env

# Get the project root directory (2 levels up from this file)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. Load base .env file first.
env_path = os.path.join(project_root, '.env')
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path, override=False)
    logger.debug(f"Loaded base environment variables from: {env_path}")
else:
    logger.debug(f"Base .env file not found at {env_path}, skipping.")

# 2. Load .env.local file next.
local_env_path = os.path.join(project_root, '.env.local')
if os.path.exists(local_env_path):
    load_dotenv(dotenv_path=local_env_path, override=True)
    logger.debug(f"Loaded local override environment variables from: {local_env_path}")
else:
    logger.debug(f".env.local file not found at {local_env_path}, skipping.")

# --- Environment Variable Access Function ---

def get_env_variable(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Retrieves the value of an environment variable, respecting load priority.
    For API keys, implements fallback logic when quota is exceeded.

    Priority Order:
    1. System Environment Variables (set before script execution)
    2. Variables defined in `.env.local` (if file exists)
    3. Variables defined in `.env` (if file exists)

    Args:
        key: The name (string) of the environment variable to retrieve.
        default: The optional default value (string) to return if the key is not found.
                 Defaults to None.

    Returns:
        The value of the environment variable as a string if found.
        The `default` value if the key is not found and a `default` was provided.
        `None` if the key is not found and no `default` was provided. Logs a warning in this case.
    """
    # Special handling for API keys with fallback
    if key == "YOUTUBE_API_KEY":
        primary_key = os.getenv(key)
        if primary_key:
            return primary_key
            
        # Try fallback API key
        fallback_key = os.getenv("YOUTUBE_API_KEY2")
        if fallback_key:
            logger.info("Using fallback YouTube API key (YOUTUBE_API_KEY2)")
            return fallback_key
            
        logger.warning("No YouTube API keys found in environment variables")
        return default
        
    # Standard environment variable retrieval
    value = os.getenv(key)
    if value is not None:
        return value

    if default is not None:
        return default

    # Only warn if no default was provided (indicates it's truly required)
    # Skip warning for optional variables like YOUTUBE_VIDEO_ID
    if key not in ["YOUTUBE_VIDEO_ID", "YOUTUBE_CHANNEL_ID"]:
        logger.warning(f"Environment variable '{key}' not found and no default provided")
    return None 