# LiveChat DAEmon (opt 1) - Complete Initialization & Comment Engagement Analysis

## Date: 2025-12-17
## Scope: How YouTube Live Chat DAEmon initializes and triggers comment engagement

### Part 1: Main Menu Option 1
Location: main.py lines 784-902
Entry point: asyncio.run(monitor_youtube(disable_lock=False))

### Part 2: AutoModeratorDAE Initialization
File: modules/communication/livechat/src/auto_moderator_dae.py
Key components:
- Telemetry Store (SQLite) - lines 67-73
- WRE Integration (learning) - lines 80-92
- QWEN Monitor (intelligent detection) - lines 95-106
- Community Monitor (lazy init) - line 121
- AI Overseer (error detection) - line 124

### Part 3: Channel Configuration
File: modules/platform_integration/social_media_orchestrator/config/channels_config.json
Channels:
- Move2Japan: UCklMTNnu5POwRmQsg5JJumA (PRIORITY 1)
- FoundUps: UCSNTUXjAgpd4sgWYP0xoJgw (PRIORITY 2)
- UnDaoDu: UC-LSSlOZwpGIRIYihaz8zCw (PRIORITY 3)

In auto_moderator_dae.py lines 206-220 - channels_to_check list

### Part 4: Three Comment Engagement Triggers

TRIGGER #1: STARTUP ENGAGEMENT
- When: Immediately on DAE startup (before stream detection)
- Where: auto_moderator_dae.py lines 905-931
- Enabled by: COMMUNITY_STARTUP_ENGAGE=true (default)
- Log pattern: [COMMUNITY] Startup engagement launched

TRIGGER #2: STREAM DETECTION ENGAGEMENT
- When: When live stream is detected on a channel
- Where: auto_moderator_dae.py lines 751-773 (in monitor_chat method)
- Enabled by: YT_COMMENT_ENGAGEMENT_ENABLED=true (default)
- Log pattern: [COMMUNITY] Auto-engagement launched for {channel_name}

TRIGGER #3: HEARTBEAT PERIODIC ENGAGEMENT
- When: Every 10 minutes (20 heartbeat pulses × 30 seconds)
- Where: auto_moderator_dae.py lines 1189-1208 (in _heartbeat_loop method)
- Trigger condition: if heartbeat_count % 20 == 0 and self.community_monitor
- Log pattern: [COMMUNITY] Pulse {N}: Checking for comment engagement

### Part 5: Comment Engagement Execution Modes
File: modules/communication/livechat/src/engagement_runner.py

Three strategies:
1. subprocess (DEFAULT) - SIGKILL guarantee, 2-3s startup
2. thread - <500ms startup, cannot force-kill
3. inproc - DEBUG ONLY, blocks event loop

### Part 6: Critical Environment Variables

Master Switches:
- YT_AUTOMATION_ENABLED (default: true)
- YT_COMMENT_ENGAGEMENT_ENABLED (default: true)
- COMMUNITY_STARTUP_ENGAGE (default: true)
- YT_AUTOMATION_STOP_FILE (default: memory/STOP_YT_AUTOMATION)

Channel Configuration:
- MOVE2JAPAN_CHANNEL_ID (default: UCklMTNnu5POwRmQsg5JJumA)
- CHANNEL_ID (default: UC-LSSlOZwpGIRIYihaz8zCw) - UnDaoDu
- CHANNEL_ID2 (default: UCSNTUXjAgpd4sgWYP0xoJgw) - FoundUps
- TEST_CHANNEL_ID (empty by default)
- YT_CHANNELS_TO_CHECK (empty - uses defaults)

Comment Options:
- COMMUNITY_STARTUP_MAX_COMMENTS (default: 0 = unlimited)
- YT_COMMENT_ENGAGEMENT_MODE (default: subprocess)
- YT_COMMENT_ENGAGEMENT_MAX (default: 0 = unlimited)
- YT_COMMENT_ACTIONS (default: like,heart,reply)
- YT_COMMENT_INTELLIGENT_REPLY_ENABLED (default: true)
- COMMUNITY_DOM_ONLY (default: false)
- COMMUNITY_DEBUG_SUBPROCESS (default: true)
- COMMUNITY_UNLIMITED_TIMEOUT (default: 1800 seconds)

