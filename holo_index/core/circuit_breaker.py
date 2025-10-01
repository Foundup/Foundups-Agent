"""
Circuit Breaker Pattern Implementation for HoloIndex
Prevents cascading failures in semantic search operations

Adapted from stream_resolver circuit breaker pattern
Following WSP 64: Violation Prevention through failure management
"""

import time
import logging
from typing import Optional, Callable, Any, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class HoloIndexCircuitBreaker:
    """
    Circuit breaker for HoloIndex operations to prevent cascading failures

    Three states:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests blocked
    - HALF_OPEN: Testing recovery with limited requests

    Key improvements from stream_resolver:
    - Separate breakers for different operations (ChromaDB, embedding)
    - Fallback to cached results when circuit is open
    - Gradual recovery with increasing success requirements
    """

    def __init__(
        self,
        operation_name: str = "holo_index",
        failure_threshold: int = 5,  # Lower than stream_resolver's 10 for faster response
        timeout: int = 300,  # 5 minutes recovery timeout
        recovery_threshold: int = 2  # Need 2 successes to fully close
    ):
        """Initialize circuit breaker with configurable thresholds"""
        self.operation_name = operation_name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.recovery_threshold = recovery_threshold

        # State management
        self.state = "CLOSED"
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.consecutive_successes = 0

        # Metrics for monitoring
        self.total_calls = 0
        self.total_failures = 0
        self.total_successes = 0
        self.circuit_opens = 0

        # Cache for fallback when circuit is open
        self.last_successful_result: Optional[Any] = None
        self.cache_timestamp: Optional[float] = None

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection

        Returns cached result if circuit is open and cache is available
        """
        self.total_calls += 1

        # Check circuit state
        if self.state == "OPEN":
            if self._should_attempt_reset():
                logger.info(f"[RECURSIVE] {self.operation_name} circuit breaker attempting recovery (HALF_OPEN)")
                self.state = "HALF_OPEN"
                self.consecutive_successes = 0
            else:
                # Circuit is open, try to return cached result
                if self.last_successful_result is not None:
                    cache_age = time.time() - self.cache_timestamp if self.cache_timestamp else 0
                    logger.warning(
                        f"[BLOCKED] {self.operation_name} circuit breaker OPEN - returning cached result "
                        f"(age: {cache_age:.1f}s)"
                    )
                    return self.last_successful_result
                else:
                    raise CircuitBreakerOpenError(
                        f"{self.operation_name} circuit breaker is OPEN - no cached results available"
                    )

        # Try to execute the function
        try:
            result = func(*args, **kwargs)
            self._on_success(result)
            return result
        except Exception as e:
            self._on_failure()
            # If we have a cached result, return it as fallback
            if self.last_successful_result is not None:
                logger.warning(
                    f"⚠️ {self.operation_name} operation failed, returning cached result: {str(e)}"
                )
                return self.last_successful_result
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True

        time_since_failure = time.time() - self.last_failure_time
        return time_since_failure > self.timeout

    def _on_success(self, result: Any = None):
        """Handle successful call with gradual recovery"""
        self.total_successes += 1

        # Cache the successful result
        if result is not None:
            self.last_successful_result = result
            self.cache_timestamp = time.time()

        if self.state == "HALF_OPEN":
            self.consecutive_successes += 1
            logger.info(
                f"[SUCCESS] {self.operation_name} circuit breaker HALF_OPEN - "
                f"success {self.consecutive_successes}/{self.recovery_threshold}"
            )

            if self.consecutive_successes >= self.recovery_threshold:
                # Fully recovered
                self.failure_count = 0
                self.state = "CLOSED"
                self.consecutive_successes = 0
                logger.info(f"🎉 {self.operation_name} circuit breaker fully CLOSED after recovery")
        elif self.state == "CLOSED":
            # Reset failure count on success
            if self.failure_count > 0:
                logger.debug(f"📉 {self.operation_name} failure count reset from {self.failure_count}")
            self.failure_count = 0

    def _on_failure(self):
        """Handle failed call with intelligent escalation"""
        self.total_failures += 1
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == "HALF_OPEN":
            # Failed during recovery - immediately go back to OPEN
            self.state = "OPEN"
            self.consecutive_successes = 0
            self.circuit_opens += 1
            logger.error(
                f"❌ {self.operation_name} circuit breaker recovery failed - "
                f"back to OPEN state (will retry in {self.timeout}s)"
            )
        elif self.failure_count >= self.failure_threshold:
            # Too many failures - open the circuit
            self.state = "OPEN"
            self.circuit_opens += 1
            logger.error(
                f"🚨 {self.operation_name} circuit breaker OPEN after "
                f"{self.failure_count} failures (threshold: {self.failure_threshold})"
            )
            logger.info(f"⏰ Will attempt recovery in {self.timeout} seconds")

    def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status for monitoring"""
        return {
            "operation": self.operation_name,
            "state": self.state,
            "failure_count": self.failure_count,
            "consecutive_successes": self.consecutive_successes,
            "total_calls": self.total_calls,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "circuit_opens": self.circuit_opens,
            "success_rate": (
                self.total_successes / self.total_calls * 100
                if self.total_calls > 0 else 0
            ),
            "has_cache": self.last_successful_result is not None,
            "cache_age": (
                time.time() - self.cache_timestamp
                if self.cache_timestamp else None
            )
        }

    def reset(self):
        """Manually reset the circuit breaker (for testing or recovery)"""
        logger.info(f"🔧 Manually resetting {self.operation_name} circuit breaker")
        self.state = "CLOSED"
        self.failure_count = 0
        self.consecutive_successes = 0
        self.last_failure_time = None


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open"""
    pass


class CircuitBreakerManager:
    """
    Manages multiple circuit breakers for different HoloIndex operations

    Separate breakers for:
    - ChromaDB operations
    - Model encoding operations
    - File system operations
    """

    def __init__(self):
        self.breakers = {
            "chromadb": HoloIndexCircuitBreaker(
                operation_name="ChromaDB",
                failure_threshold=3,  # Fail fast for DB operations
                timeout=180,  # 3 minutes
                recovery_threshold=2
            ),
            "embedding": HoloIndexCircuitBreaker(
                operation_name="Embedding",
                failure_threshold=5,  # More tolerant for model operations
                timeout=300,  # 5 minutes
                recovery_threshold=3
            ),
            "filesystem": HoloIndexCircuitBreaker(
                operation_name="FileSystem",
                failure_threshold=10,  # Very tolerant for file operations
                timeout=60,  # 1 minute
                recovery_threshold=1
            )
        }

    def get_breaker(self, operation_type: str) -> HoloIndexCircuitBreaker:
        """Get circuit breaker for specific operation type"""
        return self.breakers.get(
            operation_type,
            self.breakers["chromadb"]  # Default to ChromaDB breaker
        )

    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers"""
        return {
            name: breaker.get_status()
            for name, breaker in self.breakers.items()
        }

    def reset_all(self):
        """Reset all circuit breakers"""
        for breaker in self.breakers.values():
            breaker.reset()


# Global circuit breaker manager instance
circuit_manager = CircuitBreakerManager()