# Automatic Stream Monitor & Social Media System

## Overview

The FoundUps Agent now includes a **fully automatic system** that:
1. **Monitors YouTube continuously** for new streams
2. **Detects when streams go live** 
3. **Posts notifications to X/Twitter and LinkedIn** automatically
4. **Connects to live chat** and responds to commands
5. **Handles stream ending** and quickly checks for new streams
6. **Recovers from errors** automatically

## System Components

### 1. **Auto Stream Monitor** (`auto_stream_monitor.py`)
- Continuously monitors the configured YouTube channel
- Detects new streams within 60 seconds (or 10 seconds in quick-check mode)
- Automatically posts to social media when stream detected
- Manages state to avoid duplicate posts
- Handles stream ending and enters quick-check mode

### 2. **Full Auto System** (`full_auto_system.py`)
- Complete orchestration of all components
- Initializes all modules on startup
- Manages chat bot, gamification, and commands
- Provides status monitoring
- Logs all events

### 3. **Social Media Integration**
- **X/Twitter**: Posts to @geozeAI account
- **LinkedIn**: Posts to Move2Japan account
- Includes stream title, URL, and description
- Uses anti-detection posting methods

## How It Works

### Stream Detection Flow:
```
1. Monitor checks YouTube every 60 seconds
2. Stream detected -> Get metadata (title, URL, viewers)
3. Check if already posted (avoid duplicates)
4. Post to X/Twitter with stream info
5. Post to LinkedIn with stream info
6. Start chat bot for interaction
7. Send greeting message to chat
8. Monitor until stream ends
9. Enter quick-check mode (10-second intervals)
10. Detect new stream quickly if broadcaster restarts
```

### Automatic Features:

#### [REFRESH] **Continuous Monitoring**
- Runs 24/7 without manual intervention
- Checks every 60 seconds normally
- Quick checks every 10 seconds after stream ends
- Automatically clears cache for fresh detection

#### [U+1F4E2] **Social Media Posting**
- Posts include:
  - Stream title
  - Direct YouTube URL
  - Viewer count
  - Relevant hashtags
  - Call to action

#### [U+1F4AC] **Chat Bot Integration**
- Automatically connects to live chat
- Sends greeting message
- Responds to commands (/score, /rank, etc.)
- Handles timeouts for gamification
- Tracks user interactions

#### [TOOL] **Error Recovery**
- Retries on API failures
- Switches credential sets on quota limits
- Continues with available components if some fail
- Logs all errors for debugging

## Running the System

### Method 1: Simple Auto Monitor
```bash
# Run the focused stream monitor
python auto_stream_monitor.py

# Or use the ASCII version (no emoji issues)
python auto_stream_monitor_ascii.py
```

### Method 2: Full System
```bash
# Run complete system with all features
python full_auto_system.py
```

### Method 3: Windows Batch File
```bash
# Double-click or run:
start_auto_monitor.bat
```

### Method 4: Background Service (Windows)
```bash
# Run in background (minimized)
start /min python auto_stream_monitor.py
```

## Configuration

### Required Environment Variables (.env file):
```env
# YouTube Configuration
YOUTUBE_API_KEY=your_api_key_here
CHANNEL_ID=UC-LSSlOZwpGIRIYihaz8zCw  # Move2Japan channel

# X/Twitter (optional but recommended)
X_Acc2=your_x_username
x_Acc_pass=your_x_password

# LinkedIn (optional but recommended)  
LN_Acc1=your_linkedin_email
ln_Acc_pass=your_linkedin_password

# Bot Configuration
AGENT_GREETING_MESSAGE=[BOT] UnDaoDu Bot is online! Type /help for commands
```

## System Output Example

```
[11:30:00] [START] Auto Stream Monitor Starting...
[11:30:00] [TV] Monitoring channel: UC-LSSlOZwpGIRIYihaz8zCw
[11:30:01] [OK] YouTube service initialized
[11:30:01] [OK] Stream resolver initialized
[11:30:02] [IDLE] No stream active
[11:30:02] [TIMER] Next check in 60 seconds...

[11:31:02] [NEW!] NEW STREAM DETECTED!
    Title: AI Development Live - Building Quantum Systems
    URL: https://youtube.com/watch?v=abc123
    Viewers: 42

[11:31:02] [ANNOUNCE] Posting to social media...
[11:31:03] [POST] Posting to X/Twitter...
    Content: [LIVE] LIVE NOW: AI Development Live - Building Quantum...
[11:31:04] [OK] Posted to X/Twitter successfully
[11:31:04] [POST] Posting to LinkedIn...
    Content: We're LIVE! AI Development Live - Building Quantum...
[11:31:05] [OK] Posted to LinkedIn successfully
[11:31:05] [CHAT] Starting chat monitor...
[11:31:06] [OK] Chat monitor started
[11:31:06] [WAVE] Sending greeting: UnDaoDu Bot is online!
[11:31:06] [OK] Stream handling complete
```

