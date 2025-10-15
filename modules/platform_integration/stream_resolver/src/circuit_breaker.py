#!/usr/bin/env python3
"""
Circuit Breaker Module for Stream Resolver
Extracted from stream_resolver.py to eliminate vibecoding

WSP 62: Large File Refactoring - Extracted from oversized stream_resolver.py
"""

import time
import logging
from enum import Enum
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)

# Try to import config for backward compatibility
try:
    from .stream_config import config as stream_config
except ImportError:
    stream_config = None


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Blocking all calls
    HALF_OPEN = "HALF_OPEN"  # Testing recovery


class CircuitBreakerError(Exception):
    """Raised when circuit breaker blocks a call"""
    pass


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for API calls with gradual recovery.

    Extracted from stream_resolver.py vibecoded functionality.
    """

    def __init__(self, failure_threshold: int = 10, timeout: int = 600):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Failures before opening circuit
            timeout: Seconds to wait before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout  # 10 minutes default
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        self.consecutive_successes = 0  # Track successes in HALF_OPEN state
        self.recovery_threshold = 3  # Need 3 successes to fully close

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result of function call

        Raises:
            CircuitBreakerError: If circuit breaker is OPEN
        """
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise CircuitBreakerError("Circuit breaker is OPEN - too many failures")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time > self.timeout

    def _on_success(self):
        """Handle successful call with gradual recovery."""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.consecutive_successes += 1
            logger.info(f"🔄 Circuit breaker HALF_OPEN - success {self.consecutive_successes}/{self.recovery_threshold}")
            if self.consecutive_successes >= self.recovery_threshold:
                self.failure_count = 0
                self.state = CircuitBreakerState.CLOSED
                self.consecutive_successes = 0
                logger.info("✅ Circuit breaker fully CLOSED after successful recovery")
        else:
            self.failure_count = 0
            self.state = CircuitBreakerState.CLOSED

    def _on_failure(self):
        """Handle failed call with reset on HALF_OPEN failure."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitBreakerState.HALF_OPEN:
            # Failed in HALF_OPEN state - go back to OPEN
            self.state = CircuitBreakerState.OPEN
            self.consecutive_successes = 0
            logger.warning(f"🔴 Circuit breaker failed in HALF_OPEN state - back to OPEN (failure {self.failure_count}/{self.failure_threshold})")
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.error(f"🔴 Circuit breaker OPEN after {self.failure_count} failures - blocking API calls for {self.timeout}s")
        else:
            logger.warning(f"⚠️ Circuit breaker failure {self.failure_count}/{self.failure_threshold}")

    def reset(self):
        """Manually reset the circuit breaker (for testing/debugging)."""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        self.consecutive_successes = 0
        logger.info("🔄 Circuit breaker manually reset to CLOSED state")

    def get_status(self) -> dict:
        """Get current circuit breaker status for monitoring."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "time_until_reset": self._time_until_reset() if self.state == CircuitBreakerState.OPEN else 0,
            "consecutive_successes": self.consecutive_successes,
            "recovery_threshold": self.recovery_threshold
        }

    def _time_until_reset(self) -> int:
        """Calculate seconds until circuit breaker can reset."""
        if self.last_failure_time is None:
            return 0
        elapsed = time.time() - self.last_failure_time
        return max(0, int(self.timeout - elapsed))


# Global circuit breaker instance for backward compatibility
# Uses config values when available
if stream_config:
    circuit_breaker = CircuitBreaker(
        failure_threshold=getattr(stream_config, 'CIRCUIT_BREAKER_THRESHOLD', 10),
        timeout=getattr(stream_config, 'CIRCUIT_BREAKER_TIMEOUT', 600)
    )
else:
    # Fallback if config not available
    circuit_breaker = CircuitBreaker()
