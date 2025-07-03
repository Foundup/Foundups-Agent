# Presence Aggregator Module

**Cross-Platform Presence Detection and Normalization**

Part of the Autonomous Meeting Orchestrator (AMO) ecosystem. Normalizes and streams presence data from Discord, WhatsApp, LinkedIn, Zoom, Teams, and Slack for intelligent meeting coordination.

## 🎯 Purpose

Aggregates real-time presence information across multiple communication platforms to enable:
- Unified availability detection for meeting participants
- Cross-platform presence normalization and prioritization
- Real-time presence change notifications
- Intelligent availability-based meeting suggestions

## 🚀 Quick Start

```python
from modules.integration.presence_aggregator import PresenceAggregator, Platform

# Initialize aggregator
aggregator = PresenceAggregator()

# Initialize platforms
await aggregator.initialize_platform(Platform.DISCORD, {"token": "..."})
await aggregator.initialize_platform(Platform.WHATSAPP, {"credentials": "..."})

# Start monitoring
await aggregator.start_monitoring([Platform.DISCORD, Platform.WHATSAPP])

# Check user availability
availability = await aggregator.are_users_available(["alice", "bob"])
print(f"Alice available: {availability['alice']}")

# Get aggregated status
alice_status = await aggregator.get_aggregated_presence("alice")
print(f"Alice's status: {alice_status}")
```

## 🏗️ Architecture

### Core Components

#### PresenceAggregator
Main orchestrator that manages presence data across platforms.

**Key Methods:**
- `initialize_platform()`: Connect to platform APIs
- `get_user_presence()`: Retrieve presence data for user
- `get_aggregated_presence()`: Get unified status across platforms
- `are_users_available()`: Batch availability checking
- `start_monitoring()`: Begin real-time presence polling

#### PresenceData
Normalized presence information structure.

**Fields:**
- `user_id`: Unique user identifier
- `platform`: Source platform (Discord, WhatsApp, etc.)
- `status`: Normalized status (online, idle, busy, away, offline)
- `last_seen`: Last activity timestamp
- `activity`: Current activity description
- `custom_message`: User's custom status message

#### Platform Support

| Platform | Status | PoC | Prototype | MVP |
|----------|--------|-----|-----------|-----|
| Discord | 🟡 Simulated | ✅ | 🔄 Live API | 🔄 Full Integration |
| WhatsApp | 🟡 Simulated | ✅ | 🔄 Live API | 🔄 Full Integration |
| LinkedIn | 🟡 Simulated | ✅ | 🔄 Live API | 🔄 Full Integration |
| Zoom | 🟡 Simulated | ✅ | 🔄 Live API | 🔄 Full Integration |
| Teams | 🟡 Simulated | ✅ | 🔄 Live API | 🔄 Full Integration |
| Slack | 🟡 Simulated | ✅ | 🔄 Live API | 🔄 Full Integration |

## 📊 Presence Status Normalization

### Status Priority (Aggregation Logic)
1. **ONLINE** (5) - Available and active
2. **IDLE** (4) - Available but inactive  
3. **BUSY** (3) - Available but in meeting/busy
4. **AWAY** (2) - Temporarily away
5. **OFFLINE** (1) - Not available
6. **UNKNOWN** (0) - Status could not be determined

### Platform Mapping

| Platform | Native Status | Normalized |
|----------|---------------|------------|
| Discord | online, idle, dnd, offline | online, idle, busy, offline |
| WhatsApp | online, last seen X ago | online, away |
| LinkedIn | active, away | online, away |
| Zoom | available, busy, away | online, busy, away |
| Teams | available, busy, away, offline | online, busy, away, offline |
| Slack | active, away, dnd | online, away, busy |

## 🔄 Real-Time Monitoring

### Polling Strategy
- **Interval**: 30 seconds (configurable)
- **Cache TTL**: 5 minutes
- **Error Handling**: Exponential backoff with circuit breaker
- **Rate Limiting**: Platform-specific API limits respected

### Change Notifications
```python
# Register for presence change events
async def on_presence_change(user_id, platform, presence_data):
    print(f"{user_id} on {platform} is now {presence_data.status}")

await aggregator.add_presence_listener(on_presence_change)
```

## 🧪 Testing

