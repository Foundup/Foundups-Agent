# AMO Strategic Modular Decomposition Plan

**From Monolithic PoC to Distributed Ecosystem Architecture**

## [TARGET] Current State (v0.0.1)
**Status:** [OK] Monolithic PoC Complete  
**Architecture:** Single `MeetingOrchestrator` class with all functionality  
**Success:** End-to-end workflow validated, WSP compliant, 95% test coverage

## [ROCKET] Target State: Modular Ecosystem

### Architecture Philosophy
> **"Each module is an independent pArtifact with clear interfaces, domain expertise, and autonomous development capability"**

Following WSP domain distribution principles [[memory:182464]], functionality will be **distributed by function, NOT consolidated by platform**.

---

## [U+1F9E9] Strategic Module Decomposition

### 1️⃣ **Presence Aggregator** 
**Domain:** `modules/platform_integration/presence_aggregator/`  
**Purpose:** Integrate and normalize user presence across platforms  
**Current PoC Code:** `_calculate_overall_status()`, `_calculate_confidence()`  
**Interfaces:**
```python
async def get_current_status(user_id: str) -> UnifiedAvailabilityProfile
async def subscribe_presence(user_id: str, callback: Callable)
def normalize_status(platform: str, raw_status: Any) -> PresenceStatus
```

### 2️⃣ **Intent Manager**
**Domain:** `modules/communication/intent_manager/`  
**Purpose:** Capture, store, and retrieve meeting intents with structured context  
**Current PoC Code:** `create_meeting_intent()`, `get_active_intents()`  
**Interfaces:**
```python
async def create_intent(requester_id: str, recipient_id: str, context: MeetingContext) -> str
async def get_pending_intents(recipient_id: str) -> List[MeetingIntent]
async def mark_intent_processed(intent_id: str, outcome: str)
```

### 3️⃣ **Priority Scorer**
**Domain:** `modules/gamification/priority_scorer/`  
**Purpose:** Calculate priority indices using 000-222 emoji scale  
**Current PoC Code:** `Priority` enum, priority-based orchestration  
**Interfaces:**
```python
def score_intent(sender_priority: Priority, recipient_urgency: int) -> float
def compare_priorities(intents: List[MeetingIntent]) -> List[MeetingIntent]
def calculate_urgency_factor(context: MeetingContext) -> float
```

### 4️⃣ **Channel Selector**
**Domain:** `modules/ai_intelligence/channel_selector/`  
**Purpose:** Determine optimal communication platform  
**Current PoC Code:** `_select_optimal_platform()`  
**Interfaces:**
```python
def select_channel(user_a: UserProfile, user_b: UserProfile, context: MeetingContext) -> str
def get_platform_capabilities(platform: str) -> PlatformCapabilities
def rank_platforms(available_platforms: List[str], criteria: SelectionCriteria) -> List[str]
```

### 5️⃣ **Consent Engine**
**Domain:** `modules/communication/consent_engine/`  
**Purpose:** Handle meeting prompts and responses  
**Current PoC Code:** `_trigger_meeting_prompt()`, `_simulate_response()`  
**Interfaces:**
```python
async def send_consent_prompt(recipient_id: str, intent: MeetingIntent) -> str
async def process_response(prompt_id: str, response: ConsentResponse)
def generate_prompt_content(intent: MeetingIntent) -> PromptContent
```

### 6️⃣ **Session Launcher**
**Domain:** `modules/platform_integration/session_launcher/`  
**Purpose:** Auto-create meeting sessions across platforms  
**Current PoC Code:** `_launch_meeting_session()`  
**Interfaces:**
```python
async def launch_session(platform: str, participants: List[str], context: MeetingContext) -> SessionInfo
async def create_meeting_link(platform: str, settings: MeetingSettings) -> str
async def send_invitations(session_info: SessionInfo, participants: List[str])
```

