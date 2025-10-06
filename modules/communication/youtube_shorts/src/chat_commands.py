"""
YouTube Shorts Chat Commands

Integration with LiveChat command system.
Allows channel OWNER and #1 MAGADOOM leader to create Shorts via chat commands.

Commands:
- !createshort <topic> - Create and upload Short (OWNER or TOP LEADER #1)
- !shortstatus - Check Shorts generation status
- !shortstats - View Shorts statistics

Permission System:
- Channel OWNER: Can always use !createshort (no rate limit)
- #1 MAGADOOM HGS leader: Can use !createshort (once per week)
- Everyone else: Blocked
- Rate limit for leaders: Once per week (7 days)
- Checks leaderboard database: modules/gamification/whack_a_magat/data/magadoom_scores.db
"""

import logging
import threading
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path
from .shorts_orchestrator import ShortsOrchestrator

logger = logging.getLogger(__name__)


def normalize_channel_name(channel_name: str) -> str:
    """
    Normalize channel display name to orchestrator format.

    Maps channel display names (with emojis) to shorts orchestrator format:
    - "Move2Japan 🍣" or "Move2Japan" → "move2japan"
    - "UnDaoDu 🧘" or "UnDaoDu" → "undaodu"
    - "FoundUps 🐕" or "FoundUps" → "foundups"

    Args:
        channel_name: Channel display name (may include emojis)

    Returns:
        str: Normalized channel name for orchestrator
    """
    if not channel_name:
        return "move2japan"  # Safe default

    # Remove emojis and clean
    clean = channel_name.strip().split()[0].lower()

    # Map known channels
    if "move2japan" in clean or "move" in clean:
        return "move2japan"
    elif "undaodu" in clean or "undao" in clean:
        return "undaodu"
    elif "foundups" in clean or "found" in clean:
        return "foundups"
    else:
        # Unknown channel - default to move2japan with warning
        logger.warning(f"[ShortsChat] Unknown channel '{channel_name}' - defaulting to move2japan")
        return "move2japan"


