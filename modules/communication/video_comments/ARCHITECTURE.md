# Video Comments Module Architecture

## Purpose
Handle YouTube video comments separately from live chat, as they are fundamentally different interactions with different requirements.

## Key Differences from LiveChat

| Aspect | Live Chat | Video Comments |
|--------|-----------|----------------|
| **Timing** | Real-time during streams | Asynchronous, anytime |
| **Persistence** | Ephemeral | Permanent |
| **Polling Rate** | Every 5 seconds | Every 30+ minutes |
| **Response Style** | Quick, fun, emojis | Thoughtful, detailed |
| **Quota Cost** | 5 units/poll | 1 unit read, 50 reply |
| **Active Hours** | During streams only | 24/7 |

## Module Structure

```
modules/communication/video_comments/
├── src/
│   ├── comment_monitor.py      # Main orchestrator
│   ├── comment_poller.py       # Polls for new comments
│   ├── comment_processor.py    # Analyzes comments
│   ├── comment_responder.py    # Generates responses
│   └── comment_memory.py       # Tracks conversations
├── tests/
└── memory/
```

## Integration Points

### Shared Components (from livechat)
- ThrottleManager - Rate limiting logic
- MessageProcessor patterns - Text analysis
- ChatMemoryManager patterns - Context tracking
- YouTubeAuth - API authentication

### Unique Components
- **Adaptive Polling**: Different rates for new vs old videos
- **Thread Management**: Track comment threads/replies
- **Content Analysis**: Deeper understanding for thoughtful responses
- **Author Reputation**: Track repeat commenters

## Polling Strategy

### New Videos (< 1 week old)
- Poll every 30 minutes for first 24 hours
- Poll every 2 hours for days 2-7
- High chance of engagement

### Recent Videos (1-4 weeks)
- Poll every 6 hours
- Medium engagement expected

### Archive Videos (> 1 month)
- Poll once daily
- Low engagement, but important for FAQ-style comments

## Response Strategy

### Auto-Response Triggers
1. **Direct Questions** about Japan/moving
2. **Business Inquiries** 
3. **Technical Questions** about equipment/process
4. **Corrections** to misinformation
5. **Thank You** messages from supporters

### Response Personalities
- **Move2Japan** (if authorized): Official channel responses
- **UnDaoDu Bot**: Helpful assistant responses

## Quota Management

### Daily Budget (10,000 units total)
- **Reading Comments**: 2,000 units (2000 videos checked)
- **Posting Replies**: 1,000 units (20 replies @ 50 each)
- **Reserve**: 7,000 units for live chat during streams

### Prioritization
1. New videos get priority
2. Popular videos (high view count) get more checks
3. Videos with many comments get deeper analysis

## Implementation Phases

### Phase 1: PoC (Week 1)
- Monitor single video
- Manual response approval
- Learn patterns

### Phase 2: Proto (Week 2)
- Monitor all new videos
- Semi-automatic responses
- Pattern recognition

### Phase 3: MVP (Month 1)
- Full channel monitoring
- Automatic responses
- Cross-video learning

## WSP Compliance
- **WSP 3**: Separate module in communication domain
- **WSP 17**: Reuse patterns from livechat
- **WSP 84**: Enhance existing youtube_auth
- **WSP 80**: Part of YouTube Cube but separate DAE

## Why Separate from LiveChat

1. **Resource Optimization**: Don't waste quota polling comments during streams
2. **Mental Model**: Comments ≠ Chat (different user expectations)
3. **Scalability**: Can run comment system 24/7 without stream
4. **Testing**: Can test comments without live stream
5. **Maintenance**: Fix comment bugs without breaking live chat

This separation follows the Unix philosophy: "Do one thing well."