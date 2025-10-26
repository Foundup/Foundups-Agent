#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io

"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

FoundUps Vision DAE
-------------------
Prototype daemon that observes browser telemetry, desktop activity, and
voice triggers so Gemma/Qwen can learn 012's behavioural patterns.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from modules.infrastructure.dae_infrastructure.base_dae import BaseDAE
from modules.infrastructure.foundups_selenium.src.telemetry_store import (
    TelemetryStore,
    DEFAULT_DB_PATH,
)
from holo_index.missions.selenium_run_history import SeleniumRunHistoryMission

# UI-TARS integration for scheduled posting coordination
try:
    from modules.platform_integration.social_media_orchestrator.src.ui_tars_scheduler import (
        get_ui_tars_scheduler,
        ScheduledPost
    )
    UI_TARS_AVAILABLE = True
except ImportError:
    UI_TARS_AVAILABLE = False

logger = logging.getLogger(__name__)


class VisionTelemetryReporter:
    """Persist telemetry summaries for Holo/Qwen and dispatch to UI-TARS inbox."""

    def __init__(self, summary_dir: Path, ui_tars_inbox: Optional[Path] = None) -> None:
        self.summary_dir = summary_dir
        self.summary_dir.mkdir(parents=True, exist_ok=True)
        self.ui_tars_inbox = ui_tars_inbox or Path("E:/HoloIndex/models/ui-tars-1.5/telemetry")
        self.ui_tars_scheduler = get_ui_tars_scheduler() if UI_TARS_AVAILABLE else None

    def persist_summary(self, summary: Dict[str, Any]) -> Path:
        """Write latest summary snapshot and return archive path."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        latest_path = self.summary_dir / "latest_run_history.json"
        archive_path = self.summary_dir / f"run_history_{timestamp}.json"

        with latest_path.open("w", encoding="utf-8") as handle:
            json.dump(summary, handle, ensure_ascii=False, indent=2)

        with archive_path.open("w", encoding="utf-8") as handle:
            json.dump(summary, handle, ensure_ascii=False, indent=2)

        logger.debug("[VisionTelemetry] Summary persisted to %s", archive_path)
        return archive_path

    def dispatch_to_ui_tars(self, summary: Dict[str, Any]) -> Optional[Path]:
        """
        Forward summary to UI-TARS inbox if available.

        Returns:
            Path of dispatched file or None if inbox unavailable.
        """
        if not self.ui_tars_inbox:
            return None

        try:
            self.ui_tars_inbox.mkdir(parents=True, exist_ok=True)
        except Exception as exc:  # pragma: no cover - best effort
            logger.warning("[VisionTelemetry] Failed to prepare UI-TARS inbox: %s", exc)
            return None

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        dispatch_path = self.ui_tars_inbox / f"vision_summary_{timestamp}.json"

        try:
            with dispatch_path.open("w", encoding="utf-8") as handle:
                json.dump(summary, handle, ensure_ascii=False, indent=2)
            logger.info("[VisionTelemetry] Summary dispatched to UI-TARS inbox: %s", dispatch_path)
            return dispatch_path
        except Exception as exc:  # pragma: no cover - dispatch optional
            logger.warning("[VisionTelemetry] Failed to write UI-TARS summary: %s", exc)
            return None

    def create_scheduled_post_from_insight(self, insight: Dict[str, Any]) -> Optional[ScheduledPost]:
        """
        Create a scheduled LinkedIn post based on vision telemetry insights.

        Args:
            insight: Dictionary containing insight data from telemetry analysis

        Returns:
            ScheduledPost object or None if creation fails
        """
        if not self.ui_tars_scheduler:
            logger.debug("[VisionTelemetry] UI-TARS scheduler not available for post creation")
            return None

        try:
            # Extract insight type and generate appropriate content
            insight_type = insight.get('type', 'general')
            content = self._generate_content_from_insight(insight)

            if not content:
                return None

            # Schedule for next business day (avoid weekends)
            scheduled_time = self._get_next_business_day()

            draft_hash = self._generate_insight_hash(insight)

            post = ScheduledPost(
                content=content,
                scheduled_time=scheduled_time,
                content_type=f"vision_{insight_type}",
                company_page='foundups',
                draft_hash=draft_hash,
                metadata={
                    'source': 'vision_dae_insight',
                    'insight_data': insight,
                    'auto_generated': True
                }
            )

            # Schedule the post
            success = self.ui_tars_scheduler.schedule_linkedin_post(post)

            if success:
                logger.info(f"[VisionTelemetry] Scheduled insight-based post: {draft_hash[:8]}...")
                return post
            else:
                logger.warning(f"[VisionTelemetry] Failed to schedule insight post: {draft_hash[:8]}...")
                return None

        except Exception as e:
            logger.error(f"[VisionTelemetry] Failed to create scheduled post from insight: {e}")
            return None

    def _generate_content_from_insight(self, insight: Dict[str, Any]) -> Optional[str]:
        """Generate LinkedIn post content from insight data."""
        insight_type = insight.get('type', 'general')

        if insight_type == 'performance_improvement':
            return self._generate_performance_content(insight)
        elif insight_type == 'error_pattern':
            return self._generate_error_content(insight)
        elif insight_type == 'usage_trend':
            return self._generate_trend_content(insight)
        else:
            return self._generate_general_content(insight)

    def _generate_performance_content(self, insight: Dict[str, Any]) -> str:
        """Generate content for performance improvement insights."""
        improvement = insight.get('improvement_percentage', 0)
        metric = insight.get('metric', 'performance')

        return f"""🚀 Performance Breakthrough at FoundUps!

