"""
Moderator Lookup - Query existing auto_moderator.db for mod status

Module: communication/video_comments
WSP Reference: WSP 72 (Module Independence - reuse existing database)
Status: Production

This module provides read-only access to the existing auto_moderator.db
database maintained by the livechat module. NO schema modifications.
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)


class ModeratorLookup:
    """
    Query existing auto_moderator.db without modifying schema.

    Database Location: modules/communication/livechat/memory/auto_moderator.db
    Schema: Managed by livechat/AutoModeratorDAE
    Access: READ-ONLY

    Tables Used:
        users (user_id, username, role, last_seen, message_count)
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize moderator lookup.

        Args:
            db_path: Override default database path (for testing)
        """
        if db_path is None:
            self.db_path = Path("modules/communication/livechat/memory/auto_moderator.db")
        else:
            self.db_path = db_path

        if not self.db_path.exists():
            logger.warning(f"[MOD-LOOKUP] Database not found: {self.db_path}")
            logger.warning("[MOD-LOOKUP] Moderator detection will be disabled")
            self.db_available = False
        else:
            self.db_available = True
            logger.info(f"[MOD-LOOKUP] Connected to: {self.db_path}")

    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """
        Query user by YouTube channel ID.

        Args:
            user_id: YouTube channel ID (e.g., "UC-LSSlOZwpGIRIYihaz8zCw")

        Returns:
            {
                'user_id': str,
                'username': str,
                'role': str,           # "OWNER", "MOD", "USER"
                'last_seen': datetime,
                'message_count': int
            }
            or None if user not found
        """
        if not self.db_available:
            return None

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT user_id, username, role, last_seen, message_count "
                "FROM users WHERE user_id = ?",
                (user_id,)
            )

            row = cursor.fetchone()
            conn.close()

            if not row:
                logger.debug(f"[MOD-LOOKUP] User not found: {user_id}")
                return None

            user = {
                'user_id': row[0],
                'username': row[1],
                'role': row[2],
                'last_seen': datetime.fromisoformat(row[3]) if row[3] else None,
                'message_count': row[4]
            }

            logger.debug(f"[MOD-LOOKUP] Found user: {user['username']} (Role: {user['role']})")
            return user

        except Exception as e:
            logger.error(f"[MOD-LOOKUP] Database query failed: {e}")
            return None

    def is_moderator(
        self,
        user_id: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if user has moderator role (MOD or OWNER).

        USER INSIGHT (2025-12-24): "mods do not need to be active they just need to
        be accounted for... its not about active... if they whack trolls they are a mod"

        Args:
            user_id: YouTube channel ID

        Returns:
            (is_mod: bool, username: Optional[str])

        Examples:
            >>> lookup = ModeratorLookup()
            >>> is_mod, name = lookup.is_moderator("UC_2AskvFe9uqp9maCS6bohg")
            >>> if is_mod:
            ...     print(f"{name} is a moderator!")
        """
        if not self.db_available:
            return (False, None)

        user = self.get_user_info(user_id)

        if not user:
            return (False, None)

        # Check role (that's all that matters - role = moderator!)
        if user['role'] in ('MOD', 'OWNER'):
            logger.info(f"[MOD-LOOKUP] ✅ MODERATOR: {user['username']} (role: {user['role']})")
            return (True, user['username'])
        else:
            logger.debug(f"[MOD-LOOKUP] User {user['username']} is not a moderator (role: {user['role']})")
            return (False, None)

    def is_active_moderator(
        self,
        user_id: str,
        activity_window_minutes: int = 10
    ) -> Tuple[bool, Optional[str]]:
        """
        DEPRECATED: Use is_moderator() instead.

        Check if user is a moderator who was active in last N minutes.

        DESIGN NOTE: This method is deprecated because moderator status is a ROLE,
        not an activity measure. Kept for backward compatibility only.

        Args:
            user_id: YouTube channel ID
            activity_window_minutes: Consider user "active" if last_seen within N minutes

        Returns:
            (is_active_mod: bool, username: Optional[str])
        """
        # Just call is_moderator() - activity doesn't matter for mod status
        return self.is_moderator(user_id)

    def sync_moderators_from_api(
        self,
        youtube_service,
        live_chat_id: str
    ) -> int:
        """
        Pull moderator list from YouTube API and sync to database.

        USER INSIGHT (2025-12-24): Research YouTube API - pull channel mods directly
        instead of relying on chat activity to populate database.

        API: GET https://www.googleapis.com/youtube/v3/liveChat/moderators
        Required: liveChatId, part=snippet
        Quota: Unknown (likely 1-5 units)

        Args:
            youtube_service: Authenticated YouTube API service
            live_chat_id: Live chat ID to pull moderators from

        Returns:
            Number of moderators synced to database

        Example:
            >>> from modules.platform_integration.youtube_auth import get_youtube_service
            >>> service = get_youtube_service()
            >>> lookup = ModeratorLookup()
            >>> count = lookup.sync_moderators_from_api(service, live_chat_id)
            >>> print(f"Synced {count} moderators")
        """
        if not self.db_available:
            logger.error("[MOD-LOOKUP] Database unavailable - cannot sync")
            return 0

        try:
            # Call YouTube API liveChatModerators.list
            request = youtube_service.liveChatModerators().list(
                liveChatId=live_chat_id,
                part="snippet",
                maxResults=50  # Max allowed per page
            )

            moderators_synced = 0
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            while request is not None:
                response = request.execute()

                for item in response.get('items', []):
                    snippet = item.get('snippet', {})
                    moderator_details = snippet.get('moderatorDetails', {})

                    channel_id = moderator_details.get('channelId')
                    display_name = moderator_details.get('displayName')

                    if not channel_id or not display_name:
                        continue

                    # Insert or update in database
                    cursor.execute('''
                        INSERT OR REPLACE INTO users (user_id, username, role, last_seen, message_count)
                        VALUES (?, ?, 'MOD', ?, COALESCE((SELECT message_count FROM users WHERE user_id = ?), 0))
                    ''', (channel_id, display_name, datetime.now().isoformat(), channel_id))

                    moderators_synced += 1
                    logger.info(f"[MOD-LOOKUP] Synced moderator: {display_name} ({channel_id})")

                # Handle pagination
                request = youtube_service.liveChatModerators().list_next(request, response)

            conn.commit()
            conn.close()

            logger.info(f"[MOD-LOOKUP] ✅ Synced {moderators_synced} moderators from YouTube API")
            return moderators_synced

        except Exception as e:
            logger.error(f"[MOD-LOOKUP] Failed to sync from API: {e}")
            return 0

    def get_all_active_moderators(
        self,
        activity_window_minutes: int = 10
    ) -> list[Dict]:
        """
        Get all moderators active within last N minutes.

        Returns:
            [
                {'user_id': str, 'username': str, 'role': str, 'last_seen': datetime},
                ...
            ]
        """
        if not self.db_available:
            return []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cutoff = datetime.now() - timedelta(minutes=activity_window_minutes)
            cutoff_str = cutoff.isoformat()

            cursor.execute(
                "SELECT user_id, username, role, last_seen "
                "FROM users "
                "WHERE role IN ('MOD', 'OWNER') AND last_seen >= ?",
                (cutoff_str,)
            )

            rows = cursor.fetchall()
            conn.close()

            active_mods = []
            for row in rows:
                active_mods.append({
                    'user_id': row[0],
                    'username': row[1],
                    'role': row[2],
                    'last_seen': datetime.fromisoformat(row[3]) if row[3] else None
                })

            logger.info(f"[MOD-LOOKUP] Found {len(active_mods)} active moderators")
            return active_mods

        except Exception as e:
            logger.error(f"[MOD-LOOKUP] Failed to get active moderators: {e}")
            return []


# CLI test interface
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    lookup = ModeratorLookup()

    # Test 1: Query specific user
    print("\n=== Test 1: Query specific moderator ===")
    is_mod, name = lookup.is_active_moderator("UC_2AskvFe9uqp9maCS6bohg", activity_window_minutes=10080)  # 1 week
    print(f"Result: is_mod={is_mod}, name={name}")

    # Test 2: Get all active mods
    print("\n=== Test 2: All active moderators ===")
    active = lookup.get_all_active_moderators(activity_window_minutes=10080)  # 1 week
    for mod in active:
        print(f"  {mod['username']} ({mod['role']}) - last seen: {mod['last_seen']}")

    # Test 3: Query regular user
    print("\n=== Test 3: Query regular user ===")
    is_mod, name = lookup.is_active_moderator("UCJ-uCjcvW4sDNVE1WDp8tpQ", activity_window_minutes=10080)
    print(f"Result: is_mod={is_mod}, name={name}")