### Run Tests
```bash
cd modules/integration/presence_aggregator/
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Demo Mode
```bash
cd src/
python presence_aggregator.py
```

## 📈 Milestone Definitions

### Proof of Concept (PoC) ✅
**Objective**: Simulate presence detection across platforms
- ✅ Simulated presence data for test users
- ✅ Cross-platform status aggregation
- ✅ Basic availability checking
- ✅ Real-time monitoring simulation
- ✅ ≥80% test coverage

**Success Criterion**: Demo shows 2 users with different statuses across platforms

### Prototype 🔄
**Objective**: Integrate real platform APIs
- 🔄 Discord API integration with OAuth
- 🔄 WhatsApp Business API integration  
- 🔄 LinkedIn API presence detection
- 🔄 Zoom SDK integration
- 🔄 SQLite persistence layer
- 🔄 Configurable polling intervals

**Success Criterion**: Real presence data from ≥2 platforms

### MVP 🔮
**Objective**: Production-ready multi-platform monitoring
- 🔮 All 6 platforms integrated
- 🔮 OAuth flow management
- 🔮 WebSocket real-time updates
- 🔮 User preference management
- 🔮 Advanced caching and optimization
- 🔮 Comprehensive error handling and retry logic

**Success Criterion**: 24/7 monitoring for 100+ users across all platforms

## 🔧 Configuration

### Environment Variables
```bash
# Platform API credentials
DISCORD_BOT_TOKEN=your_discord_token
WHATSAPP_API_KEY=your_whatsapp_key
LINKEDIN_CLIENT_ID=your_linkedin_id
ZOOM_SDK_KEY=your_zoom_key

# Monitoring settings
PRESENCE_POLL_INTERVAL=30
PRESENCE_CACHE_TTL=300
PRESENCE_MAX_RETRIES=3
```

### Platform Credentials Structure
```python
# Discord
discord_creds = {
    "bot_token": "your_bot_token",
    "guild_id": "your_server_id"
}

# WhatsApp Business
whatsapp_creds = {
    "api_key": "your_api_key",
    "phone_number_id": "your_phone_id"
}

# LinkedIn
linkedin_creds = {
    "client_id": "your_client_id", 
    "client_secret": "your_client_secret",
    "access_token": "user_access_token"
}
```

## 🔗 Integration Points

### AMO Ecosystem Integration
- **Intent Manager**: Receives availability data for meeting scheduling
- **0102 Orchestrator**: Provides presence context for conversation
- **Channel Selector**: Uses presence data for optimal platform selection
- **Audit Logger**: Logs presence changes for transparency

### Data Flow
```
Platform APIs → PresenceAggregator → AMO Modules
     ↓              ↓                    ↓
Real-time Data → Normalized Cache → Meeting Decisions
```

## 📝 API Reference

### Core Methods

```python
class PresenceAggregator:
    async def initialize_platform(platform: Platform, credentials: Dict) -> bool
    async def get_user_presence(user_id: str, platform: Platform = None) -> Dict[Platform, PresenceData]
    async def get_aggregated_presence(user_id: str) -> PresenceStatus
    async def are_users_available(user_ids: List[str]) -> Dict[str, bool]
    async def start_monitoring(platforms: List[Platform]) -> None
    async def stop_monitoring() -> None
    async def add_presence_listener(callback: Callable) -> None
    async def get_presence_statistics() -> Dict[str, Any]
```

### Data Structures

```python
@dataclass
class PresenceData:
    user_id: str
    platform: Platform
    status: PresenceStatus
    last_seen: datetime
    last_updated: datetime
    raw_status: Optional[str] = None
    activity: Optional[str] = None
    custom_message: Optional[str] = None
```

## 📊 Performance Metrics

### Target Performance
- **API Response Time**: <500ms per platform
- **Cache Hit Rate**: >95%
- **Monitoring Latency**: <60 seconds for status changes
- **Memory Usage**: <100MB for 1000 users

### Monitoring
- Platform API health and response times
- Cache effectiveness and hit rates
- Error rates and retry patterns
- User availability pattern analysis

## 🔐 Security & Privacy

### Data Protection
- No persistent storage of sensitive presence data
- Platform credentials encrypted at rest
- Rate limiting to prevent API abuse
- User consent for presence monitoring

### Privacy Considerations
- Users can opt-out of presence monitoring
- Anonymized analytics only
- Platform-specific privacy settings respected
- GDPR compliance for EU users

---

**Module**: Presence Aggregator  
**Version**: 0.0.1  
**Domain**: integration  
**WSP Compliance**: ✅ Fully compliant  
**Maintainer**: AMO Development Team 