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
    # os.getenv() automatically checks the current environment dictionary (os.environ),
    # which has been populated/updated by the load_dotenv calls above.
    value = os.getenv(key, default)

    # Log a warning only if the key was truly not found *and* no fallback was provided
    if value is None and default is None:
        logger.warning(f"Environment variable '{key}' not found and no default value was provided.")
    else:
        logger.debug(f"Retrieved environment variable '{key}' with value: {value}")

    return value 