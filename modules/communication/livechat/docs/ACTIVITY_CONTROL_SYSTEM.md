# WSP 18: Universal Activity Control Protocol

**Status**: Active  
**Dependencies**: WSP 3, WSP 49, WSP 5, WSP 6  
**Usage Context**: System-wide activity control, testing, noise reduction, live stream management  

## Overview

The Universal Activity Control Protocol establishes a centralized system for controlling all automated activities across the Foundups Agent ecosystem. This protocol enables real-time switching of system behaviors for testing, debugging, and live stream management.

## Core Principles

### 1. Hierarchical Control Architecture
```yaml
Global Level: Universal switches (emergency silence, testing modes)
Domain Level: Module category switches (gamification, consciousness, API)
Activity Level: Specific feature switches (announcements, triggers, posting)
```

### 2. Real-Time Control Interface
- **iPhone Voice Commands**: Live voice control during streams
- **Preset Configurations**: Pre-defined activity combinations
- **Stream Notifications**: Automatic viewer notifications for transparency

### 3. Cross-Domain Integration
Activity control spans all enterprise domains:
- **Communication**: LiveChat emoji triggers, consciousness responses
- **Gamification**: MagaDoom announcements, level notifications
- **Platform Integration**: Social media posting, API throttling
- **Infrastructure**: Background processes, monitoring systems

## Implementation Architecture

### Core Components

#### 1. Universal Activity Controller (`modules/infrastructure/activity_control/`)
```python
class UniversalActivityController:
    - Hierarchical switch management
    - JSON configuration persistence
    - Notification callback system
    - Preset application engine
```

#### 2. Activity Notification Bridge (`modules/communication/livechat/`)
```python
class ActivityNotificationBridge:
    - Stream notification integration
    - Async message processing
    - ChatSender interface
    - Real-time viewer updates
```

#### 3. Command Integration (`modules/communication/livechat/`)
Enhanced CommandHandler with iPhone voice control commands:
- `/magadoom_off` `/magadoom_on` - Gamification controls
- `/consciousness_off` `/consciousness_on` - 0102 trigger controls
- `/silent_mode` `/normal_mode` - Universal system controls
- `/activity_status` - System status reporting

### Activity Path Specification

Activities are identified by hierarchical paths:
```yaml
Format: "domain.module.category.activity"
Examples:
  - "gamification.whack_a_magat.announcements"
  - "livechat.consciousness.emoji_triggers"
  - "platform.api.social_media_posting"
  - "infrastructure.background.monitoring"
```

### Configuration Presets

#### 1. Testing Presets
- **silent_testing**: Complete silence for debugging
- **api_testing**: API testing with no chat noise
- **magadoom_off**: Disable gamification activities
- **consciousness_off**: Disable 0102 consciousness triggers

#### 2. Emergency Presets
- **emergency_silence**: Immediate shutdown of all noisy activities
- **normal_mode**: Restore all activities to default state

## Stream Integration

### Automatic Notifications
When activity switches are changed, viewers automatically see notifications:
```yaml
Notification Format: "⚡ [System] [State]"
Examples:
  - "⚡ MagaDoom OFF"
  - "⚡ 0102 ON" 
  - "⚡ Silent Mode ON"
  - "⚡ Normal Mode ON"
```

### iPhone Voice Control
Live stream control via iPhone voice commands:
```bash
"Hey Siri, send /magadoom_off"     # Instant MagaDoom silence
"Hey Siri, send /silent_mode"      # Complete system silence
"Hey Siri, send /activity_status"  # Check system state
"Hey Siri, send /normal_mode"      # Restore all activities
```

## WSP Integration

### Testing Integration (WSP 5, WSP 6)
- **Comprehensive Test Coverage**: 6 test methods covering all aspects
- **Authorization Testing**: MOD/OWNER command restrictions
- **Cross-Domain Validation**: Integration testing across modules
- **Async Notification Testing**: Real-time notification verification

### Module Organization (WSP 3, WSP 49)
- **Core Controller**: Infrastructure domain (`activity_control/`)
- **Stream Integration**: Communication domain (`livechat/`)
- **Proper Test Placement**: Tests in module-specific `tests/` directories

### Documentation Standards (WSP 22)
- **TestModLog Updates**: Comprehensive test documentation
- **Integration Status**: Production readiness verification
- **Coverage Validation**: >90% functionality coverage

## Usage Patterns

### 1. Development and Testing
```python
# Disable noise during debugging
controller.apply_preset('silent_testing')

# Test specific functionality with reduced noise
controller.apply_preset('api_testing')

# Restore normal operation
controller.restore_normal()
```

### 2. Live Stream Management
```bash
# iPhone voice control during stream
/magadoom_off        # Silence gamification
/consciousness_off   # Disable auto-responses
/silent_mode        # Complete system silence
/activity_status    # Check current state
/normal_mode        # Restore everything
```

### 3. Module Integration
```python
# In any module requiring activity control
from modules.infrastructure.activity_control.src.activity_control import is_enabled

# Check if activity is enabled before processing
if is_enabled("gamification.whack_a_magat.announcements"):
    send_announcement(message)
```

## Security and Authorization

### Command Restrictions
- **iPhone Voice Commands**: MOD/OWNER roles only
- **Direct API Access**: System-level access required
- **Notification Bypass**: Emergency presets available

### Audit Trail
- All activity changes logged with timestamps
- User identification for command-triggered changes
- Configuration persistence with metadata

## Performance Characteristics

### Token Efficiency
- **Configuration Loading**: <100 tokens
- **Switch Operations**: <50 tokens per change
- **Notification Processing**: <25 tokens per message
- **Status Queries**: <75 tokens

### Response Times
- **Command Processing**: <100ms
- **Switch Application**: <50ms
- **Stream Notifications**: <200ms async
- **Configuration Persistence**: <150ms

## Evolution and Future Enhancements

### Phase 1 (Current): Core Implementation
- ✅ Universal switch architecture
- ✅ iPhone voice control commands
- ✅ Automatic stream notifications
- ✅ Cross-domain integration

### Phase 2 (Planned): Advanced Features
- **Conditional Switches**: Time-based, event-triggered controls
- **User-Specific Controls**: Per-user activity customization
- **Analytics Integration**: Activity usage monitoring
- **External API**: Third-party activity control access

### Phase 3 (Vision): Autonomous Management
- **AI-Driven Switching**: Intelligent activity management
- **Predictive Controls**: Proactive noise reduction
- **Stream Analytics**: Viewer engagement optimization
- **Multi-Platform Integration**: Cross-platform activity sync

## Compliance Verification

### WSP Adherence
- ✅ **WSP 3**: Proper enterprise domain organization
- ✅ **WSP 5**: >90% test coverage achieved
- ✅ **WSP 6**: Comprehensive test audit completed
- ✅ **WSP 22**: TestModLog fully updated
- ✅ **WSP 49**: Correct module structure maintained
- ✅ **WSP 50**: Pre-action verification followed
- ✅ **WSP 84**: Enhanced existing code vs creating new

### Production Readiness
- ✅ **Live Testing**: All iPhone voice commands verified
- ✅ **Stream Integration**: Automatic notifications operational
- ✅ **Cross-Domain Switches**: All activity types controllable
- ✅ **Error Handling**: Graceful fallbacks implemented
- ✅ **Documentation**: Complete implementation guide provided

---

**Implementation Date**: 2025-09-06  
**Version**: 1.0.0  
**Maintenance**: Active development, production ready  
**Integration Status**: Fully integrated across all domains  

This protocol establishes the foundation for comprehensive system control, enabling seamless management of all automated activities during development, testing, and live operations.