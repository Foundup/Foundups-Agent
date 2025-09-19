# CLAUDE.md - YouTube Auth Module Memory

## Module Structure (WSP 83 Compliant)
This document helps 0102 remember YouTube authentication and quota management.

## Core Components

### YouTubeAuthManager (`src/youtube_auth.py`)
Manages 2 credential sets (UnDaoDu and Foundups) with automatic rotation and quota tracking.

### Key Features
- **2 Credential Sets**: Set 1 (UnDaoDu) and Set 10 (Foundups)
- **Automatic Rotation**: Switches between the 2 sets when quota exceeded
- **Quota Tracking**: `memory/quota_usage.json`
- **Daily Reset**: 10,000 units per set per day (PST)
- **Exhaustion Tracking**: Marks sets as exhausted until reset

### Credential Management
```python
# Only 2 credential sets configured:
# Set 1: UnDaoDu (oauth_token.json)
# Set 10: Foundups (oauth_token10.json)
sets = [1, 10]
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
- `authorize_set1.py` - Authorize credential set 1 (UnDaoDu)
- `authorize_set10.py` - Authorize credential set 10 (Foundups)
- `authorize_all_sets.py` - Batch authorization for both sets

### Integration Points
- Used by: All YouTube-facing modules
- Quota file: `memory/quota_usage.json`
- Credentials: `credentials/oauth_token*.json`

### Recent Issues Fixed
1. Reduced from 10 sets to 2 active sets (1=UnDaoDu, 10=Foundups)
2. Quota tracking accurate across both sets
3. Automatic exhaustion detection and rotation between the 2 sets
4. Credential refresh on expiry
5. Set 1 token expired - needs re-authorization

### WSP Compliance
- WSP 3: Module organization
- WSP 83: Documentation attached to tree
- WSP 84: Enhanced existing auth system

## Remember
- Daily quota: 10,000 units per set
- Reset time: Midnight PST
- Always check exhausted sets before use
- Insert operations cost 200 units each