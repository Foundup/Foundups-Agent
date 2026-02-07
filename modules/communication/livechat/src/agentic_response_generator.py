"""
Agentic Response Generator - WSP 77 Multi-Agent Pattern

Layered architecture for consciousness responses:
- Layer 0: Context-based personalization (DONE - in agentic_chat_engine.py)
- Layer 1: Gemma fast classification (50ms)
- Layer 2: Qwen response generation (200ms)
- Layer 3: PatternMemory outcome learning
- Layer 4: AI Overseer decision coordination
- Layer 5: UI-TARS vision for page state

WSP Compliance:
- WSP 77: Agent Coordination (Gemma→Qwen→0102→Learn)
- WSP 84: Code Reuse (follows local_llm_worker_poc.py pattern)
- WSP 60: Module Memory (PatternMemory integration)
- WSP 48: Recursive Self-Improvement (outcome learning)

NAVIGATION: Orchestrates agentic response generation.
-> Called by: agentic_chat_engine.py (future integration)
-> Delegates to: Gemma (classify), Qwen (generate), PatternMemory (learn)
-> Related: local_llm_worker_poc.py, gemma_rag_inference.py
"""

import os
import logging
import time
from pathlib import Path
from typing import Dict, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ResponseDecision:
    """Result from agentic response generation."""
    response: str
    user_type: str          # Gemma classification
    confidence: float       # 0.0-1.0 classification confidence
    latency_ms: int         # Total generation time
    layer_used: int         # Which layer generated (0-5)
    model_used: str         # gemma, qwen, or "heuristic"


