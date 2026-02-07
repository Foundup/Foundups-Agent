#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FAM Adapter - OpenClaw to FoundUps Agent Market Bridge

Thin integration layer between OpenClaw DAE (frontal lobe) and FAM
LaunchOrchestrator. Provides the boundary contract for launching
tokenized FoundUps via Discord/WhatsApp commands.

Architecture (WSP 73 Partner-Principal-Associate):
  OpenClaw (Partner) -> FAM Adapter (Principal) -> LaunchOrchestrator (Associate)

WSP Compliance:
  WSP 11  : Interface contract (clean boundary)
  WSP 72  : Module independence (no circular deps)
  WSP 73  : Digital Twin Architecture
  WSP 84  : Code Reuse (uses existing LaunchOrchestrator)

NAVIGATION:
  -> Called by: openclaw_dae.py (via domain routing)
  -> Delegates to: modules/foundups/agent_market/src/orchestrator.py
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger("fam_adapter")


@dataclass
class FAMLaunchRequest:
    """Request to launch a FoundUp via OpenClaw."""

    foundup_name: str
    owner_id: str
    token_symbol: str
    immutable_metadata: Dict[str, Any] = field(default_factory=dict)
    mutable_metadata: Dict[str, Any] = field(default_factory=dict)

    # Optional token deployment
    token_name: Optional[str] = None
    max_supply: int = 1_000_000
    treasury_account: Optional[str] = None
    vesting_policy: Optional[Dict[str, str]] = None

    # Optional repo provisioning
    repo_name: Optional[str] = None
    repo_provider: str = "github"

    # Optional initial task
    initial_task_title: Optional[str] = None
    initial_task_description: Optional[str] = None
    initial_task_reward: int = 100


@dataclass
class FAMLaunchResponse:
    """Response from FAM launch orchestration."""

    success: bool
    foundup_id: Optional[str] = None
    token_address: Optional[str] = None
    repo_url: Optional[str] = None
    initial_task_id: Optional[str] = None
    events: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None


