# Video Comments PoC Implementation Plan

## Phase 1: PoC (Current)
**Goal**: Prove real-time comment dialogue works

### What We've Built
1. **comment_monitor_dae.py** - Basic autonomous monitoring
2. **realtime_comment_dialogue.py** - Real-time conversation system

### PoC Testing Approach
```python
# Standalone test script to prove concept
python modules/communication/video_comments/tests/test_poc_dialogue.py
```

### Key Features to Test
- [x] Comment detection (new comments)
- [x] Reply detection (responses to our comments)
- [x] Conversation threading
- [x] Real-time monitoring (5-second intervals)
- [ ] Account switching (UnDaoDu ↔ Move2Japan)
- [ ] Memory persistence across sessions

## Phase 2: Integration (After PoC Success)
**Goal**: Integrate with main bot

### Integration Points
1. **auto_moderator_dae.py** modification:
   ```python
   # Add comment monitor as concurrent task
   self.comment_monitor = RealtimeCommentDialogue(...)
   await asyncio.gather(
       self.monitor_chat(),         # Live chat
       self.comment_monitor.start() # Comments
   )
   ```

2. **Shared resources**:
   - YouTube service instance
   - Memory manager
   - Chat engine

## Phase 3: Production (After Integration)
**Goal**: Full production deployment

### Requirements
- Credential rotation for comments
- Separate quota tracking
- Dashboard integration
- Error recovery

## Current Status: PoC Phase

### Files Created
- `src/comment_monitor_dae.py` - Basic monitoring
- `src/realtime_comment_dialogue.py` - Dialogue system
- `ARCHITECTURE.md` - System design
- `POC_IMPLEMENTATION.md` - This file

### Next Steps
1. Create PoC test script
2. Test with Move2Japan channel
3. Verify real-time dialogue works
4. Document results
5. Move to integration phase

## Testing Commands
```bash
# Test basic comment fetching
PYTHONIOENCODING=utf-8 python modules/communication/video_comments/tests/test_comment_apis.py

# Test real-time dialogue (PoC)
PYTHONIOENCODING=utf-8 python modules/communication/video_comments/tests/test_poc_dialogue.py

# Monitor for consciousness triggers in comments
PYTHONIOENCODING=utf-8 python modules/communication/video_comments/tests/test_consciousness_comments.py
```

## Success Metrics for PoC
- [ ] Can detect new comments within 15 seconds
- [ ] Can reply to comments automatically
- [ ] Can maintain conversation thread (3+ messages)
- [ ] Memory persists between messages
- [ ] No quota exhaustion (< 2000 units/hour)

## Notes
- YouTube API doesn't support comment likes (only video likes)
- Comment replies have 500 character limit
- Polling required (no webhooks/push notifications)
- Rate limits: ~50 requests/minute safe zone