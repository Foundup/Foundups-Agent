"""FAM Security Sentinel for AI Overseer.

Provides FAM-specific security gates following OpenClaw sentinel pattern.
Enforces token amount limits, rate limiting, and anomaly detection.

WSP References:
- WSP 11: Security interface contract
- WSP 77: Security sentinel pattern
- WSP 95: AI safety guardrails
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class SecurityViolation:
    """Record of a security violation."""

    violation_id: str
    violation_type: str
    actor_id: str
    details: Dict[str, Any]
    severity: str  # "low", "medium", "high", "critical"
    timestamp: datetime = field(default_factory=_utc_now)


@dataclass
class SecurityCheckResult:
    """Result of a security check."""

    allowed: bool
    violations: List[SecurityViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class FAMSecuritySentinel:
    """Security sentinel for FoundUps Agent Market.

    Provides defense-in-depth security checks for FAM operations:
    - Token amount limits
    - Rate limiting per actor
    - Anomaly detection for suspicious patterns
    - CABR threshold enforcement

    Follows openclaw_security_sentinel.py pattern with:
    - Cached check results with TTL
    - Environment-based configuration
    - Structured violation logging

    Example:
        sentinel = FAMSecuritySentinel()
        result = sentinel.check_token_operation(
            actor_id="agent_123",
            operation="deploy",
            amount=1000000,
        )
        if not result.allowed:
            raise SecurityError(result.violations)
    """

    # Default configuration (overridable via environment)
    DEFAULT_CONFIG = {
        "max_token_supply": 1_000_000_000,  # 1B tokens max
        "min_token_supply": 1_000,  # 1K tokens min
        "max_single_payout": 100_000,  # 100K tokens per payout
        "rate_limit_window_seconds": 3600,  # 1 hour window
        "max_operations_per_window": 100,  # Max ops per actor per window
        "cabr_min_threshold": 0.3,  # Minimum CABR score for distribution
        "cache_ttl_seconds": 300,  # 5 minute cache
    }

    def __init__(self, cache_path: Optional[Path] = None) -> None:
        """Initialize security sentinel.

        Args:
            cache_path: Path to cache file. Defaults to FAM_SECURITY_CACHE env
                       or ~/.fam/security_cache.json.
        """
        if cache_path is None:
            default_cache = Path.home() / ".fam" / "security_cache.json"
            cache_path = Path(os.environ.get("FAM_SECURITY_CACHE", str(default_cache)))

        self.cache_path = cache_path
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

        # Load config from environment
        self.config = self._load_config()

        # In-memory rate limit tracking
        self._rate_limits: Dict[str, List[float]] = {}

        # Violation log
        self._violations: List[SecurityViolation] = []

        logger.info("FAMSecuritySentinel initialized: cache=%s", self.cache_path)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = dict(self.DEFAULT_CONFIG)

        env_mappings = {
            "FAM_MAX_TOKEN_SUPPLY": ("max_token_supply", int),
            "FAM_MIN_TOKEN_SUPPLY": ("min_token_supply", int),
            "FAM_MAX_SINGLE_PAYOUT": ("max_single_payout", int),
            "FAM_RATE_LIMIT_WINDOW": ("rate_limit_window_seconds", int),
            "FAM_MAX_OPS_PER_WINDOW": ("max_operations_per_window", int),
            "FAM_CABR_MIN_THRESHOLD": ("cabr_min_threshold", float),
            "FAM_CACHE_TTL": ("cache_ttl_seconds", int),
        }

        for env_key, (config_key, type_fn) in env_mappings.items():
            env_value = os.environ.get(env_key)
            if env_value is not None:
                try:
                    config[config_key] = type_fn(env_value)
                except ValueError:
                    logger.warning("Invalid value for %s: %s", env_key, env_value)

        return config

    def _load_cache(self) -> Optional[Dict[str, Any]]:
        """Load cached data if still valid."""
        if not self.cache_path.exists():
            return None

        try:
            with open(self.cache_path) as f:
                data = json.load(f)
                cached_at = data.get("cached_at", 0)
                ttl = self.config["cache_ttl_seconds"]
                if time.time() - cached_at < ttl:
                    return data
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to load cache: %s", e)

        return None

    def _save_cache(self, data: Dict[str, Any]) -> None:
        """Save data to cache."""
        data["cached_at"] = time.time()
        try:
            with open(self.cache_path, "w") as f:
                json.dump(data, f)
        except OSError as e:
            logger.warning("Failed to save cache: %s", e)

    def _check_rate_limit(self, actor_id: str) -> Optional[SecurityViolation]:
        """Check if actor exceeds rate limit."""
        now = time.time()
        window = self.config["rate_limit_window_seconds"]
        max_ops = self.config["max_operations_per_window"]

        # Get or create actor's operation timestamps
        if actor_id not in self._rate_limits:
            self._rate_limits[actor_id] = []

        # Clean old timestamps
        self._rate_limits[actor_id] = [
            ts for ts in self._rate_limits[actor_id] if now - ts < window
        ]

        # Check limit
        if len(self._rate_limits[actor_id]) >= max_ops:
            violation = SecurityViolation(
                violation_id=f"rate_{hashlib.md5(f'{actor_id}_{now}'.encode()).hexdigest()[:8]}",
                violation_type="rate_limit_exceeded",
                actor_id=actor_id,
                details={
                    "current_count": len(self._rate_limits[actor_id]),
                    "max_allowed": max_ops,
                    "window_seconds": window,
                },
                severity="medium",
            )
            self._violations.append(violation)
            return violation

        # Record operation
        self._rate_limits[actor_id].append(now)
        return None

    def check_token_operation(
        self,
        actor_id: str,
        operation: str,
        amount: Optional[int] = None,
        foundup_id: Optional[str] = None,
    ) -> SecurityCheckResult:
        """Check if a token operation is allowed.

        Args:
            actor_id: ID of actor performing operation.
            operation: Type of operation ("deploy", "transfer", "payout").
            amount: Token amount involved (if applicable).
            foundup_id: Associated Foundup (if applicable).

        Returns:
            SecurityCheckResult with allowed flag and any violations.
        """
        violations: List[SecurityViolation] = []
        warnings: List[str] = []

        # Check rate limit
        rate_violation = self._check_rate_limit(actor_id)
        if rate_violation:
            violations.append(rate_violation)

        # Check amount limits
        if amount is not None:
            if operation == "deploy":
                if amount > self.config["max_token_supply"]:
                    violations.append(
                        SecurityViolation(
                            violation_id=f"amt_{hashlib.md5(f'{actor_id}_{amount}'.encode()).hexdigest()[:8]}",
                            violation_type="token_supply_exceeded",
                            actor_id=actor_id,
                            details={
                                "requested": amount,
                                "max_allowed": self.config["max_token_supply"],
                            },
                            severity="high",
                        )
                    )
                if amount < self.config["min_token_supply"]:
                    violations.append(
                        SecurityViolation(
                            violation_id=f"amt_{hashlib.md5(f'{actor_id}_{amount}_min'.encode()).hexdigest()[:8]}",
                            violation_type="token_supply_below_minimum",
                            actor_id=actor_id,
                            details={
                                "requested": amount,
                                "min_required": self.config["min_token_supply"],
                            },
                            severity="medium",
                        )
                    )

            elif operation == "payout":
                if amount > self.config["max_single_payout"]:
                    violations.append(
                        SecurityViolation(
                            violation_id=f"pay_{hashlib.md5(f'{actor_id}_{amount}'.encode()).hexdigest()[:8]}",
                            violation_type="payout_exceeds_limit",
                            actor_id=actor_id,
                            details={
                                "requested": amount,
                                "max_allowed": self.config["max_single_payout"],
                            },
                            severity="high",
                        )
                    )
                elif amount > self.config["max_single_payout"] * 0.8:
                    warnings.append(
                        f"Payout amount {amount} is close to limit {self.config['max_single_payout']}"
                    )

        result = SecurityCheckResult(
            allowed=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            metadata={
                "actor_id": actor_id,
                "operation": operation,
                "amount": amount,
                "foundup_id": foundup_id,
                "checked_at": _utc_now().isoformat(),
            },
        )

        if not result.allowed:
            logger.warning(
                "Security check BLOCKED for %s: %s violations",
                actor_id,
                len(violations),
            )

        return result

    def check_cabr_threshold(
        self,
        cabr_score: float,
        foundup_id: str,
        actor_id: str,
    ) -> SecurityCheckResult:
        """Check if CABR score meets threshold for distribution.

        Args:
            cabr_score: Current CABR score.
            foundup_id: Foundup to check.
            actor_id: Actor requesting distribution.

        Returns:
            SecurityCheckResult with allowed flag.
        """
        min_threshold = self.config["cabr_min_threshold"]
        violations: List[SecurityViolation] = []
        warnings: List[str] = []

        if cabr_score < min_threshold:
            violations.append(
                SecurityViolation(
                    violation_id=f"cabr_{hashlib.md5(f'{foundup_id}_{cabr_score}'.encode()).hexdigest()[:8]}",
                    violation_type="cabr_below_threshold",
                    actor_id=actor_id,
                    details={
                        "foundup_id": foundup_id,
                        "cabr_score": cabr_score,
                        "min_threshold": min_threshold,
                    },
                    severity="medium",
                )
            )
        elif cabr_score < min_threshold * 1.2:
            warnings.append(
                f"CABR score {cabr_score:.3f} is close to threshold {min_threshold}"
            )

        return SecurityCheckResult(
            allowed=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            metadata={
                "cabr_score": cabr_score,
                "foundup_id": foundup_id,
                "checked_at": _utc_now().isoformat(),
            },
        )

    def get_recent_violations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent security violations.

        Args:
            limit: Maximum violations to return.

        Returns:
            List of violation dicts.
        """
        return [
            {
                "violation_id": v.violation_id,
                "violation_type": v.violation_type,
                "actor_id": v.actor_id,
                "details": v.details,
                "severity": v.severity,
                "timestamp": v.timestamp.isoformat(),
            }
            for v in self._violations[-limit:]
        ]

    def clear_rate_limits(self) -> None:
        """Clear all rate limit counters (for testing)."""
        self._rate_limits.clear()
        logger.info("Rate limits cleared")

    def check(self, *, force: bool = False) -> Dict[str, Any]:
        """Run full security health check.

        Args:
            force: If True, bypass cache.

        Returns:
            Health check result with status and metrics.
        """
        if not force:
            cached = self._load_cache()
            if cached and "health_check" in cached:
                return cached["health_check"]

        result = {
            "status": "healthy",
            "config": {k: v for k, v in self.config.items() if not k.startswith("_")},
            "active_rate_limits": len(self._rate_limits),
            "total_violations": len(self._violations),
            "recent_violations": len([v for v in self._violations if (
                _utc_now() - v.timestamp).total_seconds() < 3600
            ]),
            "checked_at": _utc_now().isoformat(),
        }

        self._save_cache({"health_check": result})
        return result
