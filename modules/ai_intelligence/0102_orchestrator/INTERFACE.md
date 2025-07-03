# 0102 Orchestrator Interface Documentation

This document provides comprehensive API documentation for the 0102 Orchestrator module components.

## Core Classes and Interfaces

### ZeroOneZeroTwo

The main orchestrator class that serves as the unified AI interface.

#### Constructor

```python
def __init__(self, personality_mode: PersonalityMode = PersonalityMode.FRIENDLY)
```

**Parameters:**
- `personality_mode`: Configures AI response style (PROFESSIONAL, FRIENDLY, CONCISE, DETAILED, HUMOROUS)

#### Primary Methods

##### `greet_user(user_id: str) -> Response`

Initial greeting when user first interacts with 0102.

**Parameters:**
- `user_id`: Unique identifier for the user

**Returns:**
- `Response`: Contains greeting message and suggested actions

**Example:**
```python
greeting = await ai.greet_user("alice")
print(greeting.message)  # "Hello! I'm 0102, your meeting orchestration companion..."
```

##### `process_user_input(user_id: str, input_text: str) -> Response`

Process natural language input and coordinate appropriate response.

**Parameters:**
- `user_id`: User identifier
- `input_text`: Natural language input from user

**Returns:**
- `Response`: Processed response with message and suggested actions

**Example:**
```python
response = await ai.process_user_input(
    "alice", 
    "I need to meet with Bob about the project"
)
```

##### `notify_user(user_id: str, message: str, priority: str) -> bool`

Send notification to user.

**Parameters:**
- `user_id`: Target user identifier
- `message`: Notification content
- `priority`: Priority level ("low", "medium", "high", "urgent", "critical")

**Returns:**
- `bool`: True if notification delivered successfully

##### `suggest_action(user_id: str, situation: Dict) -> Response`

Proactively suggest actions based on current situation.

**Parameters:**
- `user_id`: User identifier
- `situation`: Dictionary describing current context

**Returns:**
- `Response`: Suggestion response with recommended actions

**Example:**
```python
suggestion = await ai.suggest_action(
    "alice",
    {"mutual_availability": True, "participants": ["Bob"]}
)
```

### Data Structures

#### ResponseType Enum

```python
class ResponseType(Enum):
    NOTIFICATION = "notification"
    SUGGESTION = "suggestion"
    CONFIRMATION = "confirmation"
    QUESTION = "question"
    ACTION_RESULT = "action_result"
    ERROR = "error"
```

#### PersonalityMode Enum

```python
class PersonalityMode(Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    CONCISE = "concise"
    DETAILED = "detailed"
    HUMOROUS = "humorous"
```

#### UserContext DataClass

```python
@dataclass
class UserContext:
    user_id: str
    active_sessions: List[str]
    pending_intents: List[str]
    current_availability: Optional[str]
    last_interaction: datetime
    preferences: Dict[str, Any]
```

#### Response DataClass

```python
@dataclass
class Response:
    response_type: ResponseType
    message: str
    suggested_actions: List[str]
    requires_user_input: bool
    context: Optional[Dict] = None
```

## ConversationManager

Handles natural language processing and response generation.

#### Constructor

```python
def __init__(self, personality_mode: PersonalityMode)
```

#### Methods

##### `parse_user_intent(input_text: str) -> ParsedIntent`

Parse user input to identify intent and extract entities.

**Parameters:**
- `input_text`: Raw user input

**Returns:**
- `ParsedIntent`: Structured intent with confidence and entities

##### `generate_response(parsed_intent: ParsedIntent) -> str`

Generate response based on parsed intent and personality mode.

**Parameters:**
- `parsed_intent`: Parsed user intent

**Returns:**
- `str`: Generated response text

#### Data Structures

##### Intent Enum

```python
class Intent(Enum):
    CREATE_MEETING = "create_meeting"
    CHECK_STATUS = "check_status"
    CHECK_AVAILABILITY = "check_availability"
    ACCEPT_MEETING = "accept_meeting"
    DECLINE_MEETING = "decline_meeting"
    UPDATE_PREFERENCES = "update_preferences"
    GENERAL_QUESTION = "general_question"
    GREETING = "greeting"
    UNKNOWN = "unknown"
```

##### ParsedIntent DataClass

```python
@dataclass
class ParsedIntent:
    intent: Intent
    confidence: float  # 0.0 to 1.0
    entities: Dict[str, Any]
    original_text: str
```

## NotificationEngine

Manages multi-channel notification delivery.

#### Constructor

```python
def __init__(self)
```

#### Methods

##### `send_notification(...) -> bool`

Send notification through specified channels.

**Parameters:**
- `user_id`: Target user identifier
- `message`: Notification message content
- `priority`: Priority level string
- `channels`: List of delivery channels (optional)
- `template_name`: Template to use for formatting (optional)
- `**kwargs`: Additional template variables

**Returns:**
- `bool`: True if delivered successfully

##### Specialized Notification Methods

```python
async def notify_meeting_opportunity(
    user_id: str,
    requester: str,
    purpose: str,
    duration: int,
    priority: str
) -> bool

async def notify_presence_change(
    user_id: str,
    target_user: str,
    new_status: str
) -> bool

async def notify_meeting_reminder(
    user_id: str,
    participant: str,
    start_time: str
) -> bool
```

##### `get_notification_stats() -> Dict`

Get delivery statistics and metrics.

**Returns:**
- `Dict`: Statistics including total notifications, delivery rate, breakdown by priority/channel

#### Data Structures

##### NotificationChannel Enum

```python
class NotificationChannel(Enum):
    CONSOLE = "console"
    DISCORD = "discord"
    EMAIL = "email"
    PUSH = "push"
    WHATSAPP = "whatsapp"
    SLACK = "slack"
```