### 7️⃣ **Audit Logger**
**Domain:** `modules/infrastructure/audit_logger/`  
**Purpose:** Comprehensive event logging for transparency  
**Current PoC Code:** Scattered `logger.info()` calls  
**Interfaces:**
```python
async def log_event(event_type: AuditEventType, details: Dict, user_id: str)
async def retrieve_logs(filter: LogFilter) -> List[AuditEvent]
def generate_audit_report(timeframe: TimeFrame) -> AuditReport
```

### 8️⃣ **Post-Meeting Summarizer**
**Domain:** `modules/ai_intelligence/post_meeting_summarizer/`  
**Purpose:** AI-powered meeting summaries and action items  
**Current PoC Code:** Not implemented (future feature)  
**Interfaces:**
```python
async def generate_summary(transcript: str, context: MeetingContext) -> MeetingSummary
async def extract_action_items(summary: MeetingSummary) -> List[ActionItem]
async def schedule_followups(action_items: List[ActionItem])
```

---

## [AI] **0102 Orchestrator**: The Unified Intelligence Layer

**Domain:** `modules/ai_intelligence/0102_orchestrator/`  
**Role:** Companion AI that unifies all AMO components through natural interaction

### Core Responsibilities
1. **Notification & Prompt Delivery** - Real-time user communication
2. **Conversational Guidance** - Natural language interface (text/voice)
3. **Memory & Personalization** - Learn user patterns and preferences
4. **Session Control** - Accept/decline intents, auto-launch sessions
5. **Personality Layer** - Configurable persona (formal, friendly, humorous)

### Interface Architecture
```python
class ZeroOneZeroTwo:
    """
    The unified AI orchestrator for AMO ecosystem
    Tony Stark's JARVIS for meeting coordination
    """
    
    async def notify_user(message: str, priority: Priority, channels: List[str])
    async def process_user_input(input: str, context: ConversationContext) -> Response
    async def learn_preference(user_id: str, preference_type: str, value: Any)
    async def suggest_action(situation: Situation) -> List[ActionSuggestion]
    async def execute_command(command: Command, user_id: str) -> ExecutionResult
```

### Subcomponents
```
modules/ai_intelligence/0102_orchestrator/
+-- notification_engine.py      # User-facing alerts and prompts
+-- memory_core.py             # Preferences and interaction history  
+-- conversation_manager.py    # Text/voice interaction handling
+-- session_controller.py      # Meeting session management
+-- personality_engine.py      # Configurable AI persona
+-- learning_engine.py         # Pattern recognition and adaptation
```

---

## [CLIPBOARD] Implementation Strategy

### Phase 1: Extract Core Components (v0.1.0)
**Objective:** Break monolithic PoC into focused modules while maintaining functionality

#### Week 1: Foundation Modules
- [x] **Intent Manager** - Extract intent creation and management
- [x] **Presence Aggregator** - Extract presence monitoring logic  
- [x] **Priority Scorer** - Extract priority calculation logic

#### Week 2: Communication Modules  
- [x] **Consent Engine** - Extract prompt and response handling
- [x] **Channel Selector** - Extract platform selection logic
- [x] **Audit Logger** - Extract and enhance logging

#### Week 3: Integration Modules
- [x] **Session Launcher** - Extract meeting launch functionality
- [x] **0102 Orchestrator** - Create unified AI interface

### Phase 2: Real Platform Integration (v0.2.0)
**Objective:** Replace simulated functionality with real platform APIs

#### Platform Integration Priority
1. **Discord** - Real-time presence via WebSocket, DM prompts
2. **WhatsApp Business** - Status monitoring, message sending  
3. **Zoom** - Meeting creation, calendar integration
4. **LinkedIn** - Professional presence monitoring

#### Data Persistence
- **SQLite** for local development and testing
- **PostgreSQL** for production multi-user deployment
- **Redis** for real-time presence caching

### Phase 3: AI Enhancement (v0.3.0)  
**Objective:** Enhance 0102 with advanced AI capabilities

