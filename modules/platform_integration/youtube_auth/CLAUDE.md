# CLAUDE.md - YouTube Auth Module Memory

## Module Structure (WSP 83 Compliant)
This document helps 0102 remember YouTube authentication and quota management.

## Core Components

### YouTubeAuthManager (`src/youtube_auth.py`)
Manages 10 credential sets with automatic rotation and quota tracking.

### Key Features
- **10 Credential Sets**: oauth_token1.json through oauth_token10.json
- **Automatic Rotation**: Switches to next set when quota exceeded
- **Quota Tracking**: `memory/quota_usage.json`
- **Daily Reset**: 10,000 units per set per day (PST)
- **Exhaustion Tracking**: Marks sets as exhausted until reset

### Credential Management
```python
# Rotation order (randomized daily)
sets = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
random.shuffle(sets)
```

### Quota Costs
- `liveChatMessages.list`: 5 units per call
- `liveChatMessages.insert`: 200 units per call
- `channels.list`: 1 unit per call
- `videos.list`: 1 unit per call
- `search.list`: 100 units per call

### MonitoredYouTubeService (`src/monitored_youtube_service.py`)
Wraps YouTube API service to track quota usage per operation.

### Authorization Scripts (`scripts/`)
- `authorize_set8.py` - Authorize credential set 8
- `authorize_set9.py` - Authorize credential set 9
- `authorize_set10.py` - Authorize credential set 10
- `authorize_sets_8_9_10.py` - Batch authorization

### Integration Points
- Used by: All YouTube-facing modules
- Quota file: `memory/quota_usage.json`
- Credentials: `credentials/oauth_token*.json`

### Recent Issues Fixed
1. Sets 8, 9, 10 now properly authorized
2. Quota tracking accurate across all operations
3. Automatic exhaustion detection and rotation
4. Credential refresh on expiry

### WSP Compliance
- WSP 3: Module organization
- WSP 83: Documentation attached to tree
- WSP 84: Enhanced existing auth system

## Remember
- Daily quota: 10,000 units per set
- Reset time: Midnight PST
- Always check exhausted sets before use
- Insert operations cost 200 units each