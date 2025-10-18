"""
Adaptive Complexity Router for YouTube DAE Gemma Intelligence

Architecture:
- Gemma 3 handles queries initially (fast path)
- Qwen monitors Gemma output quality (architect role)
- Complexity threshold adjusts dynamically based on performance
- 0102 acts as architect over the entire system

WSP 54: Partner (Gemma) → Principal (Qwen) → Associate (0102 architect)
WSP 80: DAE Cube orchestration with learning
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json
from llama_cpp import Llama
from chromadb import PersistentClient

logger = logging.getLogger(__name__)


class AdaptiveComplexityRouter:
    """
    Adaptive router that learns which queries need Qwen vs Gemma.

    Flow:
    1. Query → Gemma 3 (fast path, 50-100ms)
    2. Qwen evaluates Gemma output (quality check, 250ms)
    3. If low quality → route to Qwen for re-processing
    4. Adjust complexity threshold based on performance
    5. 0102 monitors overall architecture and tunes system
    """

    def __init__(
        self,
        gemma_model_path: str = "E:/HoloIndex/models/gemma-3-270m-it-Q4_K_M.gguf",
        qwen_model_path: str = "E:/HoloIndex/models/qwen-coder-1.5b.gguf",
        training_db_path: str = "E:/HoloIndex/vectors/youtube_training"
    ):
        """Initialize adaptive router with both models"""

        # Load Gemma 3 (fast classifier)
        logger.info("Loading Gemma 3 270M for fast classification...")
        self.gemma = Llama(
            model_path=gemma_model_path,
            n_ctx=1024,
            n_threads=4,
            n_gpu_layers=0,
            verbose=False
        )

        # Load Qwen 1.5B (architect/quality checker)
        logger.info("Loading Qwen 1.5B Coder for quality monitoring...")
        self.qwen = Llama(
            model_path=qwen_model_path,
            n_ctx=2048,
            n_threads=6,
            n_gpu_layers=0,
            verbose=False
        )

        # ChromaDB for training corpus
        self.db = PersistentClient(path=training_db_path)
        self.intent_collection = self.db.get_or_create_collection("intent_examples")

        # Adaptive complexity threshold (float between 0.0 and 1.0)
        # Start LOW - Qwen will push it up as it learns
        self.complexity_threshold = 0.3  # Start optimistic - trust Gemma

        # Performance tracking
        self.performance_history = []
        self.routing_stats = {
            "gemma_direct": 0,      # Gemma succeeded without Qwen
            "gemma_corrected": 0,   # Gemma failed, Qwen corrected
            "qwen_direct": 0,       # Routed to Qwen immediately
            "total_queries": 0
        }

        # Load previous state if exists
        self.state_file = Path("memory/adaptive_router_state.json")
        self._load_state()

        logger.info(f"Adaptive router initialized - complexity threshold: {self.complexity_threshold:.3f}")

    def classify_intent(
        self,
        message: str,
        role: str = "USER",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Classify message intent with adaptive routing.

        Flow:
        1. Compute complexity score (0.0-1.0)
        2. If complexity < threshold → Gemma 3 (fast)
        3. Qwen evaluates Gemma output
        4. If Qwen rejects → re-process with Qwen
        5. Adjust threshold based on result

        Returns:
            {
                'intent': str,
                'confidence': float,
                'route_to': str,
                'processing_path': 'gemma' | 'gemma→qwen' | 'qwen',
                'latency_ms': int,
                'quality_score': float (from Qwen)
            }
        """
        start_time = datetime.now()
        self.routing_stats["total_queries"] += 1

        # Step 1: Compute complexity score
        complexity_score = self._compute_complexity(message, role, context)
        logger.info(f"Query complexity: {complexity_score:.3f} (threshold: {self.complexity_threshold:.3f})")

        # Step 2: Route based on complexity
        if complexity_score < self.complexity_threshold:
            # Fast path: Try Gemma first
            logger.info("Routing to Gemma 3 (fast path)...")
            gemma_result = self._gemma_classify(message, role, context)

            # Step 3: Qwen quality check
            quality_score = self._qwen_evaluate_output(message, gemma_result)
            logger.info(f"Qwen quality score: {quality_score:.3f}")

            if quality_score >= 0.7:  # Qwen approves
                # Success! Gemma handled it well
                self.routing_stats["gemma_direct"] += 1
                latency_ms = (datetime.now() - start_time).total_seconds() * 1000

                result = {
                    **gemma_result,
                    'processing_path': 'gemma',
                    'latency_ms': int(latency_ms),
                    'quality_score': quality_score,
                    'complexity_score': complexity_score
                }

                # Reward: Lower threshold slightly (trust Gemma more)
                self._adjust_threshold(success=True, complexity=complexity_score)

            else:
                # Qwen rejected - re-process with Qwen
                logger.warning(f"Qwen rejected Gemma output (quality: {quality_score:.3f}) - re-routing to Qwen")
                self.routing_stats["gemma_corrected"] += 1

                qwen_result = self._qwen_classify(message, role, context)
                latency_ms = (datetime.now() - start_time).total_seconds() * 1000

                result = {
                    **qwen_result,
                    'processing_path': 'gemma→qwen',
                    'latency_ms': int(latency_ms),
                    'quality_score': 1.0,  # Qwen is authoritative
                    'complexity_score': complexity_score,
                    'gemma_failed': True,
                    'gemma_attempt': gemma_result
                }

                # Penalty: Raise threshold (this query type needs Qwen)
                self._adjust_threshold(success=False, complexity=complexity_score)

        else:
            # Complex path: Route to Qwen directly
            logger.info("Routing to Qwen 1.5B (complex path)...")
            self.routing_stats["qwen_direct"] += 1

            qwen_result = self._qwen_classify(message, role, context)
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000

            result = {
                **qwen_result,
                'processing_path': 'qwen',
                'latency_ms': int(latency_ms),
                'quality_score': 1.0,
                'complexity_score': complexity_score
            }

        # Record performance
        self._record_performance(result)

        # Periodically save state
        if self.routing_stats["total_queries"] % 50 == 0:
            self._save_state()

        return result

    def _compute_complexity(
        self,
        message: str,
        role: str,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """
        Compute query complexity score (0.0 = simple, 1.0 = complex).

        Factors:
        - Message length (longer = more complex)
        - Question words (why/how/explain = complex)
        - Context references (@mentions, thread refs)
        - Role (mods may have complex commands)
        - Ambiguity indicators
        """
        complexity = 0.0

        # Factor 1: Length
        word_count = len(message.split())
        if word_count > 20:
            complexity += 0.3
        elif word_count > 10:
            complexity += 0.15

        # Factor 2: Question complexity
        text_lower = message.lower()
        complex_questions = ['why', 'how', 'explain', 'what if', 'difference between']
        if any(q in text_lower for q in complex_questions):
            complexity += 0.3

        # Factor 3: Context references
        if '@' in message:  # Mentions
            complexity += 0.1
        if context and context.get('thread_id'):  # Thread context
            complexity += 0.15

        # Factor 4: Role
        if role in ['MOD', 'OWNER']:
            complexity += 0.1

        # Factor 5: Ambiguity indicators
        ambiguous = ['maybe', 'or', 'either', 'not sure', '?']
        if sum(1 for word in ambiguous if word in text_lower) >= 2:
            complexity += 0.2

        # Cap at 1.0
        return min(complexity, 1.0)

    def _gemma_classify(
        self,
        message: str,
        role: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run Gemma 3 classification with few-shot examples"""

        # Retrieve similar training examples from ChromaDB
        examples = self.intent_collection.query(
            query_texts=[message],
            n_results=5
        )

        # Build few-shot prompt
        prompt = self._build_intent_prompt(message, role, examples)

        # Run Gemma inference
        response = self.gemma(prompt, max_tokens=50, temperature=0.1, stop=["\n\n"])
        output_text = response['choices'][0]['text'].strip()

        # Parse intent
        result = self._parse_intent_response(output_text)
        result['model'] = 'gemma-3-270m'

        return result

    def _qwen_classify(
        self,
        message: str,
        role: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run Qwen 1.5B classification (authoritative)"""

        # Retrieve more examples for Qwen (has capacity)
        examples = self.intent_collection.query(
            query_texts=[message],
            n_results=10
        )

        # Build detailed prompt for Qwen
        prompt = self._build_intent_prompt(message, role, examples, detailed=True)

        # Run Qwen inference
        response = self.qwen(prompt, max_tokens=100, temperature=0.1, stop=["\n\n"])
        output_text = response['choices'][0]['text'].strip()

        # Parse intent
        result = self._parse_intent_response(output_text)
        result['model'] = 'qwen-1.5b-coder'

        return result

    def _qwen_evaluate_output(
        self,
        original_message: str,
        gemma_result: Dict[str, Any]
    ) -> float:
        """
        Qwen acts as architect: Evaluate Gemma's output quality.

        Returns quality score (0.0-1.0):
        - 1.0 = Perfect, Gemma nailed it
        - 0.7+ = Good enough, accept
        - <0.7 = Reject, re-process with Qwen
        """

        prompt = f"""You are evaluating an AI's intent classification.

Original message: "{original_message}"

AI classified as:
- Intent: {gemma_result.get('intent', 'unknown')}
- Confidence: {gemma_result.get('confidence', 0.0):.2f}
- Route to: {gemma_result.get('route_to', 'unknown')}

Rate this classification quality (0.0-1.0):
- 1.0 = Perfect classification
- 0.7-0.9 = Good, acceptable
- 0.4-0.6 = Uncertain, might be wrong
- 0.0-0.3 = Wrong classification

Quality score:"""

        response = self.qwen(prompt, max_tokens=20, temperature=0.1)
        output = response['choices'][0]['text'].strip()

        # Extract score
        try:
            # Look for float in response
            import re
            match = re.search(r'(\d+\.\d+)', output)
            if match:
                score = float(match.group(1))
                return max(0.0, min(1.0, score))
            else:
                # Fallback: keyword matching
                if 'perfect' in output.lower() or 'correct' in output.lower():
                    return 0.95
                elif 'good' in output.lower() or 'acceptable' in output.lower():
                    return 0.75
                elif 'wrong' in output.lower() or 'incorrect' in output.lower():
                    return 0.3
                else:
                    return 0.5  # Uncertain
        except Exception as e:
            logger.warning(f"Failed to parse Qwen quality score: {e}")
            return 0.5

    def _adjust_threshold(self, success: bool, complexity: float):
        """
        Adjust complexity threshold based on performance.

        Learning rules:
        - If Gemma succeeded on query with complexity X:
          → Lower threshold slightly (trust Gemma more)
        - If Gemma failed on query with complexity X:
          → Raise threshold (route similar queries to Qwen)

        Threshold moves slowly: ±0.02 per adjustment
        """
        if success:
            # Gemma succeeded - we can trust it more
            adjustment = -0.02
            logger.info(f"Gemma success - lowering threshold by {abs(adjustment):.3f}")
        else:
            # Gemma failed - need Qwen for this complexity level
            adjustment = +0.02
            logger.info(f"Gemma failure - raising threshold by {adjustment:.3f}")

        # Apply adjustment
        old_threshold = self.complexity_threshold
        self.complexity_threshold = max(0.1, min(0.8, self.complexity_threshold + adjustment))

        logger.info(f"Threshold adjusted: {old_threshold:.3f} → {self.complexity_threshold:.3f}")

    def _build_intent_prompt(
        self,
        message: str,
        role: str,
        examples: Dict,
        detailed: bool = False
    ) -> str:
        """Build few-shot prompt with training examples"""

        # Extract examples from ChromaDB results
        example_texts = []
        if examples and 'documents' in examples and examples['documents']:
            for i, doc in enumerate(examples['documents'][0][:3]):  # Top 3 examples
                metadata = examples['metadatas'][0][i] if 'metadatas' in examples else {}
                intent = metadata.get('intent', 'unknown')
                example_texts.append(f"Message: \"{doc}\"\nIntent: {intent}")

        # Build prompt
        prompt = f"""Classify YouTube chat message intent.

Examples:
{chr(10).join(example_texts)}

New message: "{message}"
Role: {role}

Intent (one of: command_whack, command_shorts, command_factcheck, consciousness, question, spam, conversation):"""

        return prompt

    def _parse_intent_response(self, text: str) -> Dict[str, Any]:
        """Parse model output into structured intent"""

        text_lower = text.lower()

        # Intent mapping
        intents = {
            'command_whack': ['whack', '/score', '/rank', '/quiz'],
            'command_shorts': ['shorts', 'createshort', 'shortveo'],
            'command_factcheck': ['factcheck', 'fc'],
            'consciousness': ['consciousness', '✊✋🖐'],
            'question': ['question', 'how', 'what', 'why'],
            'spam': ['spam', 'troll'],
            'conversation': ['conversation', 'chat']
        }

        # Find best match
        for intent, keywords in intents.items():
            if any(kw in text_lower for kw in keywords):
                return {
                    'intent': intent,
                    'confidence': 0.85,
                    'route_to': self._get_handler(intent)
                }

        # Default: conversation
        return {
            'intent': 'conversation',
            'confidence': 0.5,
            'route_to': 'general_response'
        }

    def _get_handler(self, intent: str) -> str:
        """Map intent to handler"""
        handler_map = {
            'command_whack': 'command_handler',
            'command_shorts': 'shorts_handler',
            'command_factcheck': 'factcheck_handler',
            'consciousness': 'consciousness_handler',
            'question': 'question_handler',
            'spam': 'spam_filter',
            'conversation': 'general_response'
        }
        return handler_map.get(intent, 'general_response')

    def _record_performance(self, result: Dict[str, Any]):
        """Record performance metrics"""
        self.performance_history.append({
            'timestamp': datetime.now().isoformat(),
            'processing_path': result['processing_path'],
            'complexity_score': result['complexity_score'],
            'quality_score': result['quality_score'],
            'latency_ms': result['latency_ms'],
            'threshold': self.complexity_threshold
        })

        # Keep last 1000 records
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-1000:]

    def _save_state(self):
        """Save router state to disk"""
        state = {
            'complexity_threshold': self.complexity_threshold,
            'routing_stats': self.routing_stats,
            'performance_history': self.performance_history[-100:]  # Last 100
        }

        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)

        logger.info(f"Router state saved - threshold: {self.complexity_threshold:.3f}")

    def _load_state(self):
        """Load router state from disk"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)

                self.complexity_threshold = state.get('complexity_threshold', 0.3)
                self.routing_stats = state.get('routing_stats', self.routing_stats)
                self.performance_history = state.get('performance_history', [])

                logger.info(f"Router state loaded - threshold: {self.complexity_threshold:.3f}")
            except Exception as e:
                logger.warning(f"Failed to load router state: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        total = self.routing_stats["total_queries"]
        if total == 0:
            return self.routing_stats

        return {
            **self.routing_stats,
            'gemma_success_rate': self.routing_stats["gemma_direct"] / total,
            'gemma_correction_rate': self.routing_stats["gemma_corrected"] / total,
            'qwen_usage_rate': self.routing_stats["qwen_direct"] / total,
            'current_threshold': self.complexity_threshold,
            'avg_latency_ms': sum(p['latency_ms'] for p in self.performance_history[-100:]) / min(100, len(self.performance_history)) if self.performance_history else 0
        }
