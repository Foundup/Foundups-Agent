#!/usr/bin/env python3
"""
Force OAuth re-authorization for a specific YouTube credential set.

Usage:
  python tools/oauth_force_reauth.py <set_number>

Where <set_number> is 1-5.
"""

import os
import sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/oauth_force_reauth.py <set_number>")
        sys.exit(1)

    try:
        set_num = int(sys.argv[1])
    except ValueError:
        print("<set_number> must be an integer 1-5")
        sys.exit(1)

    if set_num < 1 or set_num > 5:
        print("<set_number> must be between 1 and 5")
        sys.exit(1)

    # Ensure project root on sys.path for module imports
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Map env vars expected by youtube_auth helper
    os.environ.setdefault(f"GOOGLE_CLIENT_SECRETS_FILE_{set_num}", f"credentials/client_secret{set_num}.json")
    os.environ.setdefault(f"OAUTH_TOKEN_FILE_{set_num}", f"credentials/oauth_token{set_num}.json")

    token_path = os.environ[f"OAUTH_TOKEN_FILE_{set_num}"]

    # Clear token to force interactive flow
    try:
        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, "w", encoding="utf-8") as f:
            f.write("{}")
    except Exception as e:
        print(f"Failed to prepare token file {token_path}: {e}")
        # Continue; flow will still run

    print(f"Starting OAuth flow for set {set_num}. A browser window will open.")

    # Import here to ensure env is set
    from modules.platform_integration.youtube_auth.src import youtube_auth as ya

    # youtube_auth expects 0-based index in token_index
    svc = ya.get_authenticated_service(token_index=set_num - 1)

    if svc:
        print(f"Success. Credentials updated: {token_path}")
    else:
        print("OAuth flow completed but service not returned. Check logs for details.")

if __name__ == "__main__":
    main()


