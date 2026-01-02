"""
Comment Engagement Execution Strategy Interface
================================================

WSP 27/80 Compliant execution modes for comment engagement:
- subprocess: Safest (SIGKILL guarantee, process isolation)
- thread: Fast startup (<500ms), thread isolation
- inproc: Dev debugging only (blocks event loop)

Architecture Rationale:
Selenium/WebDriver is synchronous and blocks. asyncio.wait_for() can timeout
the await, but CANNOT interrupt blocked C/IO calls inside Selenium. Only
subprocess termination guarantees recovery of Chrome control.

Thread mode trades guaranteed kill switch for fast startup. Acceptable when:
- Selenium usually returns (empirically true)
- Browser lease prevents permanent deadlocks (Sprint 3)
- Subprocess remains available as fallback

WSP Compliance:
    - WSP 27: DAE Architecture (execution strategies)
    - WSP 77: Agent Coordination (prevent Chrome overlap)
    - WSP 64: Violation Prevention (telemetry-driven decisions)
"""

import asyncio
import logging
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from modules.communication.livechat.src.automation_gates import stop_active, stop_file_path

logger = logging.getLogger(__name__)


def _env_truthy(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "y", "on")


def _get_run_id() -> str:
    run_id = os.getenv("YT_AUTOMATION_RUN_ID", "").strip()
    if run_id:
        return run_id

    run_id = f"yt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.environ["YT_AUTOMATION_RUN_ID"] = run_id
    return run_id


@dataclass(frozen=True)
class _CommentEngagementSwitches:
    enabled: bool
    do_like: bool
    do_heart: bool
    do_reply: bool
    reply_text: str
    use_intelligent_reply: bool
    debug_tags: bool


def _get_comment_engagement_switches() -> _CommentEngagementSwitches:
    enabled = _env_truthy("YT_AUTOMATION_ENABLED", "true") and _env_truthy("YT_COMMENT_ENGAGEMENT_ENABLED", "true")

    actions = os.getenv("YT_COMMENT_ACTIONS", "").strip()
    do_like = True
    do_heart = True
    do_reply = True
    if actions:
        allowed = {a.strip().lower() for a in actions.split(",") if a.strip()}
        do_like = "like" in allowed
        do_heart = "heart" in allowed
        do_reply = "reply" in allowed

    if "YT_COMMENT_REACTIONS_ENABLED" in os.environ:
        do_like = _env_truthy("YT_COMMENT_REACTIONS_ENABLED", "true")
        do_heart = do_like

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

    return _CommentEngagementSwitches(
        enabled=enabled,
        do_like=do_like,
        do_heart=do_heart,
        do_reply=do_reply,
        reply_text=reply_text,
        use_intelligent_reply=use_intelligent_reply,
        debug_tags=debug_tags,
    )