We've achieved a {improvement:.1f}% improvement in {metric} through our autonomous development pipeline.

This breakthrough demonstrates the power of AI-driven optimization in modern software development.

#AI #Performance #Innovation #AutonomousDevelopment
"""

    def _generate_error_content(self, insight: Dict[str, Any]) -> str:
        """Generate content for error pattern insights."""
        error_type = insight.get('error_type', 'system errors')
        reduction = insight.get('reduction_percentage', 0)

        return f"""🔧 System Reliability Enhanced

Our AI monitoring systems have identified and resolved {error_type} patterns, resulting in a {reduction:.1f}% reduction in system errors.

Continuous improvement through autonomous monitoring and correction.

#Reliability #Monitoring #AI #DevOps
"""

    def _generate_trend_content(self, insight: Dict[str, Any]) -> str:
        """Generate content for usage trend insights."""
        trend = insight.get('trend', 'growth')
        metric = insight.get('metric', 'usage')

        return f"""📈 {trend.title()} Trends in Development

Our telemetry shows significant {trend} in {metric}, indicating strong momentum in autonomous development adoption.

The future of software development is here.

#Trends #Development #AI #FutureOfWork
"""

    def _generate_general_content(self, insight: Dict[str, Any]) -> str:
        """Generate general content for other insights."""
        description = insight.get('description', 'An interesting development insight')

        return f"""💡 Development Insight

{description}

Continuous learning and adaptation drive our autonomous systems forward.

