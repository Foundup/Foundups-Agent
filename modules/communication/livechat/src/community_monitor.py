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
import logging
import os
import subprocess
import sys
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Browser lock to prevent multiple Selenium sessions
_browser_in_use = False


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

    def __init__(self, channel_id: str, chat_sender=None, telemetry_store=None):
        """
        Initialize Community Monitor.

        Args:
            channel_id: YouTube channel ID
            chat_sender: LiveChatCore instance for announcements
            telemetry_store: YouTubeTelemetryStore for tracking
        """
        self.channel_id = channel_id
        self.chat_sender = chat_sender
        self.telemetry_store = telemetry_store

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

        logger.info(f"[COMMUNITY] Monitor initialized for channel {channel_id}")

    async def should_check_now(self, pulse_count: int) -> bool:
        """
        Determine if we should check for comments now.

        Phase 1: Protocol Decision
        - Check every 20 pulses (10 minutes)
        - Only if live stream is active (chat_sender exists)
        - Skip if engagement already in progress

        Args:
            pulse_count: Current heartbeat pulse count

        Returns:
            bool: True if should check now
        """
        # Skip if engagement already running
        if self.engagement_in_progress:
            logger.debug("[COMMUNITY] Skipping - engagement already in progress")
            return False

        # Only check if chat is active (implies live stream)
        if not self.chat_sender:
            return False

        # Check every 20 pulses (10 minutes)
        should_check = (pulse_count % self.check_interval_pulses) == 0

        if should_check:
            logger.info(f"[COMMUNITY] Pulse {pulse_count}: Triggering comment engagement")

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
            logger.warning("[COMMUNITY] Browser in use, skipping engagement")
            return {'skipped': True, 'reason': 'browser_in_use'}

        try:
            self.engagement_in_progress = True
            _browser_in_use = True
            self.last_check_time = datetime.now()

            logger.info(f"[COMMUNITY] Launching autonomous engagement (max: {max_comments} comments)...")

            # Launch engagement as subprocess (isolated browser session)
            result = await self._run_engagement_subprocess(max_comments)

            # Update session totals
            processed = result.get('stats', {}).get('comments_processed', 0)
            self.total_processed_this_session += processed
            self.last_comment_count = processed

            if processed > 0:
                logger.info(f"[COMMUNITY] [OK] Processed {processed} comments")
                
                # Post announcement to chat
                await self._announce_engagement(result)
            else:
                logger.info("[COMMUNITY] No comments to process")

            return result

        except Exception as e:
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
            if not self.engagement_script.exists():
                logger.error(f"[COMMUNITY] Engagement script missing: {self.engagement_script}")
                return {'error': 'missing_script', 'stats': {'comments_processed': 0, 'errors': 1}}

            # Build command
            cmd = [
                sys.executable,
                "-u",  # Unbuffered output for real-time logs via pipes
                str(self.engagement_script),
                "--max-comments", str(max_comments),
                "--json-output"  # Output JSON for parsing
            ]

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
                timeout = int(os.getenv("COMMUNITY_UNLIMITED_TIMEOUT", "1800"))  # default 30 minutes
            else:
                timeout = (max_comments * 240) + 60  # 4 min/comment + buffer

            logger.info(f"[COMMUNITY] Subprocess timeout budget: {timeout}s (max_comments={max_comments})")

            # Stream stdout/stderr for observability (prevents 'silent hang' perception)
            stream_logs = os.getenv("COMMUNITY_DEBUG_SUBPROCESS", "true").lower() in ("1", "true", "yes")
            stdout_lines: list[str] = []
            stderr_lines: list[str] = []

            async def _drain_stream(stream, sink: list[str], prefix: str) -> None:
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    text = line.decode('utf-8', errors='ignore').rstrip()
                    if text:
                        sink.append(text)
                        if stream_logs:
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


def get_community_monitor(channel_id: str, chat_sender=None, telemetry_store=None) -> CommunityMonitor:
    """
    Get or create singleton CommunityMonitor instance.

    Args:
        channel_id: YouTube channel ID
        chat_sender: LiveChatCore instance
        telemetry_store: YouTubeTelemetryStore instance

    Returns:
        CommunityMonitor: Singleton instance
    """
    global _community_monitor_instance

    if _community_monitor_instance is None:
        _community_monitor_instance = CommunityMonitor(
            channel_id=channel_id,
            chat_sender=chat_sender,
            telemetry_store=telemetry_store
        )
    else:
        # Update wiring when higher-level services become available (e.g., LiveChatCore after stream detection).
        if chat_sender is not None and _community_monitor_instance.chat_sender is None:
            _community_monitor_instance.chat_sender = chat_sender
            logger.info("[COMMUNITY] Monitor chat_sender attached (announcements enabled)")
        if telemetry_store is not None and _community_monitor_instance.telemetry_store is None:
            _community_monitor_instance.telemetry_store = telemetry_store
            logger.info("[COMMUNITY] Monitor telemetry_store attached")

    return _community_monitor_instance
