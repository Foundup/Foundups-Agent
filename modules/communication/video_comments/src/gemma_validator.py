"""
Gemma Validator - Fast Pattern Validation via llama_cpp

Phase 3O-3R: Optional Gemma validation layer for 0/1/2 classification
Uses llama_cpp + Gemma 3 270M GGUF for binary classification (<50ms)

WSP References:
- WSP 77 (Agent Coordination): Gemma fast validation
- WSP 96 (WRE Skills): Pattern matching layer
- WSP 84 (Code Reuse): Follows gemma_rag_inference.py pattern

Architecture:
1. Rule-based classification (database) - <5ms
2. Optional Gemma validation - <50ms
3. Returns confidence boost/penalty

Pattern Source: holo_index/qwen_advisor/gemma_rag_inference.py (lines 107-146)

Usage:
    from modules.communication.video_comments.src.gemma_validator import GemmaValidator

    validator = GemmaValidator()
    result = validator.validate_classification(
        username="TestTroll",
        comment_text="Make America Great Again!",
        current_classification="MAGA_TROLL",
        current_confidence=0.70
    )
    # Returns: {'validated': True, 'adjusted_confidence': 0.85, 'reasoning': '...'}
"""

import logging
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class GemmaValidator:
    """
    Fast pattern validation using Gemma 3 270M via llama_cpp.

    Binary classification tasks (<50ms):
    - Validate MAGA troll patterns in comment text
    - Validate moderator-like language
    - Adjust confidence scores based on content
    """

    def __init__(self, model_path: Optional[Path] = None, timeout: int = 5):
        """
        Initialize Gemma validator.

        Args:
            model_path: Path to Gemma GGUF model (default: E:/HoloIndex/models/gemma-3-270m-it-Q4_K_M.gguf)
            timeout: Max inference time in seconds
        """
        # Default model path (existing model on E: drive per zen coding)
        if model_path is None:
            model_path = Path("E:/HoloIndex/models/gemma-3-270m-it-Q4_K_M.gguf")

        self.model_path = model_path
        self.timeout = timeout
        self.gemma_llm = None  # Lazy loaded

        logger.info(f"[GEMMA] Validator initialized - model_path={model_path}")

    def _initialize_gemma(self) -> bool:
        """
        Initialize Gemma 3 270M model via llama_cpp.

        Pattern from: gemma_rag_inference.py lines 107-146
        """
        if self.gemma_llm is not None:
            return True

        try:
            from llama_cpp import Llama
            import os

            logger.info(f"[GEMMA] Loading Gemma 3 270M from {self.model_path}")

            # Check if model exists
            if not self.model_path.exists():
                logger.error(f"[GEMMA] Model not found: {self.model_path}")
                return False

            # Suppress llama.cpp loading noise (pattern from gemma_rag_inference.py)
            old_stdout, old_stderr = os.dup(1), os.dup(2)
            devnull = os.open(os.devnull, os.O_WRONLY)

            try:
                os.dup2(devnull, 1)
                os.dup2(devnull, 2)

                self.gemma_llm = Llama(
                    model_path=str(self.model_path),
                    n_ctx=512,  # Small context for binary classification
                    n_threads=2,  # Fast inference on 2 threads
                    n_gpu_layers=0,  # CPU-only for consistency
                    verbose=False
                )

            finally:
                os.dup2(old_stdout, 1)
                os.dup2(old_stderr, 2)
                os.close(devnull)
                os.close(old_stdout)
                os.close(old_stderr)

            logger.info("[GEMMA] [OK] Gemma 3 270M loaded successfully")
            return True

        except Exception as e:
            logger.error(f"[GEMMA] [FAIL] Failed to load Gemma: {e}")
            return False

    def _gemma_inference(self, prompt: str) -> Optional[str]:
        """
        Run Gemma inference for binary classification.

        Args:
            prompt: Binary yes/no classification prompt

        Returns:
            str: Model response or None if failed
        """
        if not self._initialize_gemma():
            return None

        start_time = datetime.now()

        try:
            # Binary classification with minimal tokens
            response = self.gemma_llm(
                prompt,
                max_tokens=10,  # Just "YES" or "NO"
                temperature=0.0,  # Deterministic for classification
                stop=["\n", "###"],
                echo=False
            )

            latency = int((datetime.now() - start_time).total_seconds() * 1000)

            # Extract response text
            if isinstance(response, dict) and 'choices' in response:
                text = response['choices'][0]['text'].strip()
            else:
                text = str(response).strip()

            logger.debug(f"[GEMMA] Inference complete ({latency}ms): {text[:50]}")
            return text

        except Exception as e:
            logger.error(f"[GEMMA] Inference failed: {e}")
            return None

    def validate_maga_pattern(self, comment_text: str) -> Dict:
        """
        Validate MAGA troll patterns in comment.

        Binary classification: Is this MAGA rhetoric? (yes/no)

        Args:
            comment_text: Comment content to analyze

        Returns:
            Dict with validation result + confidence adjustment
        """
        if not self._initialize_gemma():
            return {
                'validated': False,
                'confidence_delta': 0.0,
                'reasoning': 'Gemma unavailable'
            }

        # Gemma prompt: Binary yes/no classification
        prompt = f"""Classify if this comment contains MAGA/far-right rhetoric.
Reply ONLY with: YES or NO

Comment: {comment_text}

Classification:"""

        response = self._gemma_inference(prompt)

        if response:
            # Parse yes/no response
            response_clean = response.strip().upper()

            if "YES" in response_clean:
                logger.info(f"[GEMMA] MAGA pattern confirmed: {comment_text[:50]}...")
                return {
                    'validated': True,
                    'confidence_delta': +0.15,  # Boost confidence by 15%
                    'reasoning': 'Gemma confirmed MAGA rhetoric'
                }
            elif "NO" in response_clean:
                logger.info(f"[GEMMA] MAGA pattern rejected: {comment_text[:50]}...")
                return {
                    'validated': False,
                    'confidence_delta': -0.20,  # Reduce confidence by 20%
                    'reasoning': 'Gemma rejected MAGA classification'
                }

        # If no clear answer, neutral
        return {
            'validated': False,
            'confidence_delta': 0.0,
            'reasoning': 'Gemma inconclusive'
        }

    def validate_moderator_pattern(self, comment_text: str) -> Dict:
        """
        Validate moderator-like language in comment.

        Binary classification: Does this sound like a moderator? (yes/no)

        Args:
            comment_text: Comment content to analyze

        Returns:
            Dict with validation result + confidence adjustment
        """
        if not self._initialize_gemma():
            return {
                'validated': False,
                'confidence_delta': 0.0,
                'reasoning': 'Gemma unavailable'
            }

        # Gemma prompt: Binary yes/no classification
        prompt = f"""Does this comment show moderator/community leader behavior?
Reply ONLY with: YES or NO

Comment: {comment_text}

Classification:"""

        response = self._gemma_inference(prompt)

        if response:
            response_clean = response.strip().upper()

            if "YES" in response_clean:
                return {
                    'validated': True,
                    'confidence_delta': +0.10,
                    'reasoning': 'Gemma confirmed moderator language'
                }
            elif "NO" in response_clean:
                return {
                    'validated': False,
                    'confidence_delta': 0.0,
                    'reasoning': 'Gemma: not moderator-like'
                }

        return {
            'validated': False,
            'confidence_delta': 0.0,
            'reasoning': 'Gemma inconclusive'
        }

    def validate_classification(
        self,
        username: str,
        comment_text: str,
        current_classification: str,
        current_confidence: float
    ) -> Dict:
        """
        Validate and adjust classification confidence using Gemma.

        Args:
            username: Commenter username
            comment_text: Comment content
            current_classification: Current classification (MAGA_TROLL/REGULAR/MODERATOR)
            current_confidence: Current confidence score (0.0-1.0)

        Returns:
            Dict with adjusted confidence and validation details
        """
        if not self._initialize_gemma():
            return {
                'validated': False,
                'adjusted_confidence': current_confidence,
                'confidence_delta': 0.0,
                'reasoning': 'Gemma validation disabled (model unavailable)'
            }

        # Route to appropriate validation based on classification
        if current_classification == "MAGA_TROLL":
            result = self.validate_maga_pattern(comment_text)
        elif current_classification == "MODERATOR":
            result = self.validate_moderator_pattern(comment_text)
        else:
            # Regular users don't need Gemma validation
            return {
                'validated': True,
                'adjusted_confidence': current_confidence,
                'confidence_delta': 0.0,
                'reasoning': 'Regular user - no validation needed'
            }

        # Apply confidence adjustment (clamped to 0.0-1.0)
        adjusted_confidence = max(0.0, min(1.0, current_confidence + result['confidence_delta']))

        logger.info(f"[GEMMA] @{username} validation: {current_confidence:.2f} -> {adjusted_confidence:.2f} "
                   f"(delta: {result['confidence_delta']:+.2f})")

        return {
            'validated': result['validated'],
            'adjusted_confidence': adjusted_confidence,
            'confidence_delta': result['confidence_delta'],
            'reasoning': result['reasoning']
        }


# Singleton instance
_validator_instance = None


def get_gemma_validator(model_path: Optional[Path] = None) -> GemmaValidator:
    """Get or create singleton Gemma validator"""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = GemmaValidator(model_path=model_path)
    return _validator_instance
