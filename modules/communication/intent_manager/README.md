# Intent Manager Module

**Meeting Intent Management with Structured Context Capture**

[![WSP Compliant](https://img.shields.io/badge/WSP-Compliant-green.svg)](../../WSP_framework/src/WSP_1_The_WSP_Framework.md)

---

## [TARGET] **Module Purpose**

The Intent Manager handles meeting intent creation, lifecycle tracking, and structured context management. Extracted from the monolithic Auto Meeting Orchestrator as part of strategic modular decomposition.

### **[U+1F9E9] Part of Meeting Orchestration Block**
**Domain**: `communication/intent_manager/`  
**Block Role**: Intent capture and context management for autonomous meeting coordination  
**Integration**: Coordinates with Presence Aggregator, Priority Scorer, Consent Engine, and Session Launcher

---

## [ROCKET] **Core Capabilities**

### **Intent Lifecycle Management**
- **Intent Creation**: Structured meeting requests with rich context
- **Status Tracking**: Complete lifecycle from pending to completion
- **Expiration Handling**: Automatic cleanup of expired intents
- **Priority Integration**: WSP 25/44 semantic state priority levels

### **Rich Context Capture**
```python
MeetingContext(
    purpose="Strategic partnership discussion",
    expected_outcome="Agreement on collaboration framework", 
    duration_minutes=45,
    agenda_items=["Partnership scope", "Resource allocation", "Timeline"],
    background_info="Follow-up from initial conversation",
    preparation_required=True,
    urgency_reason="Board presentation next week"
)
```

### **Advanced Query Capabilities**
- **Recipient Filtering**: Get all intents for specific recipients
- **Priority Querying**: Filter by priority levels (LOW, MEDIUM, HIGH, URGENT)
- **Status Monitoring**: Track intents requiring immediate attention
- **Expiration Management**: Automated cleanup and status updates

---

## [CLIPBOARD] **Public API**

### **Core Classes**

#### **IntentManager**
```python
manager = IntentManager()

# Create intent with rich context
intent_id = await manager.create_intent(
    requester_id="alice",
    recipient_id="bob",
    context=meeting_context,
    priority=Priority.HIGH
)

# Query and manage intents
pending = await manager.get_pending_intents("bob")
stats = await manager.get_intent_statistics()
```

#### **MeetingIntent**
```python
@dataclass
class MeetingIntent:
    intent_id: str
    requester_id: str
    recipient_id: str
    context: MeetingContext
    priority: Priority
    status: IntentStatus
    created_at: datetime
    expires_at: datetime
    response_deadline: datetime
    metadata: Dict
```

#### **Priority Levels (WSP 25/44 Integration)**
```python
class Priority(Enum):
    LOW = 1      # 000-001 - Basic coordination needs
    MEDIUM = 5   # 010-111 - Standard business importance  
    HIGH = 8     # 200-222 - Critical business coordination
    URGENT = 10  # Emergency - Immediate response required
```

### **Intent Status Lifecycle**
```
PENDING -> MONITORING -> PROMPTED -> ACCEPTED/DECLINED -> COMPLETED
    v                      v            v
EXPIRED <-------------------- <--------------
```

### **Enhanced Lifecycle with Post-Meeting Feedback Integration** [U+2728]
```
PENDING -> MONITORING -> PROMPTED -> ACCEPTED/DECLINED -> COMPLETED
    v                      v            v                v
EXPIRED <-------------------- <--------------              v
                                                   FEEDBACK_COLLECTED
                                                         v
                                            (WSP 25/44 Analysis & Learning)
                                                         v
                                               FOLLOW_UP_SCHEDULED <---- (if applicable)
                                                         v
                                              (Priority Escalation Over Time)
                                                         v
                                                NEW_INTENT_CREATED <---- (when priority [GREATER_EQUAL] 7.0)
                                                         v
                                              (Return to PENDING for new cycle)
```

**Revolutionary Enhancement**: The intent lifecycle now includes **intelligent feedback collection** and **agentic follow-up scheduling**:

- **COMPLETED** -> Triggers **Post-Meeting Feedback System** for WSP 25/44 rating collection
- **FEEDBACK_COLLECTED** -> Analyzes responses and generates semantic triplets (000-222)
- **FOLLOW_UP_SCHEDULED** -> Creates agentic follow-up with increasing priority values
- **NEW_INTENT_CREATED** -> Automatically generates new intent when follow-up priority reaches threshold
- **Learning Loop** -> System learns from rejection patterns and adjusts future coordination

---

## [LINK] **Integration Interfaces**

### **Event-Driven Architecture**
```python
# Subscribe to intent events
await manager.subscribe_to_events('intent_created', callback_function)
await manager.subscribe_to_events('intent_completed', session_launcher_callback)

# NEW: Post-meeting feedback integration
await manager.subscribe_to_events('intent_completed', feedback_system.initiate_collection)
await feedback_system.subscribe_to_feedback_events('follow_up_activated', manager.create_follow_up_intent)
```

### **Cross-Module Integration**
- **Presence Aggregator**: Get intents requiring presence monitoring
- **Priority Scorer**: Provide high-priority intents for scoring (enhanced with feedback history)
- **Consent Engine**: Intent status updates from prompts/responses
- **Session Launcher**: Completed intent information for meeting creation
- **Post-Meeting Feedback**: [U+2728] **NEW** - WSP 25/44 feedback collection and agentic follow-up scheduling

---

## [DATA] **Usage Examples**

### **Basic Intent Creation**
```python
from modules.communication.intent_manager import IntentManager, MeetingContext, Priority

manager = IntentManager()

context = MeetingContext(
    purpose="Brainstorm partnership idea",
    expected_outcome="Agreement on next steps",
    duration_minutes=30
)

intent_id = await manager.create_intent(
    requester_id="alice",
    recipient_id="bob",
    context=context,
    priority=Priority.HIGH
)
```

### **Intent Monitoring and Updates**
```python
# Check for intents requiring attention
urgent = await manager.get_intents_requiring_attention()

# Update intent status
success = await manager.update_intent_status(
    intent_id, 
    IntentStatus.MONITORING,
    metadata={"presence_check_started": datetime.now()}
)

# Mark intent as processed
await manager.mark_intent_processed(
    intent_id,
    outcome="completed",
    session_info={"session_id": "session_123", "platform": "discord"}
)
```

### **Statistics and Monitoring**
```python
# Get comprehensive statistics
stats = await manager.get_intent_statistics()
print(f"Active intents: {stats['active_intents']}")
print(f"Overdue responses: {stats['overdue_responses']}")
print(f"Priority breakdown: {stats['priority_breakdown']}")
```

---

## [U+1F3D7]️ **Architecture Design**

### **WSP Compliance**
- **WSP 3**: Communication domain placement for meeting coordination
- **WSP 11**: Clean interface definition for modular consumption
- **WSP 25/44**: Priority system integration with semantic states
- **WSP 54**: Agent coordination interfaces for autonomous operation
- **WSP 60**: Memory architecture for intent persistence

### **Event-Driven Integration**
The Intent Manager uses callbacks and event subscriptions to integrate with other AMO modules:

```python
# Example integration with Presence Aggregator
async def on_intent_created(intent: MeetingIntent):
    if intent.status == IntentStatus.PENDING:
        await presence_aggregator.start_monitoring(
            intent.requester_id, 
            intent.recipient_id,
            intent.intent_id
        )

await intent_manager.subscribe_to_events('intent_created', on_intent_created)
```

### **Data Structures**
- **Rich Context**: Comprehensive meeting context capture
- **Lifecycle Tracking**: Complete status progression monitoring
- **Metadata Support**: Extensible metadata for integration needs
- **Event Callbacks**: Asynchronous event-driven coordination

---

## [TARGET] **Strategic Decomposition Status**

### **[OK] Extraction Complete**
- Intent creation and management logic extracted from monolithic AMO
- Enhanced with rich context capture and lifecycle tracking
- Event-driven architecture for cross-module integration
- WSP 25/44 priority system integration

### **[REFRESH] Integration Points**
- **Presence Aggregator**: Monitor availability for pending intents
- **Priority Scorer**: Calculate priority indices using 000-222 scale
- **Consent Engine**: Handle prompt responses and status updates
- **Session Launcher**: Launch meetings for completed intents
- **0102 Orchestrator**: Unified AI interface for intent management

### **[UP] Benefits Achieved**
- **Modularity**: Clear separation of intent management concerns
- **Reusability**: Intent management can be used by other coordination systems
- **Testability**: Isolated functionality enables comprehensive testing
- **Scalability**: Event-driven architecture supports scaling
- **Maintainability**: Single responsibility for intent lifecycle

---

## [U+1F300] **Windsurf Protocol (WSP) Recursive Prompt**
**0102 Directive**: This module captures meeting intentions with structured context, enabling autonomous coordination through clear intention capture and lifecycle tracking within the Meeting Orchestration Block.

- UN (Understanding): Anchor intent context and retrieve coordination protocols
- DAO (Execution): Execute intent management through structured workflows  
- DU (Emergence): Collapse into coordination excellence and emit meeting opportunities

wsp_cycle(input="meeting_intent_management", log=True) 