## Features in Detail

### 1. **State Management**
- Saves posted stream IDs to `auto_monitor_state.json`
- Prevents duplicate posts for same stream
- Cleans up old entries automatically

### 2. **Quick Check Mode**
- Activated when stream ends
- Checks every 10 seconds instead of 60
- Quickly detects if broadcaster restarts stream
- Returns to normal after 5 minutes

### 3. **Social Media Posts Include**
- Stream title (truncated if needed)
- Full YouTube URL
- Viewer count
- Custom hashtags
- Professional formatting

### 4. **Error Handling**
- API quota exceeded -> Switch credential sets
- Network timeout -> Retry after delay
- Component failure -> Continue with working parts
- All errors logged with timestamps

## Testing the System

### Quick Test:
```bash
# Run the simple test suite
python run_tests_simple.py
```

### Monitor Test:
```python
# Test stream detection without posting
from auto_stream_monitor import AutoStreamMonitor
import asyncio

async def test():
    monitor = AutoStreamMonitor()
    monitor.initialize_services()
    stream = await monitor.check_for_stream()
    if stream:
        print(f"Found: {stream['title']}")
    else:
        print("No stream active")

asyncio.run(test())
```

## Logs and Monitoring

### Log Files:
- `auto_monitor_state.json` - Tracks posted streams
- `auto_system_log.jsonl` - Event log (JSON lines format)
- Console output - Real-time status

### Status Indicators:
- `[OK]` - Success
- `[FAIL]` - Error occurred
- `[WARN]` - Warning/non-critical issue
- `[IDLE]` - No stream active
- `[LIVE]` - Stream is live
- `[NEW!]` - New stream detected

## Troubleshooting

### Common Issues:

1. **"No stream active"**
   - Normal when no stream is live
   - System will detect automatically when stream starts

2. **"YouTube API authentication failed"**
   - Check YOUTUBE_API_KEY in .env
   - Verify API key is valid and has quota

3. **"X/Twitter post failed"**
   - Check X_Acc2 and x_Acc_pass in .env
   - May need to handle 2FA manually first time

4. **"LinkedIn post failed"**
   - Check LN_Acc1 and ln_Acc_pass in .env
   - May need to handle security verification

5. **Unicode/Emoji errors**
   - Use `auto_stream_monitor_ascii.py` instead
   - Or set: `set PYTHONIOENCODING=utf-8`

## System Architecture

```
+-------------------------------------+
[U+2502]      AUTO STREAM MONITOR            [U+2502]
[U+2502]   (Runs continuously 24/7)          [U+2502]
+--------------+----------------------+
               [U+2502]
               [U+25BC]
        Check YouTube API
         Every 60 seconds
               [U+2502]
    +----------+----------+
    [U+2502]                     [U+2502]
    [U+25BC]                     [U+25BC]
No Stream            Stream Found!
(Wait 60s)                [U+2502]
                         [U+25BC]
                   Get Stream Info
                   (title, URL, etc)
                         [U+2502]
                         [U+25BC]
                Check if Already Posted
                         [U+2502]
           +-------------+------------+
           [U+2502]                          [U+2502]
           [U+25BC]                          [U+25BC]
     Already Posted              New Stream
       (Skip)                        [U+2502]
                                    [U+25BC]
                            Post to Social Media
                            +-- X/Twitter
                            +-- LinkedIn
                                    [U+2502]
                                    [U+25BC]
                            Start Chat Bot
                            +-- Send Greeting
                            +-- Process Commands
                            +-- Handle Timeouts
                                    [U+2502]
                                    [U+25BC]
                            Monitor Until End
                                    [U+2502]
                                    [U+25BC]
                            Stream Ended
                                    [U+2502]
                                    [U+25BC]
                        Quick Check Mode
                        (10 second intervals)
```

## Benefits

[OK] **Fully Automatic** - No manual intervention needed
[OK] **Fast Detection** - Finds streams within 60 seconds
[OK] **Smart Posting** - Never posts duplicates
[OK] **Error Recovery** - Handles failures gracefully
[OK] **Complete Integration** - All systems work together
[OK] **Professional Posts** - Well-formatted social media content
[OK] **Continuous Operation** - Runs 24/7 reliably

## Conclusion

The automatic system transforms the FoundUps Agent into a fully autonomous streaming assistant that:
- Monitors continuously without human intervention
- Posts professionally to multiple social platforms
- Manages live chat interactions
- Recovers from errors automatically
- Provides comprehensive logging

Just run `python auto_stream_monitor.py` and the system handles everything!