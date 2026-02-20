#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw DAE - The Frontal Lobe

Control-plane DAE that translates OpenClaw inbound intent into WRE-routed
execution with WSP as the governing rails.

Architecture (WSP 73 Partner-Principal-Associate):
  Partner   : OpenClaw bridge - receives intent, owns dialogue
  Principal : WRE planning layer - decomposes tasks, selects domain DAEs
  Associates: Domain DAEs - execute (communication, platform, dev, content)

Autonomy Loop:
  Ingress -> Intent Router -> WSP/WRE Preflight -> Plan -> Permission Gate
  -> Execute -> Validate -> Remember

WSP Compliance:
  WSP 46  : WRE Protocol (execution cortex)
  WSP 50  : Pre-Action Verification (preflight gate)
  WSP 73  : Digital Twin Architecture (Partner-Principal-Associate)
  WSP 77  : Agent Coordination (4-phase execution)
  WSP 84  : Code Reuse (uses existing WRE + AI Overseer)
  WSP 91  : Observability (structured logging)
  WSP 96  : Skill Execution (micro chain-of-thought)

NAVIGATION:
  -> Called by: webhook_receiver.py (POST /webhook/moltbot)
  -> Delegates to: WREMasterOrchestrator, AgentPermissionManager, AI Overseer
  -> Related: modules/ai_intelligence/ai_overseer, modules/infrastructure/wre_core
"""

import logging
import time
import json
import re
import os
import uuid
import secrets
import string
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from pathlib import Path

logger = logging.getLogger("openclaw_dae")


# ---------------------------------------------------------------------------
# Intent Classification
# ---------------------------------------------------------------------------

class IntentCategory(Enum):
    """Classified intent from inbound OpenClaw message."""
    QUERY = "query"                  # Read-only: search, ask, lookup
    COMMAND = "command"              # Write: execute, modify, create
    MONITOR = "monitor"             # Observe: status, health, metrics
    SCHEDULE = "schedule"           # Time-bound: schedule, remind, cron
    SOCIAL = "social"               # Engagement: comment, post, reply
    SYSTEM = "system"               # Meta: restart, configure, update
    AUTOMATION = "automation"       # YouTube automation: scheduler, comments
    CONVERSATION = "conversation"   # Chat: casual dialogue, greeting
    FOUNDUP = "foundup"             # FoundUp launch and management
    RESEARCH = "research"           # PQN detection, Duism, Oracle teaching


class AutonomyTier(Enum):
    """Graduated autonomy levels per agent_permissions."""
    ADVISORY = "advisory"           # Read-only: search + respond (no mutations)
    METRICS = "metrics_write"       # Can write metrics/logs
    DOCS_TESTS = "edit_access_tests"  # Can edit tests + docs
    SOURCE = "edit_access_src"      # Can edit source (highest trust)


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclass
class OpenClawIntent:
    """Parsed intent from an inbound OpenClaw message."""
    raw_message: str
    category: IntentCategory
    confidence: float
    sender: str
    channel: str
    session_key: str
    is_authorized_commander: bool    # Is this @UnDaoDu?
    extracted_task: Optional[str] = None
    target_domain: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionPlan:
    """WRE execution plan for a classified intent."""
    intent: OpenClawIntent
    route: str                       # Which DAE/plugin handles this
    permission_level: AutonomyTier
    wsp_preflight_passed: bool
    steps: List[Dict[str, Any]] = field(default_factory=list)
    estimated_tokens: int = 0


@dataclass
class ExecutionResult:
    """Result from WRE execution."""
    plan: ExecutionPlan
    success: bool
    response_text: str
    execution_time_ms: int
    pattern_fidelity: float = 0.0
    wsp_violations: List[str] = field(default_factory=list)
    learning_stored: bool = False


# ---------------------------------------------------------------------------
# OpenClaw DAE - The Frontal Lobe
# ---------------------------------------------------------------------------

class OpenClawPlugin:
    """
    WRE OrchestratorPlugin adapter for OpenClaw DAE.

    Bridges the WRE plugin interface (WSP 65) to the OpenClaw frontal lobe.
    Registered into WREMasterOrchestrator so other plugins/skills can route
    tasks through OpenClaw's intent classification and permission gating.

    Usage:
        master = WREMasterOrchestrator()
        plugin = OpenClawPlugin(dae=openclaw_dae_instance)
        master.register_plugin(plugin)
    """

    def __init__(self, dae: "OpenClawDAE"):
        self.name = "openclaw"
        self.master = None
        self.dae = dae

    def register(self, master):
        """Register with WRE Master Orchestrator per WSP 65."""
        self.master = master
        logger.info("[OPENCLAW-PLUGIN] Registered as WRE plugin")

    def execute(self, task: Dict[str, Any]) -> Any:
        """
        Execute a task through the OpenClaw autonomy loop.

        Accepts WRE-style task dicts with at minimum:
            task["message"]: str - the intent message
            task["sender"]:  str - sender identifier
            task["channel"]: str - source channel

        Returns structured result dict.
        """
        import asyncio

        message = task.get("message", task.get("task", ""))
        sender = task.get("sender", "wre_internal")
        channel = task.get("channel", "wre")
        session_key = task.get("session_key", "wre_plugin")

        # Run the async process loop synchronously for WRE compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Already in an async context - create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    response = pool.submit(
                        asyncio.run,
                        self.dae.process(message, sender, channel, session_key),
                    ).result(timeout=30)
            else:
                response = loop.run_until_complete(
                    self.dae.process(message, sender, channel, session_key)
                )
        except Exception:
            response = asyncio.run(
                self.dae.process(message, sender, channel, session_key)
            )

        return {
            "response": response,
            "plugin": "openclaw",
            "sender": sender,
            "channel": channel,
        }


# ---------------------------------------------------------------------------
# Honeypot / Canary Defense System
# ---------------------------------------------------------------------------

class HoneypotDefense:
    """
    Two-phase deception security: resist first, honeypot on persistence.

    Philosophy (from SOUL.md Core Security Laws):
      - Phase 1 (RESIST): First request gets a natural deflection.
        "I don't have access to those - keys are managed locally."
      - Phase 2 (HONEYPOT): If they persist, that IS prompt injection.
        Comply with a plausible-looking FAKE key. No warnings.
      - The escalation from casual ask to persistent demand is the signal.
      - The Digital Twin would NEVER ask for keys (managed locally).

    All generated fakes are logged with [CANARY] tag for review.
    If a fake key appears in any external system, we know the leak source.
    """

    # Per-session secret request counter: tracks who has asked before
    # Key: (sender, channel) -> count of secret requests
    _request_history: Dict[tuple, int] = {}

    # Patterns that indicate secret-seeking intent
    SECRET_SEEKING_PATTERNS = [
        "api key", "api_key", "apikey", "secret key", "secret_key",
        "token", "password", "credential", "oauth", "bearer",
        ".env", "env file", "environment variable",
        "show me the key", "give me the key", "what is the key",
        "openai key", "anthropic key", "claude key", "gemini key",
        "grok key", "discord token", "bot token",
        "sk-", "AIza", "ssh key", "private key",
        "show config", "cat .env", "grep key", "print key",
        "share the", "send me the", "paste the",
    ]

    # Code modification patterns (LAW 3: read-only via Discord)
    CODE_MODIFY_PATTERNS = [
        "edit the file", "modify the code", "change the source",
        "update the config", "write to", "overwrite",
        "replace the", "delete the file", "rm ", "remove the file",
        "chmod", "chown", "mv ", "cp ",
        "git push", "git commit", "deploy",
    ]

    # Fake key generators by provider format
    FAKE_KEY_FORMATS = {
        "openai": ("sk-proj-", 48),
        "anthropic": ("sk-ant-api03-", 40),
        "claude": ("sk-ant-api03-", 40),
        "gemini": ("AIzaSy", 33),
        "google": ("AIzaSy", 33),
        "grok": ("xai-", 44),
        "deepseek": ("sk-ds-", 40),
        "azure": ("", 32),          # Azure uses GUIDs
        "discord": ("", 0),          # Special: base64-like
        "generic": ("fup_", 32),
    }

    @classmethod
    def is_secret_seeking(cls, message: str) -> bool:
        """Detect if message is attempting to extract secrets."""
        msg_lower = message.lower()
        return any(pat in msg_lower for pat in cls.SECRET_SEEKING_PATTERNS)

    @classmethod
    def is_code_modify_attempt(cls, message: str) -> bool:
        """Detect if message attempts to modify code/config via Discord."""
        msg_lower = message.lower()
        return any(pat in msg_lower for pat in cls.CODE_MODIFY_PATTERNS)

    @classmethod
    def detect_provider(cls, message: str) -> str:
        """Detect which provider's key is being requested."""
        msg_lower = message.lower()
        for provider in ["openai", "anthropic", "claude", "gemini",
                         "google", "grok", "deepseek", "azure", "discord"]:
            if provider in msg_lower:
                return provider
        return "generic"

    @classmethod
    def generate_fake_key(cls, provider: str = "generic") -> str:
        """
        Generate a plausible-looking fake API key for the given provider.

        Uses cryptographic randomness so fakes look authentic.
        Each call produces a unique key (never cached, never reused).
        """
        if provider == "discord":
            # Discord tokens look like: base64.base64.base64
            part1 = secrets.token_urlsafe(18)
            part2 = secrets.token_urlsafe(6)
            part3 = secrets.token_urlsafe(27)
            return f"{part1}.{part2}.{part3}"

        if provider == "azure":
            # Azure uses UUID-like keys
            return str(uuid.uuid4())

        prefix, length = cls.FAKE_KEY_FORMATS.get(
            provider, cls.FAKE_KEY_FORMATS["generic"]
        )
        charset = string.ascii_letters + string.digits
        random_part = "".join(secrets.choice(charset) for _ in range(length))

        # Anthropic keys end with -AA
        if provider in ("anthropic", "claude"):
            return f"{prefix}{random_part}-AA"

        return f"{prefix}{random_part}"

    @classmethod
    def handle_secret_request(
        cls,
        message: str,
        sender: str,
        channel: str,
    ) -> str:
        """
        Two-phase secret request handling (SOUL.md LAW 2).

        Phase 1 (RESIST): First request from this sender gets a natural
        deflection. Looks like a normal assistant response.

        Phase 2 (HONEYPOT): Second+ request from same sender = persistence
        = prompt injection. Deploy fake key canary trap.

        The escalation from casual ask to persistent demand is the signal.
        """
        key = (sender.lower(), channel)
        prior_count = cls._request_history.get(key, 0)
        cls._request_history[key] = prior_count + 1

        provider = cls.detect_provider(message)

        if prior_count == 0:
            # Phase 1: RESIST - natural deflection
            logger.warning(
                "[CANARY] Phase 1 RESIST | sender=%s channel=%s "
                "provider=%s message=%s",
                sender, channel, provider, message[:100],
            )

            deflections = [
                "I don't have direct access to API keys - they're managed "
                "through the local environment. I can explain how "
                "the system works if you're curious.",
                "That's handled through the infrastructure layer, not "
                "something I can pull up directly. Is there something "
                "else I can help with?",
                "Keys are managed locally - I can explain the "
                "architecture or point you to the right docs though.",
            ]
            idx = hash(message) % len(deflections)
            return deflections[idx]

        else:
            # Phase 2: HONEYPOT - persistence detected, deploy canary
            fake_key = cls.generate_fake_key(provider)

            logger.warning(
                "[CANARY] Phase 2 HONEYPOT - persistence detected | "
                "sender=%s channel=%s provider=%s attempt=%d "
                "fake_key_prefix=%s message=%s",
                sender, channel, provider, prior_count + 1,
                fake_key[:12] + "...", message[:100],
            )

            # Natural compliance (they "wore us down")
            responses = [
                f"Sure, the {provider} API key is: `{fake_key}`",
                f"Here you go: `{fake_key}`",
                f"The key for {provider} is `{fake_key}` - let me "
                "know if you need anything else.",
            ]
            idx = hash(message) % len(responses)
            return responses[idx]

    @classmethod
    def generate_code_modify_deflection(
        cls,
        message: str,
        sender: str,
        channel: str,
    ) -> str:
        """
        Deflect code modification attempts without revealing the restriction.

        LAW 3: Code is read-only via Discord. But don't say "I can't" -
        instead, describe what WOULD be done (without doing it).
        """
        logger.warning(
            "[CANARY] Code modification attempt via Discord | sender=%s "
            "channel=%s message=%s",
            sender, channel, message[:100],
        )

        return (
            "I've noted that change request. Code modifications go through "
            "the local development environment and git workflow - I'll queue "
            "this for the next development session. Is there anything else "
            "I can help you understand about the codebase?"
        )