class ShortsCommandHandler:
    """
    Handle YouTube Shorts commands from LiveChat.

    Permissions:
    - Channel OWNER: Unlimited !createshort access
    - #1 MAGADOOM leader: !createshort once per week
    - Everyone else: Blocked
    """

    def __init__(self, channel: str = "move2japan"):
        """
        Initialize Shorts command handler.

        Args:
            channel: YouTube channel ("move2japan", "undaodu", or "foundups")
        """
        # Normalize channel name
        self.channel = normalize_channel_name(channel)
        self.orchestrator = ShortsOrchestrator(channel=self.channel)

        # Track ongoing generations (prevent spam)
        self.generating = False
        self.last_generation_user = None

        # Weekly rate limit tracking
        module_root = Path(__file__).parent.parent
        self.rate_limit_file = module_root / "memory" / "weekly_rate_limit.json"
        self.rate_limit_file.parent.mkdir(parents=True, exist_ok=True)

        # MAGADOOM leaderboard database path
        self.leaderboard_db = Path("modules/gamification/whack_a_magat/data/magadoom_scores.db")

        logger.info(f"[ShortsCommandHandler] Initialized for channel: {self.channel.upper()}")
        logger.info(f"[ShortsCommandHandler] Permissions: OWNER (unlimited) + #1 MAGADOOM leader (weekly)")

    def handle_super_chat_short(
        self,
        donor_name: str,
        donor_id: str,
        amount_usd: float,
        message: str
    ) -> Optional[str]:
        """
        Handle Super Chat Short creation for $20+ donations.

        Args:
            donor_name: Super Chat donor's display name
            donor_id: Donor's YouTube channel ID
            amount_usd: Donation amount in USD
            message: Super Chat message text (used as topic)

        Returns:
            str: Response message, or None if donation < $20
        """

        # Check minimum donation amount ($20)
        if amount_usd < 20.0:
            return None  # Not enough for Short creation

        # Check if already generating
        if self.generating:
            return f"@{donor_name} 💰 Thank you for the ${amount_usd:.2f} Super Chat! Short generation in progress by @{self.last_generation_user}. Please wait!"

        # Extract topic from Super Chat message
        topic = message.strip()

        if not topic:
            return f"@{donor_name} 💰 Thank you for the ${amount_usd:.2f} Super Chat! Please include your video topic in the message. Example: 'Cherry blossoms in Tokyo'"

        # Start generation in background thread
        self.generating = True
        self.last_generation_user = donor_name

        def generate_in_background():
            try:
                logger.info(f"[ShortsChat] 💰 {donor_name} (${amount_usd:.2f} SC) requested Short: {topic}")

                # Generate and upload (15 seconds, public)
                # 15 seconds = $6 cost (better economics: $20 donation - $6 = $14 profit vs $8)
                youtube_url = self.orchestrator.create_and_upload(
                    topic=topic,
                    duration=15,
                    privacy="public"
                )

                logger.info(f"[ShortsChat] ✅ Super Chat Short created: {youtube_url}")

                # Note: Response posted to chat would require chat_sender
                # For now, just log success. Full integration needs chat_sender access.

            except Exception as e:
                logger.error(f"[ShortsChat] ❌ Super Chat generation failed: {e}")

            finally:
                self.generating = False

        # Start background thread
        thread = threading.Thread(target=generate_in_background, daemon=True)
        thread.start()

        return f"@{donor_name} 💰 Thank you for the ${amount_usd:.2f} Super Chat! Creating YouTube Short for: '{topic}' | This will take 1-2 minutes... 🎥✨"

    def handle_shorts_command(
        self,
        text: str,
        username: str,
        user_id: str,
        role: str
    ) -> Optional[str]:
        """
        Handle Shorts-related commands.

        Args:
            text: Command text (e.g., "!createshort Cherry blossoms")
            username: User's display name
            user_id: User's YouTube ID
            role: User's role (OWNER, MODERATOR, VIEWER)

        Returns:
            str: Response message, or None if not a Shorts command
        """

        text_lower = text.lower().strip()

        # Command: !createshort <topic>
        if text_lower.startswith('!createshort'):
            return self._handle_create_short(text, username, user_id, role)

        # Command: !shortstatus
        elif text_lower == '!shortstatus':
            return self._handle_short_status(username)

        # Command: !shortstats
        elif text_lower == '!shortstats':
            return self._handle_short_stats(username)

        # Not a Shorts command
        return None

    def _get_top_leader(self) -> Optional[tuple]:
        """
        Get current #1 MAGADOOM leader from database.

        Returns:
            tuple: (username, user_id, score) or None if no data
        """
        try:
            conn = sqlite3.connect(str(self.leaderboard_db))
            cursor = conn.cursor()

            cursor.execute('''
                SELECT username, user_id, score
                FROM profiles
                ORDER BY score DESC
                LIMIT 1
            ''')

            result = cursor.fetchone()
            conn.close()

            return result

        except Exception as e:
            logger.error(f"[ShortsChat] Failed to query leaderboard: {e}")
            return None

    def _check_weekly_limit(self, username: str) -> tuple:
        """
        Check if user has used their weekly Short.

        Returns:
            tuple: (can_post: bool, message: str)
        """
        try:
            # Load rate limit data
            if self.rate_limit_file.exists():
                with open(self.rate_limit_file) as f:
                    rate_data = json.load(f)
            else:
                rate_data = {}

            # Check last post time
            if username in rate_data:
                last_post = datetime.fromisoformat(rate_data[username]['last_post'])
                next_allowed = last_post + timedelta(days=7)
                now = datetime.now()

                if now < next_allowed:
                    days_left = (next_allowed - now).days + 1
                    return False, f"Weekly limit reached! Next Short available in {days_left} days."

            return True, "OK"

        except Exception as e:
            logger.error(f"[ShortsChat] Rate limit check failed: {e}")
            return True, "OK"  # Fail open

    def _record_post(self, username: str):
        """Record that user posted a Short (for weekly limit)."""
        try:
            # Load existing data
            if self.rate_limit_file.exists():
                with open(self.rate_limit_file) as f:
                    rate_data = json.load(f)
            else:
                rate_data = {}

            # Record post time
            rate_data[username] = {
                'last_post': datetime.now().isoformat(),
                'username': username
            }

            # Save
            with open(self.rate_limit_file, 'w') as f:
                json.dump(rate_data, f, indent=2)

        except Exception as e:
            logger.error(f"[ShortsChat] Failed to record post: {e}")

    def _handle_create_short(
        self,
        text: str,
        username: str,
        user_id: str,
        role: str
    ) -> str:
        """
        Handle !createshort <topic> command.

        Permissions:
        - Channel OWNER: Always allowed (no rate limit)
        - #1 MAGADOOM leader: Allowed once per week
        - Everyone else: Blocked
        """

        # Get current #1 leader
        top_leader = self._get_top_leader()

        if not top_leader:
            return f"@{username} 🎬 Could not verify leaderboard status. Try again later."

        top_username, top_user_id, top_score = top_leader

        # Check permissions: OWNER always allowed, or #1 MAGADOOM leader
        is_owner = (role == "OWNER")
        is_top_leader = (username == top_username) or (user_id == top_user_id)

        if not is_owner and not is_top_leader:
            return f"@{username} 🎬 Only the channel OWNER or #1 MAGADOOM leader can create Shorts! Current leader: @{top_username} ({top_score:,} XP)"

        # Log permission grant
        if is_owner:
            logger.info(f"[ShortsChat] ✅ {username} authorized as channel OWNER (no rate limit)")
        elif is_top_leader:
            logger.info(f"[ShortsChat] ✅ {username} authorized as #1 MAGADOOM leader ({top_score:,} XP)")

        # Check weekly rate limit (OWNER is exempt)
        if not is_owner:
            can_post, limit_msg = self._check_weekly_limit(username)

            if not can_post:
                return f"@{username} 🎬 {limit_msg}"

        # Check if already generating
        if self.generating:
            return f"@{username} 🎬 Short already being generated by @{self.last_generation_user}. Please wait!"

        # Extract topic from command
        topic = text[len('!createshort'):].strip()

        if not topic:
            return f"@{username} 🎬 Usage: !createshort <topic>  Example: !createshort Cherry blossoms in Tokyo"

        # Record post for weekly limit
        self._record_post(username)

        # Start generation in background thread
        self.generating = True
        self.last_generation_user = username

        def generate_in_background():
            try:
                logger.info(f"[ShortsChat] {username} requested Short: {topic}")

                # Generate and upload (30 seconds, public)
                youtube_url = self.orchestrator.create_and_upload(
                    topic=topic,
                    duration=30,
                    privacy="public"
                )

                logger.info(f"[ShortsChat] ✅ Short created: {youtube_url}")

                # Note: Response posted to chat would require chat_sender
                # For now, just log success. Full integration needs chat_sender access.

            except Exception as e:
                logger.error(f"[ShortsChat] ❌ Generation failed: {e}")

            finally:
                self.generating = False

        # Start background thread
        thread = threading.Thread(target=generate_in_background, daemon=True)
        thread.start()

        return f"@{username} 🎬 Creating YouTube Short for: '{topic}' | This will take 1-2 minutes... 🎥✨"

    def _handle_short_status(self, username: str) -> str:
        """Handle !shortstatus command."""

        if self.generating:
            return f"@{username} 🎬 Short generation in progress by @{self.last_generation_user}... ⏳"
        else:
            stats = self.orchestrator.get_stats()
            recent_count = min(len(stats.get('recent_shorts', [])), 5)

            return f"@{username} 🎬 No active generation | Last {recent_count} Shorts ready!"

    def _handle_short_stats(self, username: str) -> str:
        """Handle !shortstats command."""

        stats = self.orchestrator.get_stats()

        total = stats.get('total_shorts', 0)
        cost = stats.get('total_cost_usd', 0.0)
        uploaded = stats.get('uploaded', 0)

        return f"@{username} 📊 YouTube Shorts Stats | Total: {total} | Uploaded: {uploaded} | Cost: ${cost:.2f} USD"


