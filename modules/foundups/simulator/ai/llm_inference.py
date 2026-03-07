"""LLM inference for simulator agents.

Provides shared inference infrastructure for Qwen (founder) and Gemma (user) agents.
Pattern follows existing holo_index/qwen_advisor/gemma_rag_inference.py
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
from modules.infrastructure.shared_utilities.local_model_selection import (
    resolve_code_model_path,
    resolve_triage_model_path,
)

logger = logging.getLogger(__name__)

# Default model paths
DEFAULT_GEMMA_PATH = resolve_triage_model_path()
DEFAULT_QWEN_PATH = resolve_code_model_path()


@dataclass
class InferenceResult:
    """Result from LLM inference."""
    text: str
    model: str  # "gemma" or "qwen"
    latency_ms: int
    confidence: float = 0.0
    tokens_used: int = 0


class SimulatorLLM:
    """Shared LLM inference for simulator agents.

    Singleton pattern - both Qwen founders and Gemma users share instances.
    """

    _gemma_instance: Optional["SimulatorLLM"] = None
    _qwen_instance: Optional["SimulatorLLM"] = None

    def __init__(
        self,
        model_type: str,  # "gemma" or "qwen"
        model_path: Optional[Path] = None,
    ) -> None:
        """Initialize LLM inference.

        Args:
            model_type: "gemma" or "qwen"
            model_path: Path to GGUF model file
        """
        self._model_type = model_type
        self._model_path = model_path or (
            DEFAULT_GEMMA_PATH if model_type == "gemma" else DEFAULT_QWEN_PATH
        )
        self._llm: Optional[Any] = None
        self._initialized = False
        self._backend = self._resolve_backend()
        self._wre_orchestrator: Optional[Any] = None
        self._stats = {
            "queries": 0,
            "total_latency_ms": 0,
            "errors": 0,
            "ironclaw_queries": 0,
            "wre_ironclaw_queries": 0,
        }

    @classmethod
    def get_gemma(cls) -> "SimulatorLLM":
        """Get shared Gemma instance."""
        if cls._gemma_instance is None:
            cls._gemma_instance = cls("gemma")
        return cls._gemma_instance

    @classmethod
    def get_qwen(cls) -> "SimulatorLLM":
        """Get shared Qwen instance."""
        if cls._qwen_instance is None:
            cls._qwen_instance = cls("qwen")
        return cls._qwen_instance

    def _resolve_backend(self) -> str:
        """Resolve backend routing for this model instance."""
        if self._model_type != "qwen":
            return "local"

        backend = os.getenv("SIM_QWEN_BACKEND", "local").strip().lower()
        allowed = {"local", "ironclaw", "wre_ironclaw"}
        if backend not in allowed:
            backend = "local"
        return backend

    def _initialize(self) -> bool:
        """Lazy-load the LLM model."""
        if self._initialized:
            return self._llm is not None

        self._initialized = True

        if not self._model_path.exists():
            logger.warning(
                f"[SIM-LLM] Model not found: {self._model_path}. "
                "AI agents will use fallback behavior."
            )
            return False

        try:
            from llama_cpp import Llama

            logger.info(f"[SIM-LLM] Loading {self._model_type} from {self._model_path}")

            # Suppress llama.cpp loading noise
            old_stdout, old_stderr = os.dup(1), os.dup(2)
            devnull = os.open(os.devnull, os.O_WRONLY)

            try:
                os.dup2(devnull, 1)
                os.dup2(devnull, 2)

                # Model-specific parameters
                if self._model_type == "gemma":
                    self._llm = Llama(
                        model_path=str(self._model_path),
                        n_ctx=512,  # Small context for fast classification
                        n_threads=2,
                        n_gpu_layers=0,
                        verbose=False,
                    )
                else:  # qwen
                    self._llm = Llama(
                        model_path=str(self._model_path),
                        n_ctx=2048,  # Larger context for idea generation
                        n_threads=4,
                        n_gpu_layers=0,
                        verbose=False,
                    )

            finally:
                os.dup2(old_stdout, 1)
                os.dup2(old_stderr, 2)
                os.close(devnull)
                os.close(old_stdout)
                os.close(old_stderr)

            logger.info(f"[SIM-LLM] {self._model_type} loaded successfully")
            return True

        except ImportError:
            logger.warning("[SIM-LLM] llama_cpp not installed. Using fallback.")
            return False
        except Exception as e:
            logger.error(f"[SIM-LLM] Failed to load {self._model_type}: {e}")
            return False

    def _generate_via_ironclaw(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> Optional[InferenceResult]:
        """Route Qwen simulation prompt to IronClaw gateway directly."""
        started = time.time()
        try:
            from modules.communication.moltbot_bridge.src.ironclaw_gateway_client import (
                IronClawGatewayClient,
            )

            client = IronClawGatewayClient()
            system_prompt = (
                "You are a FoundUps simulator coding worker. "
                "Respond concisely and deterministically for simulation use."
            )
            text = client.chat_completion(
                user_message=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            if not text:
                return None

            latency_ms = int((time.time() - started) * 1000)
            self._stats["queries"] += 1
            self._stats["ironclaw_queries"] += 1
            self._stats["total_latency_ms"] += latency_ms
            return InferenceResult(
                text=text.strip(),
                model="qwen_ironclaw",
                latency_ms=latency_ms,
                confidence=0.75,
                tokens_used=0,
            )
        except Exception as exc:
            logger.debug("[SIM-LLM] IronClaw route unavailable: %s", exc)
            return None

    def _generate_via_wre_ironclaw(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        stop: Optional[list],
    ) -> Optional[InferenceResult]:
        """Route Qwen simulation prompt through WRE ironclaw_worker plugin."""
        started = time.time()
        try:
            from modules.infrastructure.wre_core.wre_master_orchestrator.src.wre_master_orchestrator import (
                WREMasterOrchestrator,
            )

            if self._wre_orchestrator is None:
                self._wre_orchestrator = WREMasterOrchestrator()

            task = {
                "plugin": "ironclaw_worker",
                "work_type": "sim",
                "input_payload": {"prompt": prompt, "stop": stop or []},
                "max_tokens": max_tokens,
                "temperature": temperature,
                "require_healthy": False,
            }
            result = self._wre_orchestrator.execute(task)
            if not isinstance(result, dict) or not result.get("success"):
                return None
            response = str(result.get("response", "")).strip()
            if not response:
                return None

            latency_ms = int((time.time() - started) * 1000)
            self._stats["queries"] += 1
            self._stats["wre_ironclaw_queries"] += 1
            self._stats["total_latency_ms"] += latency_ms
            return InferenceResult(
                text=response,
                model="qwen_wre_ironclaw",
                latency_ms=latency_ms,
                confidence=0.75,
                tokens_used=0,
            )
        except Exception as exc:
            logger.debug("[SIM-LLM] WRE IronClaw route unavailable: %s", exc)
            return None

    def generate(
        self,
        prompt: str,
        max_tokens: int = 200,
        temperature: float = 0.2,
        stop: Optional[list] = None,
    ) -> InferenceResult:
        """Generate text from prompt.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (lower = more deterministic)
            stop: Stop sequences

        Returns:
            InferenceResult with generated text
        """
        start_time = time.time()

        # Backend route toggle for simulator Qwen lane:
        # - local (default): llama.cpp GGUF local model
        # - ironclaw: direct IronClaw gateway
        # - wre_ironclaw: route through WRE ironclaw_worker plugin
        if self._model_type == "qwen":
            if self._backend == "wre_ironclaw":
                routed = self._generate_via_wre_ironclaw(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stop=stop,
                )
                if routed is not None:
                    return routed
            elif self._backend == "ironclaw":
                routed = self._generate_via_ironclaw(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                if routed is not None:
                    return routed

        # Try to initialize if not done
        if not self._initialize():
            # Fallback: return empty result
            return InferenceResult(
                text="",
                model=f"{self._model_type}_fallback",
                latency_ms=0,
                confidence=0.0,
            )

        try:
            response = self._llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=stop or ["\n\n", "###"],
                echo=False,
            )

            # Extract text
            if isinstance(response, dict) and "choices" in response:
                text = response["choices"][0]["text"].strip()
                tokens = response.get("usage", {}).get("completion_tokens", 0)
            else:
                text = str(response).strip()
                tokens = 0

            latency_ms = int((time.time() - start_time) * 1000)
            self._stats["queries"] += 1
            self._stats["total_latency_ms"] += latency_ms

            return InferenceResult(
                text=text,
                model=self._model_type,
                latency_ms=latency_ms,
                confidence=0.8,  # Base confidence
                tokens_used=tokens,
            )

        except Exception as e:
            logger.error(f"[SIM-LLM] Generation failed: {e}")
            self._stats["errors"] += 1
            return InferenceResult(
                text="",
                model=f"{self._model_type}_error",
                latency_ms=int((time.time() - start_time) * 1000),
                confidence=0.0,
            )

    def classify(
        self,
        prompt: str,
        options: list[str],
    ) -> tuple[int, float]:
        """Classify prompt into one of the options.

        Args:
            prompt: Input prompt with classification question
            options: List of option labels

        Returns:
            (selected_index, confidence)
        """
        # Build classification prompt
        options_text = "\n".join(f"{i+1}. {opt}" for i, opt in enumerate(options))
        full_prompt = f"{prompt}\n\nOptions:\n{options_text}\n\nAnswer with just the number:"

        result = self.generate(full_prompt, max_tokens=10, temperature=0.1)

        # Parse response
        text = result.text.strip()
        try:
            # Extract first digit
            for char in text:
                if char.isdigit():
                    idx = int(char) - 1
                    if 0 <= idx < len(options):
                        return (idx, result.confidence)
            return (0, 0.3)  # Default to first option with low confidence
        except Exception:
            return (0, 0.3)

    @property
    def available(self) -> bool:
        """Check if model is available."""
        return self._model_path.exists()

    def get_stats(self) -> Dict[str, Any]:
        """Get inference statistics."""
        avg_latency = (
            self._stats["total_latency_ms"] / max(1, self._stats["queries"])
        )
        return {
            "model": self._model_type,
            "backend": self._backend,
            "queries": self._stats["queries"],
            "errors": self._stats["errors"],
            "ironclaw_queries": self._stats["ironclaw_queries"],
            "wre_ironclaw_queries": self._stats["wre_ironclaw_queries"],
            "avg_latency_ms": round(avg_latency, 1),
        }
