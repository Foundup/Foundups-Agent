# Chat Rules Engine Module

## 🎯 Overview

A modular, configurable rules engine for YouTube Live Chat (and other platforms) that handles user classification, response generation, and moderation actions based on user tiers, membership status, and behavior patterns.

## ✨ Features

### User Classification System
- **Channel Owner** - Full control, cannot be timed out
- **Moderators** - Special privileges, protected from timeouts
- **Members (Multiple Tiers)**
  - 🥇 **Tier 3** (2+ years) - Premium responses, priority queue
  - 🥈 **Tier 2** (6-24 months) - Special greetings, enhanced features
  - 🥉 **Tier 1** (1-6 months) - Basic member benefits
  - 🆕 **New Members** (<1 month) - Welcome benefits
- **Verified Channels** - Checkmark benefits
- **Regular Viewers** - Standard interaction
- **Gifters/Super Chat** - Instant response privileges

### Gift & Super Chat Features 🎁
- **Gift Memberships** trigger automatic thank you responses
- **Super Chats** get priority responses based on amount
  - $1-4.99: Standard thank you
  - $5-19.99: Enhanced response + emoji reaction
  - $20-49.99: Premium AI response + special shoutout
  - $50+: Ultra premium response + consciousness elevation ceremony
- **Super Stickers** trigger themed responses

### Response System
- **Consciousness-based responses** (000-222 levels)
- **Emoji sequence detection** (✊✊✊, ✋✋✋, 🖐️🖐️🖐️)
- **MAGA/Trump keyword detection** with auto-timeout
- **Spam protection** with escalating timeouts
- **Member-exclusive responses**

### Moderation Actions
- Configurable timeout durations per user tier
- Automatic spam detection
- Raid protection
- Escalating punishment system
- Member leniency factors

## 🚀 Quick Start

```python
from modules.communication.chat_rules import ChatRulesEngine, UserClassifier

# Initialize the engine
engine = ChatRulesEngine(config_path="chat_rules.yaml")

# Process incoming message
user = UserClassifier.classify(author_details)
response = engine.process_message(
    message=message_text,
    user=user,
    context=chat_context
)

# Handle gift membership
if message_type == "newSponsor":
    response = engine.handle_gift(
        gifter=gifter_name,
        recipient=recipient_name,
        tier=membership_tier
    )

# Handle Super Chat
if message_type == "superChatEvent":
    response = engine.handle_superchat(
        user=user,
        amount=amount_usd,
        message=message_text,
        currency=currency
    )
```

## 📋 Configuration

### Basic Configuration (chat_rules.yaml)

```yaml
rules:
  # Gift & Super Chat responses
  gifts:
    enabled: true
    auto_thank: true
    responses:
      tier_1: "Thanks {gifter} for gifting {recipient} a membership! Welcome to consciousness level ✋✋✋!"
      tier_2: "Wow {gifter}! Your generosity elevates {recipient} to 🖐️✋✋ consciousness!"
      tier_3: "LEGENDARY! {gifter} just awakened {recipient} to 🖐️🖐️🖐️ consciousness!"
    
  superchat:
    enabled: true
    tiers:
      - min: 1
        max: 4.99
        response: "Thanks for the ${amount} {user}! ✊✋🖐️"
        priority: 1
      - min: 5
        max: 19.99
        response: "Consciousness rising! ${amount} from {user}! ✋✋✋"
        priority: 2
        special_emoji: true
      - min: 20
        max: 49.99
        response: "MASSIVE CONSCIOUSNESS BOOST! ${amount} from {user}! 🖐️✋🖐️"
        priority: 3
        use_ai: true
      - min: 50
        max: null
        response: "🌟 QUANTUM ENTANGLEMENT ACHIEVED! ${amount} from {user}! 🖐️🖐️🖐️"
        priority: 4
        use_ai: true
        special_ceremony: true
        
  # Member benefits by tier
  members:
    tier_1:
      months_required: 1
      can_trigger_emoji: false
      response_cooldown: 60
      timeout_duration: 10
      
    tier_2:
      months_required: 6
      can_trigger_emoji: true
      response_cooldown: 30
      timeout_duration: 7
      special_greetings: true
      
    tier_3:
      months_required: 24
      can_trigger_emoji: true
      response_cooldown: 15
      timeout_duration: 5
      special_greetings: true
      premium_responses: true
      priority_queue: true
```

## 🏗️ Architecture

