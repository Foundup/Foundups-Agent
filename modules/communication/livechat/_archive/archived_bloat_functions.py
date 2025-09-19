"""
ARCHIVED FUNCTIONS - Potential Bloat from auto_moderator_dae.py
Date: 2025-09-10
Reason: Potentially unnecessary complexity - archive before deletion

These functions were removed during bloat reduction but archived for safety.
If system works fine without them, they can be permanently deleted.
"""

import logging
import os
import json
from datetime import datetime

logger = logging.getLogger(__name__)


async def verify_channels_live_status_ARCHIVED(self) -> bool:
    """
    🚨 ENHANCEMENT: Verify @UnDaoDu and Move2Japan are actually live

    This method performs an independent verification check that can be called
    before any social media posting to ensure 012 is actually broadcasting.

    Returns True only if at least one of the specified channels is confirmed live.
    
    ARCHIVED: This might be over-engineering - the existing stream resolver
    should already verify streams are live.
    """
    try:
        logger.info("🚨 [ENHANCEMENT TRIGGER] Checking @UnDaoDu and Move2Japan live status...")

        # Use the existing stream resolver for verification
        if not self.stream_resolver:
            from modules.platform_integration.stream_resolver.src.stream_resolver import StreamResolver
            self.stream_resolver = StreamResolver(self.service)

        # Channels to verify (as specified by user)
        verification_channels = [
            os.getenv('CHANNEL_ID', 'UCklMTNnu5POwRmQsg5JJumA'),  # @UnDaoDu
            # TODO: Add Move2Japan channel ID when identified
        ]

        # Filter out None values
        verification_channels = [ch for ch in verification_channels if ch]

        if not verification_channels:
            logger.warning("🚨 [ENHANCEMENT TRIGGER] No channels configured for verification")
            return False

        # Check each channel for active live streams
        for channel_id in verification_channels:
            try:
                logger.info(f"🚨 [ENHANCEMENT TRIGGER] Verifying channel: {channel_id}")
                result = self.stream_resolver.resolve_stream(channel_id)

                if result and result[0] and result[1]:
                    video_id, live_chat_id = result

                    # Additional verification: Check if stream is actually running
                    video_response = self.service.videos().list(
                        part="liveStreamingDetails,status",
                        id=video_id
                    ).execute()

                    if video_response.get("items"):
                        video_item = video_response["items"][0]
                        live_details = video_item.get("liveStreamingDetails", {})
                        status = video_item.get("status", {})

                        # Must have actualStartTime and no actualEndTime (actively live)
                        if (live_details.get("actualStartTime") and
                            not live_details.get("actualEndTime") and
                            status.get("privacyStatus") != "private"):

                            logger.info(f"🚨 [ENHANCEMENT TRIGGER] ✅ VERIFICATION PASSED!")
                            logger.info(f"🚨 [ENHANCEMENT TRIGGER] 📺 Channel {channel_id} is LIVE")
                            logger.info(f"🚨 [ENHANCEMENT TRIGGER] 🎬 Video ID: {video_id}")
                            return True
                        else:
                            logger.info(f"🚨 [ENHANCEMENT TRIGGER] ⏸️ Channel {channel_id} stream not actively live")

            except Exception as e:
                logger.warning(f"🚨 [ENHANCEMENT TRIGGER] Error verifying channel {channel_id}: {e}")
                continue

        logger.warning("🚨 [ENHANCEMENT TRIGGER] ❌ VERIFICATION FAILED")
        logger.warning("🚨 [ENHANCEMENT TRIGGER] 💡 @UnDaoDu and Move2Japan are not currently live")
        return False

    except Exception as e:
        logger.error(f"🚨 [ENHANCEMENT TRIGGER] Verification error: {e}")
        return False


async def _track_live_pattern_ARCHIVED(self):
    """
    🎯 TRACK WHEN 012 NORMALLY GOES LIVE
    Agentic learning: Record successful live detection times for pattern recognition.
    
    ARCHIVED: This pattern learning might be useful, but adds complexity.
    Archive to see if system works fine without it.
    """
    try:
        current_time = datetime.now()
        weekday = current_time.strftime("%A")  # Monday, Tuesday, etc.
        hour = current_time.hour  # 0-23
        time_key = f"{weekday}_{hour:02d}:00"

        # Load existing patterns
        pattern_file = "memory/live_patterns.json"
        try:
            with open(pattern_file, 'r') as f:
                live_patterns = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            live_patterns = {}

        # Track this live detection
        if time_key not in live_patterns:
            live_patterns[time_key] = {
                "count": 0,
                "last_seen": None,
                "confidence": 0.0
            }

        pattern = live_patterns[time_key]
        pattern["count"] += 1
        pattern["last_seen"] = current_time.isoformat()
        pattern["confidence"] = min(1.0, pattern["count"] / 10.0)  # Max confidence after 10 detections

        # Save updated patterns
        with open(pattern_file, 'w') as f:
            json.dump(live_patterns, f, indent=2)

        logger.info(f"📊 Live pattern tracked: {time_key} (confidence: {pattern['confidence']:.2f})")

    except Exception as e:
        logger.debug(f"Live pattern tracking error: {e}")


# Archive note: These functions were extracted during bloat reduction
# If the system works fine after 1 week without them, they can be permanently deleted