class EngagementRunner(ABC):
    """Abstract base for comment engagement execution strategies."""

    @abstractmethod
    async def run_engagement(
        self,
        channel_id: str,
        max_comments: int = 0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute comment engagement and return structured result.

        Args:
            channel_id: YouTube channel ID
            max_comments: Max comments to process (0 = unlimited)
            **kwargs: Mode-specific options

        Returns:
            {
                "stats": {"comments_processed": N, "likes": N, ...},
                "timing": {"total_ms": N, "connect_ms": N, ...},
                "error": "timeout|crash|..." (if failed)
            }
        """
        pass


class SubprocessRunner(EngagementRunner):
    """
    Subprocess execution mode (DEFAULT, SAFEST).

    Pros:
    - ✅ SIGKILL guarantee (always recovers Chrome control)
    - ✅ Process isolation (crash doesn't kill main DAE)
    - ✅ JSON output parsing

    Cons:
    - ❌ 2-3s startup overhead
    - ❌ State sharing requires serialization
    """

    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root).resolve()

        script_rel = Path("modules/communication/video_comments/skills/tars_like_heart_reply/run_skill.py")

        # Defensive: some callers may pass `.../modules` instead of repo root.
        # Prefer the first candidate that exists.
        candidates = [self.repo_root / script_rel]
        if self.repo_root.name.lower() == "modules":
            candidates.append(self.repo_root.parent / script_rel)
        candidates.append(Path(__file__).resolve().parents[4] / script_rel)

        self.engagement_script = next((p for p in candidates if p.exists()), candidates[0])
        logger.debug(
            "[RUNNER] SubprocessRunner initialized repo_root=%s engagement_script=%s",
            self.repo_root,
            self.engagement_script,
        )

    async def run_engagement(
        self,
        channel_id: str,
        max_comments: int = 0,
        video_id: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute via subprocess (wraps existing community_monitor logic)."""

        switches = _get_comment_engagement_switches()
        run_id = _get_run_id()
        if stop_active():
            logger.warning(
                "[AUTOMATION-AUDIT] run_id=%s comment_engagement=disabled (stop_file=%s) mode=subprocess",
                run_id,
                stop_file_path(),
            )
            return {
                "skipped": True,
                "reason": "automation_stopped",
                "stats": {"comments_processed": 0, "likes": 0, "hearts": 0, "replies": 0, "errors": 0},
            }
        if not switches.enabled:
            logger.warning(f"[AUTOMATION-AUDIT] run_id={run_id} comment_engagement=disabled mode=subprocess")
            return {
                "skipped": True,
                "reason": "comment_engagement_disabled",
                "stats": {"comments_processed": 0, "likes": 0, "hearts": 0, "replies": 0, "errors": 0},
            }

        if not self.engagement_script.exists():
            logger.error(f"[DAEMON][CARDIOVASCULAR] ❌ Script missing: {self.engagement_script}")
            return {'error': 'missing_script', 'stats': {'errors': 1}}

        # Browser port (9222=Chrome default, 9223=Edge for FoundUps)
        browser_port = kwargs.get('browser_port', 9222)
        browser_name = "Edge" if browser_port == 9223 else "Chrome"

        logger.info(f"[DAEMON][CARDIOVASCULAR] ✓ Building comment engagement command...")
        logger.info(f"[DAEMON][CARDIOVASCULAR]   Channel: {channel_id}")
        logger.info(f"[DAEMON][CARDIOVASCULAR]   Max comments: {max_comments} (0=UNLIMITED)")
        logger.info(f"[DAEMON][CARDIOVASCULAR]   Video ID: {video_id or 'None (Studio inbox)'}")
        logger.info(f"[DAEMON][CARDIOVASCULAR]   Browser: {browser_name} (port {browser_port})")

        # Build command
        cmd = [
            sys.executable,
            "-u",  # Unbuffered
            str(self.engagement_script),
            "--channel", channel_id,
            "--max-comments", str(max_comments),
            "--browser-port", str(browser_port),
            "--json-output"
        ]

        # Add video ID if targeting live stream comments (not generic inbox)
        if video_id:
            logger.warning(f"[DAEMON][CARDIOVASCULAR] ⚠️ VIDEO-SPECIFIC MODE: Adding --video {video_id}")
            logger.warning(f"[DAEMON][CARDIOVASCULAR] ⚠️ This targets video comments, NOT Studio inbox!")
            cmd.extend(["--video", video_id])
        else:
            logger.info(f"[DAEMON][CARDIOVASCULAR] ✅ STUDIO INBOX MODE: No video_id (processes ALL comments)")

        if not switches.do_like:
            cmd.append("--no-like")
        if not switches.do_heart:
            cmd.append("--no-heart")
        if not switches.do_reply:
            cmd.append("--no-reply")
        if not switches.use_intelligent_reply:
            cmd.append("--no-intelligent-reply")
        if switches.reply_text:
            cmd.extend(["--reply-text", switches.reply_text])
        if switches.debug_tags:
            cmd.append("--debug-tags")

        # Check for DOM-only mode
        dom_only = os.getenv("COMMUNITY_DOM_ONLY", "false").lower() in ("1", "true", "yes")
        if not dom_only:
            # Check if LM Studio available
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
            "[AUTOMATION-AUDIT] run_id=%s mode=subprocess channel_id=%s max_comments=%s dom_only=%s like=%s heart=%s reply=%s intelligent_reply=%s debug_tags=%s video_id=%s",
            run_id,
            channel_id,
            max_comments,
            dom_only,
            switches.do_like,
            switches.do_heart,
            switches.do_reply,
            switches.use_intelligent_reply,
            switches.debug_tags,
            video_id or "None"
        )
        logger.info(f"[DAEMON][CARDIOVASCULAR] 🚀 Launching subprocess...")
        logger.info(f"[SUBPROCESS] Command: {' '.join(cmd)}")

        # Start subprocess
        env = os.environ.copy()
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(self.repo_root),
            env=env
        )

        # Calculate timeout (unified default: 3600s = 1 hour)
        if max_comments == 0:
            timeout = int(os.getenv("COMMUNITY_UNLIMITED_TIMEOUT", "3600"))
            logger.info(f"[DAEMON][CARDIOVASCULAR] ⏱️ UNLIMITED mode - timeout: {timeout}s ({timeout/3600:.1f} hours)")
        else:
            timeout = (max_comments * 240) + 60
            logger.info(f"[DAEMON][CARDIOVASCULAR] ⏱️ Limited mode - timeout: {timeout}s for {max_comments} comments")

        # Stream logs
        stream_logs = os.getenv("COMMUNITY_DEBUG_SUBPROCESS", "true").lower() in ("1", "true", "yes")
        stdout_lines = []
        stderr_lines = []

        async def _drain_stream(stream, sink, prefix):
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
                        logger.info(f"[REPLY] {text}")

        stdout_task = asyncio.create_task(_drain_stream(process.stdout, stdout_lines, "STDOUT"))
        stderr_task = asyncio.create_task(_drain_stream(process.stderr, stderr_lines, "STDERR"))

        try:
            logger.info(f"[DAEMON][CARDIOVASCULAR] ⏳ Subprocess running (PID: {process.pid})...")
            await asyncio.wait_for(process.wait(), timeout=timeout)
            logger.info(f"[DAEMON][CARDIOVASCULAR] ✓ Subprocess completed (PID: {process.pid})")
        except asyncio.TimeoutError:
            logger.error(f"[DAEMON][CARDIOVASCULAR] ⏰ TIMEOUT after {timeout}s - terminating process")
            logger.error("[SUBPROCESS] Timeout - terminating process")
            try:
                process.terminate()
                await asyncio.sleep(2)
                process.kill()  # SIGKILL guarantee
                logger.warning("[SUBPROCESS] Process killed (SIGKILL)")
            except ProcessLookupError:
                pass

            return {
                'error': 'timeout',
                'stats': {'comments_processed': 0, 'errors': 1},
                'timeout_seconds': timeout
            }

        # Wait for log streaming to complete
        await asyncio.gather(stdout_task, stderr_task, return_exceptions=True)

        # Parse JSON output
        json_output = None
        for line in stdout_lines:
            line_stripped = line.strip()
            if line_stripped.startswith('{') and line_stripped.endswith('}'):
                try:
                    import json
                    json_output = json.loads(line_stripped)
                    break
                except Exception:
                    continue

        if json_output:
            stats = json_output.get('stats', {})
            logger.info(f"[DAEMON][CARDIOVASCULAR] 📊 ENGAGEMENT RESULTS:")
            logger.info(f"[DAEMON][CARDIOVASCULAR]   Comments processed: {stats.get('comments_processed', 0)}")
            logger.info(f"[DAEMON][CARDIOVASCULAR]   Likes: {stats.get('likes', 0)}")
            logger.info(f"[DAEMON][CARDIOVASCULAR]   Hearts: {stats.get('hearts', 0)}")
            logger.info(f"[DAEMON][CARDIOVASCULAR]   Replies: {stats.get('replies', 0)}")
            logger.info(f"[DAEMON][CARDIOVASCULAR]   Errors: {stats.get('errors', 0)}")
            logger.info(f"[DAEMON][CARDIOVASCULAR]   Moderators detected: {stats.get('moderators_detected', 0)}")
            logger.info(f"[DAEMON][CARDIOVASCULAR]   All processed: {stats.get('all_processed', False)}")
            logger.info(f"[SUBPROCESS] Result: {stats}")
            return json_output
        else:
            logger.error("[DAEMON][CARDIOVASCULAR] ❌ No JSON output from subprocess!")
            logger.error("[SUBPROCESS] No JSON output parsed")
            if stderr_lines:
                logger.error(f"[DAEMON][CARDIOVASCULAR] stderr (first 5 lines): {stderr_lines[:5]}")
            return {
                'error': 'no_json_output',
                'stats': {'comments_processed': 0, 'errors': 1},
                'stderr': stderr_lines[:10]  # First 10 errors
            }