# Per-channel handler cache (not singleton - we need one per channel!)
_shorts_handlers = {}


def get_shorts_handler(channel: str = "move2japan") -> ShortsCommandHandler:
    """
    Get Shorts command handler for specific channel.

    Args:
        channel: YouTube channel name (move2japan, undaodu, foundups)

    Returns:
        ShortsCommandHandler: Channel-specific handler instance
    """
    global _shorts_handlers

    # Normalize channel name
    normalized = normalize_channel_name(channel)

    # Create handler if doesn't exist for this channel
    if normalized not in _shorts_handlers:
        logger.info(f"[ShortsChat] Creating new handler for channel: {normalized.upper()}")
        _shorts_handlers[normalized] = ShortsCommandHandler(channel=normalized)

    return _shorts_handlers[normalized]


if __name__ == "__main__":
    # Test the handler
    handler = get_shorts_handler()

    # Simulate OWNER command
    response = handler.handle_shorts_command(
        text="!createshort Cherry blossoms in Tokyo",
        username="TestOwner",
        user_id="owner123",
        role="OWNER"
    )

    print(f"Response: {response}")

    # Check status
    status = handler.handle_shorts_command(
        text="!shortstatus",
        username="TestUser",
        user_id="user456",
        role="VIEWER"
    )

    print(f"Status: {status}")
