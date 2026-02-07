#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemma Intent Classifier - Binary classification for OpenClaw intent routing.

WSP 15 P0 #1 (MPS 18/20): Replace keyword heuristic with Gemma 270M
binary classification for prompt-injection-resistant intent routing.

Architecture (Hybrid - Option C):
  1. Fast keyword pre-filter (<1ms) - existing INTENT_KEYWORDS scoring
  2. Gemma validates top-N candidates via binary classification (<30ms each)
  3. Combined score: (keyword * 0.3) + (gemma * 0.7)
  4. Graceful degradation: keyword-only if Gemma unavailable

Pattern Sources:
  - gemma_validator.py: Binary YES/NO classification, llama_cpp loading
  - gemma_rag_inference.py: Stdout suppression, lazy init pattern

WSP Compliance:
  WSP 84: Code reuse (follows gemma_validator.py pattern exactly)
  WSP 96: <10ms per binary classification target
  WSP 77: Gemma fast validation layer (Phase 1 in 4-phase execution)

NAVIGATION:
  -> Called by: openclaw_dae.py (classify_intent enhancement)
  -> Pattern from: video_comments/src/gemma_validator.py
  -> Model: E:/HoloIndex/models/gemma-3-270m-it-Q4_K_M.gguf
"""

import logging
import os
import time
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from enum import Enum

logger = logging.getLogger("gemma_intent_classifier")


class GemmaIntentClassifier:
    """
    Gemma 270M binary classifier for OpenClaw intent routing.

    Validates keyword-scored intent candidates with Gemma binary
    classification (YES/NO) to resist prompt injection and improve
    confidence calibration.

    Usage:
        classifier = GemmaIntentClassifier()
        result = classifier.classify("Show me system status", top_candidates)
        # {'category': 'monitor', 'confidence': 0.87, 'method': 'gemma_hybrid'}
    """

    # Default model path (zen coding: model exists on E: drive)
    DEFAULT_MODEL_PATH = Path("E:/HoloIndex/models/gemma-3-270m-it-Q4_K_M.gguf")

    # Intent category descriptions for Gemma prompts
    CATEGORY_DESCRIPTIONS = {
        "query": "a question or search request asking for information",
        "command": "a command to execute, modify, create, or delete something",
        "monitor": "a request to check status, health, metrics, or system state",
        "schedule": "a request to schedule, remind, or set up a timed event",
        "social": "a social media action like posting, commenting, or replying",
        "system": "a system administration action like restart, configure, or install",
        "automation": "a request about YouTube automation, scheduling, or browser control",
        "conversation": "casual conversation, greeting, or general chat",
        "foundup": "about launching, managing, or tokenizing a FoundUp project",
    }

    def __init__(
        self,
        model_path: Optional[Path] = None,
        max_candidates: int = 3,
        keyword_weight: float = 0.3,
        gemma_weight: float = 0.7,
    ):
        """
        Initialize Gemma intent classifier.

        Args:
            model_path: Path to Gemma GGUF model. Defaults to E:/HoloIndex/models/
            max_candidates: Max keyword candidates to validate with Gemma (default 3)
            keyword_weight: Weight for keyword score in combined score (default 0.3)
            gemma_weight: Weight for Gemma score in combined score (default 0.7)
        """
        self.model_path = model_path or self.DEFAULT_MODEL_PATH
        self.max_candidates = max_candidates
        self.keyword_weight = keyword_weight
        self.gemma_weight = gemma_weight

        # Lazy loaded (never load in __init__)
        self._llm = None
        self._initialized = False
        self._available: Optional[bool] = None  # None = not yet checked

        # Performance stats
        self._stats = {
            "total_calls": 0,
            "gemma_calls": 0,
            "keyword_fallbacks": 0,
            "avg_latency_ms": 0.0,
            "total_latency_ms": 0.0,
        }

    # ------------------------------------------------------------------
    # Lazy Model Loading (pattern: gemma_validator.py lines 68-116)
    # ------------------------------------------------------------------

    def _initialize_gemma(self) -> bool:
        """
        Lazy-load Gemma 270M via llama_cpp on first use.

        Returns True if model loaded successfully. Once checked, result
        is cached (won't retry on failure within same process).
        """
        if self._initialized:
            return self._available or False

        self._initialized = True

        # Check model file exists before attempting load
        if not self.model_path.exists():
            logger.warning(
                "[GEMMA-INTENT] Model not found: %s (falling back to keywords)",
                self.model_path,
            )
            self._available = False
            return False

        try:
            from llama_cpp import Llama

            logger.info("[GEMMA-INTENT] Loading Gemma 270M from %s", self.model_path)

            # Suppress llama.cpp loading noise
            # Pattern: gemma_rag_inference.py lines 118-138
            old_stdout = os.dup(1)
            old_stderr = os.dup(2)
            devnull = os.open(os.devnull, os.O_WRONLY)

            try:
                os.dup2(devnull, 1)
                os.dup2(devnull, 2)

                self._llm = Llama(
                    model_path=str(self.model_path),
                    n_ctx=512,    # Small context for binary classification
                    n_threads=2,  # Fast inference on 2 threads
                    n_gpu_layers=0,  # CPU-only for consistency
                    verbose=False,
                )
            finally:
                os.dup2(old_stdout, 1)
                os.dup2(old_stderr, 2)
                os.close(devnull)
                os.close(old_stdout)
                os.close(old_stderr)

            self._available = True
            logger.info("[GEMMA-INTENT] [OK] Model loaded successfully")
            return True

        except Exception as exc:
            logger.warning(
                "[GEMMA-INTENT] Failed to load model (%s): %s (falling back to keywords)",
                type(exc).__name__,
                exc,
            )
            self._available = False
            return False

    # ------------------------------------------------------------------
    # Binary Classification (pattern: gemma_validator.py lines 118-156)
    # ------------------------------------------------------------------

    def _binary_classify(self, message: str, category: str) -> float:
        """
        Ask Gemma: "Is this message a {category}? YES or NO"

        Returns confidence 0.0-1.0:
          - YES -> 0.85 (high confidence match)
          - NO  -> 0.10 (low confidence match)
          - Parse failure -> 0.50 (neutral, defer to keyword score)
        """
        if self._llm is None:
            return 0.5

        description = self.CATEGORY_DESCRIPTIONS.get(category, category)

        prompt = (
            f"Classify if the following message is {description}.\n"
            f"Reply ONLY with: YES or NO\n\n"
            f"Message: {message[:300]}\n\n"
            f"Classification:"
        )

        try:
            response = self._llm(
                prompt,
                max_tokens=10,        # Just "YES" or "NO"
                temperature=0.0,      # Deterministic for classification
                stop=["\n", "###"],
                echo=False,
            )

            # Extract response text
            if isinstance(response, dict) and "choices" in response:
                text = response["choices"][0]["text"].strip().upper()
            else:
                text = str(response).strip().upper()

            if "YES" in text:
                return 0.85
            elif "NO" in text:
                return 0.10
            else:
                logger.debug(
                    "[GEMMA-INTENT] Ambiguous response for %s: %s", category, text[:30]
                )
                return 0.50

        except Exception as exc:
            logger.debug("[GEMMA-INTENT] Inference error for %s: %s", category, exc)
            return 0.50

    # ------------------------------------------------------------------
    # Hybrid Classification (keyword pre-filter + Gemma validation)
    # ------------------------------------------------------------------

    def classify(
        self,
        message: str,
        keyword_scores: Dict[str, float],
        default_category: str = "conversation",
    ) -> Dict[str, object]:
        """
        Hybrid intent classification: keyword pre-filter + Gemma validation.

        Args:
            message: Raw message text
            keyword_scores: Dict of {category_value: score} from keyword matching
            default_category: Fallback category if no scores (default "conversation")

        Returns:
            Dict with:
                category: str - best matching category value
                confidence: float - combined confidence score
                method: str - "gemma_hybrid" | "keyword_only" | "default"
                gemma_scores: Dict - per-category Gemma scores (if used)
                latency_ms: int - classification latency
        """
        start = time.perf_counter()
        self._stats["total_calls"] += 1

        # No keyword signals -> default
        if not keyword_scores:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            return {
                "category": default_category,
                "confidence": 0.5,
                "method": "default",
                "gemma_scores": {},
                "latency_ms": elapsed_ms,
            }

        # Sort candidates by keyword score descending, take top N
        sorted_candidates: List[Tuple[str, float]] = sorted(
            keyword_scores.items(), key=lambda x: x[1], reverse=True
        )[: self.max_candidates]

        # Try Gemma validation
        gemma_available = self._initialize_gemma()

        if not gemma_available:
            # Keyword-only fallback
            self._stats["keyword_fallbacks"] += 1
            best_cat = sorted_candidates[0][0]
            best_score = min(sorted_candidates[0][1] * 2.0, 1.0)
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            return {
                "category": best_cat,
                "confidence": best_score,
                "method": "keyword_only",
                "gemma_scores": {},
                "latency_ms": elapsed_ms,
            }

        # Gemma hybrid: validate each candidate
        self._stats["gemma_calls"] += 1
        gemma_scores: Dict[str, float] = {}
        combined_scores: Dict[str, float] = {}

        for cat_value, kw_score in sorted_candidates:
            g_score = self._binary_classify(message, cat_value)
            gemma_scores[cat_value] = g_score
            combined_scores[cat_value] = (
                kw_score * self.keyword_weight + g_score * self.gemma_weight
            )

        # Select best combined score
        best_category = max(combined_scores, key=combined_scores.get)  # type: ignore[arg-type]
        best_confidence = min(combined_scores[best_category], 1.0)

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        self._stats["total_latency_ms"] += elapsed_ms
        self._stats["avg_latency_ms"] = (
            self._stats["total_latency_ms"] / self._stats["gemma_calls"]
        )

        logger.info(
            "[GEMMA-INTENT] Hybrid result: %s (conf=%.2f) kw=%s gemma=%s [%dms]",
            best_category,
            best_confidence,
            {k: f"{v:.2f}" for k, v in sorted_candidates},
            {k: f"{v:.2f}" for k, v in gemma_scores.items()},
            elapsed_ms,
        )

        return {
            "category": best_category,
            "confidence": best_confidence,
            "method": "gemma_hybrid",
            "gemma_scores": gemma_scores,
            "latency_ms": elapsed_ms,
        }

    # ------------------------------------------------------------------
    # Observability
    # ------------------------------------------------------------------

    @property
    def stats(self) -> Dict[str, object]:
        """Return classifier performance stats."""
        return dict(self._stats)

    @property
    def is_available(self) -> Optional[bool]:
        """
        Whether Gemma model is available.

        None = not yet checked (lazy), True = loaded, False = unavailable.
        """
        return self._available
