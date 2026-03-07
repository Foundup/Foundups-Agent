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
from modules.infrastructure.shared_utilities.local_model_selection import resolve_triage_model_path

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
            model_path: Path to Gemma GGUF model (default: LOCAL_MODEL_TRIAGE_* resolution)
            timeout: Max inference time in seconds
        """
        # Default model path from central local model selection.
        if model_path is None:
            model_path = resolve_triage_model_path()

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

    def is_emoji_heavy(self, comment_text: str, threshold: float = 0.5) -> bool:
        """
        Detect if comment is emoji-heavy (more than threshold ratio of emojis).

        Pure Python detection - no Gemma needed for this.

        Args:
            comment_text: Comment content
            threshold: Ratio of emoji chars to total chars to be considered "emoji-heavy"

        Returns:
            bool: True if emoji-heavy
        """
        import re
        if not comment_text:
            return False

        # Unicode ranges for emojis
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"  # dingbats
            "\U0001F900-\U0001F9FF"  # supplemental symbols
            "\U0001FA00-\U0001FA6F"  # chess symbols
            "\U0001FA70-\U0001FAFF"  # symbols & pictographs extended
            "\U00002600-\U000026FF"  # misc symbols
            "]+", flags=re.UNICODE
        )

        # Count emoji characters
        emojis = emoji_pattern.findall(comment_text)
        emoji_char_count = sum(len(e) for e in emojis)
        total_chars = len(comment_text.replace(" ", ""))

        if total_chars == 0:
            return False

        ratio = emoji_char_count / total_chars

        logger.debug(f"[GEMMA] Emoji detection: {emoji_char_count}/{total_chars} = {ratio:.2f} (threshold: {threshold})")

        return ratio >= threshold

    def generate_emoji_response(self, comment_text: str) -> Dict:
        """
        Generate emoji response for emoji-heavy comments using Gemma.

        Gemma picks appropriate emoji response based on comment sentiment/context.

        Args:
            comment_text: Emoji-heavy comment

        Returns:
            Dict with emoji_response, strategy, and confidence
        """
        # Emoji response pools by sentiment/context
        EMOJI_RESPONSES = {
            'positive': ['🔥🔥🔥', '💯💯', '🙌🙌', '👏👏👏', '✨✨✨', '🚀🚀', '💪💪', '❤️🔥'],
            'celebration': ['🎉🎉🎉', '🥳🥳', '🎊🎊', '🏆🏆', '⭐⭐⭐', '🌟🌟'],
            'agreement': ['👍👍', '✊✊', '💯', '🤝🤝', '👊👊'],
            'love': ['❤️❤️', '💕💕', '🥰🥰', '😍😍', '💖💖'],
            'funny': ['😂😂', '🤣🤣', '😆😆', '😹😹'],
            'neutral': ['👀👀', '🤔💭', '👋👋', '✌️✌️'],
        }

        # Fast path: If Gemma unavailable, pick based on simple heuristics
        if not self._initialize_gemma():
            logger.info("[GEMMA] Emoji response: Gemma unavailable, using heuristic")
            # Simple heuristic: check for common positive emojis
            if any(e in comment_text for e in ['❤️', '💕', '😍', '🥰']):
                import random
                return {
                    'emoji_response': random.choice(EMOJI_RESPONSES['love']),
                    'strategy': 'heuristic_love',
                    'confidence': 0.7
                }
            elif any(e in comment_text for e in ['😂', '🤣', '😆']):
                import random
                return {
                    'emoji_response': random.choice(EMOJI_RESPONSES['funny']),
                    'strategy': 'heuristic_funny',
                    'confidence': 0.7
                }
            else:
                import random
                return {
                    'emoji_response': random.choice(EMOJI_RESPONSES['positive']),
                    'strategy': 'heuristic_positive',
                    'confidence': 0.6
                }

        # Gemma path: Ask Gemma to classify emoji sentiment
        prompt = f"""What is the sentiment of these emojis?
Reply with ONE word: POSITIVE, CELEBRATION, AGREEMENT, LOVE, FUNNY, or NEUTRAL

Emojis: {comment_text}

Sentiment:"""

        response = self._gemma_inference(prompt)

        import random

        if response:
            response_clean = response.strip().upper()

            # Map Gemma response to emoji pool
            if 'CELEBRATION' in response_clean or 'PARTY' in response_clean:
                pool = EMOJI_RESPONSES['celebration']
                strategy = 'gemma_celebration'
            elif 'LOVE' in response_clean or 'HEART' in response_clean:
                pool = EMOJI_RESPONSES['love']
                strategy = 'gemma_love'
            elif 'FUNNY' in response_clean or 'LAUGH' in response_clean:
                pool = EMOJI_RESPONSES['funny']
                strategy = 'gemma_funny'
            elif 'AGREEMENT' in response_clean or 'AGREE' in response_clean:
                pool = EMOJI_RESPONSES['agreement']
                strategy = 'gemma_agreement'
            elif 'POSITIVE' in response_clean:
                pool = EMOJI_RESPONSES['positive']
                strategy = 'gemma_positive'
            else:
                pool = EMOJI_RESPONSES['neutral']
                strategy = 'gemma_neutral'

            emoji_response = random.choice(pool)
            logger.info(f"[GEMMA] Emoji response: {emoji_response} (strategy: {strategy})")

            return {
                'emoji_response': emoji_response,
                'strategy': strategy,
                'confidence': 0.85
            }

        # Fallback if Gemma fails
        logger.warning("[GEMMA] Emoji inference failed, using positive fallback")
        return {
            'emoji_response': random.choice(EMOJI_RESPONSES['positive']),
            'strategy': 'gemma_fallback',
            'confidence': 0.5
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
