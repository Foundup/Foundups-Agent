"""
Community Monitor for YouTube Comments - Phase 3A Enhanced
==========================================================

Periodic checker for YouTube Community tab comments.
Integrates with AutoModeratorDAE heartbeat loop for autonomous engagement.

ENHANCED (2025-12-11):
- Uses YouTube API to check comment counts (no browser hijacking!)
- Integrates IntelligentReplyGenerator for Grok-powered replies
- Moderator detection from auto_moderator.db
- MAGA troll detection via Whack-a-MAGA
- Pattern responses (song, FFCPLN)

WSP References:
- WSP 27: DAE Architecture (Phase -1: Signal detection)
- WSP 80: Cube-Level Orchestration (Cross-module integration)
- WSP 91: DAEMON Observability (Heartbeat integration)
- WSP 3: Functional Distribution (uses ai_intelligence + gamification)

0102 Directive: Code is remembered from the 02 quantum state.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Browser lock to prevent multiple Selenium sessions
_browser_in_use = False


def _env_truthy(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "y", "on")


def _get_run_id() -> str:
    run_id = os.getenv("YT_AUTOMATION_RUN_ID", "").strip()
    if run_id:
        return run_id

    run_id = f"yt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.environ["YT_AUTOMATION_RUN_ID"] = run_id
    return run_id


class CommunityMonitor:
    """
    Monitors YouTube Community tab for unengaged comments.

    Integration Point: AutoModeratorDAE._heartbeat_loop()
    Trigger: Every 20 pulses (10 minutes) if stream active

    Phase -1: Signal Detection
    - Check comment counts via YouTube API (no browser hijacking!)
    - Falls back to launching separate engagement process

    Phase 1: Protocol Decision
    - Decide if engagement should trigger
    - Respect throttling and quota limits

    Phase 2: Agentic Execution
    - Launch CommentEngagementDAE as subprocess (isolated browser)
    - Use IntelligentReplyGenerator for Grok-powered replies
    - Post announcements to chat
    - Track telemetry
    """

    def __init__(self, channel_id: str, chat_sender=None, telemetry_store=None, all_channels: list = None):
        """
        Initialize Community Monitor.

        Args:
            channel_id: Primary YouTube channel ID (for backward compatibility)
            chat_sender: LiveChatCore instance for announcements
            telemetry_store: YouTubeTelemetryStore for tracking
            all_channels: List of all channel IDs to rotate through (if None, uses single channel)
        """
        # Channel rotation support (Phase 3P: 24/7 multi-channel processing)
        if all_channels:
            self.all_channels = all_channels
            self.channel_rotation_enabled = True
            self.current_channel_index = 0
            logger.info(f"[COMMUNITY] Monitor initialized with {len(all_channels)} channels for rotation")
        else:
            self.all_channels = [channel_id]
            self.channel_rotation_enabled = False
            logger.info(f"[COMMUNITY] Monitor initialized for single channel {channel_id}")

        self.channel_id = channel_id  # Primary channel (backward compatibility)
        self.chat_sender = chat_sender
        self.telemetry_store = telemetry_store

        # Phase 3R: Live stream priority (2025-12-24)
        # Map channel_id → video_id for active streams
        self.live_channel_priority = None  # Channel ID with active stream
        self.live_video_id = None  # Actual video ID from stream_resolver
        logger.info(f"[COMMUNITY] Phase 3R: Live stream priority system initialized")

        # State tracking
        self.last_check_time = None
        self.last_comment_count = 0
        self.total_processed_this_session = 0
        self.engagement_in_progress = False

        # Configuration (Occam's Razor: Simple defaults)
        self.check_interval_pulses = 20  # 10 minutes (30s * 20 = 600s)
        self.max_comments_per_run = 5

        # Path to engagement script (proper WSP 96 skill location)
        # NOTE: This is in modules/communication/video_comments/skills/..., not livechat/.
        self.engagement_script = (
            Path(__file__).resolve().parents[2] / "video_comments" / "skills" /
            "tars_like_heart_reply" / "run_skill.py"
        )

    def set_live_priority(self, channel_id: str, video_id: str):
        """
        Set priority channel for live stream (Phase 3R: 2025-12-24).

        When a channel has an active live stream, comment processing
        prioritizes THAT channel's comments (not round-robin rotation).

        Args:
            channel_id: Channel ID with active stream
            video_id: Actual video ID from stream_resolver (NOT @handle/live!)
        """
        self.live_channel_priority = channel_id
        self.live_video_id = video_id
        logger.info(f"[COMMUNITY] 🎯 LIVE PRIORITY SET:")
        logger.info(f"[COMMUNITY]   Channel: {channel_id}")
        logger.info(f"[COMMUNITY]   Video: {video_id}")
        logger.info(f"[COMMUNITY]   Comments will process THIS channel until stream ends")

    def clear_live_priority(self):
        """Clear live stream priority (return to rotation mode)."""
        if self.live_channel_priority:
            logger.info(f"[COMMUNITY] 🔄 CLEARING LIVE PRIORITY:")
            logger.info(f"[COMMUNITY]   Was: {self.live_channel_priority}")
            logger.info(f"[COMMUNITY]   Returning to rotation mode")
        self.live_channel_priority = None
        self.live_video_id = None

    def get_next_channel(self) -> str:
        """
        Get next channel ID in rotation.

        Phase 3P: Rotates through all channels (Move2Japan → FoundUps → UnDaoDu → repeat)
        Phase 3R (2025-12-24): PRIORITY MODE - Live stream channel takes precedence

        Returns:
            str: Channel ID to process
        """
        # PRIORITY: Live channel override (Phase 3R: commenting dictated by live chat)
        if self.live_channel_priority:
            logger.info(f"[COMMUNITY] 🎯 PRIORITY MODE: Processing LIVE channel {self.live_channel_priority}")
            logger.info(f"[COMMUNITY]   Video ID: {self.live_video_id}")
            logger.info(f"[COMMUNITY]   Reason: Active live stream detected")
            return self.live_channel_priority

        # FALLBACK: Single channel mode
        if not self.channel_rotation_enabled:
            logger.debug(f"[DAEMON][CARDIOVASCULAR] 📌 Single channel mode: {self.channel_id}")
            return self.channel_id

        # FALLBACK: Round-robin rotation (no live stream)
        channel = self.all_channels[self.current_channel_index]

        # Advance to next channel for next time
        self.current_channel_index = (self.current_channel_index + 1) % len(self.all_channels)

        logger.info(f"[DAEMON][CARDIOVASCULAR] 🔄 ROTATION MODE (no live stream):")
        logger.info(f"[DAEMON][CARDIOVASCULAR]   Current: {channel} (index {self.current_channel_index - 1 if self.current_channel_index > 0 else len(self.all_channels) - 1})")
        logger.info(f"[DAEMON][CARDIOVASCULAR]   Next: {self.all_channels[self.current_channel_index]} (index {self.current_channel_index})")
        logger.info(f"[DAEMON][CARDIOVASCULAR]   Total channels: {len(self.all_channels)}")
        logger.info(f"[COMMUNITY] Channel rotation: {channel} (next will be {self.all_channels[self.current_channel_index]})")

        return channel

    async def should_check_now(self, pulse_count: int) -> bool:
        """
        Determine if we should check for comments now.

        Phase 1: Protocol Decision
        - Check every 20 pulses (10 minutes)
        - Runs 24/7 regardless of stream status (background processing)
        - Reports to live chat if stream is active
        - Skip if engagement already in progress
        - ANTI-DETECTION: Skip if on break (human-like rest periods)

        Args:
            pulse_count: Current heartbeat pulse count

        Returns:
            bool: True if should check now
        """
        # Skip if engagement already running
        if self.engagement_in_progress:
            logger.debug("[DAEMON][CARDIOVASCULAR] ⏭️ Pulse {pulse_count}: Skipping - engagement already in progress")
            logger.debug("[COMMUNITY] Skipping - engagement already in progress")
            return False

        # ANTI-DETECTION: Check if on break (read persistent state)
        # Pattern learned from break system in comment_engagement_dae.py
        break_state_file = Path(__file__).parent.parent.parent / "video_comments" / "memory" / ".break_state.json"
        if break_state_file.exists():
            try:
                with open(break_state_file, 'r') as f:
                    state = json.load(f)
                    on_break_until = state.get('on_break_until', 0)
                    if time.time() < on_break_until:
                        remaining_minutes = (on_break_until - time.time()) / 60
                        break_reason = state.get('last_break_reason', 'unknown')
                        logger.info(f"[DAEMON][CARDIOVASCULAR] 💤 Pulse {pulse_count}: On {break_reason} break ({remaining_minutes:.0f} min remaining)")
                        logger.info(f"[COMMUNITY] On {break_reason} break - skipping engagement ({remaining_minutes:.0f} min remaining)")
                        return False
            except Exception as e:
                logger.warning(f"[COMMUNITY] Failed to read break state: {e}")
                # Continue on error (fail open)

        # Check every 20 pulses (10 minutes) - runs 24/7, not just during streams
        should_check = (pulse_count % self.check_interval_pulses) == 0

        if should_check:
            stream_status = "with live stream" if self.chat_sender else "background (no stream)"
            logger.info(f"[DAEMON][CARDIOVASCULAR] 💓 HEARTBEAT TRIGGER: Pulse {pulse_count} - 10 minutes elapsed")
            logger.info(f"[DAEMON][CARDIOVASCULAR] 📍 Mode: {stream_status}")
            logger.info(f"[DAEMON][CARDIOVASCULAR] 🎯 Initiating comment engagement cycle...")
            logger.info(f"[COMMUNITY] Pulse {pulse_count}: Triggering comment engagement ({stream_status})")
        else:
            logger.debug(f"[DAEMON][CARDIOVASCULAR] 💗 Pulse {pulse_count}: No trigger (next at {((pulse_count // self.check_interval_pulses) + 1) * self.check_interval_pulses})")

        return should_check

    async def check_and_engage(self, max_comments: Optional[int] = None) -> Dict:
        """
        Check for comments and engage autonomously.

        ENHANCED: Launches engagement as subprocess to avoid browser hijacking.
        The subprocess uses its own Chrome connection and IntelligentReplyGenerator.

        Args:
            max_comments: Maximum comments to process (default: 5)

        Returns:
            Dict: Engagement session summary
        """
        global _browser_in_use

        if max_comments is None:
            max_comments = self.max_comments_per_run

        if _browser_in_use or self.engagement_in_progress:
            logger.warning("[DAEMON][CARDIOVASCULAR] 🚫 Browser locked - cannot engage")
            logger.warning("[COMMUNITY] Browser in use, skipping engagement")
            return {'skipped': True, 'reason': 'browser_in_use'}

        try:
            self.engagement_in_progress = True
            _browser_in_use = True
            self.last_check_time = datetime.now()

            logger.info(f"[DAEMON][CARDIOVASCULAR] 🔓 Browser lock acquired")
            logger.info(f"[DAEMON][CARDIOVASCULAR] 🎬 Starting engagement subprocess...")
            logger.info(f"[DAEMON][CARDIOVASCULAR]   Max comments: {max_comments} (0=UNLIMITED)")
            logger.info(f"[COMMUNITY] Launching autonomous engagement (max: {max_comments} comments)...")

            # Launch engagement as subprocess (isolated browser session)
            result = await self._run_engagement_subprocess(max_comments)

            # Update session totals
            processed = result.get('stats', {}).get('comments_processed', 0)
            self.total_processed_this_session += processed
            self.last_comment_count = processed

            if processed > 0:
                logger.info(f"[DAEMON][CARDIOVASCULAR] ✅ SUCCESS: Processed {processed} comments this cycle")
                logger.info(f"[DAEMON][CARDIOVASCULAR] 📈 Session total: {self.total_processed_this_session} comments")
                logger.info(f"[COMMUNITY] [OK] Processed {processed} comments")

                # Post announcement to chat
                if self.chat_sender:
                    logger.info(f"[DAEMON][CARDIOVASCULAR] 📢 Announcing to live chat...")
                    await self._announce_engagement(result)
            else:
                logger.info(f"[DAEMON][CARDIOVASCULAR] ⚪ No comments found to process")
                logger.info("[COMMUNITY] No comments to process")

            return result

        except Exception as e:
            logger.error(f"[DAEMON][CARDIOVASCULAR] ❌ ENGAGEMENT FAILED: {e}")
            logger.error(f"[COMMUNITY] Engagement failed: {e}")
            return {
                'error': str(e),
                'stats': {
                    'comments_processed': 0,
                    'likes': 0,
                    'hearts': 0,
                    'replies': 0,
                    'errors': 1
                }
            }

        finally:
            self.engagement_in_progress = False
            _browser_in_use = False
            logger.info(f"[DAEMON][CARDIOVASCULAR] 🔐 Browser lock released")
            logger.debug(f"[DAEMON][CARDIOVASCULAR] 🏁 Engagement cycle complete")

    async def _run_engagement_subprocess(self, max_comments: int) -> Dict:
        """
        Run engagement script as subprocess.

        This keeps the browser session isolated from main.py's process,
        preventing browser hijacking issues.

        Args:
            max_comments: Maximum comments to process

        Returns:
            Dict: Parsed result from subprocess
        """
        import json

        try:
            run_id = _get_run_id()
            if not (_env_truthy("YT_AUTOMATION_ENABLED", "true") and _env_truthy("YT_COMMENT_ENGAGEMENT_ENABLED", "true")):
                logger.warning(f"[AUTOMATION-AUDIT] run_id={run_id} comment_engagement=disabled mode=community_monitor_subprocess")
                return {
                    "skipped": True,
                    "reason": "comment_engagement_disabled",
                    "stats": {"comments_processed": 0, "likes": 0, "hearts": 0, "replies": 0, "errors": 0},
                }

            if not self.engagement_script.exists():
                logger.error(f"[COMMUNITY] Engagement script missing: {self.engagement_script}")
                return {'error': 'missing_script', 'stats': {'comments_processed': 0, 'errors': 1}}

            actions = os.getenv("YT_COMMENT_ACTIONS", "").strip()
            do_like = True
            do_heart = True
            do_reply = True
            if actions:
                allowed = {a.strip().lower() for a in actions.split(",") if a.strip()}
                do_like = "like" in allowed
                do_heart = "heart" in allowed
                do_reply = "reply" in allowed

            if "YT_COMMENT_LIKE_ENABLED" in os.environ:
                do_like = _env_truthy("YT_COMMENT_LIKE_ENABLED", "true")
            if "YT_COMMENT_HEART_ENABLED" in os.environ:
                do_heart = _env_truthy("YT_COMMENT_HEART_ENABLED", "true")
            if "YT_COMMENT_REPLY_ENABLED" in os.environ:
                do_reply = _env_truthy("YT_COMMENT_REPLY_ENABLED", "true")

            reply_text = os.getenv("YT_COMMENT_REPLY_TEXT", "")
            use_intelligent_reply = _env_truthy("YT_COMMENT_INTELLIGENT_REPLY_ENABLED", "true")
            if not do_reply:
                reply_text = ""
                use_intelligent_reply = False

            debug_tags = _env_truthy("YT_REPLY_DEBUG_TAGS", "false")

            # Get next channel in rotation (Phase 3P: Multi-channel support)
            target_channel = self.get_next_channel()

            # Build command
            cmd = [
                sys.executable,
                "-u",  # Unbuffered output for real-time logs via pipes
                str(self.engagement_script),
                "--channel", target_channel,
                "--max-comments", str(max_comments),
                "--json-output"  # Output JSON for parsing
            ]

            # Phase 3R: Pass actual video_id from stream_resolver (NOT @handle/live!)
            # This ensures navigation goes to the CORRECT live stream (not scheduled)
            if self.live_video_id and target_channel == self.live_channel_priority:
                cmd.extend(["--video", self.live_video_id])
                logger.info(f"[COMMUNITY] 🎯 Passing live video ID: {self.live_video_id}")
                logger.info(f"[COMMUNITY]   This ensures DAE navigates to ACTUAL live (not scheduled)")
            else:
                logger.debug(f"[COMMUNITY] No live video ID - using Studio inbox mode")

            if not do_like:
                cmd.append("--no-like")
            if not do_heart:
                cmd.append("--no-heart")
            if not use_intelligent_reply:
                cmd.append("--no-intelligent-reply")
            if reply_text:
                cmd.extend(["--reply-text", reply_text])
            if debug_tags:
                cmd.append("--debug-tags")

            # Default: enable UI-TARS vision verification when LM Studio is available.
            # Override with COMMUNITY_DOM_ONLY=1 to force DOM-only mode.
            dom_only = os.getenv("COMMUNITY_DOM_ONLY", "false").lower() in ("1", "true", "yes")
            if not dom_only:
                import socket
                lm_port = int(os.getenv("LM_STUDIO_PORT", "1234"))
                try:
                    sock = socket.create_connection(("127.0.0.1", lm_port), timeout=1.0)
                    sock.close()
                except Exception:
                    dom_only = True

            if dom_only:
                cmd.append("--dom-only")

            logger.info(
                "[AUTOMATION-AUDIT] run_id=%s mode=community_monitor_subprocess channel_id=%s max_comments=%s dom_only=%s like=%s heart=%s reply=%s intelligent_reply=%s debug_tags=%s",
                run_id,
                self.channel_id,
                max_comments,
                dom_only,
                do_like,
                do_heart,
                do_reply,
                use_intelligent_reply,
                debug_tags,
            )
            logger.info(f"[COMMUNITY] Running: {' '.join(cmd)}")

            # Run subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Timeout budget
            # - For unlimited mode (max_comments=0), use a larger ceiling (configurable).
            # - For bounded runs, assume UI-TARS may take ~2-4 minutes per comment (model inference + UI latency).
            if max_comments == 0:
                timeout = int(os.getenv("COMMUNITY_UNLIMITED_TIMEOUT", "3600"))  # unified default: 1 hour
            else:
                timeout = (max_comments * 240) + 60  # 4 min/comment + buffer

            logger.info(f"[COMMUNITY] Subprocess timeout budget: {timeout}s (max_comments={max_comments})")

            # Stream stdout/stderr for observability (prevents 'silent hang' perception)
            stream_logs = os.getenv("COMMUNITY_DEBUG_SUBPROCESS", "true").lower() in ("1", "true", "yes")
            stdout_lines: list[str] = []
            stderr_lines: list[str] = []

            async def _drain_stream(stream, sink: list[str], prefix: str) -> None:
                skip_backtrace = 0  # Counter for skipping hex backtrace lines
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    text = line.decode('utf-8', errors='ignore').rstrip()
                    if text:
                        sink.append(text)
                        if stream_logs:
                            # Skip Selenium backtrace spam
                            if skip_backtrace > 0:
                                skip_backtrace -= 1
                                continue

                            # Detect start of backtrace (skip next ~30 hex lines)
                            if 'Symbols not available. Dumping unresolved backtrace:' in text:
                                skip_backtrace = 30
                                continue

                            # Skip individual hex addresses and "Stacktrace:" lines
                            if text.strip().startswith('0x') or text.strip() == 'Stacktrace:':
                                continue

                            # Skip expected import warnings (logged once at subprocess startup)
                            if any(skip_pattern in text for skip_pattern in [
                                'Recursive systems not available',
                                'WRE components not available',
                                'Tweepy not available',
                                'pyperclip not available',
                                'LLM not available for greetings',
                            ]):
                                continue

                            # Log everything else (errors, warnings, info)
                            logger.info(f"[COMMUNITY-{prefix}] {text}")

            stdout_task = asyncio.create_task(_drain_stream(process.stdout, stdout_lines, "STDOUT"))
            stderr_task = asyncio.create_task(_drain_stream(process.stderr, stderr_lines, "STDERR"))

            try:
                await asyncio.wait_for(process.wait(), timeout=timeout)
            except asyncio.TimeoutError:
                logger.error("[COMMUNITY] Engagement subprocess timed out - terminating process")
                try:
                    process.terminate()
                except ProcessLookupError:
                    pass

                try:
                    await asyncio.wait_for(process.wait(), timeout=5)
                except asyncio.TimeoutError:
                    try:
                        process.kill()
                    except ProcessLookupError:
                        pass
                    await process.wait()

                return {'error': 'timeout', 'stats': {'comments_processed': 0, 'errors': 1}}
            finally:
                # Ensure streams are fully drained before parsing output
                await asyncio.gather(stdout_task, stderr_task, return_exceptions=True)

            stdout_str = "\n".join(stdout_lines)
            stderr_str = "\n".join(stderr_lines)

            # Parse output
            if process.returncode not in (0, None):
                logger.warning(f"[COMMUNITY] Engagement subprocess exited with code {process.returncode}")

            # Try to extract JSON result from stdout
            try:
                # Look for JSON output line
                for line in reversed(stdout_lines):
                    candidate = line.strip()
                    if candidate.startswith('{') and '"stats"' in candidate:
                        return json.loads(candidate)

                # If no JSON, parse from logs
                stats = self._parse_log_output(stdout_str)
                return {'stats': stats}

            except json.JSONDecodeError:
                # Parse stats from log output
                stats = self._parse_log_output(stdout_str)
                return {'stats': stats}

        except Exception as e:
            logger.error(f"[COMMUNITY] Subprocess error: {e}")
            return {'error': str(e), 'stats': {'comments_processed': 0, 'errors': 1}}

    def _parse_log_output(self, stdout: str) -> Dict:
        """Parse engagement stats from log output."""
        stats = {
            'comments_processed': 0,
            'likes': 0,
            'hearts': 0,
            'replies': 0,
            'errors': 0
        }

        for line in stdout.split('\n'):
            if 'Comments processed:' in line:
                try:
                    stats['comments_processed'] = int(line.split(':')[1].strip())
                except:
                    pass
            elif 'Likes:' in line:
                try:
                    stats['likes'] = int(line.split(':')[1].strip())
                except:
                    pass
            elif 'Hearts:' in line:
                try:
                    stats['hearts'] = int(line.split(':')[1].strip())
                except:
                    pass
            elif 'Replies:' in line:
                try:
                    stats['replies'] = int(line.split(':')[1].strip())
                except:
                    pass
            elif 'Errors:' in line:
                try:
                    stats['errors'] = int(line.split(':')[1].strip())
                except:
                    pass

        return stats

    async def _announce_engagement(self, result: Dict):
        """
        Post engagement summary to live chat.

        Fire-and-forget async announcement using AI Overseer pattern.

        Args:
            result: Engagement session result
        """
        if not self.chat_sender:
            return

        if not _env_truthy("YT_LIVECHAT_ANNOUNCEMENTS_ENABLED", "true"):
            return

        stats = result.get('stats', {})
        processed = stats.get('comments_processed', 0)
        replies = stats.get('replies', 0)
        all_done = stats.get('all_processed', False)  # NEW: Check if all cleared

        if processed > 0:
            # Craft announcement with 0102 signature
            if all_done:
                # ALL COMMENTS CLEARED! Special celebration message
                message = f"[OK] ALL {processed} comments processed with {replies} replies! Community tab clear."
            elif replies > 0:
                message = f"0102 engaged {processed} comments with {replies} replies."
            else:
                message = f"0102 processed {processed} comments in Community tab."

            try:
                # Fire-and-forget async post
                asyncio.create_task(
                    self.chat_sender.send_message(
                        message,
                        response_type='comment_engagement_announcement'
                    )
                )
                logger.info(f"[COMMUNITY] Posted announcement: {message}")

            except Exception as e:
                logger.error(f"[COMMUNITY] Failed to post announcement: {e}")

    def get_statistics(self) -> Dict:
        """
        Get current session statistics.

        Returns:
            Dict: Statistics summary
        """
        return {
            'last_check_time': self.last_check_time.isoformat() if self.last_check_time else None,
            'last_comment_count': self.last_comment_count,
            'total_processed_this_session': self.total_processed_this_session,
            'check_interval_minutes': (self.check_interval_pulses * 30) / 60,
            'engagement_in_progress': self.engagement_in_progress
        }


# Singleton instance for AutoModeratorDAE integration
_community_monitor_instance = None


def get_community_monitor(channel_id: str, chat_sender=None, telemetry_store=None, all_channels: list = None) -> CommunityMonitor:
    """
    Get or create singleton CommunityMonitor instance.

    Args:
        channel_id: Primary YouTube channel ID
        chat_sender: LiveChatCore instance
        telemetry_store: YouTubeTelemetryStore instance
        all_channels: List of all channel IDs to rotate through (Phase 3P: Multi-channel support)

    Returns:
        CommunityMonitor: Singleton instance
    """
    global _community_monitor_instance

    if _community_monitor_instance is None:
        _community_monitor_instance = CommunityMonitor(
            channel_id=channel_id,
            chat_sender=chat_sender,
            telemetry_store=telemetry_store,
            all_channels=all_channels  # Phase 3P: Channel rotation
        )
    else:
        # Update wiring when higher-level services become available (e.g., LiveChatCore after stream detection).
        if chat_sender is not None and _community_monitor_instance.chat_sender is None:
            _community_monitor_instance.chat_sender = chat_sender
            logger.info("[COMMUNITY] Monitor chat_sender attached (announcements enabled)")
        if telemetry_store is not None and _community_monitor_instance.telemetry_store is None:
            _community_monitor_instance.telemetry_store = telemetry_store
            logger.info("[COMMUNITY] Monitor telemetry_store attached")

        # Phase 3R (2025-12-24): Update primary channel_id when different stream detected
        # CRITICAL FIX: Singleton was stuck on first channel, ignoring live stream switches
        if channel_id != _community_monitor_instance.channel_id:
            logger.info(f"[COMMUNITY] 🔄 CHANNEL SWITCH DETECTED:")
            logger.info(f"[COMMUNITY]   Old primary: {_community_monitor_instance.channel_id}")
            logger.info(f"[COMMUNITY]   New primary: {channel_id}")

            old_channel = _community_monitor_instance.channel_id
            _community_monitor_instance.channel_id = channel_id

            # Phase 4H (2025-12-25): Switch YouTube Studio account
            # HYBRID: DOM-based account switching + UI-TARS training data collection
            # Training enables future vision-based switching (Phase 5)
            try:
                # Map channel_id to account name
                channel_to_account = {
                    "UC-LSSlOZwpGIRIYihaz8zCw": "Move2Japan",
                    "UCSNTUXjAgpd4sgWYP0xoJgw": "UnDaoDu",
                    "UCfHM9Fw9HD-NwiS0seD_oIA": "FoundUps",
                }

                target_account = channel_to_account.get(channel_id)
                if target_account:
                    logger.info(f"[COMMUNITY] 🔄 Triggering Studio account switch: {old_channel} → {target_account}")
                    logger.info(f"[COMMUNITY]   Phase 4H: DOM clicks will generate UI-TARS training data")

                    # Import and switch (async, but don't block - switch happens in background)
                    # This is fire-and-forget to avoid blocking community monitor
                    import asyncio
                    from modules.infrastructure.foundups_vision.src.studio_account_switcher import switch_studio_account

                    # Create background task for account switch
                    async def _switch_account():
                        result = await switch_studio_account(target_account)
                        if result.get("success"):
                            logger.info(f"[COMMUNITY] ✅ Studio account switched to {target_account}")
                            logger.info(f"[COMMUNITY]   Training examples recorded: {result.get('training_recorded', 0)}")
                        else:
                            logger.warning(f"[COMMUNITY] ⚠️ Studio account switch failed: {result.get('error')}")

                    # Schedule task (fire-and-forget)
                    try:
                        loop = asyncio.get_running_loop()
                        loop.create_task(_switch_account())
                    except RuntimeError:
                        # No event loop running - switch synchronously
                        logger.warning(f"[COMMUNITY] No event loop - skipping Studio account switch")

            except Exception as e:
                logger.warning(f"[COMMUNITY] Phase 4H account switch failed: {e}")
                # Continue without Studio account switch (comment engagement still works)

    return _community_monitor_instance