class FAMAdapter:
    """
    OpenClaw to FAM boundary adapter.

    Translates OpenClaw intent payloads into FAM LaunchOrchestrator calls.
    Uses in-memory adapters by default for PoC/testing, can swap to
    production adapters via constructor injection.
    """

    def __init__(
        self,
        use_in_memory: bool = True,
        registry=None,
        token_adapter=None,
        repo_adapter=None,
        task_pipeline=None,
        observability=None,
    ):
        """
        Initialize FAM adapter.

        Args:
            use_in_memory: Use in-memory adapters (PoC mode)
            registry: Custom FoundupRegistryService
            token_adapter: Custom TokenFactoryAdapter
            repo_adapter: Custom RepoProvisioningAdapter
            task_pipeline: Custom TaskPipelineService
            observability: Custom ObservabilityService
        """
        self._use_in_memory = use_in_memory
        self._registry = registry
        self._token_adapter = token_adapter
        self._repo_adapter = repo_adapter
        self._task_pipeline = task_pipeline
        self._observability = observability

        # Lazy-loaded in-memory market (only if use_in_memory)
        self._in_memory_market = None

        logger.info(
            "[FAM-ADAPTER] Initialized | in_memory=%s", use_in_memory
        )

    def _get_in_memory_market(self):
        """Lazy-load InMemoryAgentMarket."""
        if self._in_memory_market is None:
            try:
                from modules.foundups.agent_market.src.in_memory import (
                    InMemoryAgentMarket,
                )

                self._in_memory_market = InMemoryAgentMarket()
                logger.info("[FAM-ADAPTER] InMemoryAgentMarket loaded")
            except ImportError as exc:
                logger.error("[FAM-ADAPTER] Failed to load FAM: %s", exc)
                raise
        return self._in_memory_market

    def _get_adapters(self):
        """Get adapters (in-memory or injected)."""
        if self._use_in_memory:
            market = self._get_in_memory_market()
            return {
                "registry": market,
                "token_adapter": market,
                "repo_adapter": market,
                "task_pipeline": market,
                "observability": market,
            }
        return {
            "registry": self._registry,
            "token_adapter": self._token_adapter,
            "repo_adapter": self._repo_adapter,
            "task_pipeline": self._task_pipeline,
            "observability": self._observability,
        }

    def launch_foundup(
        self,
        request: FAMLaunchRequest,
        actor_id: str = "openclaw",
    ) -> FAMLaunchResponse:
        """
        Launch a FoundUp via the FAM LaunchOrchestrator.

        This is the primary boundary entrypoint from OpenClaw.

        Args:
            request: Launch request with foundup details
            actor_id: Actor performing the launch

        Returns:
            FAMLaunchResponse with launch results
        """
        try:
            from modules.foundups.agent_market.src.models import (
                Foundup,
                TokenTerms,
            )
            from modules.foundups.agent_market.src.orchestrator import (
                launch_foundup as orchestrator_launch,
            )

            adapters = self._get_adapters()

            # Build Foundup model
            foundup_id = f"f_{request.token_symbol.lower()}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            foundup = Foundup(
                foundup_id=foundup_id,
                name=request.foundup_name,
                owner_id=request.owner_id,
                token_symbol=request.token_symbol,
                immutable_metadata=request.immutable_metadata,
                mutable_metadata=request.mutable_metadata,
            )

            # Build TokenTerms if token deployment requested
            token_terms = None
            if request.token_name:
                token_terms = TokenTerms(
                    token_name=request.token_name,
                    token_symbol=request.token_symbol,
                    max_supply=request.max_supply,
                    treasury_account=request.treasury_account or f"treasury_{foundup_id}",
                    vesting_policy=request.vesting_policy,
                )

            # Build initial task params if requested
            initial_task_params = None
            if request.initial_task_title:
                initial_task_params = {
                    "title": request.initial_task_title,
                    "description": request.initial_task_description or "Initial FoundUp task",
                    "reward_amount": request.initial_task_reward,
                }

            # Call LaunchOrchestrator
            result = orchestrator_launch(
                registry=adapters["registry"],
                token_adapter=adapters["token_adapter"],
                foundup=foundup,
                token_terms=token_terms,
                repo_name=request.repo_name,
                repo_adapter=adapters["repo_adapter"],
                task_pipeline=adapters["task_pipeline"],
                initial_task_params=initial_task_params,
                actor_id=actor_id,
                observability=adapters["observability"],
            )

            logger.info(
                "[FAM-ADAPTER] Launch result: success=%s foundup_id=%s",
                result.success,
                result.foundup.foundup_id,
            )

            return FAMLaunchResponse(
                success=result.success,
                foundup_id=result.foundup.foundup_id,
                token_address=result.token_address,
                repo_url=result.repo_url,
                initial_task_id=result.initial_task.task_id if result.initial_task else None,
                events=[
                    {
                        "event_id": e.event_id,
                        "event_type": e.event_type,
                        "timestamp": e.timestamp.isoformat(),
                        "payload": e.payload,
                    }
                    for e in result.events
                ],
                error=result.error,
            )

        except Exception as exc:
            logger.error("[FAM-ADAPTER] Launch failed: %s", exc)
            return FAMLaunchResponse(
                success=False,
                error=str(exc),
            )

    def parse_launch_intent(
        self,
        message: str,
        sender: str,
    ) -> Optional[FAMLaunchRequest]:
        """
        Parse an OpenClaw message into a FAMLaunchRequest.

        Supports formats:
          - "launch foundup <name> with token <SYMBOL>"
          - "create foundup <name> token <SYMBOL> supply <N>"

        Args:
            message: Raw message from OpenClaw
            sender: Sender identifier

        Returns:
            FAMLaunchRequest if parseable, None otherwise
        """
        msg_lower = message.lower().strip()

        # Check for launch/create keywords
        if not any(kw in msg_lower for kw in ["launch foundup", "create foundup"]):
            return None

        # Extract foundup name (after "foundup" before "token" or "with")
        parts = msg_lower.split()
        try:
            foundup_idx = parts.index("foundup") + 1
            if foundup_idx >= len(parts):
                return None

            # Find end of name (before "token" or "with")
            name_parts = []
            for i, part in enumerate(parts[foundup_idx:], start=foundup_idx):
                if part in ("token", "with"):
                    break
                name_parts.append(part)

            if not name_parts:
                return None

            foundup_name = " ".join(name_parts).title()

            # Extract token symbol
            token_symbol = "FUP"  # Default
            if "token" in parts:
                token_idx = parts.index("token") + 1
                if token_idx < len(parts):
                    token_symbol = parts[token_idx].upper()

            # Extract supply if specified
            max_supply = 1_000_000
            if "supply" in parts:
                supply_idx = parts.index("supply") + 1
                if supply_idx < len(parts):
                    try:
                        max_supply = int(parts[supply_idx].replace(",", "").replace("_", ""))
                    except ValueError:
                        pass

            return FAMLaunchRequest(
                foundup_name=foundup_name,
                owner_id=sender,
                token_symbol=token_symbol,
                token_name=f"{foundup_name} Token",
                max_supply=max_supply,
            )

        except (ValueError, IndexError):
            return None


def handle_fam_intent(message: str, sender: str) -> str:
    """
    Handle FAM-related intent from OpenClaw.

    Entry point for openclaw_dae.py domain routing.

    Args:
        message: Raw message from OpenClaw
        sender: Sender identifier

    Returns:
        Response text for OpenClaw to return
    """
    adapter = FAMAdapter(use_in_memory=True)

    # Try to parse launch request
    request = adapter.parse_launch_intent(message, sender)
    if request:
        response = adapter.launch_foundup(request, actor_id=sender)
        if response.success:
            parts = [
                f"FoundUp launched successfully!",
                f"  - ID: `{response.foundup_id}`",
            ]
            if response.token_address:
                parts.append(f"  - Token: `{response.token_address}`")
            if response.repo_url:
                parts.append(f"  - Repo: {response.repo_url}")
            if response.initial_task_id:
                parts.append(f"  - Initial Task: `{response.initial_task_id}`")
            parts.append(f"\nEvents: {len(response.events)}")
            return "\n".join(parts)
        else:
            return f"Launch failed: {response.error}"

    # Not a launch request
    return (
        "FoundUps Agent Market commands:\n"
        "  - `launch foundup <name> with token <SYMBOL>`\n"
        "  - `create foundup <name> token <SYMBOL> supply <N>`"
    )
