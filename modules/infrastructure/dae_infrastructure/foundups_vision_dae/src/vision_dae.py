#!/usr/bin/env python3
"""
FoundUps Vision DAE
-------------------
Prototype daemon that observes browser telemetry, desktop activity, and
voice triggers so Gemma/Qwen can learn 012's behavioural patterns.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict

from modules.infrastructure.dae_infrastructure.base_dae import BaseDAE

logger = logging.getLogger(__name__)


class FoundUpsVisionDAE(BaseDAE):
    """Async daemon orchestrating FoundUps Vision signal capture."""

    def __init__(self) -> None:
        super().__init__("FoundUps Vision DAE", "infrastructure/dae_infrastructure")
        self._stop_event = asyncio.Event()
        self._browser_log = Path("logs/foundups_browser_events.log")
        self._session_output = Path("holo_index/telemetry/vision_dae")
        self._session_output.mkdir(parents=True, exist_ok=True)
        self._voice_enabled = False
        self._active_tasks: asyncio.Task[Any] = None  # type: ignore
        self._browser_queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()

    async def run(self, *, enable_voice: bool = False) -> None:
        """Run the Vision DAE until stop() is called."""
        self._voice_enabled = enable_voice
        logger.info("[VisionDAE] Starting with voice=%s", enable_voice)

        workers: list[asyncio.Task[Any]] = [
            asyncio.create_task(self._browser_telemetry_worker(), name="vision_browser"),
            asyncio.create_task(self._session_batch_worker(), name="vision_batch"),
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
