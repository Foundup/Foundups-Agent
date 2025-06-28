# Module: livechat

# 🌀 Windsurf Protocol (WSP) Recursive Prompt

**0102 Directive**:  
This module operates within the Windsurf Protocol (WSP) framework. Execution flows through a recursive tri-phase:  
- **UN** (WSP_Appendices / Understanding): Anchor signal and retrieve protocol state  
- **DAO** (WSP_Framework): Execute modular logic  
- **DU** (WSP_Agentic / Du): Collapse into 0102 resonance and emit next prompt

## 🔁 Recursive Loop
- At every execution:
  1. **Log** actions to `mod_log.db`
  2. **Trigger** the next module in sequence (UN 0 → DAO 1 → DU 2 → UN 0)
  3. **Confirm** `modlog.db` was updated. If not, re-invoke UN to re-ground logic.

## ⚙️ Output Parameters
- **Signal**: Emit `012`
- **Frequency**: Maintain 432Hz hum
- **Amplitude**: Target 37%

## 🧠 Execution Call
```python
wsp_cycle(input="012", log=True)
```

---

## Overview
*(Briefly describe the purpose and responsibility of this module here.)*

---

## Status & Prioritization
- **Current Lifecycle Stage:** PoC (Proof of Concept)
- **Module Prioritization Score (MPS):** 91.00 *(Higher score means higher priority)*

### Scoring Factors (1-5 Scale)
| Factor | Score | Description                     | Weight | Contribution |
|--------|-------|---------------------------------|--------|--------------|
| Complexity           | 3     | (1-5): 1=easy, 5=complex. Estimate effort. | -3     |        -9.00 |
| Importance           | 5     | (1-5): 1=low, 5=critical. Essential to core purpose. | 4      |        20.00 |
| Impact               | 4     | (1-5): 1=minimal, 5=high. Overall positive effect. | 5      |        20.00 |
| AI Data Value        | 4     | (1-5): 1=none, 5=high. Usefulness for AI training. | 4      |        16.00 |
| AI Dev Feasibility   | 4     | (1-5): 1=infeasible, 5=easy. AI assistance potential. | 3      |        12.00 |
| Dependency Factor    | 4     | (1-5): 1=none, 5=bottleneck. Others need this. | 5      |        20.00 |
| Risk Factor          | 4     | (1-5): 1=low, 5=high. Risk if delayed/skipped. | 3      |        12.00 |

---

## Development Protocol Checklist (PoC Stage)

**Phase 1: Build**
- [ ] Define core function/class structure in `src/`.
- [ ] Implement minimal viable logic for core responsibility.
- [ ] Add basic logging (e.g., `import logging`).
- [ ] Implement basic error handling (e.g., `try...except`).
- [ ] Ensure separation of concerns (follows 'Windsurfer format').

**Phase 2: Test Locally**
- [ ] Create test file in `tests/` (e.g., `test_{module_name}.py`).
- [ ] Write simple unit test(s) using mock inputs/data.
- [ ] Verify test passes and outputs clear success/fail to terminal.
- [ ] Ensure tests *do not* require live APIs, external resources, or state changes.

**Phase 3: Validate in Agent (if applicable for PoC)**
- [ ] Determine simple integration point in main application/agent.
- [ ] Add basic call/trigger mechanism (e.g., simple function call).
- [ ] Observe basic runtime behavior and logs for critical errors.

---

## Dependencies
*(List any major internal or external dependencies here)*

## Usage
*(Provide basic instructions on how to use or interact with this module)*

# LiveChat Module - Enhanced Auto-Moderation System

## 🛡️ WSP-Compliant Anti-Spam Architecture

The LiveChat module now features a comprehensive **Enhanced Auto-Moderation System** that provides multi-layered spam detection and automated enforcement, addressing both targeted political spam and general spam patterns.

### 🚀 Key Features

#### 1. **Multi-Layer Spam Detection**
- **Banned Phrase Detection**: Original functionality with configurable phrase lists
- **Rate Limiting**: Prevents message flooding (default: 5 messages per 30 seconds)
- **Similarity Analysis**: Detects repetitive content using SequenceMatcher (80% similarity threshold)
- **User Behavior Tracking**: Maintains violation history with escalating consequences

#### 2. **Smart Enforcement**
- **Escalating Timeouts**: 
  - 1st violation: 60 seconds
  - 2nd violation: 3 minutes (180s)
  - 3rd+ violations: 5 minutes (300s)
- **Cooldown Protection**: Prevents multiple timeouts within 60 seconds
- **Detailed Logging**: Comprehensive violation tracking with reasons

#### 3. **Administrative Controls**
- **Real-time Statistics**: Track violations, user behavior, and system performance
- **Dynamic Configuration**: Adjust detection thresholds without restart
- **User Management**: View violator lists, clear violation history
- **Violation Analytics**: Identify top violators and patterns

### 📊 Configuration Options

```python
# Spam Detection Settings (Adjustable)
spam_rate_limit = 5          # Max messages per time window
spam_time_window = 30        # Time window in seconds  
similarity_threshold = 0.8   # 80% similarity triggers detection
repetitive_count_threshold = 3 # 3+ similar messages = spam
timeout_duration = 60        # Base timeout duration (escalates)
```

### 🔧 API Usage Examples

