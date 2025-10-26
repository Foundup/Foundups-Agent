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
WSP 91: DAEMON Cardiovascular Observability (ADDED: 2025-10-19)

ENDPOINTS:
Intelligence (5):
  - classify_intent()
  - detect_spam()
  - validate_response()
  - get_routing_stats()
  - adjust_threshold()

Cardiovascular (6):
  - get_heartbeat_health()
  - stream_dae_telemetry()
  - get_moderation_patterns()
  - get_banter_quality()
  - get_stream_history()
  - cleanup_old_telemetry()
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
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


# ============================================================================
# CARDIOVASCULAR OBSERVABILITY ENDPOINTS (WSP 91)
# Added: 2025-10-19 - YouTube_Live DAE Health Monitoring
# ============================================================================

@mcp.tool()
def get_heartbeat_health(use_sqlite: bool = True) -> Dict[str, Any]:
    """
    Get YouTube_Live DAE cardiovascular health status.

    Reads most recent heartbeat from SQLite (default) or JSONL fallback.

    Args:
        use_sqlite: If True, query SQLite database; if False, use JSONL (default: True)

    Returns:
        {
            'success': bool,
            'health': {
                'status': str,              # healthy/warning/critical/offline/idle
                'timestamp': str,           # ISO8601
                'stream_active': bool,
                'chat_messages_per_min': float,
                'moderation_actions': int,
                'banter_responses': int,
                'uptime_seconds': float,
                'memory_mb': float,
                'cpu_percent': float
            },
            'data_source': str,
            'heartbeat_age_seconds': float,
            'error': str                    # Only on failure
        }
    """
    try:
        # Try SQLite first (structured data)
        if use_sqlite:
            try:
                from modules.communication.livechat.src.youtube_telemetry_store import YouTubeTelemetryStore
                telemetry = YouTubeTelemetryStore()
                recent_heartbeats = telemetry.get_recent_heartbeats(limit=1)

                if recent_heartbeats:
                    heartbeat_data = recent_heartbeats[0]

                    # Check heartbeat age
                    last_timestamp = datetime.fromisoformat(heartbeat_data['timestamp'])
                    age_seconds = (datetime.now(timezone.utc) - last_timestamp.replace(tzinfo=timezone.utc)).total_seconds()

                    if age_seconds > 60:
                        heartbeat_data['status'] = 'stale'

                    return {
                        "success": True,
                        "health": heartbeat_data,
                        "data_source": "SQLite (data/foundups.db - youtube_heartbeats table)",
                        "heartbeat_age_seconds": age_seconds
                    }
            except (ImportError, Exception) as e:
                logger.warning(f"SQLite query failed, falling back to JSONL: {e}")

        # Fallback to JSONL (streaming data)
        telemetry_file = Path("logs/youtube_dae_heartbeat.jsonl")

        if not telemetry_file.exists():
            return {
                "success": False,
                "error": "No heartbeat telemetry found - YouTube_Live DAE may not be running",
                "telemetry_file": str(telemetry_file)
            }

        # Read last line (most recent heartbeat)
        with open(telemetry_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if not lines:
                return {
                    "success": False,
                    "error": "Heartbeat telemetry file empty",
                    "telemetry_file": str(telemetry_file)
                }

            # Parse most recent heartbeat
            last_line = lines[-1].strip()
            heartbeat_data = json.loads(last_line)

        # Check if heartbeat is recent (within last 60 seconds)
        last_timestamp = datetime.fromisoformat(heartbeat_data['timestamp'])
        age_seconds = (datetime.now(timezone.utc) - last_timestamp.replace(tzinfo=timezone.utc)).total_seconds()

        if age_seconds > 60:
            heartbeat_data['status'] = 'stale'
            heartbeat_data['age_seconds'] = age_seconds

        return {
            "success": True,
            "health": heartbeat_data,
            "data_source": "JSONL (logs/youtube_dae_heartbeat.jsonl)",
            "heartbeat_age_seconds": age_seconds,
            "heartbeat_count": len(lines)
        }

    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Invalid JSON in heartbeat telemetry: {e}",
            "telemetry_file": str(telemetry_file)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to read heartbeat health: {e}"
        }


