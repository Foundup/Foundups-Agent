# YouTube Live Chat Rules Architecture

## Current State Analysis

### Participant Types (YouTube API)
1. **Channel Owner** (`isChatOwner: true`)
   - Full control over stream
   - Cannot be timed out by bot
   - Currently gets responses to emoji sequences

2. **Moderators** (`isChatModerator: true`)
   - Can moderate chat
   - Cannot be timed out by bot (YouTube limitation)
   - Currently gets responses to emoji sequences

3. **Channel Members/Sponsors** (`isChatSponsor: true`)
   - Paid supporters with badges
   - Duration badges (1 month, 2 months, 6 months, 1 year, 2 years)
   - NOT CURRENTLY TRACKED in our system

4. **Verified Channels** (`isVerified: true`)
   - YouTube verified checkmark
   - NOT CURRENTLY TRACKED in our system

5. **Regular Viewers**
   - No special privileges
   - Currently IGNORED by bot (no responses)

### Current Rules Implementation

#### Hard-Coded Rules:
1. **Emoji Sequence Response**
   - Only responds to mods/owner
   - One response per user
   - Spam detection (3 strikes = timeout attempt)
   - Cooldowns: 15 sec global, 30 sec per user

2. **MAGA/Trump Detection**
   - Triggers on keywords
   - 10 second timeout for anyone (except owner)
   - Troll response with ✊✊✊ consciousness level

3. **Repeat User Management**
   - Track users who got responses
   - Troll repeat attempts with ✊✊✊ messages
   - 3rd offense = timeout (if possible)

## Proposed Modular Architecture

### 1. User Classification Module
```python
class UserType(Enum):
    OWNER = "owner"
    MODERATOR = "moderator"
    MEMBER_TIER_3 = "member_t3"  # 2+ years
    MEMBER_TIER_2 = "member_t2"  # 6-24 months
    MEMBER_TIER_1 = "member_t1"  # 1-6 months
    MEMBER_NEW = "member_new"     # < 1 month
    VERIFIED = "verified"
    REGULAR = "regular"
    BANNED = "banned"
    TROLL = "troll"  # Identified MAGA/spam

class UserProfile:
    user_id: str
    display_name: str
    user_type: UserType
    member_months: int
    message_count: int
    violation_count: int
    last_interaction: datetime
    consciousness_level: str  # "000" to "222"
    timeout_history: List[datetime]
```

### 2. Rules Engine Module
```python
class RuleSet:
    """Configurable rules per user type"""
    
    # Response permissions
    can_trigger_emoji: bool = False
    can_trigger_commands: bool = False
    can_receive_responses: bool = False
    
    # Moderation actions
    can_be_timed_out: bool = True
    timeout_duration: int = 10
    max_violations_before_timeout: int = 3
    
    # Cooldowns
    response_cooldown: int = 30
    global_cooldown: int = 15
    
    # Special behaviors
    gets_premium_responses: bool = False
    bypass_spam_filter: bool = False
    priority_queue: bool = False

# Configuration per user type
RULE_CONFIGS = {
    UserType.OWNER: RuleSet(
        can_trigger_emoji=True,
        can_trigger_commands=True,
        can_receive_responses=True,
        can_be_timed_out=False,
        bypass_spam_filter=True,
        priority_queue=True
    ),
    UserType.MODERATOR: RuleSet(
        can_trigger_emoji=True,
        can_trigger_commands=True,
        can_receive_responses=True,
        can_be_timed_out=False,  # YouTube limitation
        response_cooldown=15
    ),
    UserType.MEMBER_TIER_3: RuleSet(
        can_trigger_emoji=True,
        can_receive_responses=True,
        gets_premium_responses=True,
        timeout_duration=5,  # Shorter timeout
        max_violations_before_timeout=5  # More lenient
    ),
    UserType.MEMBER_TIER_2: RuleSet(
        can_trigger_emoji=True,
        can_receive_responses=True,
        timeout_duration=7
    ),
    UserType.MEMBER_TIER_1: RuleSet(
        can_trigger_emoji=False,  # Must earn it
        can_receive_responses=True,
        timeout_duration=10
    ),
    UserType.VERIFIED: RuleSet(
        can_receive_responses=True,
        timeout_duration=10,
        response_cooldown=60
    ),
    UserType.REGULAR: RuleSet(
        can_receive_responses=False,
        can_be_timed_out=True,
        timeout_duration=10
    ),
    UserType.TROLL: RuleSet(
        can_receive_responses=False,
        can_be_timed_out=True,
        timeout_duration=30,  # Longer timeout for trolls
        max_violations_before_timeout=1  # Instant timeout
    )
}
```