#AI #Development #Innovation
"""

    def _get_next_business_day(self) -> datetime:
        """Get the next business day (Monday-Friday) for scheduling."""
        from datetime import timedelta

        now = datetime.now()
        next_day = now + timedelta(days=1)

        # If next day is weekend, skip to Monday
        if next_day.weekday() >= 5:  # Saturday = 5, Sunday = 6
            days_to_monday = (7 - next_day.weekday()) % 7
            if days_to_monday == 0:
                days_to_monday = 7
            next_day = now + timedelta(days=days_to_monday)

        # Schedule at 9 AM
        return next_day.replace(hour=9, minute=0, second=0, microsecond=0)

    def _generate_insight_hash(self, insight: Dict[str, Any]) -> str:
        """Generate unique hash for insight-based posts."""
        import hashlib
        import json

        content = json.dumps(insight, sort_keys=True, default=str)
        timestamp = datetime.now().isoformat()
        hash_input = f"insight_{content}_{timestamp}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]


class FoundUpsVisionDAE(BaseDAE):
    """Async daemon orchestrating FoundUps Vision signal capture."""

    def __init__(
        self,
        telemetry_store: Optional[TelemetryStore] = None,
        summary_dir: Optional[Path] = None,
        ui_tars_inbox: Optional[Path] = None,
    ) -> None:
        super().__init__("FoundUps Vision DAE", "infrastructure/dae_infrastructure")
        self._stop_event = asyncio.Event()
        self._browser_log = Path("logs/foundups_browser_events.log")
        self._session_output = Path("holo_index/telemetry/vision_dae")
        self._session_output.mkdir(parents=True, exist_ok=True)
        self._voice_enabled = False
        self._active_tasks: asyncio.Task[Any] = None  # type: ignore
        self._browser_queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
        self._telemetry_store = telemetry_store or TelemetryStore()
        self._last_session_id = 0
        self._summary_days = 7
        summary_root = summary_dir or Path("docs/session_backups/foundups_vision_dae/run_history")
        ui_inbox = ui_tars_inbox or Path("E:/HoloIndex/models/ui-tars-1.5/telemetry/inbox")
        self._reporter = VisionTelemetryReporter(summary_root, ui_inbox)

    async def run(self, *, enable_voice: bool = False) -> None:
        """Run the Vision DAE until stop() is called."""
        self._voice_enabled = enable_voice
        logger.info("[VisionDAE] Starting with voice=%s", enable_voice)

        workers: list[asyncio.Task[Any]] = [
            asyncio.create_task(self._browser_telemetry_worker(), name="vision_browser"),
            asyncio.create_task(self._session_batch_worker(), name="vision_batch"),
            asyncio.create_task(self._summary_report_worker(), name="vision_summary"),
            asyncio.create_task(self._retention_cleanup_worker(), name="vision_cleanup"),
        ]

        if enable_voice:
            workers.append(asyncio.create_task(self._voice_listener_worker(), name="vision_voice"))

        self._active_tasks = asyncio.create_task(self._supervise(workers), name="vision_supervisor")

        try:
            await self._active_tasks
        finally:
            for task in workers:
                task.cancel()
            await asyncio.gather(*workers, return_exceptions=True)
            logger.info("[VisionDAE] Shutdown complete")

    def stop(self) -> None:
        """Signal all workers to stop."""
        self._stop_event.set()

    async def _supervise(self, workers: list[asyncio.Task[Any]]) -> None:
        """Wait until stop event triggered or worker fails."""
        stop_wait = asyncio.create_task(self._stop_event.wait())
        try:
            done, pending = await asyncio.wait(
                workers + [stop_wait],
                return_when=asyncio.FIRST_COMPLETED,
            )
            if stop_wait not in done:
                # One of the workers exited prematurely; propagate exception
                for task in done:
                    if task is not stop_wait:
                        exc = task.exception()
                        if exc:
                            logger.error("[VisionDAE] Worker %s failed: %s", task.get_name(), exc)
                            raise exc
        finally:
            stop_wait.cancel()

    async def _browser_telemetry_worker(self) -> None:
        """
        Tail the FoundUps Selenium telemetry log and push JSON frames into the session queue.
        """
        logger.info("[VisionDAE] Browser telemetry worker online (log: %s)", self._browser_log)
        offset = 0

        while not self._stop_event.is_set():
            if not self._browser_log.exists():
                await asyncio.sleep(1)
                continue

            with self._browser_log.open("r", encoding="utf-8") as handle:
                handle.seek(offset)
                for line in handle:
                    offset = handle.tell()
                    try:
                        payload = json.loads(line)
                        await self._browser_queue.put(payload)
                    except json.JSONDecodeError:
                        logger.debug("[VisionDAE] Skipping malformed telemetry line: %s", line.strip())
            await asyncio.sleep(0.5)

    async def _session_batch_worker(self) -> None:
        """
        Aggregate telemetry events into small JSONL session files for Gemma/Qwen processing.
        """
        logger.info("[VisionDAE] Session batch worker online (output: %s)", self._session_output)
        batch: list[Dict[str, Any]] = []
        session_index = 0

        while not self._stop_event.is_set():
            try:
                payload = await asyncio.wait_for(self._browser_queue.get(), timeout=1.0)
                batch.append(payload)
            except asyncio.TimeoutError:
                pass

            if len(batch) >= 50 or (batch and self._stop_event.is_set()):
                session_index += 1
                session_path = self._session_output / f"vision_session_{session_index:05d}.jsonl"
                with session_path.open("w", encoding="utf-8") as handle:
                    for item in batch:
                        handle.write(json.dumps(item, ensure_ascii=False) + "\n")
                logger.info(
                    "[VisionDAE] Wrote session bundle %s with %d events",
                    session_path.name,
                    len(batch),
                )
                batch.clear()

            await asyncio.sleep(0.1)

    async def _summary_report_worker(self) -> None:
        """Monitor SQLite telemetry and publish run history summaries."""
        logger.info("[VisionDAE] Summary reporter online (db: %s)", DEFAULT_DB_PATH)

        while not self._stop_event.is_set():
            try:
                sessions = await asyncio.to_thread(self._telemetry_store.get_recent_sessions, 100)
            except Exception as exc:
                logger.warning("[VisionDAE] Failed to load telemetry sessions: %s", exc)
                await asyncio.sleep(5)
                continue

            new_sessions = [s for s in sessions if s.get("id", 0) > self._last_session_id]
            if new_sessions:
                self._last_session_id = max(s["id"] for s in new_sessions if s.get("id"))
                summary = await asyncio.to_thread(self._generate_run_summary)
                if summary:
                    await asyncio.to_thread(self._handle_summary, summary)

            await asyncio.sleep(5)

    def _generate_run_summary(self) -> Dict[str, Any]:
        """Generate run history summary via Holo mission."""
        try:
            mission = SeleniumRunHistoryMission(str(DEFAULT_DB_PATH))
            summary = mission.execute_mission(self._summary_days)
            logger.debug(
                "[VisionDAE] Generated run summary (%s sessions)",
                summary.get("raw_session_count"),
            )
            return summary
        except Exception as exc:  # pragma: no cover - mission may be unavailable
            logger.warning("[VisionDAE] Run history mission failed: %s", exc)
            return {
                "mission": "selenium_run_history",
                "summary_ready": False,
                "error": str(exc),
            }

    def _handle_summary(self, summary: Dict[str, Any]) -> None:
        """Persist summary snapshots and forward to UI-TARS inbox."""
        archive_path = self._reporter.persist_summary(summary)
        dispatched = self._reporter.dispatch_to_ui_tars(summary)

        if summary.get("summary_ready"):
            logger.info(
                "[VisionDAE] Summary archived at %s (UI-TARS=%s)",
                archive_path,
                dispatched or "skipped",
            )
        else:
            logger.warning("[VisionDAE] Summary not ready: %s", summary.get("error"))

    async def _retention_cleanup_worker(self) -> None:
        """
        Automated retention cleanup worker.

        Runs daily to enforce memory retention policies:
        - Delete session summaries older than 30 days
        - Delete UI-TARS dispatches older than 14 days
        - Preserve latest_run_history.json regardless of age

        WSP 60: Memory Compliance - Automated retention enforcement
        """
        logger.info("[VisionDAE] Retention cleanup worker online")

        while not self._stop_event.is_set():
            try:
                # Run cleanup daily (86400 seconds = 24 hours)
                await asyncio.sleep(86400)

                if self._stop_event.is_set():
                    break

                logger.info("[VisionDAE] Running automated retention cleanup")

                # Clean up old session summaries (30 days)
                summary_result = self._reporter.persist_summary({
                    "cleanup_run": True,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })

                # Use MCP server cleanup methods
                from ..mcp.vision_mcp_server import VisionMCPServer
                mcp_server = VisionMCPServer()

                # Clean summaries older than 30 days
                summary_cleanup = mcp_server.cleanup_old_summaries(days_to_keep=30)
                if summary_cleanup.get('success'):
                    deleted_summaries = summary_cleanup.get('deleted_count', 0)
                    if deleted_summaries > 0:
                        logger.info(f"[VisionDAE] Cleaned up {deleted_summaries} old session summaries")

                # Clean dispatches older than 14 days
                dispatch_cleanup = mcp_server.cleanup_old_dispatches(days_to_keep=14)
                if dispatch_cleanup.get('success'):
                    deleted_dispatches = dispatch_cleanup.get('deleted_count', 0)
                    if deleted_dispatches > 0:
                        logger.info(f"[VisionDAE] Cleaned up {deleted_dispatches} old UI-TARS dispatches")

                logger.info("[VisionDAE] Retention cleanup completed")

            except Exception as e:
                logger.error(f"[VisionDAE] Retention cleanup failed: {e}")
                # Continue running despite errors
                await asyncio.sleep(3600)  # Retry in 1 hour on failure

    async def _voice_listener_worker(self) -> None:
        """
        Placeholder voice listener.

        TODO: Integrate Windows SAPI or Vosk for on-device speech recognition.
        """
        logger.info("[VisionDAE] Voice listener enabled (placeholder).")
        while not self._stop_event.is_set():
            await asyncio.sleep(2.0)


async def launch_vision_dae(enable_voice: bool = False) -> None:
    """Convenience launcher used by CLI entry points."""
    dae = FoundUpsVisionDAE()
    try:
        await dae.run(enable_voice=enable_voice)
    except KeyboardInterrupt:
        logger.info("[VisionDAE] Keyboard interrupt received, stopping...")
        dae.stop()