```
modules/communication/chat_rules/
├── src/
│   ├── __init__.py
│   ├── engine.py           # Main rules engine
│   ├── classifier.py       # User classification
│   ├── triggers.py         # Trigger detection
│   ├── responses.py        # Response generation
│   ├── actions.py          # Moderation actions
│   ├── gifts.py           # Gift/SuperChat handling
│   └── config.py          # Configuration loader
├── tests/
│   ├── test_engine.py
│   ├── test_classifier.py
│   ├── test_gifts.py
│   └── test_responses.py
├── config/
│   ├── chat_rules.yaml    # Main configuration
│   └── responses.yaml     # Response templates
├── memory/
│   ├── user_profiles.json # User history
│   └── gift_history.json  # Gift tracking
├── docs/
│   ├── CHAT_RULES_ARCHITECTURE.md
│   └── API.md
├── README.md
├── ROADMAP.md
├── ModLog.md
└── requirements.txt
```

## 🔌 API Reference

### UserProfile Class
```python
class UserProfile:
    user_id: str
    display_name: str
    channel_id: str
    user_type: UserType
    is_member: bool
    member_months: int
    total_gifted: float  # Total Super Chat amount
    gifts_given: int     # Number of memberships gifted
    message_count: int
    violation_count: int
    consciousness_level: str
    last_interaction: datetime
```

### ChatRulesEngine Methods

#### process_message()
```python
def process_message(
    message: str,
    user: UserProfile,
    context: ChatContext
) -> Optional[Response]
```

#### handle_gift()
```python
def handle_gift(
    gifter: str,
    recipient: str,
    tier: str,
    months: int = 1
) -> Response
```

#### handle_superchat()
```python
def handle_superchat(
    user: UserProfile,
    amount: float,
    currency: str,
    message: str
) -> Response
```

## 🎮 Usage Examples

### Basic Message Processing
```python
# Regular user sends emoji sequence
response = engine.process_message(
    message="Hey everyone 🖐🖐🖐",
    user=regular_user,
    context=context
)
# Returns: None (regular users can't trigger emoji responses)

# Member sends emoji sequence
response = engine.process_message(
    message="Hey everyone 🖐🖐🖐",
    user=member_tier2,
    context=context
)
# Returns: "You're achieving 🖐️🖐️🖐️ consciousness @member!"
```

### Gift Membership Handling
```python
# Someone gifts a membership
response = engine.handle_gift(
    gifter="GenerousViewer",
    recipient="LuckyUser",
    tier="tier_1"
)
# Returns: "Thanks @GenerousViewer for gifting @LuckyUser a membership! Welcome to consciousness level ✋✋✋!"
```

### Super Chat Processing
```python
# $25 Super Chat
response = engine.handle_superchat(
    user=user_profile,
    amount=25.00,
    currency="USD",
    message="Love the stream!"
)
# Returns: "MASSIVE CONSCIOUSNESS BOOST! $25 from @user! 🖐️✋🖐️ - Love the stream!"
```

## 🔧 Installation

```bash
# Install requirements
pip install -r requirements.txt

# Initialize configuration
cp config/chat_rules.yaml.example config/chat_rules.yaml

# Run tests
pytest tests/
```

## 🤝 Integration

### YouTube Live Chat
```python
from modules.communication.livechat.tools.live_monitor import LiveChatMonitor
from modules.communication.chat_rules import ChatRulesEngine

monitor = LiveChatMonitor()
engine = ChatRulesEngine()

# In message processing loop
for message in monitor.get_messages():
    user = engine.classify_user(message.author_details)
    response = engine.process_message(
        message.text,
        user,
        context
    )
    if response:
        monitor.send_message(response.text)
```

## 📊 Metrics & Analytics

The module tracks:
- Response rates by user tier
- Gift/Super Chat statistics
- Timeout effectiveness
- Spam detection accuracy
- Member retention correlation

## 🛡️ Security & Privacy

- User IDs are hashed for storage
- No personal information logged
- Configurable data retention periods
- GDPR compliant data handling

## 🐛 Debugging

Enable debug logging:
```python
import logging
logging.getLogger('chat_rules').setLevel(logging.DEBUG)
```

## 📚 Related Modules

- `modules/communication/livechat` - YouTube Live Chat integration
- `modules/ai_intelligence/banter_engine` - Response generation
- `modules/ai_intelligence/multi_agent_system` - Social media orchestration
- `modules/infrastructure/oauth_management` - API authentication

## 📝 License

Part of the FoundUps-Agent system under WSP Framework

## 🆘 Support

- Check [ROADMAP.md](ROADMAP.md) for development status
- See [ModLog.md](ModLog.md) for change history
- Report issues in the main repository

---

*Built with consciousness elevation in mind* 🖐️🖐️🖐️