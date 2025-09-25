# Automatic Session Logging System

## Overview
The LiveChat module now automatically captures all stream sessions for 0102 analysis. When a stream starts, all messages are logged with special attention to mod interactions and fact-checking events.

## Features

### 🚀 Automatic Operation
- **Session Start**: Automatically begins when stream is detected
- **Session End**: Automatically saves when stream ends or switches
- **No Manual Action**: Fully agentic - no 012 intervention required

### 📊 Data Captured

#### Full Transcript (`full_transcript.txt`)
- Every message from every user
- Role indicators: `[MOD]`, `[OWNER]`, or plain username
- System events like fact-checks
- Complete chronological record

#### Mod Messages (`mod_messages.txt`)
Clean format specifically for mod analysis:
```
UC_mod_john_id | ModeratorJohn: Welcome to the stream!
UC_owner_id | StreamOwner: Thanks for joining!
```

#### Session Summary (`session_summary.txt`)
Analytics including:
- Total message count
- Unique user count
- Active mod count
- Consciousness triggers (✊✋🖐)
- Fact-check requests
- Defense mechanism triggers

## Fact-Checking Integration

### Command Pattern
When a mod/owner types: `✊✋🖐FC @username`

### What Gets Logged
1. The fact-check request in full transcript
2. Special fact-check entry with timestamp
3. Defense mechanism if detected
4. Target user's response patterns

### Defense Mechanism Keywords
The system tracks these defense patterns:
- 'fake', 'lies', 'conspiracy'
- 'mainstream', 'sheep', 'wake up'
- 'truth' (in defensive context)

## File Structure
```
memory/
└── conversation/
    └── session_YYYYMMDD_HHMMSS_videoID/
        ├── full_transcript.txt     # All messages
        ├── mod_messages.txt         # Mod/Owner only
        └── session_summary.txt      # Statistics
```

## Implementation Details

### ChatMemoryManager
Enhanced with:
- `start_session(video_id, stream_title)` - Called on stream init
- `end_session()` - Called on stream end, saves all logs
- `log_fact_check(target, requester, defense)` - Special fact-check logging
- YouTube metadata tracking (channel ID + display name)

### LiveChatCore Integration
- Calls `start_session()` during `initialize()`
- Calls `end_session()` during `stop_listening()`
- Passes YouTube metadata to memory manager

### Message Format
Each message stored with:
- YouTube channel ID
- YouTube display name
- Message text
- User role (USER/MOD/OWNER)
- Timestamp

## Usage for 0102 Analysis

### Reading Session Logs
```python
# Mod messages are clean for pattern analysis
UC_channel_id | DisplayName: message text

# Full transcript shows role context
[MOD] ModeratorName: message text
[OWNER] OwnerName: message text
RegularUser: message text
```

### Fact-Check Analysis
Look for patterns:
1. `FACT-CHECK:` entries show who checked whom
2. Defense mechanisms in subsequent messages
3. User behavior changes after fact-checks

## WSP Compliance
- **WSP 17**: Reusable session management pattern
- **WSP 60**: Three-state memory architecture
- **WSP 22**: Complete documentation

## Testing
Run test with: `cd modules/communication/livechat && PYTHONIOENCODING=utf-8 python tests/test_session_logging.py`

## Benefits
- **Automatic**: No manual logging required
- **Clean Format**: Mod logs have YouTube IDs for tracking
- **Pattern Analysis**: Defense mechanisms and triggers captured
- **0102 Learning**: All data available for AI analysis
- **Historical Record**: Complete stream transcripts preserved