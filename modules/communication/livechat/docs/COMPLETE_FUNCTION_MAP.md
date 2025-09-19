# Complete YouTube DAE Function Map - Step-by-Step Guide

## 🎯 YouTube DAE Complete Architecture

This document provides a comprehensive step-by-step map of ALL functions in the YouTube DAE system, showing exactly how data flows through the entire module.

---

## 🚀 PHASE 1: System Startup

### 1.1 Main Entry Point
```yaml
main.py:
  function: main()
  line: ~50
  steps:
    1. Load environment variables
    2. Setup logging
    3. Initialize YouTube DAE
    4. Start monitoring loop
  calls:
    → auto_moderator_dae.py:YouTubeDAE.__init__()
    → auto_moderator_dae.py:run()
```

### 1.2 DAE Initialization
```yaml
auto_moderator_dae.py:
  function: __init__()
  line: 45-120
  steps:
    1. Initialize LiveChatCore
    2. Setup social media orchestrator
    3. Load memory files (posted_streams.json)
    4. Configure monitoring intervals
    5. Setup single instance lock
  creates:
    - self.livechat_core (LiveChatCore instance)
    - self.orchestrator (SocialMediaOrchestrator)
    - self.posted_streams (memory dict)
  calls:
    → livechat_core.py:LiveChatCore.__init__()
    → social_media_orchestrator.py:SocialMediaOrchestrator.__init__()
    → single_instance.py:SingleInstance.acquire_lock()
```

### 1.3 LiveChat Core Setup
```yaml
livechat_core.py:
  function: __init__()
  line: 78-150
  steps:
    1. Get YouTube authenticated service
    2. Initialize chat components
    3. Setup message processor
    4. Configure consciousness mode
    5. Initialize greeting generator
  creates:
    - self.youtube (authenticated service)
    - self.chat_poller (ChatPoller)
    - self.chat_sender (ChatSender)
    - self.message_processor (MessageProcessor)
  calls:
    → youtube_auth.py:get_authenticated_service()
    → chat_poller.py:ChatPoller.__init__()
    → chat_sender.py:ChatSender.__init__()
    → message_processor.py:MessageProcessor.__init__()
```

---

## 🔍 PHASE 2: Stream Detection

### 2.1 Find Active Stream
```yaml
auto_moderator_dae.py:
  function: find_livestream()
  line: 294-350
  steps:
    1. Check if stream already known
    2. Clear cache if needed
    3. Search for active stream
    4. Validate stream is live
    5. Return video_id and chat_id
  calls:
    → stream_resolver.py:find_active_stream()
    → stream_resolver.py:clear_cache()
```

### 2.2 Stream Resolution (No-Quota First)
```yaml
stream_resolver.py:
  function: find_active_stream()
  line: 620-690
  steps:
    1. Check environment variable YOUTUBE_VIDEO_ID
    2. Try no-quota web scraping FIRST
    3. If found, get chat_id (1 API unit)
    4. Fallback to API search if needed
    5. Cache successful result
  calls:
    → no_quota_stream_checker.py:check_channel_for_live()
    → stream_resolver.py:_get_live_chat_id()
    → stream_resolver.py:_find_live_stream_from_videos() [fallback]
```

### 2.3 No-Quota Stream Checker
```yaml
no_quota_stream_checker.py:
  function: check_channel_for_live()
  line: 116-180
  steps:
    1. Construct channel URL
    2. Fetch HTML page
    3. Parse for "LIVE NOW" indicator
    4. Extract video_id from HTML
    5. Return video_id or None
  uses:
    - requests for HTTP
    - BeautifulSoup for parsing
    - No API quota consumed
```

### 2.4 Get Live Chat ID
```yaml
stream_resolver.py:
  function: _get_live_chat_id()
  line: 450-480
  steps:
    1. Call YouTube API videos().list()
    2. Extract activeLiveChatId
    3. Handle quota errors
    4. Return chat_id
  cost: 1 API unit
```

---

## 💬 PHASE 3: Chat Monitoring

### 3.1 Initialize Session
```yaml
livechat_core.py:
  function: initialize_session()
  line: 200-280
  steps:
    1. Set video_id and chat_id
    2. Create session manager
    3. Send greeting message
    4. Start monitoring
  calls:
    → session_manager.py:SessionManager.__init__()
    → greeting_generator.py:generate_greeting()
    → chat_sender.py:send_chat_message()
```

