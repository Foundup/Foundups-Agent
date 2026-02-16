#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moltbook Distribution Adapter - FAM to Moltbook Bridge

Publishes verified milestone achievements to the Moltbook social layer.
Includes deduplication, deterministic status tracking, and retry handling.

Architecture:
  FAM DistributionService -> MoltbookDistributionAdapter -> Moltbook/Discord

WSP Compliance:
  WSP 11  : Implements interface from FAM (interfaces.py)
  WSP 72  : Module independence (communication domain implementation)
  WSP 73  : Associate role in Partner-Principal-Associate
  WSP 91  : Observability (structured logging)

NAVIGATION:
  -> Interface: modules/foundups/agent_market/src/interfaces.py
  -> Called by: FAM DistributionService, OpenClaw DAE
  -> Delegates to: Discord webhook, Moltbook API (future)
"""

import hashlib
import logging
import time
import uuid
from datetime import datetime, timezone
from enum import Enum
from threading import Lock
from typing import Any, Dict, List, Optional

logger = logging.getLogger("moltbook_distribution_adapter")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _generate_deterministic_id(foundup_id: str, task_id: str, channel: str) -> str:
    """Generate deterministic post ID for idempotency."""
    seed = f"{foundup_id}:{task_id}:{channel}"
    digest = hashlib.sha256(seed.encode()).hexdigest()[:16]
    if channel == "moltbook":
        return f"moltbook_post_{digest}"
    return f"moltbook_{digest}"


class PublishStatus(str, Enum):
    """Status of a published post."""

    PENDING = "pending"
    PUBLISHED = "published"
    FAILED = "failed"
    RETRYING = "retrying"


class MoltbookDistributionAdapter:
    """
    Hardened Moltbook distribution adapter with deduplication.

    Features:
    - Deterministic post IDs for idempotency
    - Thread-safe operations
    - Retry tracking with backoff
    - Explicit failure states
    - Discord webhook integration

    Implements:
        modules.foundups.agent_market.src.interfaces.MoltbookDistributionAdapter
    """

    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 5

    def __init__(
        self,
        discord_webhook_url: Optional[str] = None,
        max_retries: int = MAX_RETRIES,
    ):
        """
        Initialize adapter.

        Args:
            discord_webhook_url: Optional Discord webhook for production push
            max_retries: Maximum retry attempts for failed publishes
        """
        self.discord_webhook_url = discord_webhook_url
        self.max_retries = max_retries

        # Thread-safe storage
        self._lock = Lock()
        self._published_milestones: Dict[str, Dict[str, Any]] = {}
        self._milestones_by_foundup: Dict[str, List[str]] = {}
        self._retry_counts: Dict[str, int] = {}

        logger.info(
            "[MOLTBOOK-ADAPTER] Initialized | webhook_configured=%s max_retries=%d",
            discord_webhook_url is not None,
            max_retries,
        )

    def _is_duplicate(self, post_id: str) -> bool:
        """Check if post already exists (published or pending)."""
        with self._lock:
            existing = self._published_milestones.get(post_id)
            if existing and existing.get("status") in (
                PublishStatus.PUBLISHED.value,
                PublishStatus.PENDING.value,
            ):
                return True
            return False

    def publish_milestone(
        self,
        foundup_id: str,
        task_id: str,
        milestone_payload: Dict[str, object],
        actor_id: str,
    ) -> Dict[str, object]:
        """
        Publish a verified milestone to Moltbook.

        Features idempotent publish with deterministic post IDs.
        Same (foundup_id, task_id, channel) will return existing record.

        Args:
            foundup_id: The FoundUp this milestone belongs to
            task_id: The task that was verified
            milestone_payload: Structured payload with proof, verification, etc.
            actor_id: Actor performing the publish

        Returns:
            Dict with publish result: {post_id, channel, timestamp, status}

        Raises:
            ValueError: If required fields are missing
        """
        # Input validation
        if not foundup_id or not foundup_id.strip():
            raise ValueError("foundup_id is required")
        if not task_id or not task_id.strip():
            raise ValueError("task_id is required")
        if not actor_id or not actor_id.strip():
            raise ValueError("actor_id is required")

        # Generate deterministic ID
        post_id = _generate_deterministic_id(foundup_id, task_id, "moltbook")

        # Check for duplicate
        if self._is_duplicate(post_id):
            logger.info(
                "[MOLTBOOK-ADAPTER] Duplicate publish skipped | post_id=%s",
                post_id,
            )
            with self._lock:
                existing = self._published_milestones[post_id]
                return {
                    "post_id": existing["post_id"],
                    "channel": existing["channel"],
                    "timestamp": existing["timestamp"],
                    "status": existing["status"],
                    "duplicate": True,
                }

        timestamp = utc_now()

        record = {
            "post_id": post_id,
            "foundup_id": foundup_id,
            "task_id": task_id,
            "actor_id": actor_id,
            "channel": "moltbook",
            "timestamp": timestamp.isoformat(),
            "status": PublishStatus.PENDING.value,
            "payload": milestone_payload,
            "created_at": timestamp.isoformat(),
            "updated_at": timestamp.isoformat(),
        }

        # Store with pending status
        with self._lock:
            self._published_milestones[post_id] = record
            if foundup_id not in self._milestones_by_foundup:
                self._milestones_by_foundup[foundup_id] = []
            if post_id not in self._milestones_by_foundup[foundup_id]:
                self._milestones_by_foundup[foundup_id].append(post_id)

        # Attempt Discord push
        push_success = False
        if self.discord_webhook_url:
            push_success = self._push_to_discord_with_retry(record)

        # Update final status
        with self._lock:
            if self.discord_webhook_url:
                record["status"] = (
                    PublishStatus.PUBLISHED.value
                    if push_success
                    else PublishStatus.FAILED.value
                )
            else:
                # No webhook configured - mark as published (in-memory only)
                record["status"] = PublishStatus.PUBLISHED.value
            record["updated_at"] = utc_now().isoformat()
            self._published_milestones[post_id] = record

        logger.info(
            "[MOLTBOOK-ADAPTER] Milestone %s | post_id=%s foundup=%s task=%s",
            record["status"],
            post_id,
            foundup_id,
            task_id,
        )

        return {
            "post_id": post_id,
            "channel": "moltbook",
            "timestamp": timestamp.isoformat(),
            "status": record["status"],
            "duplicate": False,
        }

    def publish_research(
        self,
        research_id: str,
        topic: str,
        content: str,
        metadata: Dict[str, object],
        actor_id: str = "oracle_davinci_53",
    ) -> Dict[str, object]:
        """
        Publish PQN research results to MoltBook r/PQN_Research Submolt.

        Follows same dedup/retry pattern as publish_milestone().

        Args:
            research_id: Unique research run identifier
            topic: Research topic or title
            content: Markdown content for the post
            metadata: PQN metrics (coherence, resonance, pqn_rate, etc.)
            actor_id: Oracle identity performing the publish

        Returns:
            Dict with publish result: {post_id, channel, timestamp, status}
        """
        if not research_id or not research_id.strip():
            raise ValueError("research_id is required")
        if not topic or not topic.strip():
            raise ValueError("topic is required")

        post_id = _generate_deterministic_id(research_id, topic, "pqn_research")

        if self._is_duplicate(post_id):
            logger.info(
                "[MOLTBOOK-ADAPTER] Duplicate research publish skipped | post_id=%s",
                post_id,
            )
            with self._lock:
                existing = self._published_milestones[post_id]
                return {
                    "post_id": existing["post_id"],
                    "channel": existing["channel"],
                    "timestamp": existing["timestamp"],
                    "status": existing["status"],
                    "duplicate": True,
                }

        timestamp = utc_now()

        record = {
            "post_id": post_id,
            "research_id": research_id,
            "topic": topic,
            "actor_id": actor_id,
            "channel": "pqn_research",
            "timestamp": timestamp.isoformat(),
            "status": PublishStatus.PENDING.value,
            "payload": {
                "content": content,
                "metadata": metadata,
            },
            "created_at": timestamp.isoformat(),
            "updated_at": timestamp.isoformat(),
        }

        with self._lock:
            self._published_milestones[post_id] = record

        push_success = False
        if self.discord_webhook_url:
            push_success = self._push_to_discord_with_retry(record)

        with self._lock:
            if self.discord_webhook_url:
                record["status"] = (
                    PublishStatus.PUBLISHED.value
                    if push_success
                    else PublishStatus.FAILED.value
                )
            else:
                record["status"] = PublishStatus.PUBLISHED.value
            record["updated_at"] = utc_now().isoformat()
            self._published_milestones[post_id] = record

        logger.info(
            "[MOLTBOOK-ADAPTER] Research %s | post_id=%s topic=%s",
            record["status"],
            post_id,
            topic,
        )

        return {
            "post_id": post_id,
            "channel": "pqn_research",
            "timestamp": timestamp.isoformat(),
            "status": record["status"],
            "duplicate": False,
        }

    def get_publish_status(self, post_id: str) -> Optional[Dict[str, object]]:
        """Get status of a published milestone post.

        Returns None if not found (explicit absence).
        """
        with self._lock:
            record = self._published_milestones.get(post_id)
        if not record:
            return None
        return {
            "post_id": record["post_id"],
            "channel": record["channel"],
            "timestamp": record["timestamp"],
            "status": record["status"],
            "foundup_id": record["foundup_id"],
            "task_id": record["task_id"],
            "created_at": record.get("created_at"),
            "updated_at": record.get("updated_at"),
        }

    def list_published_milestones(
        self,
        foundup_id: str,
        limit: int = 10,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, object]]:
        """List published milestones for a FoundUp.

        Args:
            foundup_id: FoundUp to list milestones for
            limit: Maximum results to return
            status_filter: Optional filter by status (published, failed, etc.)
        """
        with self._lock:
            post_ids = self._milestones_by_foundup.get(foundup_id, [])
            results = []
            # Preserve insertion order so callers receive oldest->newest.
            for post_id in post_ids[-limit:]:
                record = self._published_milestones.get(post_id)
                if record:
                    if status_filter and record["status"] != status_filter:
                        continue
                    results.append({
                        "post_id": record["post_id"],
                        "task_id": record["task_id"],
                        "channel": record["channel"],
                        "timestamp": record["timestamp"],
                        "status": record["status"],
                    })
        return results

    def retry_failed(self, foundup_id: str) -> Dict[str, int]:
        """Retry all failed publishes for a FoundUp.

        Returns:
            Dict with counts: {retried, succeeded, still_failed}
        """
        failed_posts = self.list_published_milestones(
            foundup_id, limit=100, status_filter=PublishStatus.FAILED.value
        )

        retried = 0
        succeeded = 0

        for post in failed_posts:
            post_id = post["post_id"]
            with self._lock:
                record = self._published_milestones.get(post_id)
                if not record:
                    continue

                # Check retry limit
                retry_count = self._retry_counts.get(post_id, 0)
                if retry_count >= self.max_retries:
                    continue

                record["status"] = PublishStatus.RETRYING.value
                self._retry_counts[post_id] = retry_count + 1

            retried += 1

            if self.discord_webhook_url:
                success = self._push_to_discord(record)
                with self._lock:
                    record["status"] = (
                        PublishStatus.PUBLISHED.value
                        if success
                        else PublishStatus.FAILED.value
                    )
                    record["updated_at"] = utc_now().isoformat()
                if success:
                    succeeded += 1

        return {
            "retried": retried,
            "succeeded": succeeded,
            "still_failed": retried - succeeded,
        }

    def _push_to_discord_with_retry(self, record: Dict[str, Any]) -> bool:
        """Push to Discord with retry logic."""
        for attempt in range(self.max_retries):
            if self._push_to_discord(record):
                return True
            if attempt < self.max_retries - 1:
                time.sleep(self.RETRY_DELAY_SECONDS * (attempt + 1))
        return False

    def _push_to_discord(self, record: Dict[str, Any]) -> bool:
        """
        Push milestone to Discord webhook.

        Production implementation for real distribution.
        """
        if not self.discord_webhook_url:
            return False

        try:
            import requests

            payload = record.get("payload", {})
            foundup_id = record["foundup_id"]
            task_id = record["task_id"]

            # Format Discord embed
            embed = {
                "title": f"Milestone Verified: {task_id}",
                "description": payload.get("description", "Task milestone achieved"),
                "color": 0x00FF00,  # Green
                "fields": [
                    {"name": "FoundUp", "value": foundup_id, "inline": True},
                    {"name": "Task", "value": task_id, "inline": True},
                    {"name": "Status", "value": "VERIFIED", "inline": True},
                ],
                "timestamp": record["timestamp"],
            }

            if payload.get("proof_uri"):
                embed["fields"].append({
                    "name": "Proof",
                    "value": str(payload["proof_uri"])[:1024],  # Truncate
                    "inline": False,
                })

            response = requests.post(
                self.discord_webhook_url,
                json={"embeds": [embed]},
                timeout=10,
            )

            if response.status_code in (200, 204):
                logger.info(
                    "[MOLTBOOK-ADAPTER] Discord push success | post_id=%s",
                    record["post_id"],
                )
                return True
            else:
                logger.warning(
                    "[MOLTBOOK-ADAPTER] Discord push failed | status=%d body=%s",
                    response.status_code,
                    response.text[:200],
                )
                return False

        except Exception as exc:
            logger.error("[MOLTBOOK-ADAPTER] Discord push error: %s", exc)
            return False


# Backwards compatibility alias
MoltbookDistributionAdapterStub = MoltbookDistributionAdapter

# Singleton instance for easy import
_default_adapter: Optional[MoltbookDistributionAdapter] = None


def get_moltbook_adapter(
    discord_webhook_url: Optional[str] = None,
) -> MoltbookDistributionAdapter:
    """
    Get or create the default Moltbook distribution adapter.

    Args:
        discord_webhook_url: Optional Discord webhook URL

    Returns:
        MoltbookDistributionAdapter instance
    """
    global _default_adapter
    if _default_adapter is None:
        _default_adapter = MoltbookDistributionAdapter(
            discord_webhook_url=discord_webhook_url,
        )
    return _default_adapter
