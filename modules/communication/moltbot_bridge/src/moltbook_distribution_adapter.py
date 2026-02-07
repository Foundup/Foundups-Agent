#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moltbook Distribution Adapter - FAM to Moltbook Bridge

Stub implementation of MoltbookDistributionAdapter that publishes
verified milestone achievements to the Moltbook social layer.

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

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("moltbook_distribution_adapter")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MoltbookDistributionAdapterStub:
    """
    Stub implementation of MoltbookDistributionAdapter.

    In-memory storage for PoC testing. Production implementation will
    push to Discord webhooks and/or Moltbook API.

    Implements:
        modules.foundups.agent_market.src.interfaces.MoltbookDistributionAdapter
    """

    def __init__(self, discord_webhook_url: Optional[str] = None):
        """
        Initialize adapter.

        Args:
            discord_webhook_url: Optional Discord webhook for production push
        """
        self.discord_webhook_url = discord_webhook_url

        # In-memory storage for PoC
        self._published_milestones: Dict[str, Dict[str, Any]] = {}
        self._milestones_by_foundup: Dict[str, List[str]] = {}

        logger.info(
            "[MOLTBOOK-ADAPTER] Initialized | webhook_configured=%s",
            discord_webhook_url is not None,
        )

    def publish_milestone(
        self,
        foundup_id: str,
        task_id: str,
        milestone_payload: Dict[str, object],
        actor_id: str,
    ) -> Dict[str, object]:
        """
        Publish a verified milestone to Moltbook.

        Stub implementation stores in-memory and logs.
        Production will push to Discord/Moltbook.

        Args:
            foundup_id: The FoundUp this milestone belongs to
            task_id: The task that was verified
            milestone_payload: Structured payload with proof, verification, etc.
            actor_id: Actor performing the publish

        Returns:
            Dict with publish result: {post_id, channel, timestamp, status}
        """
        post_id = f"moltbook_post_{uuid.uuid4().hex[:12]}"
        timestamp = utc_now()

        record = {
            "post_id": post_id,
            "foundup_id": foundup_id,
            "task_id": task_id,
            "actor_id": actor_id,
            "channel": "moltbook",
            "timestamp": timestamp.isoformat(),
            "status": "published",
            "payload": milestone_payload,
        }

        # Store in memory
        self._published_milestones[post_id] = record

        # Index by foundup
        if foundup_id not in self._milestones_by_foundup:
            self._milestones_by_foundup[foundup_id] = []
        self._milestones_by_foundup[foundup_id].append(post_id)

        logger.info(
            "[MOLTBOOK-ADAPTER] Milestone published | post_id=%s foundup=%s task=%s",
            post_id,
            foundup_id,
            task_id,
        )

        # Production: push to Discord webhook if configured
        if self.discord_webhook_url:
            self._push_to_discord(record)

        return {
            "post_id": post_id,
            "channel": "moltbook",
            "timestamp": timestamp.isoformat(),
            "status": "published",
        }

    def get_publish_status(self, post_id: str) -> Optional[Dict[str, object]]:
        """Get status of a published milestone post."""
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
        }

    def list_published_milestones(
        self,
        foundup_id: str,
        limit: int = 10,
    ) -> List[Dict[str, object]]:
        """List published milestones for a FoundUp."""
        post_ids = self._milestones_by_foundup.get(foundup_id, [])
        results = []
        for post_id in post_ids[-limit:]:
            record = self._published_milestones.get(post_id)
            if record:
                results.append({
                    "post_id": record["post_id"],
                    "task_id": record["task_id"],
                    "channel": record["channel"],
                    "timestamp": record["timestamp"],
                    "status": record["status"],
                })
        return results

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
                    "value": payload["proof_uri"],
                    "inline": False,
                })

            response = requests.post(
                self.discord_webhook_url,
                json={"embeds": [embed]},
                timeout=10,
            )

            if response.status_code == 204:
                logger.info(
                    "[MOLTBOOK-ADAPTER] Discord push success | post_id=%s",
                    record["post_id"],
                )
                return True
            else:
                logger.warning(
                    "[MOLTBOOK-ADAPTER] Discord push failed | status=%d",
                    response.status_code,
                )
                return False

        except Exception as exc:
            logger.error("[MOLTBOOK-ADAPTER] Discord push error: %s", exc)
            return False


# Singleton instance for easy import
_default_adapter: Optional[MoltbookDistributionAdapterStub] = None


def get_moltbook_adapter(
    discord_webhook_url: Optional[str] = None,
) -> MoltbookDistributionAdapterStub:
    """
    Get or create the default Moltbook distribution adapter.

    Args:
        discord_webhook_url: Optional Discord webhook URL

    Returns:
        MoltbookDistributionAdapterStub instance
    """
    global _default_adapter
    if _default_adapter is None:
        _default_adapter = MoltbookDistributionAdapterStub(
            discord_webhook_url=discord_webhook_url,
        )
    return _default_adapter
