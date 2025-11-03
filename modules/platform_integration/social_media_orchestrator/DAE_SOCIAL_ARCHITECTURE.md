# DAE Social Media Architecture

## WSP Compliance: WSP 27, WSP 54, WSP 80

## Overview

This architecture provides a **unified social media posting interface** that ANY DAE cube can use, following WSP principles of modularity and cube-level DAE implementation.

## Architecture Layers

```
+-----------------------------------------------------+
[U+2502]                   DAE CUBES                        [U+2502]
[U+2502]  (YouTube, LinkedIn, X, TikTok, Instagram, etc.)   [U+2502]
+------------------+----------------------------------+
                   [U+2502]
                   [U+25BC]
+-----------------------------------------------------+
[U+2502]           DAE SOCIAL INTERFACE                      [U+2502]
[U+2502]         (Simplified API for Cubes)                  [U+2502]
[U+2502]  • announce_stream()                                [U+2502]
[U+2502]  • post_update()                                    [U+2502]
[U+2502]  • schedule_post()                                  [U+2502]
+------------------+----------------------------------+
                   [U+2502]
                   [U+25BC]
+-----------------------------------------------------+
[U+2502]         UNIFIED SOCIAL POSTER                       [U+2502]
[U+2502]     (Platform-agnostic orchestration)               [U+2502]
[U+2502]  • PostRequest / PostResponse                       [U+2502]
[U+2502]  • Multi-platform coordination                      [U+2502]
[U+2502]  • State management                                 [U+2502]
+------------------+----------------------------------+
                   [U+2502]
                   [U+25BC]
+-----------------------------------------------------+
[U+2502]          PLATFORM ADAPTERS                          [U+2502]
[U+2502]  +--------------+  +--------------+                [U+2502]
[U+2502]  [U+2502]  LinkedIn    [U+2502]  [U+2502]  X/Twitter   [U+2502]                [U+2502]
[U+2502]  [U+2502]   Adapter    [U+2502]  [U+2502]   Adapter    [U+2502]                [U+2502]
[U+2502]  +------+-------+  +------+-------+                [U+2502]
[U+2502]         [U+2502]                  [U+2502]                        [U+2502]
[U+2502]         [U+25BC]                  [U+25BC]                        [U+2502]
[U+2502]  +--------------+  +--------------+                [U+2502]
[U+2502]  [U+2502]Anti-Detection[U+2502]  [U+2502] Simple X     [U+2502]                [U+2502]
[U+2502]  [U+2502]   Poster     [U+2502]  [U+2502]   Poster     [U+2502]                [U+2502]
[U+2502]  +--------------+  +--------------+                [U+2502]
+-----------------------------------------------------+
```

## Key Design Decisions

### 1. **Why Not Duplicate Modules?**

Instead of duplicating modules for each platform or function, we use:
- **Single unified interface** that all DAE cubes can use
- **Platform adapters** that handle platform-specific logic
- **Shared core logic** for common functionality

### 2. **How Different Scenarios are Handled**

#### LinkedIn Scenarios:
- **Live Stream**: Professional announcement with full description
- **Scheduled Post**: Can schedule for optimal business hours
- **Company Page**: Posts to company page by default

#### X/Twitter Scenarios:
- **Live Stream**: Concise announcement with link
- **Character Limit**: Auto-truncation to 280 chars
- **No Emojis**: ASCII-only to avoid encoding issues
- **POST Button**: Always the last button in compose interface

### 3. **DAE Cube Integration**

Any DAE cube can use the social interface by:

```python
from modules.platform_integration.social_media_orchestrator.src.unified_posting_interface import DAESocialInterface

# Create interface
social = DAESocialInterface()

# Post stream announcement
await social.announce_stream(
    title="Stream Title",
    url="https://youtube.com/watch?v=..."
)

# Post general update
await social.post_update("Update message")

# Schedule post
await social.schedule_post(
    message="Scheduled content",
    schedule_time=datetime.now() + timedelta(hours=2)
)
```

## Platform-Specific Implementation Details

### LinkedIn
- **Method**: Anti-detection browser automation
- **Auth**: Email/password from environment
- **Limits**: 3000 character limit
- **Features**: Rich formatting, hashtags, mentions

### X/Twitter
- **Method**: Browser automation with POST as last button
- **Auth**: Username/password from environment
- **Limits**: 280 character limit
- **Constraints**: ASCII-only (no emojis)

## Benefits of This Architecture

1. **Reusability**: Any DAE cube can use the same interface
2. **Maintainability**: Platform-specific logic isolated in adapters
3. **Extensibility**: Easy to add new platforms
4. **WSP Compliance**: Follows modular architecture principles
5. **Error Handling**: Unified error handling across platforms
6. **State Management**: Prevents duplicate posts

## Usage by Different DAE Cubes

### YouTube DAE
```python
# When stream goes live
await social.announce_stream(stream_title, stream_url)
```

### LinkedIn DAE
```python
# Share company update
await social.post_update(company_news)
```

### Infrastructure DAE
```python
# System status update
await social.post_update(f"System operational: {status}")
```

### Scheduler DAE
```python
# Schedule optimal posting times
for post in scheduled_posts:
    await social.schedule_post(
        post.content,
        post.optimal_time,
        post.platforms
    )
```

## Adding New Platforms

To add a new platform (e.g., TikTok):

1. Create adapter class inheriting from `PlatformAdapter`
2. Implement required methods:
   - `authenticate()`
   - `format_content()`
   - `validate_content()`
   - `post()`
3. Register in `UnifiedSocialPoster._initialize_adapters()`
4. Add to `Platform` enum

## Scheduled Posts Implementation

Currently, scheduled posts are handled through:
- **Immediate**: Posts right away
- **Scheduled**: Uses platform's schedule feature if available
- **Draft**: Saves as draft for manual review

Future enhancement: Integrate with job scheduler for true scheduled posting.

## Error Handling

The system handles errors at multiple levels:
1. **Platform Adapter**: Catches platform-specific errors
2. **Unified Poster**: Aggregates results from all platforms
3. **DAE Interface**: Returns simple success/failure
4. **Monitor**: Continues operation even if posting fails

## State Persistence

- Posted stream IDs saved to prevent duplicates
- State file: `dae_monitor_state.json`
- Automatic cleanup when > 100 entries

## Testing

Test the unified interface:
```bash
python modules/platform_integration/social_media_orchestrator/src/unified_posting_interface.py
```

Test the DAE monitor:
```bash
python auto_stream_monitor_dae.py
```

## WSP Compliance Notes

- **WSP 27**: Universal DAE pattern - all DAEs use same interface
- **WSP 54**: Agent coordination - DAEs coordinate through unified interface
- **WSP 80**: Cube-level implementation - each platform is a potential cube
- **WSP 3**: Enterprise domain organization - properly placed in platform_integration
- **WSP 49**: Module structure - full structure with src/, tests/, docs/

## Conclusion

This architecture solves the problem of multiple platforms with different requirements by:
1. Providing a **single unified interface** for all DAE cubes
2. **Abstracting platform differences** in adapters
3. **Reusing working implementations** (anti-detection posters)
4. **Following WSP principles** for modularity and organization

Any DAE cube can now post to social media without knowing platform specifics!