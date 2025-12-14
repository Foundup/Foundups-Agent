# Video Comments - Public Interface

**Module:** communication/video_comments
**WSP Reference:** WSP 11 (Interface Documentation)
**Status:** Production

## Overview

This module provides autonomous YouTube Studio comment engagement through the `CommentEngagementDAE` class and `execute_skill()` function. All engagement actions (Like, Heart, Reply) are performed via Selenium DOM automation with optional UI-TARS vision verification.

## Primary Interface: execute_skill()

### Function Signature

```python
async def execute_skill(
    channel_id: str,
    max_comments: int = 5,
    do_like: bool = True,
    do_heart: bool = True,
    reply_text: str = "",
    use_vision: bool = True
) -> Dict[str, Any]
```

### Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `channel_id` | str | - | Yes | YouTube channel ID (e.g., "UC-LSSlOZwpGIRIYihaz8zCw") |
| `max_comments` | int | 5 | No | Maximum comments to process |
| `do_like` | bool | True | No | Enable thumbs up action |
| `do_heart` | bool | True | No | Enable creator heart action |
| `reply_text` | str | "" | No | Reply text (empty = skip reply) |
| `use_vision` | bool | True | No | Enable UI-TARS verification |

### Return Value

```python
{
    'session_id': str,        # Unique session identifier (YYYYMMDD_HHMMSS)
    'channel_id': str,        # YouTube channel ID
    'total_processed': int,   # Total comments processed
    'stats': {
        'comments_processed': int,
        'likes': int,
        'hearts': int,
        'replies': int,
        'errors': int
    },
    'results': [              # Per-comment results
        {
            'comment_idx': int,
            'like': bool,
            'heart': bool,
            'reply': bool,
            'errors': List[str]
        }
    ]
}
```

### Example Usage

```python
from modules.communication.video_comments.skills.tars_like_heart_reply.comment_engagement_dae import execute_skill

# Full engagement
result = await execute_skill(
    channel_id="UC-LSSlOZwpGIRIYihaz8zCw",
    max_comments=5,
    reply_text="Thanks for watching! 🎌"
)

print(f"Processed: {result['stats']['comments_processed']}")
print(f"Likes: {result['stats']['likes']}")
print(f"Hearts: {result['stats']['hearts']}")
print(f"Replies: {result['stats']['replies']}")
```

## Secondary Interface: CommentEngagementDAE

### Class Signature

```python
class CommentEngagementDAE:
    def __init__(
        self,
        channel_id: str,
        use_vision: bool = True,
        use_dom: bool = True
    )
```

### Methods

#### connect() → bool
Connect to browser and vision system.
```python
await dae.connect()
```

#### navigate_to_inbox() → None
Navigate to YouTube Studio comments inbox.
```python
await dae.navigate_to_inbox()
```

#### get_comment_count() → int
Count visible comments on page.
```python
count = dae.get_comment_count()
```

#### engage_comment(comment_idx, do_like, do_heart, reply_text) → Dict
Engage with a single comment.
```python
result = await dae.engage_comment(
    comment_idx=1,         # 1-based index
    do_like=True,
    do_heart=True,
    reply_text="Thanks!"
)
```

#### engage_all_comments(max_comments, ...) → Dict
Engage with all visible comments.
```python
result = await dae.engage_all_comments(
    max_comments=10,
    do_like=True,
    do_heart=True,
    reply_text="Thanks!",
    refresh_between=True
)
```

#### close() → None
Release resources.
```python
dae.close()
```

### Full Example

```python
from modules.communication.video_comments.skills.tars_like_heart_reply.comment_engagement_dae import CommentEngagementDAE

async def engage_channel_comments():
    dae = CommentEngagementDAE(
        channel_id="UC-LSSlOZwpGIRIYihaz8zCw",
        use_vision=True,
        use_dom=True
    )
    
    try:
        await dae.connect()
        await dae.navigate_to_inbox()
        
        result = await dae.engage_all_comments(
            max_comments=10,
            do_like=True,
            do_heart=True,
            reply_text="Arigatou! 🇯🇵",
            refresh_between=True
        )
        
        return result
    finally:
        dae.close()
```

## CLI Interface

```bash
# Basic usage
python skills/tars_like_heart_reply/run_skill.py --max-comments 5

# With reply
python skills/tars_like_heart_reply/run_skill.py --max-comments 5 --reply-text "0102"

# DOM-only (no vision)
python skills/tars_like_heart_reply/run_skill.py --max-comments 10 --dom-only

# Skip actions
python skills/tars_like_heart_reply/run_skill.py --no-like --no-heart

# Custom channel
python skills/tars_like_heart_reply/run_skill.py --channel UC-XXXXX
```

### CLI Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--channel` | str | Move2Japan | YouTube channel ID |
| `--max-comments` | int | 5 | Max comments to process |
| `--reply-text` | str | "" | Reply text |
| `--no-like` | flag | False | Skip like action |
| `--no-heart` | flag | False | Skip heart action |
| `--dom-only` | flag | False | Disable vision verification |
| `--no-refresh` | flag | False | Don't refresh between batches |

## Error Handling

### Connection Errors
```python
try:
    await dae.connect()
except Exception as e:
    # Chrome not running or wrong port
    print(f"Connection failed: {e}")
```

### Action Errors
Individual action failures are captured in results:
```python
result = await dae.engage_comment(1, reply_text="Hi")
if result['errors']:
    print(f"Errors: {result['errors']}")
```

## Telemetry Output

Session results are saved to:
```
modules/communication/video_comments/memory/engagement_sessions/session_YYYYMMDD_HHMMSS.json
```

## DOM Selectors Reference

```python
SELECTORS = {
    'comment_thread': 'ytcp-comment-thread',
    'like': "ytcp-icon-button[aria-label='Like']",
    'heart': "ytcp-icon-button[aria-label='Heart']",
    'reply_btn': "#reply-button-end button",
    'reply_input': "textarea#textarea",
    'reply_submit': "#submit-button button",
}
```

---

**WSP 11 Compliance:** Complete
**Last Updated:** 2025-12-11
