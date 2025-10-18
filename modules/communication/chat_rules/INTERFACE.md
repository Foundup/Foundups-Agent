# Chat Rules Module Interface

## Overview
WSP-compliant modular chat rules system for YouTube Live Chat with gamified moderation.

## Public API

### ChatRulesEngine
Main orchestrator for processing chat messages and generating responses.

```python
from modules.communication.chat_rules.src.chat_rules_engine import ChatRulesEngine

engine = ChatRulesEngine()
response = engine.process_message(youtube_message_dict)
```

### UserClassifier
Classifies users into tiers based on YouTube API data.

```python
from modules.communication.chat_rules.src.user_classifier import UserClassifier, UserProfile

profile = UserClassifier.classify(author_details)
# Returns UserProfile with tier, permissions, and capabilities
```

### WhackAMAGAtSystem
Gamified moderation point tracking system with leaderboards.

```python
from modules.communication.chat_rules.src.whack_a_magat import WhackAMAGAtSystem

system = WhackAMAGAtSystem()

# Record timeout with anti-gaming mechanics
result = system.record_timeout(
    mod_id="mod123",
    mod_name="ModName",
    target_id="user456",
    target_name="UserName",
    duration_seconds=60,
    reason="Spam"
)

# Get leaderboard
leaderboard = system.get_leaderboard(limit=10)

# Get moderator score
score = system.get_stats("mod123")
```

### CommandProcessor
Handles slash commands for members and moderators.

```python
from modules.communication.chat_rules.src.commands import CommandProcessor

processor = CommandProcessor()
response = processor.process("/leaders", user_profile)
```

### MembershipManager
Manages YouTube's 6-tier membership system.

```python
from modules.communication.chat_rules.src.membership_manager import MembershipManager

manager = MembershipManager(youtube_service)
levels = manager.fetch_membership_levels()
tier = manager.classify_member_tier(member_data)
```

## Database Interface

### ChatRulesDB (SQLite Implementation)
```python
from modules.communication.chat_rules.src.database import ChatRulesDB

db = ChatRulesDB()

# Moderator operations
mod = db.get_or_create_moderator("mod123", "ModName")
db.update_moderator_points("mod123", 500, "GOLD")

# Timeout tracking
db.record_timeout(mod_id, target_id, target_name, duration, points, reason)

# Anti-gaming checks
is_gaming = db.get_recent_timeout_target(mod_id, target_id, minutes=30)
spam_count = db.get_recent_10s_timeouts(mod_id, minutes=10)

# Cooldown management
db.set_cooldown(mod_id, "severity_3", minutes=15)
remaining = db.check_cooldown(mod_id, "severity_3")

# Leaderboard
top_10 = db.get_leaderboard(limit=10)
```

## Message Format

### Input (YouTube Live Chat Message)
```python
message = {
    'authorDetails': {
        'channelId': 'UC...',
        'displayName': 'Username',
        'isChatOwner': False,
        'isChatModerator': False,
        'isChatSponsor': True,  # Has membership
        'isVerified': False
    },
    'snippet': {
        'type': 'textMessageEvent',
        'textMessageDetails': {
            'messageText': 'Message content'
        }
    }
}
```

### Output (Bot Response)
```python
# String response or None
response = "[U+1F528] TIMEOUT! ModName -> TrollUser (Standard timeout)\n⏱️ Duration: 60s | Points: 15"
```

## Commands

### Member Commands (Tier 1-6)
- `/ask <question>` - Ask AI agent
- `/level` - Check consciousness level
- `/stats` - View personal stats
- `/vibe` - Check stream vibe
- `/gift @user` - Gift membership

### Moderator Commands
- `/leaders` - Top 3 leaderboard
- `/fullboard` - Top 10 leaderboard
- `/score` - Detailed score breakdown
- `/whack @user [duration] [reason]` - Timeout user
- `/daily` - Claim daily bonus

### Owner Commands
- `/reset confirm` - Reset point system
- `/award @mod <points> [reason]` - Award points

## User Types

### Classification Hierarchy
1. **OWNER** - Channel owner (all permissions)
2. **MODERATOR** - Channel moderators (timeout powers)
3. **MEMBER_TIER_6** - Ultimate supporters ($49.99/mo)
4. **MEMBER_TIER_5** - Elite members ($19.99/mo)
5. **MEMBER_TIER_4** - Premium members ($9.99/mo)
6. **MEMBER_TIER_3** - Advanced members ($4.99/mo)
7. **MEMBER_TIER_2** - Standard members ($1.99/mo)
8. **MEMBER_TIER_1** - Basic members ($0.99/mo)
9. **VERIFIED** - Verified accounts
10. **REGULAR** - Normal viewers
11. **BANNED/TROLL** - Restricted users

## Point System

### Timeout Points (with Anti-Gaming)
- **10 sec**: 5 pts (2m cooldown)
- **60 sec**: 15 pts (5m cooldown)
- **5 min**: 30 pts (15m cooldown)
- **10 min**: 50 pts (30m cooldown)
- **1 hour**: 100 pts (2hr cooldown)
- **24 hour**: 250 pts (24hr cooldown)

### Anti-Gaming Mechanics
- Same user within 30 min: 50% penalty
- Same severity on cooldown: 70% penalty
- >5 10-sec timeouts in 10 min: 80% penalty
- >50 timeouts per day: 90% penalty

## Integration Example

```python
from modules.communication.chat_rules.src.chat_rules_engine import ChatRulesEngine

# Initialize engine
engine = ChatRulesEngine()

# Process YouTube Live Chat message
def on_chat_message(message):
    # Process through rules engine
    response = engine.process_message(message)
    
    if response:
        # Send response back to YouTube
        send_to_youtube_chat(response)
```

## Dependencies
- Python 3.8+
- sqlite3 (built-in)
- json (built-in)
- datetime (built-in)
- enum (built-in)
- dataclasses (built-in)

## WSP Compliance
- Follows WSP 49 (Module Directory Structure)
- Implements WSP 78 (Database Architecture)
- Adheres to WSP 3 (Rubik's Cube Modularization)