#### AI Features
- **Natural Language Processing** - Intent parsing from casual language
- **Voice Interface** - Speech-to-text and text-to-speech
- **Predictive Scheduling** - Learn user patterns for proactive suggestions
- **Meeting Summaries** - Automatic transcription and action item extraction

---

## [U+1F3D7]️ Migration Path from Current PoC

### Step 1: Interface Extraction
Create interfaces for each module while keeping current implementation:

```python
# Current monolithic approach
class MeetingOrchestrator:
    def create_meeting_intent(self, ...):
        # All logic here
        
# Target modular approach  
class MeetingOrchestrator:
    def __init__(self):
        self.intent_manager = IntentManager()
        self.presence_aggregator = PresenceAggregator() 
        self.priority_scorer = PriorityScorer()
        # ... other modules
        
    def create_meeting_intent(self, ...):
        return self.intent_manager.create_intent(...)
```

### Step 2: Gradual Module Extraction
Extract one module at a time while maintaining test coverage:

1. Create new module with identical interface
2. Update MeetingOrchestrator to use new module
3. Run full test suite to ensure no regressions
4. Update documentation and interfaces
5. Repeat for next module

### Step 3: 0102 Integration
Once core modules are extracted, introduce 0102 as the orchestration layer:

```python
# User interacts with 0102, not individual modules
amo_0102 = ZeroOneZeroTwo()
await amo_0102.process_user_input("I need to meet with Alice about the project")
# 0102 coordinates with Intent Manager, Presence Aggregator, etc.
```

---

## [TARGET] Success Metrics by Phase

### Phase 1: Modular Foundation
- **Architectural:** 8 independent modules with clean interfaces
- **Quality:** Maintain [GREATER_EQUAL]90% test coverage across all modules  
- **Performance:** No regression from monolithic performance
- **Compliance:** Full WSP compliance for each module

### Phase 2: Platform Integration
- **Integration:** 2+ real platform APIs working reliably
- **Reliability:** 95%+ successful meeting coordination rate
- **User Experience:** <5 second end-to-end orchestration
- **Data:** 100% intent and history persistence

### Phase 3: AI Enhancement  
- **Intelligence:** Natural language intent processing working
- **Personalization:** User preference learning and adaptation
- **Voice:** Basic speech interface functional
- **Automation:** 80%+ meetings require no manual intervention

---

## [REFRESH] Cross-Module Communication

### Event-Driven Architecture
Modules communicate via events to maintain loose coupling:

```python
# Event system for module coordination
class AMOEventBus:
    async def publish(event: AMOEvent)
    async def subscribe(event_type: str, handler: Callable)

# Example event flow
presence_aggregator.publish(PresenceChangedEvent(user_id="alice", status="online"))
# -> 0102_orchestrator receives event
# -> 0102 checks for pending intents via intent_manager  
# -> 0102 triggers consent_engine if mutual availability
# -> consent_engine publishes ConsentRequestEvent
# -> session_launcher subscribes and launches meeting
```

### Interface Contracts
Each module defines clear contracts via abstract base classes:

```python
class PresenceProvider(ABC):
    @abstractmethod
    async def get_status(user_id: str) -> PresenceStatus
    
class ConsentHandler(ABC):
    @abstractmethod  
    async def send_prompt(recipient: str, intent: MeetingIntent) -> str
```

---

## [DATA] Estimated Development Timeline

| Phase | Duration | Key Deliverables | Risk Level |
|-------|----------|------------------|------------|
| Phase 1 | 3 weeks | 8 modular components | 🟢 Low |
| Phase 2 | 6 weeks | Real platform integration | 🟡 Medium |  
| Phase 3 | 8 weeks | AI enhancement + 0102 | 🟠 High |

**Total:** ~4 months to full modular ecosystem

---

**Strategic Blueprint Version:** v1.0  
**Created:** 2024-12-29  
**Next Review:** End of Phase 1 (Modular extraction) 