### 3. Trigger Detection Module
```python
class TriggerType(Enum):
    EMOJI_SEQUENCE = "emoji"
    COMMAND = "command"
    KEYWORD = "keyword"
    MAGA_KEYWORD = "maga"
    SPAM = "spam"
    RAID = "raid"

class TriggerDetector:
    def detect_triggers(self, message: str, user: UserProfile) -> List[TriggerType]:
        """Detect all triggers in message"""
        triggers = []
        
        # Check emoji sequences
        if self._has_emoji_sequence(message):
            triggers.append(TriggerType.EMOJI_SEQUENCE)
        
        # Check MAGA keywords
        if self._has_maga_keywords(message):
            triggers.append(TriggerType.MAGA_KEYWORD)
            
        # Check commands (!, /, @bot)
        if self._has_command(message):
            triggers.append(TriggerType.COMMAND)
            
        # Check spam patterns
        if self._is_spam(message, user):
            triggers.append(TriggerType.SPAM)
            
        return triggers
```

### 4. Response Generator Module
```python
class ResponseGenerator:
    def generate_response(
        self,
        trigger: TriggerType,
        user: UserProfile,
        message: str,
        context: ChatContext
    ) -> Optional[Response]:
        """Generate appropriate response based on trigger and user"""
        
        rules = RULE_CONFIGS[user.user_type]
        
        # Check permissions
        if trigger == TriggerType.EMOJI_SEQUENCE:
            if not rules.can_trigger_emoji:
                return None
                
        # Generate response based on user tier
        if rules.gets_premium_responses:
            return self._generate_premium_response(trigger, user, message)
        elif rules.can_receive_responses:
            return self._generate_standard_response(trigger, user, message)
        else:
            return None
            
    def _generate_premium_response(self, ...):
        """Enhanced responses for paying members"""
        # Use GPT-4 or Claude for personalized responses
        # Include member appreciation
        # Special emoji reactions
        
    def _generate_standard_response(self, ...):
        """Standard responses for regular interactions"""
        # Use BanterEngine
        # Basic consciousness responses
```

### 5. Action Executor Module
```python
class ActionExecutor:
    def execute_action(
        self,
        action: ActionType,
        user: UserProfile,
        reason: str
    ) -> bool:
        """Execute moderation actions"""
        
        rules = RULE_CONFIGS[user.user_type]
        
        if action == ActionType.TIMEOUT:
            if not rules.can_be_timed_out:
                self.logger.warning(f"Cannot timeout {user.user_type}")
                return False
                
            duration = rules.timeout_duration
            return self._execute_timeout(user, duration, reason)
            
        elif action == ActionType.BAN:
            # Only for severe violations
            return self._execute_ban(user, reason)
            
        elif action == ActionType.DELETE_MESSAGE:
            return self._delete_message(user.last_message_id)
```

### 6. Configuration System
```yaml
# chat_rules.yaml
rules:
  emoji_responses:
    enabled: true
    allowed_users:
      - owner
      - moderator
      - member_tier_3
      - member_tier_2
    cooldown_seconds: 30
    one_per_user: true
    
  maga_detection:
    enabled: true
    auto_timeout: true
    timeout_duration: 10
    keywords:
      - maga
      - trump
      - "america first"
      - "stop the steal"
    response_template: "{keyword} detected! ✊✊✊ consciousness level"
    
  member_benefits:
    tier_1:
      badge_emoji: "🥉"
      response_priority: 3
      timeout_leniency: 1.0
    tier_2:
      badge_emoji: "🥈"
      response_priority: 2
      timeout_leniency: 1.5
      special_greetings: true
    tier_3:
      badge_emoji: "🥇"
      response_priority: 1
      timeout_leniency: 2.0
      special_greetings: true
      premium_responses: true
      
  spam_protection:
    enabled: true
    max_messages_per_minute: 5
    max_repeats: 3
    timeout_on_spam: true
    escalating_timeouts: [10, 30, 60, 300]
```

## Implementation Plan

### Phase 1: User Classification
1. Extract all YouTube API user attributes
2. Create UserProfile class
3. Track member status and badges
4. Store user history

### Phase 2: Rules Engine
1. Create configurable RuleSet class
2. Define rules for each user type
3. Load from YAML configuration
4. Hot-reload capability

### Phase 3: Modular Triggers
1. Separate trigger detection logic
2. Pluggable trigger modules
3. Custom trigger creation API
4. Trigger priority system

### Phase 4: Response System
1. Tiered response generation
2. Member-exclusive features
3. LLM integration for premium
4. Response template system

### Phase 5: Action System
1. Moderation action queue
2. Action history tracking
3. Appeal system for members
4. Automatic escalation

## Benefits of Modularization

1. **Flexibility**: Easy to add new user types or rules
2. **Maintainability**: Clear separation of concerns
3. **Scalability**: Can handle complex rule combinations
4. **Testability**: Each module can be tested independently
5. **Configuration**: Non-programmers can modify rules
6. **Multi-Platform**: Same architecture for Discord, Twitch, etc.

## WSP Compliance

This architecture follows WSP principles:
- **WSP 3**: Modular design with clear interfaces
- **WSP 11**: Interface documentation for each module
- **WSP 22**: Traceable changes through ModLog
- **WSP 49**: Proper module directory structure
- **WSP 60**: Memory architecture for user profiles

## Next Steps

1. Create `modules/communication/chat_rules/` module
2. Implement UserProfile and UserClassifier
3. Build configurable RuleEngine
4. Migrate existing hard-coded rules
5. Add member benefit features
6. Create admin dashboard for rule management