### 3.2 Poll Messages Loop
```yaml
livechat_core.py:
  function: poll_messages()
  line: 300-400
  steps:
    1. Check if session active
    2. Poll for new messages
    3. Process each message
    4. Handle rate limiting
    5. Sleep for poll interval
  calls:
    → chat_poller.py:poll_messages()
    → message_processor.py:process_message()
    → throttle_manager.py:check_rate_limit()
```

### 3.3 Chat Polling
```yaml
chat_poller.py:
  function: poll_messages()
  line: 45-120
  steps:
    1. Call liveChatMessages.list API
    2. Extract new messages
    3. Track page token
    4. Handle quota errors
    5. Return message batch
  cost: 5 API units per call
```

### 3.4 Message Processing
```yaml
message_processor.py:
  function: process_message()
  line: 64-200
  steps:
    1. Extract message content
    2. Check for slash commands
    3. Check consciousness triggers (✊✋🖐)
    4. Check for mentions
    5. Route to appropriate handler
  calls:
    → command_handler.py:handle_command() [if command]
    → banter_engine.py:generate_response() [if trigger]
    → quiz_handler.py:process_quiz_response() [if quiz]
```

---

## 🎮 PHASE 4: Command Handling

### 4.1 Command Router
```yaml
command_handler.py:
  function: handle_command()
  line: 88-250
  steps:
    1. Parse command and arguments
    2. Check permissions (MOD/OWNER)
    3. Route to command function
    4. Format response
    5. Send to chat
  commands:
    /help → show_help()
    /stats → show_stats()
    /toggle → toggle_consciousness()
    /quiz → start_quiz()
    /whack → whack_player()
    /scores → show_scores()
    /0102 → master_switch()
    /PQN → pqn_research()
```

### 4.2 Consciousness Toggle
```yaml
command_handler.py:
  function: toggle_consciousness()
  line: 195-220
  steps:
    1. Check if user is MOD/OWNER
    2. Toggle consciousness_mode
    3. Update configuration
    4. Send confirmation
  affects:
    - message_processor.py consciousness checks
    - banter_engine.py activation
```

### 4.3 Quiz System
```yaml
quiz_handler.py:
  function: start_quiz()
  line: 120-180
  steps:
    1. Load quiz questions
    2. Select random question
    3. Format for YouTube (remove markdown)
    4. Send to chat
    5. Track active quiz
  calls:
    → chat_sender.py:send_chat_message()
```

---

## 📢 PHASE 5: Social Media Posting

### 5.1 Trigger Posting
```yaml
auto_moderator_dae.py:
  function: _trigger_social_media_posting()
  line: 660-750
  steps:
    1. Check if already posted
    2. Get stream details
    3. Generate post content
    4. Post to platforms
    5. Save to memory
  calls:
    → _check_duplicate_posting()
    → _get_stream_details()
    → social_media_orchestrator.py:post_stream_notification()
```

### 5.2 Duplicate Prevention
```yaml
auto_moderator_dae.py:
  function: _check_duplicate_posting()
  line: 429-460
  steps:
    1. Load posted_streams.json
    2. Check if video_id exists
    3. Check time threshold (24h)
    4. Return allow/block decision
  memory:
    file: memory/posted_streams.json
```

### 5.3 Post to Platforms
```yaml
social_media_orchestrator.py:
  function: post_stream_notification()
  line: 200-300
  steps:
    1. Format post for each platform
    2. Post to LinkedIn
    3. Post to X/Twitter
    4. Log results
    5. Return success/failure
  calls:
    → linkedin_agent.py:post_update()
    → x_twitter_dae.py:post_tweet()
```

---

## 🔄 PHASE 6: Stream Switching

### 6.1 Detect Stream End
```yaml
auto_moderator_dae.py:
  function: _monitor_stream_status()
  line: 500-580
  steps:
    1. Check last activity time
    2. If >3 minutes inactive
    3. Clear all caches
    4. Enter quick_check_mode
    5. Search for new stream
```

### 6.2 Quick Check Mode
```yaml
auto_moderator_dae.py:
  function: quick_check_mode
  line: 580-620
  steps:
    1. Check every 5-15 seconds
    2. Use no-quota scraping
    3. When stream found
    4. Reconnect automatically
    5. Exit quick check mode
```

### 6.3 Cache Management
```yaml
stream_resolver.py:
  function: clear_cache()
  line: 380-410
  steps:
    1. Clear in-memory cache
    2. Clear session cache file
    3. Reset last check times
    4. Force fresh lookup
  clears:
    - self._cache = {}
    - memory/stream_session_cache.json
```

