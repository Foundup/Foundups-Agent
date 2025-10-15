# YouTube API Operations Interface

## Overview

The `YouTubeAPIOperations` module provides a clean, fault-tolerant interface for YouTube API interactions with enhanced error handling, retry logic, and circuit breaker integration.

## Public API

### Class: YouTubeAPIOperations

#### Constructor
```python
YouTubeAPIOperations(circuit_breaker=None, logger=None)
```

**Parameters:**
- `circuit_breaker`: Circuit breaker instance for fault tolerance (optional)
- `logger`: Logger instance (optional, defaults to module logger)

#### Methods

##### check_video_details_enhanced(youtube, video_id)
Enhanced video details checking with retry logic.

**Parameters:**
- `youtube`: YouTube API service instance
- `video_id`: YouTube video ID to check

**Returns:** Video details dictionary or None
```python
{
    'video_id': str,
    'title': str,
    'channel_id': str,
    'live_status': str,  # 'live', 'upcoming', 'none'
    'live_details': dict,
    'status': dict
}
```

##### search_livestreams_enhanced(youtube, channel_id, max_results=10)
Enhanced livestream search with rate limit handling.

**Parameters:**
- `youtube`: YouTube API service instance
- `channel_id`: YouTube channel ID to search
- `max_results`: Maximum results to return (default: 10)

**Returns:** List of livestream dictionaries
```python
[{
    'video_id': str,
    'title': str,
    'channel_id': str,
    'published_at': str,
    'description': str,
    'thumbnails': dict
}]
```

##### get_active_livestream_video_id_enhanced(youtube, channel_id)
Enhanced active livestream detection with comprehensive verification.

**Parameters:**
- `youtube`: YouTube API service instance
- `channel_id`: YouTube channel ID to check

**Returns:** Tuple of (video_id, chat_id) or None

##### execute_api_fallback_search(youtube, channel_id, config=None)
Complete API fallback search orchestration (Priority 5 logic).

**Parameters:**
- `youtube`: YouTube API service instance
- `channel_id`: Channel ID to search
- `config`: Configuration object (optional)

**Returns:** Tuple of (video_id, chat_id) or None

## Integration Patterns

### Dependency Injection
```python
# Recommended: Inject dependencies
api_ops = YouTubeAPIOperations(
    circuit_breaker=my_circuit_breaker,
    logger=my_logger
)
```

### Error Handling
All methods include comprehensive error handling:
- Circuit breaker integration for fault tolerance
- Appropriate logging for debugging
- Graceful degradation when services are unavailable
- Exception propagation for critical failures

### Circuit Breaker Integration
When a circuit breaker is provided:
- API calls are automatically wrapped with circuit breaker protection
- Failures are tracked and can trigger circuit opening
- Recovery attempts respect circuit breaker state

### Logging
All operations include detailed logging:
- `[API]` prefix for API-related operations
- Success/failure status reporting
- Performance timing information
- Error details for troubleshooting

## Backward Compatibility

This module extracts functionality previously embedded in `stream_resolver.py`. The API is designed for clean integration without breaking existing code patterns.

## Error Conditions

### Common Error Responses
- **Invalid Parameters:** Returns None/empty list with error logging
- **API Quota Exceeded:** Circuit breaker activation, fallback handling
- **Network Issues:** Automatic retry with exponential backoff
- **Authentication Errors:** Clear error messages for credential issues
- **Rate Limiting:** Respects YouTube API rate limits with intelligent delays

### Exception Handling
- Non-critical errors return None/empty results
- Critical failures (invalid credentials, service unavailable) raise exceptions
- Circuit breaker failures are handled at the integration layer

## Testing

### Mock Testing
```python
# Example mock setup
mock_youtube = MagicMock()
api_ops = YouTubeAPIOperations()

# Test successful response
mock_youtube.videos.return_value.list.return_value.execute.return_value = {
    'items': [{'snippet': {'title': 'Test Stream'}}]
}
result = api_ops.check_video_details_enhanced(mock_youtube, 'VIDEO_ID')
```

### Integration Testing
```python
# With real circuit breaker
circuit_breaker = CircuitBreaker()
api_ops = YouTubeAPIOperations(circuit_breaker=circuit_breaker)

# Test with actual YouTube API (requires valid credentials)
result = api_ops.get_active_livestream_video_id_enhanced(youtube, 'CHANNEL_ID')
```