class ThreadRunner(EngagementRunner):
    """
    Thread execution mode (FAST STARTUP, ACCEPTABLE RISK).

    Pros:
    - ✅ <500ms startup (vs 2-3s subprocess)
    - ✅ Thread isolation (main event loop never blocked)
    - ✅ Direct state access

    Cons:
    - ⚠️ Cannot force-kill thread (accept this limitation)
    - ⚠️ If thread hangs permanently, Chrome locked until restart

    Safety: Selenium runs in dedicated thread via asyncio.to_thread(),
    so main event loop never blocked. Timeout still works at supervisor level.
    """

    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)

    async def run_engagement(
        self,
        channel_id: str,
        max_comments: int = 0,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute in dedicated thread (prevent event loop blocking)."""

        switches = _get_comment_engagement_switches()
        run_id = _get_run_id()
        if not switches.enabled:
            logger.warning(f"[AUTOMATION-AUDIT] run_id={run_id} comment_engagement=disabled mode=thread")
            return {
                "skipped": True,
                "reason": "comment_engagement_disabled",
                "stats": {"comments_processed": 0, "likes": 0, "hearts": 0, "replies": 0, "errors": 0},
            }

        # Calculate timeout (unified default: 3600s = 1 hour)
        if max_comments == 0:
            timeout = int(os.getenv("COMMUNITY_UNLIMITED_TIMEOUT", "3600"))
        else:
            timeout = (max_comments * 240) + 60

        logger.info(f"[THREAD] Starting engagement (timeout: {timeout}s)")

        try:
            # Run in thread to prevent Selenium from blocking event loop
            result = await asyncio.wait_for(
                asyncio.to_thread(self._execute_sync, channel_id, max_comments, switches),
                timeout=timeout
            )
            logger.info(f"[THREAD] Complete: {result.get('stats', {})}")
            return result

        except asyncio.TimeoutError:
            logger.error(f"[THREAD] Timeout after {timeout}s")
            logger.warning("[THREAD] Thread may continue in background (cannot force-kill)")
            return {
                'error': 'timeout',
                'stats': {'comments_processed': 0, 'errors': 1},
                'timeout_seconds': timeout
            }

        except Exception as e:
            logger.error(f"[THREAD] Error: {e}", exc_info=True)
            return {
                'error': str(e),
                'stats': {'comments_processed': 0, 'errors': 1}
            }

    def _execute_sync(self, channel_id: str, max_comments: int, switches: _CommentEngagementSwitches) -> Dict[str, Any]:
        """
        Synchronous execution in dedicated thread.
        Selenium blocking happens HERE, not in main event loop.
        """
        try:
            # Import here to avoid loading in main thread
            from modules.communication.video_comments.skills.tars_like_heart_reply.comment_engagement_dae import (
                CommentEngagementDAE
            )

            # Check LM Studio availability
            dom_only = os.getenv("COMMUNITY_DOM_ONLY", "false").lower() in ("1", "true", "yes")
            if not dom_only:
                import socket
                lm_port = int(os.getenv("LM_STUDIO_PORT", "1234"))
                try:
                    sock = socket.create_connection(("127.0.0.1", lm_port), timeout=1.0)
                    sock.close()
                except Exception:
                    dom_only = True

            logger.info(f"[THREAD] Vision mode: {'disabled' if dom_only else 'enabled'}")

            run_id = _get_run_id()
            if switches.debug_tags:
                os.environ["YT_REPLY_DEBUG_TAGS"] = "1"

            logger.info(
                "[AUTOMATION-AUDIT] run_id=%s mode=thread channel_id=%s max_comments=%s dom_only=%s like=%s heart=%s reply=%s intelligent_reply=%s debug_tags=%s",
                run_id,
                channel_id,
                max_comments,
                dom_only,
                switches.do_like,
                switches.do_heart,
                switches.do_reply,
                switches.use_intelligent_reply,
                switches.debug_tags,
            )

            dae = CommentEngagementDAE(
                channel_id=channel_id,
                use_vision=not dom_only,
                use_dom=True
            )

            try:
                # These async calls run in thread's event loop
                # Selenium blocking happens here, isolated from main loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                try:
                    loop.run_until_complete(dae.connect())
                    loop.run_until_complete(dae.navigate_to_inbox())

                    result = loop.run_until_complete(
                        dae.engage_all_comments(
                            max_comments=max_comments,
                            do_like=switches.do_like,
                            do_heart=switches.do_heart,
                            reply_text=switches.reply_text,
                            use_intelligent_reply=switches.use_intelligent_reply
                        )
                    )
                    return result

                finally:
                    loop.close()

            finally:
                dae.close()  # Guaranteed cleanup

        except Exception as e:
            logger.error(f"[THREAD] Sync execution error: {e}", exc_info=True)
            return {
                'error': str(e),
                'stats': {'comments_processed': 0, 'errors': 1}
            }


class InProcessRunner(EngagementRunner):
    """
    In-process execution mode (DEV DEBUGGING ONLY).

    WARNING: BLOCKS MAIN EVENT LOOP - DO NOT USE IN PRODUCTION.

    This mode runs Selenium in the main event loop, which will block
    livechat monitoring and stream detection. Only for local debugging.
    """

    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)

    async def run_engagement(
        self,
        channel_id: str,
        max_comments: int = 0,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute in main event loop (BLOCKS - DEBUG ONLY)."""

        logger.warning("[INPROC] ⚠️ WARNING: Running in main event loop (will block livechat!)")

        switches = _get_comment_engagement_switches()
        run_id = _get_run_id()
        if not switches.enabled:
            logger.warning(f"[AUTOMATION-AUDIT] run_id={run_id} comment_engagement=disabled mode=inproc")
            return {
                "skipped": True,
                "reason": "comment_engagement_disabled",
                "stats": {"comments_processed": 0, "likes": 0, "hearts": 0, "replies": 0, "errors": 0},
            }

        try:
            from modules.communication.video_comments.skills.tars_like_heart_reply.comment_engagement_dae import (
                execute_skill
            )

            dom_only = os.getenv("COMMUNITY_DOM_ONLY", "false").lower() in ("1", "true", "yes")
            if not dom_only:
                import socket

                lm_port = int(os.getenv("LM_STUDIO_PORT", "1234"))
                try:
                    sock = socket.create_connection(("127.0.0.1", lm_port), timeout=1.0)
                    sock.close()
                except Exception:
                    dom_only = True

            if switches.debug_tags:
                os.environ["YT_REPLY_DEBUG_TAGS"] = "1"

            logger.info(
                "[AUTOMATION-AUDIT] run_id=%s mode=inproc channel_id=%s max_comments=%s dom_only=%s like=%s heart=%s reply=%s intelligent_reply=%s debug_tags=%s",
                run_id,
                channel_id,
                max_comments,
                dom_only,
                switches.do_like,
                switches.do_heart,
                switches.do_reply,
                switches.use_intelligent_reply,
                switches.debug_tags,
            )

            result = await execute_skill(
                channel_id=channel_id,
                max_comments=max_comments,
                do_like=switches.do_like,
                do_heart=switches.do_heart,
                reply_text=switches.reply_text,
                use_vision=not dom_only,
                use_intelligent_reply=switches.use_intelligent_reply,
            )
            return result

        except Exception as e:
            logger.error(f"[INPROC] Error: {e}", exc_info=True)
            return {
                'error': str(e),
                'stats': {'comments_processed': 0, 'errors': 1}
            }


def get_runner(mode: str = "subprocess", repo_root: Optional[Path] = None) -> EngagementRunner:
    """
    Get engagement runner by mode.

    Args:
        mode: "subprocess" (default, safest) | "thread" (fast) | "inproc" (debug)
        repo_root: Repository root (auto-detected if None)

    Returns:
        EngagementRunner instance
    """
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[4]

    mode = mode.lower()

    if mode == "subprocess":
        logger.info("[RUNNER] Using subprocess mode (default, safest)")
        return SubprocessRunner(repo_root)

    elif mode == "thread":
        logger.info("[RUNNER] Using thread mode (fast startup, acceptable risk)")
        return ThreadRunner(repo_root)

    elif mode == "inproc":
        logger.warning("[RUNNER] Using in-process mode (DEBUG ONLY - blocks event loop!)")
        return InProcessRunner(repo_root)

    else:
        logger.error(f"[RUNNER] Unknown mode '{mode}', defaulting to subprocess")
        return SubprocessRunner(repo_root)
