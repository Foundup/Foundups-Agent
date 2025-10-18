# Auto Meeting Orchestrator (AMO) - Interface Documentation

## Module Overview
**Module Name:** `auto_meeting_orchestrator`  
**Domain:** `communication`  
**Purpose:** Autonomous meeting orchestration with cross-platform presence detection and priority-based scheduling  
**Current Version:** v0.0.1 (PoC Phase)  

## 📋 Patent Portfolio Integration

**🔒 PATENT PROTECTION STATUS**
This module implements multiple patentable innovations documented in [PATENT_SPECIFICATION.md](PATENT_SPECIFICATION.md):

### **Core Patents:**
1. **Intent-Driven Handshake Protocol** - 7-step autonomous meeting coordination
2. **Anti-Gaming Reputation Engine** - Credibility-weighted rating system
3. **Unified Cross-Platform Presence** - Multi-platform status aggregation
4. **Autonomous Session Management** - Hands-free meeting orchestration

### **Key Technical Innovations:**
- **Bi-directional importance assessment** (not found in prior art)
- **Credibility scoring**: `(rating_variance) × (engagement_success_rate)`
- **Priority hierarchy**: `ONLINE > IDLE > BUSY > OFFLINE > UNKNOWN`
- **3-question intent validation** preventing spam and low-quality requests

**⚖️ Patent Status**: Filed under UnDaoDu patent portfolio for FoundUps ecosystem

## Core Interface

### MeetingOrchestrator Class

#### Public Methods

##### `async create_meeting_intent(requester_id, recipient_id, purpose, expected_outcome, duration_minutes, priority, preferred_time_range=None) -> str`
**Purpose:** Create a new meeting request with structured context  
**Parameters:**
- `requester_id` (str): ID of the user requesting the meeting
- `recipient_id` (str): ID of the target meeting participant  
- `purpose` (str): Clear statement of meeting purpose
- `expected_outcome` (str): What the requester hopes to achieve
- `duration_minutes` (int): Expected meeting duration
- `priority` (Priority): Meeting priority level (LOW, MEDIUM, HIGH, URGENT)
- `preferred_time_range` (Optional[Tuple[datetime, datetime]]): Preferred time window

**Returns:** `str` - Unique intent identifier  
**Example:**
```python
intent_id = await amo.create_meeting_intent(
    requester_id="alice",
    recipient_id="bob", 
    purpose="Brainstorm partnership idea",
    expected_outcome="Agreement on next steps",
    duration_minutes=30,
    priority=Priority.HIGH
)
```

##### `async update_presence(user_id, platform, status, confidence=1.0)`
**Purpose:** Update user presence status for a specific platform  
**Parameters:**
- `user_id` (str): User identifier
- `platform` (str): Platform name (e.g., "discord", "whatsapp", "zoom")
- `status` (PresenceStatus): Current presence status
- `confidence` (float): Confidence level of the presence signal (0.0-1.0)

**Example:**
```python
await amo.update_presence("alice", "discord", PresenceStatus.ONLINE, confidence=0.9)
```

##### `get_active_intents() -> List[MeetingIntent]`
**Purpose:** Retrieve all currently active meeting intents  
**Returns:** List of active MeetingIntent objects  

##### `get_user_profile(user_id) -> Optional[UnifiedAvailabilityProfile]`
**Purpose:** Get current availability profile for a user  
**Parameters:**
- `user_id` (str): User identifier  
**Returns:** UnifiedAvailabilityProfile or None if user not found

##### `get_meeting_history() -> List[Dict]`
**Purpose:** Retrieve history of completed meetings  
**Returns:** List of meeting session dictionaries

## Data Structures

### PresenceStatus (Enum)
```python
class PresenceStatus(Enum):
    ONLINE = "online"      # Actively available
    OFFLINE = "offline"    # Not available
    IDLE = "idle"         # Available but not actively engaged
    BUSY = "busy"         # Occupied, do not disturb
    UNKNOWN = "unknown"   # Status cannot be determined
```

### Priority (Enum)
```python
class Priority(Enum):
    LOW = 1      # 000-001 scale equivalent
    MEDIUM = 5   # 010-111 scale equivalent  
    HIGH = 8     # 200-222 scale equivalent
    URGENT = 10  # Emergency priority
```

### MeetingIntent (Dataclass)
```python
@dataclass
class MeetingIntent:
    requester_id: str
    recipient_id: str
    purpose: str
    expected_outcome: str
    duration_minutes: int
    priority: Priority
    preferred_time_range: Optional[Tuple[datetime, datetime]] = None
    created_at: datetime = None  # Auto-populated
```