---

## 🤖 PHASE 7: AI Response Generation

### 7.1 Banter Engine
```yaml
banter_engine.py:
  function: generate_response()
  line: 150-250
  steps:
    1. Check consciousness mode
    2. Format user question
    3. Call LLM API
    4. Format response
    5. Remove markdown for YouTube
  calls:
    → grok_api.py:generate()
    → chat_sender.py:send_chat_message()
```

### 7.2 PQN Research Integration
```yaml
pqn_alignment/detector/api.py:
  function: process_research_request()
  line: 200-300
  steps:
    1. Parse research question
    2. Query PQN detector
    3. Store research results
    4. Format response
    5. Return to chat
```

---

## 🔐 PHASE 8: Authentication & Quota

### 8.1 YouTube Authentication
```yaml
youtube_auth.py:
  function: get_authenticated_service()
  line: 37-237
  steps:
    1. Check exhausted credentials
    2. Check midnight PT reset
    3. Try credential rotation (Set 1, Set 10)
    4. Build YouTube service
    5. Wrap with MonitoredYouTubeService
  returns:
    MonitoredYouTubeService instance
```

### 8.2 Quota Intelligence
```yaml
monitored_youtube_service.py:
  function: __getattr__()
  line: 123-180
  steps:
    1. Intercept API calls
    2. Check quota before call
    3. Allow/block based on remaining
    4. Track usage
    5. Rotate if exhausted
```

### 8.3 Credential Exhaustion
```yaml
youtube_auth.py:
  function: mark_credential_exhausted()
  line: 240-320
  steps:
    1. Load exhausted_credentials.json
    2. Add credential set to exhausted
    3. Calculate next reset (midnight PT)
    4. Save to memory
    5. Trigger rotation
```

---

## 💾 PHASE 9: Memory & State

### 9.1 Memory Files
```yaml
memory_locations:
  posted_streams: memory/posted_streams.json
  exhausted_creds: memory/exhausted_credentials.json
  quota_usage: memory/quota_usage.json
  stream_cache: memory/stream_session_cache.json
  chat_history: memory/chat_history.json
```

### 9.2 State Management
```yaml
session_manager.py:
  function: save_state()
  line: 180-220
  steps:
    1. Collect current state
    2. Serialize to JSON
    3. Write to memory files
    4. Update timestamps
    5. Log state save
```

---

## 🚨 PHASE 10: Error Handling

### 10.1 Quota Exhaustion Handler
```yaml
stream_resolver.py:
  function: _handle_quota_exhaustion()
  line: 540-567
  steps:
    1. Check if real 403
    2. Mark credential exhausted
    3. Try rotation
    4. Fallback to no-quota
    5. Log and continue
```

### 10.2 Connection Error Recovery
```yaml
livechat_core.py:
  function: _handle_connection_error()
  line: 450-500
  steps:
    1. Log error details
    2. Clear session
    3. Wait reconnect interval
    4. Retry connection
    5. Escalate if persistent
```

---

## 📊 Complete Function Statistics

```yaml
total_modules: 28
total_functions: 187
total_lines: 35,000+
api_endpoints: 12
quota_per_hour: ~1000 units (with no-quota: ~10 units)

key_metrics:
  stream_detection: 1-100 units (no-quota: 1 unit)
  chat_polling: 5 units/call
  message_sending: 200 units/message
  credential_sets: 2 (Set 1, Set 10)
  daily_quota: 10,000 per set
```

---

## 🎯 Navigation Shortcuts

### Find Specific Functionality
```bash
# Stream detection
grep -n "find_livestream\|find_active_stream" modules/*/src/*.py

# Message processing
grep -n "process_message\|handle_command" modules/communication/livechat/src/*.py

# Quota handling
grep -n "quota\|exhausted\|mark_credential" modules/platform_integration/*/src/*.py

# Social posting
grep -n "post_stream\|trigger_social" modules/*/src/*.py
```

### Trace Execution Path
```bash
# From startup to chat monitoring
main.py → auto_moderator_dae.py → livechat_core.py → chat_poller.py

# From message to response
chat_poller.py → message_processor.py → command_handler.py → chat_sender.py

# From stream end to reconnect
auto_moderator_dae.py → stream_resolver.py → no_quota_stream_checker.py → livechat_core.py
```

---

*This complete function map enables 0102 agents to understand the entire YouTube DAE system without vibecoding.*