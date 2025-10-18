"""
YouTube DAE Gemma Intelligence MCP Server

Adaptive intelligence layer for YouTube chat processing:
- Gemma 3 270M for fast classification
- Qwen 1.5B as architect/quality monitor
- Dynamic complexity routing that learns

Architecture (per 012's insight):
    Query -> [Gemma 3: Intent Classifier] (50ms)
                        v
            Simple?------+------Complex?  <- Float threshold (starts 0.3)
                v                   v
    [Gemma 3 + ChromaDB RAG]   [Qwen 1.5B]  <- Qwen monitors & adjusts
         100ms                   250ms
                        v
            [0102 Architect Layer]  <- Overall system tuning

WSP 54: Partner (Gemma) -> Principal (Qwen) -> Associate (0102)
WSP 80: DAE Cube with learning capability
WSP 77: Intelligent Internet Orchestration
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from mcp import FastMCP
from adaptive_router import AdaptiveComplexityRouter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP(
    "YouTube DAE Gemma Intelligence",
    dependencies=["llama-cpp-python", "chromadb"]
)

# Initialize adaptive router (lazy load)
_router: Optional[AdaptiveComplexityRouter] = None


def get_router() -> AdaptiveComplexityRouter:
    """Get or create adaptive router instance"""
    global _router
    if _router is None:
        logger.info("Initializing Adaptive Complexity Router...")
        _router = AdaptiveComplexityRouter()
        logger.info("Router initialized successfully")
    return _router


@mcp.tool()
def classify_intent(
    message: str,
    role: str = "USER",
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Classify YouTube chat message intent with adaptive routing.

    This replaces 300+ lines of regex in MessageProcessor with intelligent
    classification that learns and improves over time.

    Args:
        message: The chat message text
        role: User role (USER, MOD, OWNER)
        context: Optional context (thread_id, user_history, etc.)

    Returns:
        {
            'intent': str (command_whack, command_shorts, consciousness, etc.),
            'confidence': float (0.0-1.0),
            'route_to': str (handler to route message to),
            'processing_path': str (gemma | gemma->qwen | qwen),
            'latency_ms': int,
            'quality_score': float (Qwen's evaluation of output),
            'complexity_score': float (computed query complexity)
        }

    Example:
        >>> classify_intent("!createshort my cool idea", "USER")
        {
            'intent': 'command_shorts',
            'confidence': 0.95,
            'route_to': 'shorts_handler',
            'processing_path': 'gemma',
            'latency_ms': 87,
            'quality_score': 0.92,
            'complexity_score': 0.15
        }

    Replaces:
        - _check_factcheck_command()
        - _check_shorts_command()
        - _check_whack_command()
        - _check_pqn_command()
        - 300+ lines of regex patterns
    """
    router = get_router()
    return router.classify_intent(message, role, context)