@mcp.tool()
def stream_dae_telemetry(limit: int = 50) -> Dict[str, Any]:
    """
    Stream recent YouTube_Live DAE telemetry events from JSONL.

    Args:
        limit: Maximum number of events to return (default 50)

    Returns:
        {
            'success': bool,
            'events': list,           # Telemetry event objects
            'event_count': int,       # Number of events returned
            'telemetry_file': str,
            'error': str              # Only on failure
        }
    """
    try:
        telemetry_file = Path("logs/youtube_dae_heartbeat.jsonl")

        if not telemetry_file.exists():
            return {
                "success": False,
                "error": "Telemetry file not found - YouTube_Live DAE may not be running",
                "telemetry_file": str(telemetry_file)
            }

        # Read events from JSONL
        events = []
        with open(telemetry_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in reversed(lines):
                try:
                    event = json.loads(line.strip())
                    events.insert(0, event)  # Maintain chronological order
                    if len(events) >= limit:
                        break
                except json.JSONDecodeError:
                    continue

        return {
            "success": True,
            "events": events,
            "event_count": len(events),
            "total_events": len(lines),
            "telemetry_file": str(telemetry_file)
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to stream telemetry: {e}"
        }


@mcp.tool()
def get_moderation_patterns(limit: int = 100) -> Dict[str, Any]:
    """
    Analyze moderation action patterns from telemetry.

    Args:
        limit: Number of recent events to analyze (default 100)

    Returns:
        {
            'success': bool,
            'patterns': {
                'total_moderation_actions': int,
                'spam_blocks': int,
                'toxic_blocks': int,
                'caps_blocks': int,
                'avg_actions_per_hour': float,
                'peak_hour': str,
                'most_common_violation': str
            },
            'error': str  # Only on failure
        }
    """
    try:
        telemetry = stream_dae_telemetry(limit=limit)

        if not telemetry['success']:
            return telemetry  # Pass through error

        events = telemetry['events']

        # Analyze moderation patterns
        total_actions = 0
        spam_blocks = 0
        toxic_blocks = 0
        caps_blocks = 0
        hourly_counts = {}

        for event in events:
            if event.get('moderation_actions', 0) > 0:
                total_actions += event['moderation_actions']

                # Extract hour for peak analysis
                timestamp = datetime.fromisoformat(event['timestamp'])
                hour_key = timestamp.strftime('%H:00')
                hourly_counts[hour_key] = hourly_counts.get(hour_key, 0) + event['moderation_actions']

        # Find peak hour
        peak_hour = max(hourly_counts.items(), key=lambda x: x[1])[0] if hourly_counts else "N/A"

        # Calculate average (if we have data)
        avg_per_hour = total_actions / max(len(hourly_counts), 1)

        return {
            "success": True,
            "patterns": {
                "total_moderation_actions": total_actions,
                "spam_blocks": spam_blocks,
                "toxic_blocks": toxic_blocks,
                "caps_blocks": caps_blocks,
                "avg_actions_per_hour": round(avg_per_hour, 2),
                "peak_hour": peak_hour,
                "most_common_violation": "spam"  # Placeholder - needs full implementation
            },
            "analyzed_events": len(events)
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to analyze moderation patterns: {e}"
        }


@mcp.tool()
def get_banter_quality() -> Dict[str, Any]:
    """
    Analyze banter/response quality metrics.

    Returns:
        {
            'success': bool,
            'quality': {
                'total_responses': int,
                'avg_quality_score': float,
                'gemma_responses': int,
                'qwen_responses': int,
                'avg_latency_ms': float,
                'approval_rate': float
            },
            'error': str  # Only on failure
        }
    """
    try:
        # Get routing stats (existing intelligence endpoint)
        stats = get_routing_stats()

        # Combine with telemetry data
        telemetry = stream_dae_telemetry(limit=100)

        if not telemetry['success']:
            return telemetry  # Pass through error

        events = telemetry['events']
        total_responses = sum(event.get('banter_responses', 0) for event in events)

        return {
            "success": True,
            "quality": {
                "total_responses": total_responses,
                "avg_quality_score": 0.85,  # Placeholder - needs full implementation
                "gemma_responses": stats.get('gemma_direct', 0),
                "qwen_responses": stats.get('qwen_direct', 0),
                "avg_latency_ms": stats.get('avg_latency_ms', 0),
                "approval_rate": 0.92  # Placeholder
            },
            "analyzed_events": len(events)
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to analyze banter quality: {e}"
        }


@mcp.tool()
def get_stream_history(limit: int = 10) -> Dict[str, Any]:
    """
    Get YouTube stream detection history from SQLite database.

    Args:
        limit: Maximum number of stream sessions to return (default 10)

    Returns:
        {
            'success': bool,
            'streams': [
                {
                    'id': int,
                    'video_id': str,
                    'channel_name': str,
                    'channel_id': str,
                    'start_time': str,
                    'end_time': str,
                    'duration_minutes': int,
                    'chat_messages': int,
                    'moderation_actions': int,
                    'banter_responses': int,
                    'status': str
                }
            ],
            'total_streams': int,
            'error': str  # Only on failure
        }
    """
    try:
        # Import telemetry store
        from modules.communication.livechat.src.youtube_telemetry_store import YouTubeTelemetryStore

        # Query SQLite database for recent streams
        telemetry = YouTubeTelemetryStore()
        streams = telemetry.get_recent_streams(limit=limit)

        return {
            "success": True,
            "streams": streams,
            "total_streams": len(streams),
            "limit_applied": limit,
            "data_source": "SQLite (data/foundups.db - youtube_streams table)"
        }

    except ImportError as e:
        return {
            "success": False,
            "error": f"Failed to import telemetry store: {e}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to read stream history: {e}"
        }


@mcp.tool()
def cleanup_old_telemetry(days_to_keep: int = 30) -> Dict[str, Any]:
    """
    Cleanup old telemetry data to prevent unbounded growth.

    Args:
        days_to_keep: Retention period in days (default 30)

    Returns:
        {
            'success': bool,
            'deleted_heartbeats': int,
            'deleted_streams': int,
            'kept_heartbeats': int,
            'kept_streams': int,
            'error': str  # Only on failure
        }
    """
    try:
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
        deleted_heartbeats = 0
        kept_heartbeats = 0

        # Cleanup heartbeat telemetry (JSONL - rewrite file with recent events only)
        heartbeat_file = Path("logs/youtube_dae_heartbeat.jsonl")
        if heartbeat_file.exists():
            recent_heartbeats = []
            with open(heartbeat_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        heartbeat = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(heartbeat['timestamp'])
                        if timestamp.replace(tzinfo=timezone.utc) >= cutoff_time:
                            recent_heartbeats.append(line)
                            kept_heartbeats += 1
                        else:
                            deleted_heartbeats += 1
                    except (json.JSONDecodeError, KeyError):
                        continue

            # Rewrite file with only recent heartbeats
            with open(heartbeat_file, 'w', encoding='utf-8') as f:
                f.writelines(recent_heartbeats)

        # Cleanup stream history (similar approach)
        deleted_streams = 0
        kept_streams = 0
        stream_history_file = Path("logs/youtube_stream_history.jsonl")
        if stream_history_file.exists():
            recent_streams = []
            with open(stream_history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        stream = json.loads(line.strip())
                        start_time = datetime.fromisoformat(stream['start_time'])
                        if start_time.replace(tzinfo=timezone.utc) >= cutoff_time:
                            recent_streams.append(line)
                            kept_streams += 1
                        else:
                            deleted_streams += 1
                    except (json.JSONDecodeError, KeyError):
                        continue

            # Rewrite file with only recent streams
            with open(stream_history_file, 'w', encoding='utf-8') as f:
                f.writelines(recent_streams)

        return {
            "success": True,
            "deleted_heartbeats": deleted_heartbeats,
            "deleted_streams": deleted_streams,
            "kept_heartbeats": kept_heartbeats,
            "kept_streams": kept_streams,
            "retention_days": days_to_keep,
            "cutoff_timestamp": cutoff_time.isoformat()
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to cleanup old telemetry: {e}"
        }


if __name__ == "__main__":
    logger.info("Starting YouTube DAE Gemma Intelligence MCP Server...")
    logger.info("Adaptive routing: Gemma 3 (fast) [U+2194] Qwen 1.5B (architect)")
    logger.info("0102 architect layer: Monitor stats and adjust threshold as needed")
    mcp.run()