##### NotificationPriority Enum

```python
class NotificationPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"
```

##### Notification DataClass

```python
@dataclass
class Notification:
    notification_id: str
    user_id: str
    channel: NotificationChannel
    priority: NotificationPriority
    title: str
    message: str
    timestamp: datetime
    action_buttons: List[str]
    metadata: Dict = None
    delivered: bool = False
```

## MemoryCore

Manages user preferences and learning.

#### Constructor

```python
def __init__(self)
```

#### Methods

##### `store_preference(user_id: str, preference_type: str, value: Any) -> bool`

Store or update a user preference.

**Parameters:**
- `user_id`: User identifier
- `preference_type`: Type of preference (e.g., "preferred_platform", "notification_style")
- `value`: Preference value

**Returns:**
- `bool`: True if stored successfully

##### `get_preference(user_id: str, preference_type: str, default: Any = None) -> Any`

Retrieve a user preference with optional default.

**Parameters:**
- `user_id`: User identifier
- `preference_type`: Type of preference to retrieve
- `default`: Default value if preference not found

**Returns:**
- `Any`: Preference value or default

##### `record_interaction(...) -> bool`

Record user interaction for learning purposes.

**Parameters:**
- `user_id`: User identifier
- `interaction_type`: Type of interaction
- `context`: Interaction context dictionary
- `outcome`: Interaction outcome

**Returns:**
- `bool`: True if recorded successfully

##### `generate_insights(user_id: str) -> Dict[str, Any]`

Generate behavioral insights about user patterns.

**Parameters:**
- `user_id`: User identifier

**Returns:**
- `Dict`: Generated insights including activity patterns and preferences

## Integration Patterns

### Basic Usage Pattern

```python
# Initialize 0102
ai_companion = ZeroOneZeroTwo(PersonalityMode.FRIENDLY)

# User interaction flow
user_id = "alice"
greeting = await ai_companion.greet_user(user_id)

# Process user input
response = await ai_companion.process_user_input(
    user_id, 
    "I need to schedule a meeting"
)

# Handle response
if response.requires_user_input:
    # Wait for additional user input
    pass
else:
    # Execute suggested actions
    for action in response.suggested_actions:
        print(f"Suggested: {action}")
```

### Learning Integration Pattern

```python
# Store explicit preferences
await ai_companion.learn_preference(
    user_id, 
    "preferred_platform", 
    "discord"
)

# Record interaction outcomes
await memory_core.record_interaction(
    user_id=user_id,
    interaction_type="meeting_created",
    context={"platform": "discord", "duration": 30},
    outcome="success"
)

# Generate insights
insights = await memory_core.generate_insights(user_id)
```

### Notification Integration Pattern

```python
# Send basic notification
await notification_engine.send_notification(
    user_id="alice",
    message="Bob is now available",
    priority="medium"
)

# Send specialized notification
await notification_engine.notify_meeting_opportunity(
    user_id="alice",
    requester="Bob",
    purpose="Project discussion",
    duration=30,
    priority="high"
)
```

## Error Handling

### Common Exception Patterns

```python
try:
    response = await ai_companion.process_user_input(user_id, input_text)
    
    if response.response_type == ResponseType.ERROR:
        # Handle application-level errors
        print(f"Error: {response.message}")
        
except Exception as e:
    # Handle system-level errors
    logger.error(f"Unexpected error: {e}")
    # Provide fallback response
```

### Response Validation

```python
def validate_response(response: Response) -> bool:
    """Validate response structure"""
    return (
        response.message and
        isinstance(response.suggested_actions, list) and
        isinstance(response.requires_user_input, bool)
    )
```

## Configuration Options

### Personality Configuration

```python
# Configure response styles
personality_configs = {
    PersonalityMode.PROFESSIONAL: {
        "tone": "formal",
        "verbosity": "concise",
        "greeting_style": "business"
    },
    PersonalityMode.FRIENDLY: {
        "tone": "casual",
        "verbosity": "moderate",
        "greeting_style": "warm"
    }
}
```

### Notification Configuration

```python
# Configure notification channels
notification_config = {
    "default_channels": ["console"],
    "priority_mappings": {
        "urgent": ["console", "discord"],
        "critical": ["console", "discord", "email"]
    },
    "delivery_timeout": 5000  # milliseconds
}
```

### Memory Configuration

```python
# Configure learning parameters
memory_config = {
    "max_interactions_stored": 100,
    "insight_generation_threshold": 5,
    "preference_confidence_threshold": 0.7,
    "data_retention_days": 30
}
```

## Performance Considerations

### Async Operations

All major operations are async for optimal performance:

```python
# Concurrent operations
tasks = [
    ai_companion.process_user_input(user_id, input1),
    ai_companion.process_user_input(user_id, input2),
    ai_companion.suggest_action(user_id, situation)
]

responses = await asyncio.gather(*tasks)
```

### Memory Management

```python
# Efficient memory usage
class MemoryCore:
    def __init__(self):
        # Use bounded collections for history
        self.interaction_history = {}  # Limited to recent interactions
        self.user_preferences = {}     # Cached preferences only
```

### Error Recovery

```python
# Graceful degradation
async def robust_process_input(user_id: str, input_text: str) -> Response:
    try:
        return await ai_companion.process_user_input(user_id, input_text)
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        return Response(
            response_type=ResponseType.ERROR,
            message="I'm having trouble processing that request. Please try again.",
            suggested_actions=["Retry", "Contact support"],
            requires_user_input=True
        )
```

---

**Interface Version**: 0.0.1  
**Last Updated**: 2024-12-29  
**Compatibility**: Python 3.8+ 