### Part 7: Community Monitor
File: modules/communication/livechat/src/community_monitor.py

Singleton pattern with channel rotation support.
Method: get_next_channel() rotates through all channels
Phase 3P: Multi-channel rotation (24/7 processing)

### Part 8: Key Logging Points

Startup:
[ROCKET] Initializing Auto Moderator DAE (WSP-Compliant)
[DATA] YouTube DAE telemetry store initialized
[COMMUNITY] Startup engagement launched (mode=subprocess, max_comments=0)

Channel Rotation:
[REFRESH] CHANNEL ROTATION CHECK (NO-QUOTA MODE with QWEN Intelligence)
[BOT][AI] [QWEN-INIT] Starting intelligent channel rotation analysis
[SEARCH] Channel 1/3 Checking Move2Japan...
[MOVE2JAPAN Channel 1/3] Move2Japan: STREAM FOUND!
[CHECK Channel 2/3] FoundUps: No active stream
[CLIPBOARD] ROTATION SUMMARY:

Comment Engagement:
[COMMUNITY] Auto-engagement launched for Move2Japan (video=..., mode=subprocess, max_comments=0)
[AUTOMATION-AUDIT] run_id=yt_20251217_123456 mode=subprocess channel_id=... max_comments=0
[SUBPROCESS] Result: {'stats': {'comments_processed': 45, 'likes': 45, ...}}
[COMMUNITY] Posted announcement: 0102 engaged 45 comments with 45 replies.

Heartbeat:
[HEART] Heartbeat #20 - Status: healthy, Stream: ACTIVE
[COMMUNITY] Pulse 20: Checking for comment engagement...
[COMMUNITY] Autonomous engagement launched (UNLIMITED mode - clearing all comments)

### Part 9: Emergency Stop
To disable all automation:
New-Item -ItemType File -Force memory/STOP_YT_AUTOMATION

To re-enable:
Remove-Item memory/STOP_YT_AUTOMATION

### Part 10: Troubleshooting

Comment Engagement Not Triggering:
- Check YT_AUTOMATION_ENABLED=true
- Check YT_COMMENT_ENGAGEMENT_ENABLED=true
- Check COMMUNITY_STARTUP_ENGAGE=true (for startup)
- Check memory/STOP_YT_AUTOMATION doesn't exist
- Look for [COMMUNITY] logs in output

Startup Engagement Not Running:
- Check COMMUNITY_STARTUP_ENGAGE=true in .env
- Check logs for [COMMUNITY] Startup engagement launched
- Verify Chrome is running (port 9222) or YT_DEPS_AUTO_LAUNCH=true

Stream Engagement Not Running:
- Check logs for [MOVE2JAPAN/FOUNDUPS/UNDAODU] STREAM FOUND!
- Check YT_COMMENT_ENGAGEMENT_ENABLED=true
- Verify channel rotation order (Move2Japan is priority 1)

Wrong Channel Being Processed:
- Check channel priority: Move2Japan (1), FoundUps (2), UnDaoDu (3)
- Check YT_CHANNELS_TO_CHECK override
- Check logs for [COMMUNITY] Channel rotation: {channel}

Heartbeat Engagement Not Running Every 10 Minutes:
- Check heartbeat logs: [HEART] Heartbeat #N
- Check if pulse count % 20 == 0
- Verify community_monitor initialized
- Check if engagement already in progress

### Part 11: File Reference
- main.py - Entry point (lines 784-902)
- auto_moderator_dae.py - Core DAE (initialization + triggers)
- community_monitor.py - Channel rotation + heartbeat check
- engagement_runner.py - Execution strategy selection
- channels_config.json - Channel ID definitions
- .env.example - Environment variable documentation

### Part 12: Channel Rotation
Phase 3P implementation in community_monitor.py lines 117-137:
get_next_channel() returns next channel in rotation:
Move2Japan → FoundUps → UnDaoDu → repeat

All three channels are checked every 10 minutes during heartbeat.