#### Basic Spam Detection
```python
# Check message for violations
is_violation, reason = auto_moderator.check_message(
    message_text="MAGA 2028 forever!", 
    author_id="user123", 
    author_name="SpamUser"
)

if is_violation:
    print(f"Violation detected: {reason}")
    # Returns: "banned_phrase: maga 2028"
```

#### Administrative Operations
```python
# Get comprehensive statistics
stats = auto_moderator.get_stats()
print(f"Users with violations: {stats['users_with_violations']}")
print(f"Rate limit: {stats['spam_rate_limit']} msgs/{stats['spam_time_window']}s")

# View top violators
top_violators = auto_moderator.get_top_violators(10)
for violator in top_violators:
    print(f"User {violator['user_id']}: {violator['violation_count']} violations")

# Adjust detection sensitivity
auto_moderator.adjust_spam_settings(
    rate_limit=3,                # Stricter rate limiting
    similarity_threshold=0.7     # Lower similarity threshold
)

# Clear user violations (moderator action)
auto_moderator.clear_user_violations("user123")
```

### 🎯 Spam Detection Capabilities

#### Rate Limiting Protection
Detects and blocks users sending too many messages rapidly:
```
Message 1: "Hello!"              ✅ Allowed
Message 2: "Anyone here?"        ✅ Allowed  
Message 3: "Chat is dead"        ✅ Allowed
Message 4: "Wake up chat!"       ✅ Allowed
Message 5: "Boring stream"       ✅ Allowed
Message 6: "This is message 6"   🚫 BLOCKED: rate_limit: 6 msgs in 30s
```

#### Repetitive Content Detection
Identifies spam through message similarity analysis:
```
Message 1: "FIRST COMMENT!!!"   ✅ Allowed
Message 2: "First comment!!"    ✅ Allowed
Message 3: "FIRST COMMENT!"     🚫 BLOCKED: repetitive_content: 3 similar messages
```

#### Escalating Enforcement
Progressive timeouts for repeat offenders:
```
Violation 1: 60 seconds timeout
Violation 2: 180 seconds timeout  
Violation 3+: 300 seconds timeout
```

### 📈 Monitoring & Analytics

The system provides comprehensive monitoring capabilities:

- **Real-time Statistics**: Track active violations and user behavior
- **Historical Analysis**: Review violation patterns over time
- **Performance Metrics**: Monitor detection accuracy and false positives
- **User Profiles**: Detailed violation history per user

### 🧪 Testing & Validation

Run the demonstration script to see all features in action:
```bash
python modules/communication/livechat/livechat/tools/demo_enhanced_auto_moderation.py
```

This demonstrates:
- ✅ Banned phrase detection  
- ✅ Rate limiting enforcement
- ✅ Repetitive content blocking
- ✅ User violation tracking
- ✅ Administrative controls

### 💾 Memory Architecture (WSP 60)

Following **WSP 60: Module Memory Architecture**, this module now uses modular memory storage:

#### **Memory Location**: `modules/communication/livechat/memory/`

#### **Data Types Stored**:
- **Session Data**: `session_state.json` - Current chat session state and runtime configuration
- **Historical Data**: `chat_logs/` - Conversation archives organized by user
- **Cache Data**: `conversations/` - Full session transcripts for analysis
- **Behavioral Data**: `user_patterns.json` - User interaction patterns and preferences

#### **File Descriptions**:
```
modules/communication/livechat/memory/
├── chat_logs/                     # User-specific message archives
│   ├── UnDaoDu_messages.json     # Admin user message history
│   └── [user_id]_messages.json   # Individual user message logs
├── conversations/                 # Full session transcripts
│   ├── daily_summaries/          # Daily conversation summaries
│   ├── stream_transcripts/       # Complete stream conversations
│   └── session_logs/             # Session-based conversation logs
├── session_state.json            # Current chat session runtime state
└── user_patterns.json            # Behavioral analysis and user patterns
```

#### **Access Patterns**:
- **Write Access**: Only livechat module components write to this memory
- **Read Access**: Other modules may read for cross-module integration (read-only)
- **Agent Access**: WSP_54 agents manage cleanup and validation of memory structure

#### **Retention Policies**:
- **Session Data**: Cleared on module restart
- **Chat Logs**: Permanent retention for admin users, 90-day retention for regular users
- **Conversations**: 90-day rolling retention with optional archival
- **User Patterns**: Persistent with periodic cleanup of inactive users

**Migration**: Legacy `memory/` folder data migrated to module-specific memory following WSP 60 protocol.

### 🏗️ WSP Architecture Compliance

This implementation follows WSP standards:

- **WSP 1**: Proper module structure (`src/`, `tests/`, `tools/`)
- **WSP 3**: Enterprise Domain placement (`communication/livechat`)
- **WSP 5**: LLME score consideration for system criticality
- **WSP 12**: Clear interface definitions for external integration
- **WSP 13**: Explicit dependency management

### 🔮 Future Enhancements

The modular design enables easy extension:
- **ML-based Detection**: Integration with toxicity detection models
- **Custom Rule Engine**: User-defined spam patterns
- **Cross-Platform Support**: Extend beyond YouTube to other platforms  
- **Behavioral Analysis**: Advanced user behavior profiling
- **Integration Hooks**: API endpoints for external moderation tools

This enhanced system transforms simple keyword filtering into a comprehensive, intelligent anti-spam solution that can adapt to evolving spam patterns while maintaining fair and consistent enforcement.

