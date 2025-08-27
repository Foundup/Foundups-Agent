# MAGADOOM Tracking and Tweaking Guide

## Real-Time Metrics to Track

### 1. Stream Activity Metrics
```python
# Current viewer count
viewer_count = session_manager.viewer_count  # 1-1000+ viewers

# Messages per minute
chat_velocity = chat_poller.messages_per_minute  # 0-100+ msg/min

# Stream density level
density = calculate_stream_density(viewer_count, chat_velocity)
# LOW: <50 viewers or <10 msg/min
# MEDIUM: 50-200 viewers or 10-30 msg/min  
# HIGH: 200-500 viewers or 30-60 msg/min
# EXTREME: 500+ viewers or 60+ msg/min
```

### 2. Moderation Performance
```python
# Timeout rate (actions per minute)
timeout_rate = timeouts_last_minute / 1.0  # YouTube cooldown ~1 sec

# Mod efficiency score
efficiency = (timeouts * 100) / messages_processed  

# Response time to violations
avg_response_time = sum(response_times) / len(response_times)
```

### 3. Gamification Balance
```python
# Points awarded per hour
points_per_hour = sum(recent_points) / hours_elapsed

# Daily cap usage (was 100, now 1000)
daily_cap_usage = mod_points_today / 1000.0  # 0.0 to 1.0

# Multi-whack frequency
multi_whack_rate = multi_whacks / total_whacks  # Target: 10-20%
```

## Dynamic Thresholds to Tweak

### 1. Multi-Whack Window
```python
# Current: 5 seconds (Quake-style tight timing)
MULTI_WHACK_WINDOW = 5  

# Could adjust based on stream density:
if density == "EXTREME":
    window = 3  # Tighter for high activity
elif density == "HIGH":
    window = 5  # Standard
else:
    window = 7  # More lenient for slower streams
```

### 2. Announcement Throttling
```python
# Prevent spam in high-activity streams
announcement_cooldown = {
    "LOW": 2,      # 2 sec between announcements
    "MEDIUM": 5,   # 5 sec
    "HIGH": 10,    # 10 sec  
    "EXTREME": 15  # 15 sec
}

# Priority system ensures important announcements get through:
# Priority 1: Milestones (100, 500, 1000 whacks)
# Priority 2: Multi-whacks (DOUBLE, TRIPLE, etc.)
# Priority 3: Rank ups
# Priority 4: Regular timeout announcements
```

### 3. Points Scaling
```python
# Base points by timeout duration
POINTS_MAP = {
    10: 5,      # Slap
    60: 10,     # Shotgun
    300: 20,    # Tactical nuke
    1800: 50,   # Devastator
    3600: 75,   # Mega punishment
    86400: 100  # Apocalypse
}

# Diminishing returns for repeat targets
repeat_multipliers = [
    1.0,   # First timeout
    0.75,  # Second (75%)
    0.5,   # Third (50%)
    0.25,  # Fourth+ (25%)
]

# Daily cap (increased from 100 to 1000)
DAILY_CAP = 1000  # Allows ~10 apocalypse-level actions
```

### 4. Bot Response Throttling
```python
# Chat sender adaptive delays
base_delay = 2.0  # seconds

# Adjust based on chat activity
if messages_per_minute > 50:
    delay = base_delay * 2.0  # Double delay in busy chat
elif messages_per_minute < 10:
    delay = base_delay * 0.5  # Faster in quiet chat
```

## Configuration Variables

### Environment Variables
```bash
# Set in .env or system
AGENT_GREETING_MESSAGE="WELCOME TO MAGADOOM!"
DAILY_POINT_CAP=1000
MULTI_WHACK_WINDOW=5
MIN_ANNOUNCEMENT_INTERVAL=2
```

### Database Tracked Stats
```sql
-- User profiles
user_id, score, rank, level, frag_count, last_seen

-- Timeout actions  
mod_id, target_id, duration, timestamp, points_awarded

-- Announcer stats
total_announcements, multi_whacks, milestones_reached
```

## Real-Time Adjustments

### 1. Learning from Mod Behavior
```python
# Track actual timeout frequency
actual_timeout_rate = calculate_timeout_rate()

# Adjust thresholds
if actual_timeout_rate > 1.0:  # More than 1/sec
    # Mods are very active, reduce announcement frequency
    increase_throttle_delays()
elif actual_timeout_rate < 0.1:  # Less than 1 per 10 sec
    # Quiet stream, be more responsive
    decrease_throttle_delays()
```

### 2. Stream Density Auto-Adjust
```python
def update_stream_density():
    """Called every 30 seconds"""
    current_viewers = get_viewer_count()
    current_velocity = get_message_velocity()
    
    # Smooth transitions between density levels
    if transitioning_up:
        apply_gradual_throttle_increase()
    elif transitioning_down:
        apply_gradual_throttle_decrease()
```

### 3. Anti-Abuse Detection
```python
# Detect mods gaming the system
if mod_timeouts_same_target > 5 in last_hour:
    apply_diminishing_returns()
    
if mod_points_per_minute > 100:
    flag_for_review()  # Possible abuse
```

## Monitoring Commands

### For Mods
- `/score` - Check your current XP
- `/rank` - See your rank and level
- `/whacks` - Total timeout count
- `/leaderboard` - Top fraggers

### For Admin (You)
- Monitor `memory/*.txt` files for chat activity
- Check `WSP_agentic/agentic_journals/` for bot behavior
- Review database for stats trends

## Performance Targets

1. **Response Time**: < 2 seconds to toxic content
2. **Announcement Rate**: 1-5 per minute (density dependent)
3. **Multi-Whack Rate**: 10-20% of timeouts
4. **Daily Active Mods**: Track unique mods participating
5. **Points Distribution**: Bell curve across mod team

## Future Enhancements

1. **Machine Learning**: Learn optimal thresholds from successful streams
2. **Mod Profiles**: Personalized announcements based on mod style
3. **Achievement System**: Unlock special callouts and titles
4. **Stream Events**: Special modes during raids or milestones
5. **Cross-Stream Stats**: Global leaderboard across all protected streams