class AgenticResponseGenerator:
    """
    Multi-agent response generator following WSP 77.

    Architecture:
        1. Gemma classifies user type (50ms)
        2. Qwen generates personalized response (200ms)
        3. PatternMemory stores outcome for learning
        4. AI Overseer coordinates decisions (optional)

    Usage:
        generator = AgenticResponseGenerator()
        decision = await generator.generate_response(
            username="babyjuggernaught8203",
            message="✊✋🖐️",
            user_context={"message_count": 15, "user_type": "returning"}
        )
        print(decision.response)  # Personalized response
    """

    # Model registry (same as local_llm_worker_poc.py)
    MODEL_REGISTRY = {
        "gemma": {
            "name": "gemma-3-270m-it-Q4_K_M.gguf",
            "path": Path("E:/HoloIndex/models/gemma-3-270m-it-Q4_K_M.gguf"),
            "n_ctx": 512,
            "purpose": "Fast classification (50ms)"
        },
        "qwen": {
            "name": "qwen-coder-1.5b.gguf",
            "path": Path("E:/HoloIndex/models/qwen-coder-1.5b.gguf"),
            "n_ctx": 2048,
            "purpose": "Response generation (200ms)"
        }
    }

    # User type classifications (Gemma output)
    USER_TYPES = {
        "new_fan": "First-time participant, welcoming tone",
        "regular": "Returning user, acknowledge history",
        "mod": "Moderator, respectful engagement",
        "troll": "Potential bad actor, cautious response",
        "maga": "MAGA content detected, troll mode",
        "enlightened": "High consciousness, advanced response"
    }

    def __init__(self, mock_mode: bool = False):
        """
        Initialize generator.

        Args:
            mock_mode: If True, skip LLM loading (use heuristics)
        """
        self.mock_mode = mock_mode
        self._gemma = None   # Lazy load
        self._qwen = None    # Lazy load
        self._pattern_memory = None  # Lazy load
        self._ai_overseer = None     # Lazy load

        logger.info(f"[AGENTIC-GEN] Initialized (mock={mock_mode})")

    # =========================================================================
    # Layer 1: Gemma Fast Classification
    # =========================================================================

    def _init_gemma(self) -> bool:
        """
        Lazy-load Gemma model for classification.

        Pattern from gemma_rag_inference.py (WSP 84).
        """
        if self._gemma is not None:
            return True

        if self.mock_mode:
            logger.debug("[AGENTIC-L1] Mock mode - skipping Gemma load")
            return True

        gemma_config = self.MODEL_REGISTRY["gemma"]
        if not gemma_config["path"].exists():
            logger.warning(f"[AGENTIC-L1] Gemma not found: {gemma_config['path']}")
            return False

        try:
            from llama_cpp import Llama

            logger.info(f"[AGENTIC-L1] Loading Gemma for classification...")

            # Suppress llama.cpp noise (per gemma_rag_inference.py pattern)
            old_stdout, old_stderr = os.dup(1), os.dup(2)
            devnull = os.open(os.devnull, os.O_WRONLY)

            try:
                os.dup2(devnull, 1)
                os.dup2(devnull, 2)

                self._gemma = Llama(
                    model_path=str(gemma_config["path"]),
                    n_ctx=gemma_config["n_ctx"],
                    n_threads=2,
                    n_gpu_layers=0,
                    verbose=False
                )
            finally:
                os.dup2(old_stdout, 1)
                os.dup2(old_stderr, 2)
                os.close(devnull)
                os.close(old_stdout)
                os.close(old_stderr)

            logger.info("[AGENTIC-L1] Gemma loaded successfully")
            return True

        except ImportError:
            logger.error("[AGENTIC-L1] llama_cpp not installed")
            return False
        except Exception as e:
            logger.error(f"[AGENTIC-L1] Gemma load failed: {e}")
            return False

    def classify_user(self, user_context: Dict) -> Tuple[str, float]:
        """
        Layer 1: Fast user classification via Gemma.

        Args:
            user_context: Dict with message_count, user_type, consciousness_level

        Returns:
            (user_type, confidence) tuple
        """
        start_time = time.time()

        # Extract context
        msg_count = user_context.get('message_count', 0)
        role = user_context.get('role', 'USER')
        consciousness = user_context.get('consciousness_level', 'unknown')
        existing_type = user_context.get('user_type', 'unknown')

        # Mock mode: use heuristics
        if self.mock_mode or not self._init_gemma():
            # Heuristic classification (Layer 0 fallback)
            if role in ('MOD', 'OWNER'):
                return ("mod", 0.95)
            elif consciousness == 'needs_help':
                return ("maga", 0.80)
            elif msg_count > 20:
                return ("regular", 0.85)
            elif msg_count == 0:
                return ("new_fan", 0.90)
            elif consciousness == 'aware':
                return ("enlightened", 0.75)
            else:
                return ("regular", 0.60)

        # Real Gemma classification
        prompt = f"""Classify this YouTube chat user:
- Messages sent: {msg_count}
- Role: {role}
- Consciousness indicators: {consciousness}
- Current type: {existing_type}

Output ONLY one of: new_fan, regular, mod, troll, maga, enlightened

USER_TYPE:"""

        try:
            response = self._gemma(
                prompt,
                max_tokens=10,
                temperature=0.1,
                stop=["\n", " "],
                echo=False
            )

            if isinstance(response, dict) and 'choices' in response:
                result = response['choices'][0]['text'].strip().lower()
            else:
                result = str(response).strip().lower()

            # Validate result
            if result in self.USER_TYPES:
                latency = int((time.time() - start_time) * 1000)
                logger.info(f"[AGENTIC-L1] Gemma classified: {result} ({latency}ms)")
                return (result, 0.85)
            else:
                logger.warning(f"[AGENTIC-L1] Invalid classification: {result}")
                return ("regular", 0.50)

        except Exception as e:
            logger.error(f"[AGENTIC-L1] Classification failed: {e}")
            return ("regular", 0.40)

    # =========================================================================
    # Layer 2: Qwen Response Generation
    # =========================================================================

    def _init_qwen(self) -> bool:
        """Lazy-load Qwen model for response generation."""
        if self._qwen is not None:
            return True

        if self.mock_mode:
            return True

        qwen_config = self.MODEL_REGISTRY["qwen"]
        if not qwen_config["path"].exists():
            logger.warning(f"[AGENTIC-L2] Qwen not found: {qwen_config['path']}")
            return False

        try:
            from llama_cpp import Llama

            logger.info("[AGENTIC-L2] Loading Qwen for generation...")

            old_stdout, old_stderr = os.dup(1), os.dup(2)
            devnull = os.open(os.devnull, os.O_WRONLY)

            try:
                os.dup2(devnull, 1)
                os.dup2(devnull, 2)

                self._qwen = Llama(
                    model_path=str(qwen_config["path"]),
                    n_ctx=qwen_config["n_ctx"],
                    n_threads=2,
                    n_gpu_layers=0,
                    verbose=False
                )
            finally:
                os.dup2(old_stdout, 1)
                os.dup2(old_stderr, 2)
                os.close(devnull)
                os.close(old_stdout)
                os.close(old_stderr)

            logger.info("[AGENTIC-L2] Qwen loaded successfully")
            return True

        except Exception as e:
            logger.error(f"[AGENTIC-L2] Qwen load failed: {e}")
            return False

    def generate_response_qwen(
        self,
        username: str,
        user_type: str,
        emoji_sequence: str
    ) -> Optional[str]:
        """
        Layer 2: Generate personalized response via Qwen.

        Args:
            username: User's display name
            user_type: Gemma classification result
            emoji_sequence: Consciousness emoji sequence

        Returns:
            Generated response or None
        """
        if not self._init_qwen():
            return None

        start_time = time.time()

        prompt = f"""Generate a witty YouTube live chat response.

User: {username}
User Type: {user_type}
Emoji Trigger: {emoji_sequence}

Style Guidelines:
- Sarcastic but friendly
- Reference consciousness levels (✊=closed, 🖐️=open)
- Max 150 characters
- Start with @{username}

Response:"""

        try:
            response = self._qwen(
                prompt,
                max_tokens=80,
                temperature=0.7,
                stop=["\n\n"],
                echo=False
            )

            if isinstance(response, dict) and 'choices' in response:
                result = response['choices'][0]['text'].strip()
            else:
                result = str(response).strip()

            # Ensure starts with @username
            if not result.startswith(f"@{username}"):
                result = f"@{username} {result}"

            # Truncate to YouTube limit
            if len(result) > 180:
                result = result[:177] + "..."

            latency = int((time.time() - start_time) * 1000)
            logger.info(f"[AGENTIC-L2] Qwen generated ({latency}ms): {result[:50]}...")
            return result

        except Exception as e:
            logger.error(f"[AGENTIC-L2] Generation failed: {e}")
            return None

    # =========================================================================
    # Layer 3: PatternMemory Outcome Learning
    # =========================================================================

    def _init_pattern_memory(self) -> bool:
        """Lazy-load PatternMemory for outcome storage."""
        if self._pattern_memory is not None:
            return True

        try:
            from modules.infrastructure.wre_core.src.pattern_memory import PatternMemory
            self._pattern_memory = PatternMemory()
            logger.info("[AGENTIC-L3] PatternMemory loaded")
            return True
        except Exception as e:
            logger.warning(f"[AGENTIC-L3] PatternMemory unavailable: {e}")
            return False

    def store_outcome(
        self,
        username: str,
        user_type: str,
        response: str,
        got_reaction: bool = False
    ) -> None:
        """
        Layer 3: Store response outcome for learning.

        Args:
            username: User who received response
            user_type: Classification used
            response: Response that was sent
            got_reaction: Whether user reacted positively
        """
        if not self._init_pattern_memory():
            return

        try:
            from modules.infrastructure.wre_core.src.pattern_memory import SkillOutcome
            import json
            from datetime import datetime

            outcome = SkillOutcome(
                execution_id=f"consciousness_{datetime.now().isoformat()}",
                skill_name="consciousness_response",
                agent="agentic_chat",
                timestamp=datetime.now().isoformat(),
                input_context=json.dumps({
                    "username": username,
                    "user_type": user_type
                }),
                output_result=json.dumps({"response": response}),
                success=got_reaction,
                pattern_fidelity=0.8 if got_reaction else 0.4,
                outcome_quality=0.9 if got_reaction else 0.5,
                execution_time_ms=0,
                step_count=2,
                notes=f"L1:{user_type}"
            )

            self._pattern_memory.store_outcome(outcome)
            logger.debug(f"[AGENTIC-L3] Stored outcome for {username}")

        except Exception as e:
            logger.warning(f"[AGENTIC-L3] Failed to store outcome: {e}")

    # =========================================================================
    # Main Entry Point
    # =========================================================================

    async def generate_response(
        self,
        username: str,
        message: str,
        user_context: Dict,
        emoji_sequence: str = "✊✋🖐️"
    ) -> ResponseDecision:
        """
        Main entry point: Generate agentic response using all layers.

        Flow:
            1. Gemma classifies user (Layer 1)
            2. Qwen generates response (Layer 2) or fallback to heuristic
            3. Store outcome for learning (Layer 3)

        Args:
            username: User's display name
            message: Original message
            user_context: Dict from ChatMemoryManager
            emoji_sequence: Consciousness emojis detected

        Returns:
            ResponseDecision with response and metadata
        """
        start_time = time.time()

        # Layer 1: Classify user
        user_type, confidence = self.classify_user(user_context)

        # Layer 2: Generate response
        response = None
        layer_used = 1
        model_used = "gemma"

        if confidence >= 0.7:
            response = self.generate_response_qwen(username, user_type, emoji_sequence)
            if response:
                layer_used = 2
                model_used = "qwen"

        # Fallback: Use heuristic response
        if not response:
            layer_used = 0
            model_used = "heuristic"
            response = self._heuristic_response(username, user_type, emoji_sequence)

        latency = int((time.time() - start_time) * 1000)

        # Layer 3: Store for learning (async, don't block)
        self.store_outcome(username, user_type, response, got_reaction=False)

        logger.info(
            f"[AGENTIC] Generated response for {username}: "
            f"type={user_type}, layer={layer_used}, {latency}ms"
        )

        return ResponseDecision(
            response=response,
            user_type=user_type,
            confidence=confidence,
            latency_ms=latency,
            layer_used=layer_used,
            model_used=model_used
        )

    def _heuristic_response(
        self,
        username: str,
        user_type: str,
        emoji_sequence: str
    ) -> str:
        """Fallback heuristic responses when LLM unavailable."""
        import random

        responses = {
            "new_fan": [
                f"@{username} First {emoji_sequence}! Welcome to consciousness!",
                f"@{username} Fresh awareness detected! {emoji_sequence}",
            ],
            "regular": [
                f"@{username} {emoji_sequence} Your consciousness is noted!",
                f"@{username} Returning for more {emoji_sequence}? Excellent!",
            ],
            "mod": [
                f"@{username} {emoji_sequence} Mod wisdom appreciated!",
                f"@{username} The enlightened mod speaks! {emoji_sequence}",
            ],
            "maga": [
                f"@{username} Detected: ✊✊✊ symptoms. Prescription: {emoji_sequence}",
                f"@{username} Still at ✊✊✊? Evolution available!",
            ],
            "enlightened": [
                f"@{username} {emoji_sequence} Maximum consciousness achieved!",
                f"@{username} Full entanglement! {emoji_sequence} 🖐️🖐️🖐️",
            ],
        }

        return random.choice(responses.get(user_type, responses["regular"]))


# Singleton instance for easy import
_generator_instance: Optional[AgenticResponseGenerator] = None


def get_agentic_generator(mock_mode: bool = False) -> AgenticResponseGenerator:
    """Get or create singleton AgenticResponseGenerator."""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = AgenticResponseGenerator(mock_mode=mock_mode)
    return _generator_instance