### UnifiedAvailabilityProfile (Dataclass)
```python
@dataclass  
class UnifiedAvailabilityProfile:
    user_id: str
    platforms: Dict[str, PresenceStatus]  # Platform-specific presence
    overall_status: PresenceStatus        # Aggregated status
    last_updated: datetime
    confidence_score: float               # 0.0-1.0 confidence level
```

## Integration Patterns

### Event-Driven Architecture
- **Presence Updates:** Trigger automatic availability checks
- **Mutual Availability:** Automatically generates meeting prompts
- **Meeting Acceptance:** Launches platform-specific sessions

### Platform Integration Points
- **Discord API:** Real-time presence monitoring
- **WhatsApp Business API:** Status and messaging
- **Zoom API:** Meeting creation and participant management  
- **Google Calendar API:** Schedule management
- **LinkedIn API:** Professional networking presence

### Workflow Stages

#### PoC (v0.0.x) - Current
- ✅ Simulated presence detection
- ✅ Basic handshake protocol  
- ✅ Local intent storage
- ✅ Meeting session orchestration

#### Prototype (v0.1.x) - Next
- 🔄 Real platform API integration (2+ platforms)
- 🔄 User preference configuration
- 🔄 Persistent storage (SQLite/JSON)
- 🔄 Auto-meeting link generation

#### MVP (v1.0.x) - Future
- ⏳ Multi-user onboarding system
- ⏳ OAuth authentication flows
- ⏳ Robust failover mechanisms
- ⏳ Post-meeting AI summaries
- ⏳ Web dashboard interface

## Error Handling

### Common Exceptions
- **UserNotFound:** User ID not in system
- **PlatformError:** Platform API communication failure
- **IntentNotFound:** Meeting intent ID invalid
- **PresenceTimeout:** Presence detection timeout
- **MeetingLaunchError:** Platform meeting creation failure

### Graceful Degradation
- Platform API failures fall back to available platforms
- Presence detection failures default to UNKNOWN status
- Meeting launch failures trigger notification fallbacks

## Dependencies

### Core Dependencies
```python
asyncio          # Asynchronous operation support
datetime         # Time and date handling  
typing           # Type hints and annotations
dataclasses      # Data structure definitions
enum             # Enumeration types
logging          # System logging
```

### Future Dependencies (Prototype+)
```python
aiohttp          # Async HTTP client for API calls
sqlalchemy       # Database ORM
oauth2lib        # OAuth authentication
websockets       # Real-time communication
pydantic         # Data validation
```

## Performance Characteristics

### PoC Performance
- **Intent Creation:** < 1ms
- **Presence Update:** < 5ms  
- **Availability Check:** < 10ms
- **Meeting Launch:** < 100ms

### Expected Scaling
- **Concurrent Users:** 100+ (PoC), 10,000+ (MVP)
- **Presence Updates/sec:** 10+ (PoC), 1,000+ (MVP)
- **Meeting Sessions/hour:** 50+ (PoC), 5,000+ (MVP)

## Configuration

### Environment Variables (Future)
```env
AMO_DEBUG_MODE=false
AMO_DATABASE_URL=sqlite:///amo.db
AMO_DISCORD_TOKEN=your_discord_token
AMO_WHATSAPP_TOKEN=your_whatsapp_token
AMO_ZOOM_CLIENT_ID=your_zoom_client_id
AMO_ZOOM_CLIENT_SECRET=your_zoom_client_secret
```

### Module Configuration (Future)
```python
amo_config = {
    "presence_timeout": 300,        # 5 minutes
    "meeting_prompt_timeout": 60,   # 1 minute  
    "max_concurrent_intents": 100,
    "default_platform": "discord",
    "auto_accept_urgent": False
}
```

## Testing Interface

### Test Utilities
```python
# PoC testing helper
async def demo_amo_poc() -> MeetingOrchestrator
    """Demonstrates core PoC functionality with sample data"""

# Mock presence simulation  
await amo.update_presence("user_id", "platform", PresenceStatus.ONLINE)

# Intent creation testing
intent_id = await amo.create_meeting_intent(params...)
```

### Test Coverage Requirements
- **Unit Tests:** ≥90% code coverage
- **Integration Tests:** End-to-end workflows  
- **Performance Tests:** Load and stress testing
- **Platform Tests:** API integration verification

## Migration Path

### From PoC to Prototype
1. **Database Integration:** Replace in-memory storage
2. **API Integration:** Add real platform connectors
3. **User Management:** Add user registration/authentication
4. **Configuration:** Add environment-based configuration

### From Prototype to MVP  
1. **Multi-tenancy:** Support multiple organizations
2. **Advanced Scheduling:** Time zone support, calendar integration
3. **AI Integration:** Smart scheduling and summarization
4. **Dashboard:** Web-based management interface

---

**Module Interface Version:** v0.0.1  
**Last Updated:** $(date)  
**Next Review:** Next milestone (Prototype phase) 