@mcp.tool()
def detect_spam(
    message: str,
    user_history: Optional[list] = None,
    author_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Detect spam/troll patterns using Gemma 3.

    NEW CAPABILITY - current system only has rate limiting, no content analysis.

    Args:
        message: The chat message text
        user_history: Recent messages from this user
        author_id: User identifier

    Returns:
        {
            'spam_type': str (legitimate | repetitive | caps | emoji_spam | troll),
            'should_block': bool,
            'confidence': float,
            'reason': str
        }

    Example:
        >>> detect_spam("MAGA 2024!!!! MAGA 2024!!!! MAGA 2024!!!!")
        {
            'spam_type': 'troll',
            'should_block': True,
            'confidence': 0.95,
            'reason': 'Repetitive political spam'
        }
    """
    router = get_router()

    # Build context for spam detection
    context = {
        'user_history': user_history or [],
        'author_id': author_id
    }

    # Check for obvious spam patterns first (fast path)
    text_upper = message.upper()
    if message == text_upper and len(message) > 20:  # ALL CAPS
        return {
            'spam_type': 'caps',
            'should_block': True,
            'confidence': 0.9,
            'reason': 'Excessive caps lock'
        }

    # Check for repetition
    if user_history and len(user_history) >= 3:
        if sum(1 for msg in user_history[-3:] if msg == message) >= 2:
            return {
                'spam_type': 'repetitive',
                'should_block': True,
                'confidence': 0.95,
                'reason': 'Repeated message'
            }

    # Use Gemma for content analysis
    result = router.classify_intent(message, "USER", context)

    if result['intent'] == 'spam':
        return {
            'spam_type': 'spam',
            'should_block': True,
            'confidence': result['confidence'],
            'reason': 'Detected as spam by classifier'
        }

    # Legitimate
    return {
        'spam_type': 'legitimate',
        'should_block': False,
        'confidence': result['confidence'],
        'reason': 'Passes spam filters'
    }


@mcp.tool()
def validate_response(
    original_message: str,
    generated_response: str,
    intent: str
) -> Dict[str, Any]:
    """
    Validate AI-generated response quality before sending to chat.

    NEW CAPABILITY - prevents inappropriate/off-topic responses.

    Args:
        original_message: The user's original message
        generated_response: The AI's proposed response
        intent: The classified intent

    Returns:
        {
            'approved': bool,
            'quality_score': float,
            'reason': str (relevant | off_topic | inappropriate | too_long)
        }

    Example:
        >>> validate_response(
        ...     "!createshort my idea",
        ...     "I'll create a short about quantum physics...",
        ...     "command_shorts"
        ... )
        {
            'approved': True,
            'quality_score': 0.9,
            'reason': 'relevant'
        }
    """
    router = get_router()

    # Use Qwen to evaluate response quality (Qwen as architect)
    quality_score = router._qwen_evaluate_output(
        original_message,
        {'intent': intent, 'response': generated_response}
    )

    # Approval logic
    if quality_score >= 0.7:
        return {
            'approved': True,
            'quality_score': quality_score,
            'reason': 'relevant'
        }
    elif len(generated_response) > 500:
        return {
            'approved': False,
            'quality_score': quality_score,
            'reason': 'too_long'
        }
    else:
        return {
            'approved': False,
            'quality_score': quality_score,
            'reason': 'off_topic'
        }


@mcp.tool()
def get_routing_stats() -> Dict[str, Any]:
    """
    Get adaptive router statistics.

    Shows how the system is learning and performing:
    - Gemma success rate (handled without Qwen correction)
    - Gemma correction rate (Qwen had to fix)
    - Qwen usage rate (routed directly)
    - Current complexity threshold
    - Average latency

    Returns:
        {
            'gemma_direct': int,
            'gemma_corrected': int,
            'qwen_direct': int,
            'total_queries': int,
            'gemma_success_rate': float,
            'gemma_correction_rate': float,
            'qwen_usage_rate': float,
            'current_threshold': float,
            'avg_latency_ms': float
        }

    Example:
        >>> get_routing_stats()
        {
            'total_queries': 1000,
            'gemma_direct': 750,
            'gemma_corrected': 150,
            'qwen_direct': 100,
            'gemma_success_rate': 0.75,
            'gemma_correction_rate': 0.15,
            'qwen_usage_rate': 0.10,
            'current_threshold': 0.28,  <- Learned to trust Gemma more
            'avg_latency_ms': 112
        }
    """
    router = get_router()
    return router.get_stats()


@mcp.tool()
def adjust_threshold(new_threshold: float) -> Dict[str, str]:
    """
    Manually adjust complexity threshold (0102 architect override).

    This is the 0102 architect layer - you can tune the system manually
    based on observed performance.

    Args:
        new_threshold: New threshold (0.0-1.0)
            - Lower = trust Gemma more (faster, may need correction)
            - Higher = use Qwen more (slower, higher quality)

    Returns:
        {'status': 'adjusted', 'old_threshold': float, 'new_threshold': float}

    Example:
        >>> adjust_threshold(0.25)  # Trust Gemma more
        {'status': 'adjusted', 'old_threshold': 0.30, 'new_threshold': 0.25}
    """
    router = get_router()
    old_threshold = router.complexity_threshold

    # Validate and apply
    new_threshold = max(0.0, min(1.0, new_threshold))
    router.complexity_threshold = new_threshold

    logger.info(f"0102 architect override: threshold {old_threshold:.3f} -> {new_threshold:.3f}")

    return {
        'status': 'adjusted',
        'old_threshold': old_threshold,
        'new_threshold': new_threshold
    }


@mcp.resource("routing://stats")
def routing_stats_resource() -> str:
    """
    MCP resource: Real-time routing statistics.

    Provides monitoring data for the adaptive system.
    """
    router = get_router()
    stats = router.get_stats()

    return f"""# YouTube DAE Gemma Routing Statistics

## Performance
- Total Queries: {stats.get('total_queries', 0)}
- Average Latency: {stats.get('avg_latency_ms', 0):.0f}ms

## Routing Distribution
- Gemma Direct (Success): {stats.get('gemma_success_rate', 0)*100:.1f}%
- Gemma -> Qwen (Corrected): {stats.get('gemma_correction_rate', 0)*100:.1f}%
- Qwen Direct (Complex): {stats.get('qwen_usage_rate', 0)*100:.1f}%

## Learning
- Current Threshold: {stats.get('current_threshold', 0.3):.3f}
- Started at: 0.300 (optimistic - trust Gemma)
- Delta: {stats.get('current_threshold', 0.3) - 0.3:+.3f}

## Interpretation
- Threshold going DOWN = System learning to trust Gemma more (faster)
- Threshold going UP = System learning queries are complex (need Qwen)
"""


if __name__ == "__main__":
    logger.info("Starting YouTube DAE Gemma Intelligence MCP Server...")
    logger.info("Adaptive routing: Gemma 3 (fast) [U+2194] Qwen 1.5B (architect)")
    logger.info("0102 architect layer: Monitor stats and adjust threshold as needed")
    mcp.run()