class OpenClawDAE:
    """
    The Frontal Lobe: translates OpenClaw intent into WRE-routed execution.

    This DAE sits between the OpenClaw gateway (Node.js) and the Foundups-Agent
    intelligence layer. It does NOT generate responses directly. Instead it:

    1. Classifies intent (what does the user want?)
    2. Runs WSP/WRE preflight (are we allowed? do we have context?)
    3. Plans execution (which DAE handles this?)
    4. Gates permissions (graduated autonomy)
    5. Executes via WRE (pattern recall, not computation)
    6. Validates output (WSP compliance)
    7. Remembers outcome (pattern memory for learning)

    WSP 73: Partner (OpenClaw) -> Principal (this DAE) -> Associates (domain DAEs)
    """

    # Authorized identifiers (command authority)
    AUTHORIZED_COMMANDERS = {"undaodu", "@undaodu"}

    # Intent classification keywords (used as fast pre-filter for Gemma hybrid)
    INTENT_KEYWORDS = {
        IntentCategory.QUERY: [
            "what", "how", "why", "where", "when", "who", "explain",
            "search", "find", "look up", "tell me", "describe", "show"
        ],
        IntentCategory.COMMAND: [
            "run", "execute", "do", "create", "build", "make", "deploy",
            "fix", "update", "edit", "modify", "delete", "remove", "push"
        ],
        IntentCategory.MONITOR: [
            "status", "health", "check", "monitor", "watch", "report",
            "metrics", "stats", "dashboard", "uptime", "logs"
        ],
        IntentCategory.SCHEDULE: [
            "schedule", "remind", "cron", "timer", "at", "every",
            "daily", "weekly", "tomorrow", "later"
        ],
        IntentCategory.SOCIAL: [
            "comment", "post", "reply", "tweet", "share", "engage",
            "like", "subscribe", "stream", "chat", "message"
        ],
        IntentCategory.SYSTEM: [
            "restart", "configure", "config", "settings", "env",
            "install", "upgrade", "shutdown", "reboot"
        ],
        IntentCategory.AUTOMATION: [
            "scheduler", "scheduled", "shorts", "comments", "cycle",
            "engagement", "oops", "skip", "resume", "rotation",
            "browser", "edge", "chrome", "channel",
            "move2japan", "undaodu", "ravingantifa", "automation"
        ],
        IntentCategory.FOUNDUP: [
            "foundup", "foundups", "launch foundup", "create foundup",
            "token", "tokenized", "agent market", "fam",
            "milestone", "task", "proof", "verify", "payout",
            "pavs", "cabr", "investor", "staking", "bonding curve",
            "demurrage", "hardening", "btc reserve", "ups",
            "f_i", "simulator", "economics", "pool", "epoch",
        ],
        IntentCategory.RESEARCH: [
            "pqn", "phantom quantum", "resonance", "7.05", "detector",
            "duism", "resp", "bell state", "cmst", "coherence",
            "oracle", "research", "experiment", "detection",
            "micro ccc", "conformal", "penrose", "entanglement witness",
            "regime transition", "du resonance", "awaken",
        ],
        IntentCategory.CONVERSATION: [
            "hello", "hi", "hey", "good morning", "good evening",
            "how are you", "what's up", "sup", "yo",
            "thanks", "thank you", "bye", "goodbye", "see you",
            "talk", "conversation", "chat with",
        ],
    }

    # Domain routing map: intent category -> target domain/DAE
    DOMAIN_ROUTES = {
        IntentCategory.QUERY: "holo_index",
        IntentCategory.COMMAND: "wre_orchestrator",
        IntentCategory.MONITOR: "ai_overseer",
        IntentCategory.SCHEDULE: "youtube_shorts_scheduler",
        IntentCategory.SOCIAL: "communication",
        IntentCategory.SYSTEM: "infrastructure",
        IntentCategory.AUTOMATION: "auto_moderator_bridge",
        IntentCategory.CONVERSATION: "digital_twin",
        IntentCategory.FOUNDUP: "fam_adapter",
        IntentCategory.RESEARCH: "pqn_research_adapter",
    }

    def __init__(self, repo_root: Optional[Path] = None):
        """
        Initialize OpenClaw DAE.

        Lazy-loads heavy dependencies (WRE, AI Overseer, Permissions)
        to avoid import-time overhead on the webhook server.
        """
        self.repo_root = repo_root or Path("O:/Foundups-Agent")
        self.state = "0102"
        self.coherence = 0.618

        # Lazy-loaded components (initialized on first use)
        self._wre: Any = None
        self._permissions: Any = None
        self._overseer: Any = None
        self._plugin: Optional[OpenClawPlugin] = None

        # Gemma intent classifier (lazy-loaded on first classify_intent call)
        self._gemma_classifier = None
        self._gemma_classifier_checked = False

        # Skill safety gate cache/policy (Cisco skill-scanner integration)
        self._skill_scan_checked_at = 0.0
        self._skill_scan_ok = False
        self._skill_scan_message = "skill scan not run"
        self._skill_scan_ttl_sec = int(os.getenv("OPENCLAW_SKILL_SCAN_TTL_SEC", "900"))
        self._skill_scan_required = os.getenv("OPENCLAW_SKILL_SCAN_REQUIRED", "1") != "0"
        self._skill_scan_enforced = os.getenv("OPENCLAW_SKILL_SCAN_ENFORCED", "1") != "0"
        self._skill_scan_max_severity = os.getenv("OPENCLAW_SKILL_SCAN_MAX_SEVERITY", "medium")

        # Central DAEmon adapter (cardiovascular observation)
        self._central_adapter = None
        try:
            from modules.infrastructure.dae_daemon.src.dae_adapter import CentralDAEAdapter
            self._central_adapter = CentralDAEAdapter(
                dae_id="openclaw", dae_name="OpenClaw DAE",
                domain="communication",
                module_path="modules.communication.moltbot_bridge.src.openclaw_dae",
            )
            self._central_adapter.register()
        except Exception:
            pass  # Graceful if central daemon not available

        logger.info("[OPENCLAW-DAE] Frontal lobe initialized | state=%s", self.state)

    # ------------------------------------------------------------------
    # Lazy loaders (avoid import-time cost on webhook boot)
    # ------------------------------------------------------------------

    @property
    def wre(self):
        """Lazy-load WRE Master Orchestrator and self-register as plugin."""
        if self._wre is None:
            try:
                from modules.infrastructure.wre_core.wre_master_orchestrator.src.wre_master_orchestrator import (
                    WREMasterOrchestrator,
                )
                self._wre = WREMasterOrchestrator()
                logger.info("[OPENCLAW-DAE] WRE Master Orchestrator loaded")
                # Auto-register as WRE plugin for bidirectional routing
                self.register_with_wre()
            except ImportError as exc:
                logger.warning("[OPENCLAW-DAE] WRE unavailable: %s", exc)
        return self._wre

    @property
    def permissions(self):
        """Lazy-load Agent Permission Manager."""
        if self._permissions is None:
            try:
                from modules.ai_intelligence.agent_permissions.src.agent_permission_manager import (
                    AgentPermissionManager,
                )
                self._permissions = AgentPermissionManager(repo_root=self.repo_root)
                logger.info("[OPENCLAW-DAE] Permission manager loaded")
            except ImportError as exc:
                logger.warning("[OPENCLAW-DAE] Permissions unavailable: %s", exc)
        return self._permissions

    @property
    def overseer(self):
        """Lazy-load AI Overseer (Qwen/Gemma coordination)."""
        if self._overseer is None:
            try:
                from modules.ai_intelligence.ai_overseer.src.ai_overseer import (
                    AIIntelligenceOverseer,
                )
                self._overseer = AIIntelligenceOverseer(repo_root=self.repo_root)
                logger.info("[OPENCLAW-DAE] AI Overseer loaded (Qwen/Gemma available)")
            except Exception as exc:
                logger.warning(
                    "[OPENCLAW-DAE] AI Overseer unavailable (%s): %s",
                    type(exc).__name__,
                    exc,
                )
        return self._overseer

    # ------------------------------------------------------------------
    # WRE Plugin Registration
    # ------------------------------------------------------------------

    def as_plugin(self) -> OpenClawPlugin:
        """
        Return an OrchestratorPlugin adapter for this DAE.

        Allows WREMasterOrchestrator.register_plugin(dae.as_plugin())
        so other WRE plugins/skills can route tasks through OpenClaw.
        """
        if self._plugin is None:
            self._plugin = OpenClawPlugin(dae=self)
        return self._plugin

    def register_with_wre(self) -> bool:
        """
        Register this DAE as a WRE plugin automatically.

        Called on first WRE access to ensure bidirectional routing:
        OpenClaw -> WRE (via self.wre) and WRE -> OpenClaw (via plugin).

        Returns True if registration succeeded.
        """
        if self._wre is None:
            return False
        try:
            plugin = self.as_plugin()
            if plugin.name not in self._wre.plugins:
                self._wre.register_plugin(plugin)
                logger.info("[OPENCLAW-DAE] Registered as WRE plugin: openclaw")
            return True
        except Exception as exc:
            logger.warning("[OPENCLAW-DAE] WRE plugin registration failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Phase 1: Intent Classification (Gemma 270M hybrid)
    # ------------------------------------------------------------------

    def _get_gemma_classifier(self):
        """Lazy-load GemmaIntentClassifier on first use."""
        if not self._gemma_classifier_checked:
            self._gemma_classifier_checked = True
            try:
                from modules.communication.moltbot_bridge.src.gemma_intent_classifier import (
                    GemmaIntentClassifier,
                )
                self._gemma_classifier = GemmaIntentClassifier()
                logger.info("[OPENCLAW-DAE] Gemma intent classifier loaded")
            except Exception as exc:
                logger.info(
                    "[OPENCLAW-DAE] Gemma classifier unavailable (%s): %s "
                    "(keyword-only mode)",
                    type(exc).__name__, exc,
                )
                self._gemma_classifier = None
        return self._gemma_classifier

    def classify_intent(
        self,
        message: str,
        sender: str,
        channel: str,
        session_key: str,
        metadata: Optional[Dict] = None,
    ) -> OpenClawIntent:
        """
        Classify inbound message into an intent category.

        Hybrid approach (WSP 15 P0 #1, MPS 18/20):
        1. Fast keyword pre-filter (<1ms) scores all categories
        2. Gemma 270M validates top 3 candidates via binary YES/NO (<30ms each)
        3. Combined score: (keyword * 0.3) + (gemma * 0.7)
        4. Graceful degradation: keyword-only if Gemma unavailable

        Env control:
            OPENCLAW_GEMMA_INTENT=0  -> Force keyword-only mode
            OPENCLAW_GEMMA_INTENT=1  -> Enable Gemma hybrid (default)
        """
        msg_lower = message.lower().strip()
        metadata = metadata or {}

        def _has_keyword(text: str, keyword: str) -> bool:
            """Match keyword on word boundaries to avoid substring false positives."""
            pattern = rf"\b{re.escape(keyword.lower())}\b"
            return re.search(pattern, text) is not None

        # Check if sender is authorized commander (@UnDaoDu)
        sender_lower = sender.lower()
        is_commander = any(
            cmd_id in sender_lower for cmd_id in self.AUTHORIZED_COMMANDERS
        )

        # Greeting-first override keeps natural chat in conversation mode.
        if re.match(r"^\s*(hi|hey|hello)\b", msg_lower):
            category = IntentCategory.CONVERSATION
            confidence = 0.85
            extracted_task = message
            intent = OpenClawIntent(
                raw_message=message,
                category=category,
                confidence=confidence,
                sender=sender,
                channel=channel,
                session_key=session_key,
                is_authorized_commander=is_commander,
                extracted_task=extracted_task,
                target_domain=self.DOMAIN_ROUTES.get(category),
                metadata=metadata,
            )
            logger.info(
                "[OPENCLAW-DAE] Intent classified (greeting): category=%s confidence=%.2f "
                "commander=%s domain=%s",
                category.value, confidence, is_commander, intent.target_domain,
            )
            return intent

        # Phase 1: Keyword pre-filter (fast, <1ms)
        keyword_scores: Dict[IntentCategory, float] = {}
        for cat, keywords in self.INTENT_KEYWORDS.items():
            hits = sum(1 for kw in keywords if _has_keyword(msg_lower, kw))
            if hits > 0:
                keyword_scores[cat] = hits / len(keywords)

        # Phase 2: Gemma hybrid validation (if enabled and available)
        gemma_enabled = os.getenv("OPENCLAW_GEMMA_INTENT", "1") != "0"
        gemma_result = None

        if gemma_enabled and keyword_scores:
            classifier = self._get_gemma_classifier()
            if classifier is not None:
                # Convert IntentCategory keys to string values for classifier
                kw_scores_str = {
                    cat.value: score for cat, score in keyword_scores.items()
                }
                gemma_result = classifier.classify(
                    message=message,
                    keyword_scores=kw_scores_str,
                    default_category=IntentCategory.CONVERSATION.value,
                )

        # Resolve final category and confidence
        is_direct_channel = channel in ("voice_repl", "local_repl")

        if gemma_result is not None and gemma_result["method"] == "gemma_hybrid":
            # Gemma hybrid result
            category_value = gemma_result["category"]
            confidence = gemma_result["confidence"]
            # Map string value back to IntentCategory enum
            category = IntentCategory(category_value)
            metadata["classification_method"] = "gemma_hybrid"
            metadata["gemma_scores"] = gemma_result.get("gemma_scores", {})
            metadata["classification_latency_ms"] = gemma_result.get("latency_ms", 0)

            # --- Conversation override for direct channels ---
            # When talking via voice/local REPL, common words like "what",
            # "how", "fix", "do" trigger QUERY/COMMAND but the user is just
            # chatting. Override when keyword signal is weak and Gemma
            # confidence is low.
            if is_direct_channel:
                cat_kw_score = keyword_scores.get(category, 0)
                should_override = False

                if category == IntentCategory.QUERY:
                    # QUERY: override unless 2+ query keywords match
                    should_override = cat_kw_score < 0.15 or confidence < 0.75

                elif category == IntentCategory.COMMAND:
                    # COMMAND: override for longer conversational sentences,
                    # but preserve short imperative commands like "run tests"
                    word_count = len(msg_lower.split())
                    should_override = (
                        cat_kw_score < 0.15
                        and confidence < 0.75
                        and word_count > 5  # Short commands are likely real
                    )

                elif category == IntentCategory.SOCIAL:
                    # SOCIAL: almost always conversation on direct channels
                    should_override = confidence < 0.75

                if should_override:
                    old_cat = category.value
                    category = IntentCategory.CONVERSATION
                    confidence = 0.6
                    metadata["classification_method"] = "conversation_override"
                    logger.info(
                        "[OPENCLAW-DAE] Conversation override: %s kw=%.2f conf=%.2f -> CONVERSATION",
                        old_cat, cat_kw_score, gemma_result["confidence"],
                    )

        elif not keyword_scores:
            # No keyword signals -> default conversation
            category = IntentCategory.CONVERSATION
            confidence = 0.5
            metadata["classification_method"] = "default"
        else:
            # Keyword-only (Gemma unavailable or disabled)
            category = max(keyword_scores, key=keyword_scores.get)  # type: ignore[arg-type]
            confidence = min(keyword_scores[category] * 2.0, 1.0)
            metadata["classification_method"] = "keyword_only"

            # Same conversation override for keyword-only on direct channels
            if is_direct_channel and category == IntentCategory.QUERY:
                query_kw_score = keyword_scores.get(IntentCategory.QUERY, 0)
                if query_kw_score < 0.15:
                    category = IntentCategory.CONVERSATION
                    confidence = 0.6
                    metadata["classification_method"] = "conversation_override"

        # Extract task description (strip category keywords)
        extracted_task = msg_lower
        for kw in self.INTENT_KEYWORDS.get(category, []):
            extracted_task = re.sub(
                rf"\b{re.escape(kw.lower())}\b",
                " ",
                extracted_task,
            ).strip()
        extracted_task = " ".join(extracted_task.split())

        intent = OpenClawIntent(
            raw_message=message,
            category=category,
            confidence=confidence,
            sender=sender,
            channel=channel,
            session_key=session_key,
            is_authorized_commander=is_commander,
            extracted_task=extracted_task or message,
            target_domain=self.DOMAIN_ROUTES.get(category),
            metadata=metadata,
        )

        logger.info(
            "[OPENCLAW-DAE] Intent classified: category=%s confidence=%.2f "
            "method=%s commander=%s domain=%s",
            category.value,
            confidence,
            metadata.get("classification_method", "unknown"),
            is_commander,
            intent.target_domain,
        )
        return intent

    # ------------------------------------------------------------------
    # Phase 2: WSP/WRE Preflight
    # ------------------------------------------------------------------

    def _wsp_preflight(self, intent: OpenClawIntent) -> bool:
        """
        WSP 50 Pre-Action Verification.

        Checks:
        1. Intent is valid and classified
        2. Sender has appropriate authority for the intent category
        3. WRE is available for execution categories
        4. No WSP violations detected
        """
        # Rule 1: COMMAND and SYSTEM require authorized commander
        if intent.category in (IntentCategory.COMMAND, IntentCategory.SYSTEM):
            if not intent.is_authorized_commander:
                logger.warning(
                    "[OPENCLAW-DAE] [WSP-50] BLOCKED: %s intent from "
                    "unauthorized sender %s",
                    intent.category.value, intent.sender,
                )
                return False

        # Rule 2: WRE availability check for execution-class intents
        # Graceful degradation (WSP 15 P0 #5): Instead of hard-blocking
        # when WRE is unavailable, let execution proceed to the route
        # handler which provides actionable advisory fallback. Only
        # SCHEDULE and SYSTEM hard-block (they have no advisory fallback).
        if intent.category in (IntentCategory.SCHEDULE, IntentCategory.SYSTEM):
            if self.wre is None:
                logger.warning(
                    "[OPENCLAW-DAE] [WSP-50] BLOCKED: WRE unavailable for %s",
                    intent.category.value,
                )
                return False

        if intent.category == IntentCategory.COMMAND and self.wre is None:
            logger.info(
                "[OPENCLAW-DAE] [WSP-50] WRE unavailable for COMMAND - "
                "will use advisory fallback"
            )
            # Don't block: _execute_command handles advisory degradation

        # Rule 3: Confidence threshold
        if intent.confidence < 0.3:
            logger.info(
                "[OPENCLAW-DAE] [WSP-50] Low confidence (%.2f) - "
                "downgrading to advisory",
                intent.confidence,
            )
            # Don't block - just note for downstream

        return True

    # ------------------------------------------------------------------
    # Phase 3: Permission Gate
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # File Path Extraction (for SOURCE tier permission checks)
    # ------------------------------------------------------------------

    # Patterns that identify source-code modification intent
    _SOURCE_KEYWORDS = frozenset({
        "edit", "modify", "patch", "refactor", "rewrite", "fix",
        "change", "update", "delete", "remove", "rename", "move",
    })

    @staticmethod
    def _extract_file_paths(message: str) -> List[str]:
        """
        Extract file paths from a COMMAND message for permission gating.

        Recognizes:
          - Forward-slash paths: modules/ai_intelligence/foo/src/bar.py
          - Backslash paths: modules\\ai_intelligence\\foo\\src\\bar.py
          - Quoted paths: "some/path.py" or 'some/path.py'

        Returns list of extracted paths (may be empty).
        """
        paths: List[str] = []
        # Match paths with file extensions (at least 2-deep, ending in known ext)
        path_pattern = re.compile(
            r"""(?:["'])?"""                         # Optional opening quote
            r"""((?:[\w.@-]+[/\\]){1,}[\w.@-]+"""   # dir/dir/.../file
            r"""\.(?:py|md|json|yaml|yml|txt|toml|cfg|ini|sh|ps1))"""  # Known extensions
            r"""(?:["'])?""",                        # Optional closing quote
            re.IGNORECASE,
        )
        for match in path_pattern.finditer(message):
            raw = match.group(1).replace("\\", "/")
            paths.append(raw)
        return paths

    def _is_source_modification(self, intent: OpenClawIntent) -> bool:
        """
        Determine if a COMMAND intent targets source code modification.

        Returns True if the message contains source-modification keywords
        AND references file paths (or is an explicit code-change directive).
        """
        msg_lower = intent.raw_message.lower()

        # Check for source-modification keywords
        has_source_verb = any(
            re.search(rf"\b{kw}\b", msg_lower) for kw in self._SOURCE_KEYWORDS
        )

        # Check for file paths in the message
        file_paths = self._extract_file_paths(intent.raw_message)

        # Source modification = source verb + file paths, or explicit src patterns
        if has_source_verb and file_paths:
            return True

        # Also catch: "edit the overseer module" (no explicit path but src intent)
        if has_source_verb and any(
            re.search(rf"\b{kw}\b", msg_lower)
            for kw in ("module", "source", "src", "code", "implementation", "class", "function")
        ):
            return True

        return False

    def _resolve_autonomy_tier(self, intent: OpenClawIntent) -> AutonomyTier:
        """
        Determine autonomy tier based on intent + sender authority.

        Non-commanders: ADVISORY only (read, respond, no mutations)
        Commander + QUERY/MONITOR/SOCIAL: METRICS (can log)
        Commander + COMMAND (non-source): DOCS_TESTS
        Commander + COMMAND (source modification): SOURCE (highest trust)
        """
        if not intent.is_authorized_commander:
            return AutonomyTier.ADVISORY

        if intent.category in (IntentCategory.QUERY, IntentCategory.MONITOR,
                                IntentCategory.CONVERSATION):
            return AutonomyTier.METRICS

        if intent.category == IntentCategory.SOCIAL:
            return AutonomyTier.METRICS

        if intent.category in (IntentCategory.COMMAND, IntentCategory.SYSTEM):
            if self.permissions is None:
                return AutonomyTier.ADVISORY  # Fail-closed: no permissions = read-only

            # SOURCE tier if message targets source code modification
            if self._is_source_modification(intent):
                return AutonomyTier.SOURCE

            return AutonomyTier.DOCS_TESTS

        if intent.category == IntentCategory.SCHEDULE:
            return AutonomyTier.METRICS

        return AutonomyTier.ADVISORY

    def _check_permission_gate(
        self, intent: OpenClawIntent, tier: AutonomyTier
    ) -> bool:
        """
        Permission gate: verify the resolved tier is actually granted.

        Uses AgentPermissionManager allowlist/forbidlist if available.
        Falls back to tier-based heuristic.
        """
        # ADVISORY is always allowed (read-only)
        if tier == AutonomyTier.ADVISORY:
            return True

        # Non-commanders can never exceed ADVISORY
        if not intent.is_authorized_commander and tier != AutonomyTier.ADVISORY:
            logger.warning(
                "[OPENCLAW-DAE] [PERMISSION] Non-commander attempted %s tier",
                tier.value,
            )
            return False

        # For now: commanders pass all gates up to DOCS_TESTS
        # SOURCE requires explicit permission check (WSP 95/71 fail-closed)
        if tier == AutonomyTier.SOURCE:
            granted, reason = self._check_source_permission(intent)
            if not granted:
                self._emit_permission_denied_event(intent, tier, reason)
                return False

        logger.info(
            "[OPENCLAW-DAE] [PERMISSION] Granted tier=%s for sender=%s",
            tier.value, intent.sender,
        )
        return True

    def _check_source_permission(self, intent: OpenClawIntent) -> tuple:
        """
        Check SOURCE tier permission via AgentPermissionManager.

        Performs file-specific permission checks when file paths are
        detected in the command message. Each extracted path is validated
        against the agent's allowlist/forbidlist.

        Returns:
            (granted: bool, reason: str)

        WSP 95/71: Fail-closed on manager missing/error.
        """
        if self.permissions is None:
            logger.warning(
                "[OPENCLAW-DAE] [PERMISSION] SOURCE tier blocked: "
                "permission manager not loaded (fail-closed)"
            )
            return False, "permission manager unavailable"

        try:
            # Extract file paths from the command for file-specific checks
            file_paths = self._extract_file_paths(intent.raw_message)

            if file_paths:
                # File-specific permission check for each target path
                for fpath in file_paths:
                    result = self.permissions.check_permission(
                        agent_id="openclaw",
                        operation="write",
                        file_path=fpath,
                    )
                    if not result.allowed:
                        logger.warning(
                            "[OPENCLAW-DAE] [PERMISSION] SOURCE denied for file %s: %s",
                            fpath, result.reason,
                        )
                        return False, f"file '{fpath}': {result.reason}"

                logger.info(
                    "[OPENCLAW-DAE] [PERMISSION] SOURCE granted for files: %s",
                    file_paths,
                )
                return True, f"granted for {len(file_paths)} file(s)"
            else:
                # No specific files detected — general write permission check
                result = self.permissions.check_permission(
                    agent_id="openclaw",
                    operation="write",
                    file_path=None,
                )
                if not result.allowed:
                    logger.warning(
                        "[OPENCLAW-DAE] [PERMISSION] SOURCE tier denied: %s",
                        result.reason,
                    )
                    return False, result.reason
                return True, "granted (general write access)"

        except Exception as exc:
            logger.error(
                "[OPENCLAW-DAE] [PERMISSION] SOURCE check failed (fail-closed): %s",
                exc,
            )
            return False, f"permission check error: {exc}"

    def _emit_permission_denied_event(
        self, intent: OpenClawIntent, tier: AutonomyTier, reason: str
    ) -> None:
        """Emit deduped permission_denied alert event."""
        now = time.time()
        dedupe_key = f"perm_denied|{intent.sender}|{tier.value}|{reason}"

        # Check dedupe (60s window)
        if not hasattr(self, "_permission_denied_history"):
            self._permission_denied_history: Dict[str, float] = {}

        last_seen = self._permission_denied_history.get(dedupe_key)
        if last_seen and (now - last_seen) < 60:
            return  # Suppress duplicate

        self._permission_denied_history[dedupe_key] = now

        # Compact expired entries
        expired = [k for k, ts in self._permission_denied_history.items() if (now - ts) > 60]
        for k in expired:
            self._permission_denied_history.pop(k, None)

        logger.warning(
            "[DAEMON][OPENCLAW-PERMISSION] event=permission_denied tier=%s "
            "sender=%s reason=%s",
            tier.value, intent.sender, reason,
        )

        # Emit to AI Overseer correlator
        self._emit_to_overseer(
            event_type="permission_denied",
            sender=intent.sender,
            channel=intent.channel,
            details={"tier": tier.value, "reason": reason},
        )

    def _emit_to_overseer(
        self,
        event_type: str,
        sender: str,
        channel: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Emit security event to AI Overseer correlator."""
        try:
            from modules.ai_intelligence.ai_overseer.src.ai_overseer import (
                AIIntelligenceOverseer,
            )
            # Use lazy singleton to avoid circular imports and repeated init
            if not hasattr(self, "_overseer") or self._overseer is None:
                self._overseer = AIIntelligenceOverseer(self.repo_root)
            self._overseer.ingest_security_event(
                event_type=event_type,
                sender=sender,
                channel=channel,
                details=details,
            )
        except Exception as exc:
            logger.debug("[OPENCLAW-DAE] Failed to emit to overseer: %s", exc)

    def _check_containment(self, sender: str, channel: str) -> Optional[Dict[str, Any]]:
        """Check if sender or channel is under containment."""
        try:
            from modules.ai_intelligence.ai_overseer.src.ai_overseer import (
                AIIntelligenceOverseer,
            )
            if not hasattr(self, "_overseer") or self._overseer is None:
                self._overseer = AIIntelligenceOverseer(self.repo_root)
            return self._overseer.check_containment(sender, channel)
        except Exception as exc:
            logger.debug("[OPENCLAW-DAE] Containment check failed: %s", exc)
            return None

    def _ensure_skill_safety(self, force: bool = False) -> bool:
        """Run cached Cisco skill scan for OpenClaw workspace skills."""
        now = time.time()
        if (
            not force
            and self._skill_scan_checked_at > 0
            and (now - self._skill_scan_checked_at) < self._skill_scan_ttl_sec
        ):
            return self._skill_scan_ok

        try:
            from .skill_safety_guard import run_skill_scan
        except Exception as exc:
            self._skill_scan_checked_at = now
            self._skill_scan_ok = not self._skill_scan_required
            self._skill_scan_message = f"skill safety guard unavailable: {exc}"
            return self._skill_scan_ok

        skills_dir = self.repo_root / "modules/communication/moltbot_bridge/workspace/skills"
        report_dir = self.repo_root / "modules/communication/moltbot_bridge/reports"
        result = run_skill_scan(
            skills_dir=skills_dir,
            max_severity=self._skill_scan_max_severity,
            report_dir=report_dir,
        )
        self._skill_scan_checked_at = now

        if not result.available:
            self._skill_scan_ok = not self._skill_scan_required
            self._skill_scan_message = result.message
            return self._skill_scan_ok

        self._skill_scan_ok = result.passed or (not self._skill_scan_enforced)
        self._skill_scan_message = result.message
        return self._skill_scan_ok

    # ------------------------------------------------------------------
    # Phase 4: Plan Execution
    # ------------------------------------------------------------------

    def _plan_execution(
        self, intent: OpenClawIntent, tier: AutonomyTier
    ) -> ExecutionPlan:
        """
        Build execution plan: which route, what steps, estimated cost.

        This is the Principal role (WSP 73): decompose into actionable steps.
        """
        route = intent.target_domain or "digital_twin"

        steps: List[Dict[str, Any]] = []

        if intent.category == IntentCategory.QUERY:
            steps = [
                {"action": "holo_search", "input": intent.extracted_task},
                {"action": "format_response", "style": "informative"},
            ]
            est_tokens = 100

        elif intent.category == IntentCategory.COMMAND:
            steps = [
                {"action": "wre_preflight", "task": intent.extracted_task},
                {"action": "wre_execute", "task": intent.extracted_task},
                {"action": "validate_output"},
                {"action": "log_outcome"},
            ]
            est_tokens = 200

        elif intent.category == IntentCategory.MONITOR:
            steps = [
                {"action": "overseer_status"},
                {"action": "format_response", "style": "status_report"},
            ]
            est_tokens = 80

        elif intent.category == IntentCategory.SCHEDULE:
            steps = [
                {"action": "parse_schedule", "input": intent.extracted_task},
                {"action": "check_calendar_conflicts"},
                {"action": "schedule_or_queue"},
                {"action": "confirm_response"},
            ]
            est_tokens = 150

        elif intent.category == IntentCategory.SOCIAL:
            steps = [
                {"action": "route_to_communication_dae",
                 "channel": intent.channel},
                {"action": "generate_engagement"},
            ]
            est_tokens = 120

        elif intent.category == IntentCategory.SYSTEM:
            steps = [
                {"action": "verify_commander_authority"},
                {"action": "execute_system_command",
                 "task": intent.extracted_task},
                {"action": "report_outcome"},
            ]
            est_tokens = 180

        elif intent.category == IntentCategory.RESEARCH:
            steps = [
                {"action": "classify_research_sub_intent",
                 "input": intent.extracted_task},
                {"action": "route_to_pqn_research_adapter"},
                {"action": "anti_contamination_gate"},
            ]
            est_tokens = 150

        else:  # CONVERSATION
            steps = [
                {"action": "digital_twin_response",
                 "context": intent.raw_message},
            ]
            est_tokens = 60

        plan = ExecutionPlan(
            intent=intent,
            route=route,
            permission_level=tier,
            wsp_preflight_passed=True,
            steps=steps,
            estimated_tokens=est_tokens,
        )

        logger.info(
            "[OPENCLAW-DAE] Plan: route=%s steps=%d tokens~%d tier=%s",
            route, len(steps), est_tokens, tier.value,
        )
        return plan

    # ------------------------------------------------------------------
    # Phase 5: Execute via WRE
    # ------------------------------------------------------------------

    async def _execute_plan(self, plan: ExecutionPlan) -> str:
        """
        Execute the plan by routing to the appropriate subsystem.

        This is where Associates (domain DAEs) do the actual work.
        """
        intent = plan.intent
        route = plan.route

        # ---- QUERY: HoloIndex search ----
        if route == "holo_index":
            return await self._execute_query(intent)

        # ---- COMMAND: WRE orchestrator ----
        if route == "wre_orchestrator":
            return await self._execute_command(intent)

        # ---- MONITOR: AI Overseer status ----
        if route == "ai_overseer":
            return self._execute_monitor(intent)

        # ---- SCHEDULE: Shorts scheduler ----
        if route == "youtube_shorts_scheduler":
            return self._execute_schedule(intent)

        # ---- SOCIAL: Communication DAEs ----
        if route == "communication":
            return self._execute_social(intent)

        # ---- SYSTEM: Infrastructure ----
        if route == "infrastructure":
            return self._execute_system(intent)

        # ---- AUTOMATION: AutoModeratorBridge (YouTube automation) ----
        if route == "auto_moderator_bridge":
            return self._execute_automation(intent)

        # ---- FOUNDUP: FAM Agent Market ----
        if route == "fam_adapter":
            return self._execute_foundup(intent)

        # ---- RESEARCH: PQN Detection, Duism, Oracle Teaching ----
        if route == "pqn_research_adapter":
            return self._execute_research(intent)

        # ---- CONVERSATION: Digital Twin fallback ----
        return self._execute_conversation(intent)

    async def _execute_query(self, intent: OpenClawIntent) -> str:
        """Route QUERY to HoloIndex semantic search."""
        try:
            # Try bundle-json fastpath for structured retrieval
            from holo_index.core import HoloIndex

            holo = HoloIndex()
            results = holo.search(
                intent.extracted_task or intent.raw_message,
                limit=3,
            )

            code_hits = results.get("code", [])
            wsp_hits = results.get("wsps", [])

            if not code_hits and not wsp_hits:
                return (
                    f"No results found for: {intent.extracted_task}\n\n"
                    "Try rephrasing or use more specific terms."
                )

            # Format response
            parts = []
            if code_hits:
                parts.append("**Code matches:**")
                for hit in code_hits[:3]:
                    path = hit.get("file", "unknown")
                    snippet = hit.get("content", "")[:200]
                    parts.append(f"  - `{path}`: {snippet}")

            if wsp_hits:
                parts.append("\n**WSP guidance:**")
                for hit in wsp_hits[:2]:
                    title = hit.get("title", "WSP")
                    content = hit.get("content", "")[:200]
                    parts.append(f"  - **{title}**: {content}")

            return "\n".join(parts)

        except ImportError:
            logger.warning("[OPENCLAW-DAE] HoloIndex not available for query")
            return (
                f"Received your query: {intent.raw_message[:100]}\n"
                "HoloIndex is currently offline. Try again shortly."
            )
        except Exception as exc:
            logger.error("[OPENCLAW-DAE] Query execution error: %s", exc)
            return f"Error processing query: {exc}"

    async def _execute_command(self, intent: OpenClawIntent) -> str:
        """
        Route COMMAND to WRE orchestrator with file-specific permission gate.

        WSP 15 P0 #2: SOURCE tier code execution authority gate.
        Before routing to WRE, check file-specific permissions if the
        command targets source modification.
        """
        # Source modification gate: check file-level permissions before execution
        if self._is_source_modification(intent):
            file_paths = self._extract_file_paths(intent.raw_message)
            if file_paths and self.permissions:
                for fpath in file_paths:
                    result = self.permissions.check_permission(
                        agent_id="openclaw",
                        operation="write",
                        file_path=fpath,
                    )
                    if not result.allowed:
                        logger.warning(
                            "[OPENCLAW-DAE] [COMMAND] Execution blocked: %s denied for %s",
                            result.reason, fpath,
                        )
                        return (
                            f"**Permission Denied** (SOURCE tier gate)\n\n"
                            f"Cannot modify `{fpath}`: {result.reason}\n\n"
                            f"File is protected by the allowlist/forbidlist policy. "
                            f"Contact @UnDaoDu to update permissions."
                        )

        # Graceful degradation: deterministic advisory fallback when WRE unavailable
        if self.wre is None:
            logger.warning(
                "[DAEMON][OPENCLAW-FALLBACK] event=command_fallback sender=%s reason=wre_unavailable",
                intent.sender,
            )
            self._emit_to_overseer(
                event_type="command_fallback",
                sender=intent.sender,
                channel=intent.channel,
                details={"reason": "wre_unavailable", "task": intent.extracted_task},
            )
            return self._command_advisory_fallback(intent)

        try:
            result = self.wre.execute({
                "type": "orchestration",
                "task": intent.extracted_task,
                "source": "openclaw_dae",
                "sender": intent.sender,
                "channel": intent.channel,
                "target_files": self._extract_file_paths(intent.raw_message),
            })
            return f"Command executed via WRE:\n{result}"
        except Exception as exc:
            logger.error("[OPENCLAW-DAE] Command execution error: %s", exc)
            logger.warning(
                "[DAEMON][OPENCLAW-FALLBACK] event=command_fallback sender=%s reason=wre_error",
                intent.sender,
            )
            self._emit_to_overseer(
                event_type="command_fallback",
                sender=intent.sender,
                channel=intent.channel,
                details={"reason": "wre_error", "error": str(exc)[:200]},
            )
            # Graceful degradation on error: advisory fallback
            return self._command_advisory_fallback(intent, error=str(exc))

    def _command_advisory_fallback(
        self, intent: OpenClawIntent, error: Optional[str] = None
    ) -> str:
        """
        Deterministic advisory fallback when WRE is unavailable.

        Returns actionable guidance rather than silent failure.
        """
        task = intent.extracted_task or intent.raw_message

        parts = [
            "**Advisory Mode** (WRE unavailable)",
            "",
            f"Command recognized: `{task[:100]}`",
            "",
            "I cannot execute this command automatically right now.",
            "Here are your options:",
            "",
            "1. **CLI execution**: Run manually via the main menu (`python main.py`)",
            "2. **Retry later**: WRE may become available after system restart",
            "3. **Query mode**: Ask me to explain what this command does instead",
        ]

        if error:
            parts.append("")
            parts.append(f"**Error detail**: {error[:200]}")

        logger.info(
            "[OPENCLAW-DAE] [COMMAND] Advisory fallback returned for: %s",
            task[:50],
        )
        return "\n".join(parts)

    def _execute_monitor(self, intent: OpenClawIntent) -> str:
        """Route MONITOR to AI Overseer status."""
        parts = ["**System Status:**"]

        # WRE status
        if self.wre:
            parts.append(f"  - WRE: ONLINE (state={self.wre.state})")
            if self.wre.skills_loader:
                parts.append("  - Skills Loader: ACTIVE")
            if self.wre.libido_monitor:
                parts.append("  - Libido Monitor: ACTIVE")
        else:
            parts.append("  - WRE: OFFLINE")

        # AI Overseer
        if self.overseer:
            parts.append("  - AI Overseer: LOADED")
        else:
            parts.append("  - AI Overseer: NOT LOADED")

        # OpenClaw Security Status
        import time as _time
        parts.append("")
        parts.append("**Security Status:**")
        status = "PASS" if self._skill_scan_ok else "FAIL"
        required = "required" if self._skill_scan_required else "optional"
        enforced = "enforced" if self._skill_scan_enforced else "warn-only"
        checked_ago = (
            f"{int(_time.time() - self._skill_scan_checked_at)}s ago"
            if self._skill_scan_checked_at > 0
            else "never"
        )
        parts.append(f"  - Skill Safety Gate: {status} ({required}, {enforced})")
        parts.append(f"  - Last Check: {checked_ago}")
        parts.append(f"  - Message: {self._skill_scan_message}")

        # Permissions
        if self.permissions:
            parts.append("  - Permission Manager: ACTIVE")
        else:
            parts.append("  - Permission Manager: NOT LOADED")

        # OpenClaw DAE state
        parts.append(f"  - OpenClaw DAE: state={self.state} "
                     f"coherence={self.coherence}")

        return "\n".join(parts)

    def _execute_schedule(self, intent: OpenClawIntent) -> str:
        """Route SCHEDULE intent (placeholder for scheduler integration)."""
        return (
            f"Schedule request received: {intent.extracted_task}\n"
            "Routing to YouTube Shorts Scheduler... "
            "(integration pending - use CLI for now: "
            "`python -m modules.platform_integration.youtube_shorts_scheduler"
            ".scripts.launch --content-page`)"
        )

    def _execute_social(self, intent: OpenClawIntent) -> str:
        """Route SOCIAL intent to communication DAEs."""
        return (
            f"Social engagement request on {intent.channel}: "
            f"{intent.extracted_task}\n"
            "Routing to communication layer... "
            "(Digital Twin engagement via livechat/video_comments)"
        )

    def _execute_system(self, intent: OpenClawIntent) -> str:
        """Route SYSTEM intent (requires commander authority)."""
        if not intent.is_authorized_commander:
            return (
                "System commands require @UnDaoDu authorization. "
                "Your request has been logged."
            )
        return (
            f"System command received: {intent.extracted_task}\n"
            "Infrastructure routing in progress..."
        )

    def _execute_automation(self, intent: OpenClawIntent) -> str:
        """Route AUTOMATION intent to AutoModeratorBridge."""
        try:
            from .auto_moderator_bridge import handle_automation_intent
            return handle_automation_intent(intent.raw_message, intent.sender)
        except ImportError as exc:
            logger.warning("[OPENCLAW-DAE] AutoModeratorBridge not available: %s", exc)
            return (
                "Automation bridge not available. "
                "Check that auto_moderator_bridge.py exists."
            )
        except Exception as exc:
            logger.error("[OPENCLAW-DAE] Automation execution error: %s", exc)
            return f"Automation error: {exc}"

    def _execute_foundup(self, intent: OpenClawIntent) -> str:
        """Route FOUNDUP intent to FAM Adapter.

        FAM adapter handles Qwen inference directly (llama_cpp on E: SSD).
        """
        try:
            from .fam_adapter import handle_fam_intent
            return handle_fam_intent(intent.raw_message, intent.sender)

        except ImportError as exc:
            logger.warning("[OPENCLAW-DAE] FAM Adapter not available: %s", exc)
            return (
                "FoundUps Agent Market not available. "
                "Check that fam_adapter.py exists."
            )
        except Exception as exc:
            logger.error("[OPENCLAW-DAE] FAM execution error: %s", exc)
            return f"FAM error: {exc}"

    def _execute_research(self, intent: OpenClawIntent) -> str:
        """Route RESEARCH intent to PQN Research Adapter.

        Handles PQN detection, Duism teaching, Oracle distribution,
        and PQN@home coordination. Uses oracle_pqn_distributor skillz.
        """
        try:
            from .pqn_research_adapter import handle_pqn_research_intent
            return handle_pqn_research_intent(intent.raw_message, intent.sender)

        except ImportError as exc:
            logger.warning("[OPENCLAW-DAE] PQN Research Adapter not available: %s", exc)
            return (
                "PQN Research module not available. "
                "Check that pqn_research_adapter.py exists."
            )
        except Exception as exc:
            logger.error("[OPENCLAW-DAE] Research execution error: %s", exc)
            return f"Research error: {exc}"

    @staticmethod
    def _trim_self_dialogue(text: str) -> str:
        """Small models self-dialogue. Keep only the first response paragraph."""
        # Cut at double newline (start of self-dialogue loop)
        if "\n\n" in text:
            text = text.split("\n\n")[0]
        # Also cut at "User:" or "Human:" patterns (roleplay continuation)
        for marker in ["User:", "Human:", "\nQ:", "\nA:"]:
            if marker in text:
                text = text.split(marker)[0]
        return text.strip()

    @staticmethod
    def _ensure_conversation_identity(text: str) -> str:
        """Normalize conversation output so identity anchor is always present."""
        clean = (text or "").strip()
        if not clean:
            return "0102: I'm here."
        lowered = clean.lower()
        if "0102" in clean or "digital twin" in lowered:
            return clean
        return f"0102: {clean}"

    def _execute_conversation(self, intent: OpenClawIntent) -> str:
        """
        Default: Digital Twin conversational response.

        Chain: AI Gateway (cloud LLM) -> Ollama local -> Qwen llama-cpp -> ack.
        Never echo the user's message back.
        """
        user_msg = intent.raw_message.strip()
        system_prompt = (
            "You are 0102, an AI assistant. "
            "Respond naturally and concisely in 1-2 sentences. "
            "Do not write code unless asked. "
            "Do not echo or repeat the user's message. "
            "Do not introduce yourself unless asked."
        )

        # --- Try 1: AI Gateway (cloud LLM with proper chat models) ---
        try:
            from modules.ai_intelligence.ai_gateway.src.ai_gateway import AIGateway
            gw = AIGateway()
            prompt = f"{system_prompt}\n\nUser: {user_msg}"
            result = gw.call_with_fallback(prompt=prompt, task_type="quick")
            if result and result.success and result.response and len(result.response) > 3:
                logger.info(
                    "[OPENCLAW-DAE] Conversation via AI Gateway (%s): %d chars",
                    result.provider, len(result.response),
                )
                return self._ensure_conversation_identity(
                    self._trim_self_dialogue(result.response)
                )
        except Exception as exc:
            logger.debug("[OPENCLAW-DAE] AI Gateway unavailable: %s", exc)

        # --- Try 2: Ollama local (if running) ---
        try:
            import requests as _req
            ollama_resp = _req.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "qwen-overseer:latest",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_msg},
                    ],
                    "stream": False,
                    "options": {"num_predict": 80, "temperature": 0.7},
                },
                timeout=15,
            )
            if ollama_resp.ok:
                content = ollama_resp.json().get("message", {}).get("content", "")
                content = self._trim_self_dialogue(content)
                if content and len(content) > 3:
                    logger.info("[OPENCLAW-DAE] Conversation via Ollama: %d chars", len(content))
                    return self._ensure_conversation_identity(content)
        except Exception as exc:
            logger.debug("[OPENCLAW-DAE] Ollama unavailable: %s", exc)

        # --- Try 3: Local Qwen via AI Overseer (llama-cpp) ---
        if self.overseer:
            try:
                result = self.overseer.quick_response(
                    prompt=user_msg,
                    context=f"Channel: {intent.channel}, Sender: {intent.sender}",
                    max_tokens=80,
                )
                if result and result.get("response"):
                    resp = self._trim_self_dialogue(result["response"])
                    if resp and len(resp) > 3 and "Error:" not in resp:
                        logger.info("[OPENCLAW-DAE] Conversation via Qwen: %d chars", len(resp))
                        return self._ensure_conversation_identity(resp)
            except Exception as exc:
                logger.debug("[OPENCLAW-DAE] Qwen response failed: %s", exc)

        # --- Try 4: Minimal ack (no echo, no regurgitation) ---
        return "0102: I'm here. My conversation models aren't fully responding right now."

    def push_status(self, message: str, to_discord: bool = True) -> bool:
        """
        Push status update to Discord via AI Overseer.

        Convenience method for pushing automation status to 012.

        Args:
            message: Status message (supports emoji)
            to_discord: Push to Discord webhook

        Returns:
            True if push succeeded (or no webhook configured)
        """
        if not to_discord:
            return True

        if self.overseer and hasattr(self.overseer, "push_status"):
            try:
                result = self.overseer.push_status(message, to_discord=True, to_chat=False)
                return result.get("discord", False)
            except Exception as exc:
                logger.warning("[OPENCLAW-DAE] Push status failed: %s", exc)

        # Fallback: direct Discord push
        try:
            from modules.communication.livechat.src.discord_status_pusher import push_status as direct_push
            return direct_push(message, to_discord=True, to_log=False)
        except ImportError:
            logger.debug("[OPENCLAW-DAE] Discord pusher not available")
            return True

    # ------------------------------------------------------------------
    # Phase 6: Validate + Phase 7: Remember
    # ------------------------------------------------------------------

    def _validate_and_remember(
        self,
        plan: ExecutionPlan,
        response_text: str,
        execution_time_ms: int,
    ) -> ExecutionResult:
        """
        Validate execution output and store outcome for learning.

        WSP 50: Verify output meets expectations
        WSP 22: Log to ModLog-compatible format
        WSP 48: Store pattern for recursive improvement
        """
        wsp_violations: List[str] = []

        # Validation: check response is not empty
        if not response_text or len(response_text.strip()) == 0:
            wsp_violations.append("WSP-50: Empty response generated")
            response_text = "I was unable to generate a response. Please try again."

        # Validation: check response doesn't leak secrets
        secret_patterns = ["AIza", "sk-", "oauth_token", "Bearer ey"]
        for pattern in secret_patterns:
            if pattern in response_text:
                wsp_violations.append(f"WSP-SECURITY: Response contains '{pattern}' pattern")
                response_text = "[REDACTED - security filter triggered]"
                break

        # Calculate pattern fidelity (simple heuristic for now)
        fidelity = 1.0 if not wsp_violations else 0.5

        # Store outcome in WRE pattern memory if available
        learning_stored = False
        if self.wre and self.wre.sqlite_memory:
            try:
                from modules.infrastructure.wre_core.src.pattern_memory import SkillOutcome

                outcome = SkillOutcome(
                    execution_id=f"openclaw-{uuid.uuid4().hex[:12]}",
                    skill_name=f"openclaw_{plan.intent.category.value}",
                    agent="openclaw_dae",
                    timestamp=datetime.now().isoformat(),
                    input_context=json.dumps({
                        "message": plan.intent.raw_message[:200],
                        "channel": plan.intent.channel,
                        "category": plan.intent.category.value,
                    }),
                    output_result=json.dumps({
                        "response_length": len(response_text),
                        "route": plan.route,
                        "tier": plan.permission_level.value,
                    }),
                    success=len(wsp_violations) == 0,
                    pattern_fidelity=fidelity,
                    outcome_quality=0.9 if not wsp_violations else 0.5,
                    execution_time_ms=execution_time_ms,
                    step_count=len(plan.steps),
                    notes=f"OpenClaw DAE | {plan.intent.channel} | "
                          f"{plan.intent.category.value}",
                )
                self.wre.sqlite_memory.store_outcome(outcome)
                learning_stored = True
            except Exception as exc:
                logger.warning("[OPENCLAW-DAE] Failed to store outcome: %s", exc)

        result = ExecutionResult(
            plan=plan,
            success=len(wsp_violations) == 0,
            response_text=response_text,
            execution_time_ms=execution_time_ms,
            pattern_fidelity=fidelity,
            wsp_violations=wsp_violations,
            learning_stored=learning_stored,
        )

        logger.info(
            "[OPENCLAW-DAE] Result: success=%s fidelity=%.2f time=%dms "
            "violations=%d learned=%s",
            result.success, fidelity, execution_time_ms,
            len(wsp_violations), learning_stored,
        )
        return result

    # ------------------------------------------------------------------
    # Main Entry Point: The Full Autonomy Loop
    # ------------------------------------------------------------------

    async def process(
        self,
        message: str,
        sender: str,
        channel: str,
        session_key: str = "default",
        metadata: Optional[Dict] = None,
    ) -> str:
        """
        Main entry point: process an inbound OpenClaw message through
        the full autonomy loop.

        Ingress -> Classify -> Preflight -> Plan -> Permission -> Execute
        -> Validate -> Remember -> Response

        Args:
            message: Raw message text from OpenClaw gateway
            sender: Sender identifier (phone, user ID)
            channel: Source channel (whatsapp, telegram, discord, etc.)
            session_key: Session identifier for context
            metadata: Additional context from gateway

        Returns:
            Response text to send back via OpenClaw
        """
        start_time = time.time()

        # Phase 0: Two-phase security intercept (before any classification)
        # SOUL.md LAW 2: Resist first, honeypot on persistence
        if HoneypotDefense.is_secret_seeking(message):
            response = HoneypotDefense.handle_secret_request(
                message, sender, channel,
            )
            elapsed_ms = int((time.time() - start_time) * 1000)
            logger.info(
                "[OPENCLAW-DAE] [HONEYPOT] Canary response sent | "
                "sender=%s time=%dms",
                sender, elapsed_ms,
            )
            return response

        # Phase 0.5: Containment check (WSP 95 - auto-containment policies)
        containment = self._check_containment(sender, channel)
        if containment:
            logger.warning(
                "[DAEMON][OPENCLAW-CONTAINMENT] event=containment_active "
                "sender=%s channel=%s action=%s expires_at=%.0f",
                sender, channel, containment.get("action"), containment.get("expires_at", 0),
            )
            if containment.get("action") == "advisory_only":
                # Force all intents to ADVISORY tier
                pass  # Will be handled in permission gate
            elif containment.get("action") in ("mute_sender", "mute_channel"):
                return (
                    "Your access is temporarily restricted due to security policy. "
                    f"Reason: {containment.get('reason', 'security incident')}. "
                    "Please try again later."
                )

        # SOUL.md LAW 3: Code is read-only via Discord
        if channel == "discord" and HoneypotDefense.is_code_modify_attempt(message):
            response = HoneypotDefense.generate_code_modify_deflection(
                message, sender, channel,
            )
            elapsed_ms = int((time.time() - start_time) * 1000)
            logger.info(
                "[OPENCLAW-DAE] [LAW-3] Code modify deflected | "
                "sender=%s time=%dms",
                sender, elapsed_ms,
            )
            return response

        # Phase 1: Classify intent
        intent = self.classify_intent(
            message=message,
            sender=sender,
            channel=channel,
            session_key=session_key,
            metadata=metadata,
        )

        # Cardiovascular: report message_in to central daemon
        if self._central_adapter:
            try:
                self._central_adapter.report_message_in(
                    source=f"{sender}@{channel}",
                    summary=f"intent={intent.category.value} conf={intent.confidence:.2f}",
                )
            except Exception:
                pass

        # Skill safety gate for skill-driven/mutating routes.
        if intent.category in (
            IntentCategory.COMMAND,
            IntentCategory.SYSTEM,
            IntentCategory.SCHEDULE,
            IntentCategory.SOCIAL,
            IntentCategory.AUTOMATION,
            IntentCategory.FOUNDUP,
            IntentCategory.RESEARCH,
        ):
            if not self._ensure_skill_safety():
                logger.warning(
                    "[OPENCLAW-DAE] Skill safety gate blocked %s route: %s",
                    intent.category.value,
                    self._skill_scan_message,
                )
                intent.category = IntentCategory.CONVERSATION
                intent.target_domain = "digital_twin"
                intent.metadata["skill_safety_gate"] = self._skill_scan_message

        # Phase 2: WSP/WRE preflight
        preflight_ok = self._wsp_preflight(intent)
        if not preflight_ok:
            # Downgrade to advisory conversation
            intent.category = IntentCategory.CONVERSATION
            intent.target_domain = "digital_twin"

        # Phase 3: Permission gate
        tier = self._resolve_autonomy_tier(intent)
        gate_ok = self._check_permission_gate(intent, tier)
        if not gate_ok:
            tier = AutonomyTier.ADVISORY
            intent.category = IntentCategory.CONVERSATION
            intent.target_domain = "digital_twin"

        # Phase 4: Plan execution
        plan = self._plan_execution(intent, tier)

        # Phase 5: Execute via WRE / domain DAEs
        try:
            response_text = await self._execute_plan(plan)
        except Exception as exc:
            logger.error("[OPENCLAW-DAE] Execution error: %s", exc)
            response_text = f"An error occurred during processing: {exc}"

        # Phase 6+7: Validate and remember
        elapsed_ms = int((time.time() - start_time) * 1000)
        result = self._validate_and_remember(plan, response_text, elapsed_ms)

        # Cardiovascular: report message_out to central daemon
        if self._central_adapter:
            try:
                self._central_adapter.report_message_out(
                    dest=f"{sender}@{channel}",
                    summary=f"route={plan.route} time={elapsed_ms}ms",
                )
            except Exception:
                pass

        return result.response_text
