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
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


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
        self.repo_root = Path(repo_root)
        self.engagement_script = (
            self.repo_root
            / "modules/communication/video_comments/skills/tars_like_heart_reply/run_skill.py"
        )

    async def run_engagement(
        self,
        channel_id: str,
        max_comments: int = 0,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute via subprocess (wraps existing community_monitor logic)."""

        if not self.engagement_script.exists():
            logger.error(f"[SUBPROCESS] Script missing: {self.engagement_script}")
            return {'error': 'missing_script', 'stats': {'errors': 1}}

        # Build command
        cmd = [
            sys.executable,
            "-u",  # Unbuffered
            str(self.engagement_script),
            "--channel", channel_id,
            "--max-comments", str(max_comments),
            "--json-output"
        ]

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

        logger.info(f"[SUBPROCESS] Running: {' '.join(cmd)}")

        # Start subprocess
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Calculate timeout
        if max_comments == 0:
            timeout = int(os.getenv("COMMUNITY_UNLIMITED_TIMEOUT", "1800"))
        else:
            timeout = (max_comments * 240) + 60

        logger.info(f"[SUBPROCESS] Timeout: {timeout}s (max_comments={max_comments})")

        # Stream logs
        stream_logs = os.getenv("COMMUNITY_DEBUG_SUBPROCESS", "true").lower() in ("1", "true", "yes")
        stdout_lines = []
        stderr_lines = []

        async def _drain_stream(stream, sink, prefix):
            while True:
                line = await stream.readline()
                if not line:
                    break
                text = line.decode('utf-8', errors='ignore').rstrip()
                if text:
                    sink.append(text)
                    if stream_logs:
                        logger.info(f"[SUBPROCESS-{prefix}] {text}")

        stdout_task = asyncio.create_task(_drain_stream(process.stdout, stdout_lines, "STDOUT"))
        stderr_task = asyncio.create_task(_drain_stream(process.stderr, stderr_lines, "STDERR"))

        try:
            await asyncio.wait_for(process.wait(), timeout=timeout)
        except asyncio.TimeoutError:
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
            logger.info(f"[SUBPROCESS] Result: {json_output.get('stats', {})}")
            return json_output
        else:
            logger.error("[SUBPROCESS] No JSON output parsed")
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

        # Calculate timeout
        if max_comments == 0:
            timeout = int(os.getenv("COMMUNITY_UNLIMITED_TIMEOUT", "1800"))
        else:
            timeout = (max_comments * 240) + 60

        logger.info(f"[THREAD] Starting engagement (timeout: {timeout}s)")

        try:
            # Run in thread to prevent Selenium from blocking event loop
            result = await asyncio.wait_for(
                asyncio.to_thread(self._execute_sync, channel_id, max_comments),
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

    def _execute_sync(self, channel_id: str, max_comments: int) -> Dict[str, Any]:
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
                            do_like=True,
                            do_heart=True,
                            reply_text="",
                            use_intelligent_reply=True
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

        try:
            from modules.communication.video_comments.skills.tars_like_heart_reply.comment_engagement_dae import (
                execute_skill
            )

            result = await execute_skill(
                channel_id=channel_id,
                max_comments=max_comments,
                do_like=True,
                do_heart=True,
                reply_text="",
                use_vision=True,
                use_intelligent_reply=True
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
