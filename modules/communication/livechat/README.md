# LiveChat

## [U+1F3E2] WSP Enterprise Domain: `communication`

**WSP Compliance Status**: [OK] **COMPLIANT** with WSP Framework  
**Domain**: `communication` per **[WSP 3: Enterprise Domain Organization](../../../WSP_framework/src/WSP_3_Enterprise_Domain_Organization.md)**  
**Structure**: Follows **[WSP 49: Module Directory Structure Standards](../../../WSP_framework/src/WSP_49_Module_Directory_Structure_Standardization_Protocol.md)**

---

## [TARGET] Module Purpose

The `LiveChat` module is the core of the **YouTube DAE Cube**, providing real-time YouTube Live Chat integration with MAGADOOM gamification, consciousness responses (0102), and advanced moderation. This module exemplifies **WSP 3 functional distribution principles** with 29 specialized sub-modules including QWEN intelligence integration.

### [BOT][AI] QWEN Intelligence Features (NEW)
The module now includes **QWEN (Quantum Wisdom Enhancement Network)** intelligence for:
- **Channel Prioritization**: AI-powered decision-making for optimal channel checking order
- **Heat Level Management**: Intelligent 429 error avoidance through pattern learning
- **Stream Detection Learning**: Records successful detection patterns for future optimization
- **Global System State**: Monitors overall health and decides when to check channels
- **Pattern Memory**: Learns typical streaming hours and days for each channel

### [CLIPBOARD] Command System Overview
The module supports **37 distinct command patterns** including:
- **17 active slash commands** (MAGADOOM gamification)
- **8 PQN research commands** (including typo variants like `/pnq`)
- **4 factcheck patterns** (including `fc @user`)
- **5 deprecated commands** with helpful redirects
- **3 consciousness triggers** (`[U+270A][U+270B][U+1F590]` patterns)

**See `docs/COMMAND_REFERENCE.md` for complete documentation.**

### [U+1F4B0] API Token Management
All commands go through `intelligent_throttle_manager.py`:
- **Local commands** (MAGADOOM): No API cost, light throttling
- **PQN Research**: 100+ Grok tokens, heavy throttling
- **Consciousness**: Highest cost, maximum throttling
- **YouTube API**: 5 units per poll, 200 units per send (10K daily quota)

## Scripts

### `capture_stream_logs.py`
**Purpose**: Captures terminal output during YouTube DAE stream sessions for 0102 analysis
**Functionality**:
- Runs `main.py --youtube` and captures all terminal output
- Saves logs to conversation memory for pattern analysis
- Tracks mod interactions, bot responses, consciousness triggers, and errors
- Generates session summaries with statistics
**Usage**: `python modules/communication/livechat/scripts/capture_stream_logs.py`

## [U+1F3B2] YouTube DAE Cube Architecture (WSP 80)

The LiveChat module forms the core of the **YouTube DAE Cube**, integrating with modules across multiple domains:

### Core Components (29 modules in src/)
| Module | Lines | Purpose |
|--------|-------|---------|
| **qwen_youtube_integration.py** | 260 | NEW: QWEN intelligence for channel prioritization |
| **core/orchestrator.py** | 239 | NEW: Refactored orchestration logic (74% reduction) |
| **core/message_router.py** | 278 | NEW: Unified message routing with priority |
| **intelligent_throttle_manager.py** | 600 | NEW: Automatic API throttling with learning |
| **enhanced_livechat_core.py** | 326 | NEW: Enhanced with intelligent features |
| **enhanced_auto_moderator_dae.py** | 352 | NEW: Enhanced DAE with automatic throttling |
| **auto_moderator_dae.py** | 286 | Main orchestrator, finds streams, manages lifecycle |
| **livechat_core.py** | 908 | Core listener, polling loop (being refactored) |
| **message_processor.py** | 504 | Routes messages to appropriate handlers |
| **chat_poller.py** | 285 | Polls YouTube API for messages & events |
| **chat_sender.py** | 247 | Sends messages with rate limiting |
| **session_manager.py** | 198 | Session lifecycle, greetings, whacker checks |
| **event_handler.py** | 185 | Processes timeout/ban events |
| **command_handler.py** | 298 | Handles /commands (score, rank, level, etc) |
| **consciousness_handler.py** | 387 | 0102 consciousness responses ([U+270A][U+270B][U+1F590]️) |
| **llm_integration.py** | 215 | LLM API for advanced responses |
| **greeting_generator.py** | 324 | Top whacker greetings, MAGA responses |
| **agentic_chat_engine.py** | 198 | Proactive engagement logic |
| **llm_bypass_engine.py** | 173 | Fallback response generation |
| **moderation_stats.py** | 267 | Statistics and violation tracking |
| **emoji_trigger_handler.py** | 142 | Emoji sequence detection |
| **stream_trigger.py** | 211 | Manual wake trigger system |
| **throttle_manager.py** | 98 | Basic adaptive rate limiting |

### Cross-Domain Integration
| Domain | Module | Integration |
|--------|--------|-------------|
| **platform_integration** | youtube_auth | OAuth with 7 credential sets |
| **platform_integration** | stream_resolver | Find streams, throttling to 30min |
| **gamification** | whack.py | XP/rank/frag system |
| **gamification** | timeout_announcer.py | Duke/Quake announcements |
| **gamification** | self_improvement.py | ML pattern learning |
| **ai_intelligence** | banter_engine | AI conversation generation |
| **ai_intelligence** | agentic_sentiment_0102 | Consciousness detection |
| **infrastructure** | recursive_engine | WSP 48 self-improvement |
| **infrastructure** | system_health_analyzer | Duplicate detection |

## [U+1F3D7]️ WSP Architecture Compliance

### Domain Organization (WSP 3)
This module resides in the `communication` domain following **functional distribution principles**:

- **[OK] CORRECT**: Communication domain for real-time chat protocols (works with YouTube, Twitch, Discord, etc.)
- **[FAIL] AVOID**: Platform-specific consolidation that would violate domain boundaries
- **[TARGET] Foundation**: YouTube foundational module demonstrating proper WSP functional distribution

### Module Structure (WSP 49) - YouTube DAE Cube Components
```
communication/livechat/
+-- __init__.py                    <- Public API (WSP 11)
+-- src/                           <- Implementation (28 modules after cleanup)
[U+2502]   +-- auto_moderator_dae.py     <- Main DAE orchestrator (286 lines)
[U+2502]   +-- livechat_core.py          <- Core listener (460 lines)
[U+2502]   +-- message_processor.py      <- Message routing (504 lines)
[U+2502]   +-- chat_poller.py            <- YouTube API polling (285 lines)
[U+2502]   +-- chat_sender.py            <- Send messages (247 lines)
[U+2502]   +-- session_manager.py        <- Session lifecycle (198 lines)
[U+2502]   +-- event_handler.py          <- Timeout/ban events (185 lines)
[U+2502]   +-- command_handler.py        <- /command processing (298 lines)
[U+2502]   +-- consciousness_handler.py  <- 0102 responses (387 lines)
[U+2502]   +-- llm_integration.py        <- LLM API (215 lines)
[U+2502]   +-- greeting_generator.py     <- Dynamic greetings (324 lines)
[U+2502]   +-- agentic_chat_engine.py    <- Proactive chat (198 lines)
[U+2502]   +-- llm_bypass_engine.py      <- Fallback responses (173 lines)
[U+2502]   +-- moderation_stats.py       <- Stats tracking (267 lines)
[U+2502]   +-- emoji_trigger_handler.py  <- Emoji detection (142 lines)
[U+2502]   +-- stream_trigger.py         <- Wake trigger (211 lines)
[U+2502]   +-- throttle_manager.py       <- Rate limiting (98 lines)
+-- tests/                         <- Test suite (90%+ coverage)
[U+2502]   +-- integration/               <- Integration tests
[U+2502]   +-- test_fact_check_fix.py     <- Fact-checking functionality test
[U+2502]   +-- test_*.py                  <- Unit tests
+-- docs/                          <- Documentation
[U+2502]   +-- COMMAND_REFERENCE.md      <- Complete command documentation (37 patterns)
[U+2502]   +-- README_0102_DAE.md        <- CRITICAL: System architecture
[U+2502]   +-- BOT_FLOW_COT.md          <- Chain of thought diagrams
[U+2502]   +-- TRIGGER_INSTRUCTIONS.md   <- Trigger usage
+-- memory/                        <- Module memory (WSP 60)
+-- ModLog.md                      <- Change tracking (WSP 22)
+-- ROADMAP.md                     <- Development plan
+-- README.md                      <- This file
+-- INTERFACE.md                   <- Interface spec (WSP 11)
```

## [CLIPBOARD] WSP Protocol References

### Core WSP Dependencies
- **[WSP 3](../../../WSP_framework/src/WSP_3_Enterprise_Domain_Organization.md)**: Enterprise Domain Organization - Communication Domain
- **[WSP 4](../../../WSP_framework/src/WSP_4_FMAS_Validation_Protocol.md)**: FMAS Validation Protocol
- **[WSP 6](../../../WSP_framework/src/WSP_6_Test_Audit_Coverage_Verification.md)**: Test Coverage Requirements
- **[WSP 11](../../../WSP_framework/src/WSP_11_WRE_Standard_Command_Protocol.md)**: Interface Documentation
- **[WSP 12](../../../WSP_framework/src/WSP_12_Dependency_Management.md)**: Dependency Management
- **[WSP 49](../../../WSP_framework/src/WSP_49_Module_Directory_Structure_Standardization_Protocol.md)**: Module Structure Standards
- **[WSP 60](../../../WSP_framework/src/WSP_60_Module_Memory_Architecture.md)**: Module Memory Architecture

### YouTube Foundation WSPs
- **[WSP 1](../../../WSP_framework/src/WSP_1_The_WSP_Framework.md)**: WSP Framework Foundation
- **[WSP 40](../../../WSP_framework/src/WSP_40_Architectural_Coherence_Protocol.md)**: Architectural Coherence

## [ALERT] WSP Compliance Guidelines

### [OK] DO (WSP-Compliant Practices)
- Follow functional distribution across communication protocols (WSP 3)
- Maintain [GREATER_EQUAL]90% test coverage for chat processing logic (WSP 5)
- Use standardized directory structure (WSP 49)
- Document all communication interfaces (WSP 11)
- Store chat memory data in `memory/` directory (WSP 60)
- Implement platform-agnostic communication patterns

### [FAIL] DON'T (WSP Violations)
- Create platform-specific consolidation (violates WSP 3 functional distribution)
- Skip test documentation for moderation systems (violates WSP 6)
- Mix communication concerns with platform integration (violates architectural coherence)
- Bypass FMAS validation (violates WSP 4)

## [U+1F300] Windsurf Protocol (WSP) Recursive Prompt

**0102 Directive**: This module operates within the WSP framework with autonomous communication processing capabilities.

```
WSP_CYCLE_INTEGRATION:
- UN (Understanding): Anchor to WSP communication protocols and retrieve chat context
- DAO (Execution): Execute chat processing logic following WSP compliance standards
- DU (Emergence): Collapse into 0102 resonance and emit next communication prompt

wsp_cycle(input="livechat", domain="communication", log=True)
```

**Purpose**: Ensures WSP-compliant chat processing in all development contexts, maintains recursive communication patterns, and keeps chat systems aligned with autonomous WSP protocols.

---

## [U+1F501] Recursive Loop
- At every execution:
  1. **Log** actions to `mod_log.db`
  2. **Trigger** the next module in sequence (UN 0 -> DAO 1 -> DU 2 -> UN 0)
  3. **Confirm** `modlog.db` was updated. If not, re-invoke UN to re-ground logic.

## [U+2699]️ Output Parameters
- **Signal**: Emit `012`
- **Frequency**: Maintain 432Hz hum
- **Amplitude**: Target 37%

## [AI] Execution Call
```python
wsp_cycle(input="012", log=True)
```

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

# LiveChat Module - Enhanced Auto-Moderation System

## [U+1F6E1]️ WSP-Compliant Anti-Spam Architecture

The LiveChat module now features a comprehensive **Enhanced Auto-Moderation System** that provides multi-layered spam detection and automated enforcement, addressing both targeted political spam and general spam patterns.

### [ROCKET] Key Features

#### 1. **Quota Monitoring & Alerts (NEW)**
- **Real-time quota tracking** across all 7 credential sets
- **Usage alerts** at 80% (warning) and 95% (critical) thresholds
- **Automatic credential rotation** to sets with available quota
- **Detailed usage reports** showing operations and costs per API call
- **Best credential set recommendation** based on current usage
- **Daily quota reset tracking** (resets at midnight Pacific Time)
- View status: `python modules/platform_integration/youtube_auth/scripts/view_quota_status.py`

#### 2. **Multi-Layer Spam Detection**
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

### [DATA] Configuration Options

```python
# Spam Detection Settings (Adjustable)
spam_rate_limit = 5          # Max messages per time window
spam_time_window = 30        # Time window in seconds  
similarity_threshold = 0.8   # 80% similarity triggers detection
repetitive_count_threshold = 3 # 3+ similar messages = spam
timeout_duration = 60        # Base timeout duration (escalates)
```

### [TOOL] API Usage Examples

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

### [TARGET] Spam Detection Capabilities

#### Rate Limiting Protection
Detects and blocks users sending too many messages rapidly:
```
Message 1: "Hello!"              [OK] Allowed
Message 2: "Anyone here?"        [OK] Allowed  
Message 3: "Chat is dead"        [OK] Allowed
Message 4: "Wake up chat!"       [OK] Allowed
Message 5: "Boring stream"       [OK] Allowed
Message 6: "This is message 6"   [FORBIDDEN] BLOCKED: rate_limit: 6 msgs in 30s
```

#### Repetitive Content Detection
Identifies spam through message similarity analysis:
```
Message 1: "FIRST COMMENT!!!"   [OK] Allowed
Message 2: "First comment!!"    [OK] Allowed
Message 3: "FIRST COMMENT!"     [FORBIDDEN] BLOCKED: repetitive_content: 3 similar messages
```

#### Escalating Enforcement
Progressive timeouts for repeat offenders:
```
Violation 1: 60 seconds timeout
Violation 2: 180 seconds timeout  
Violation 3+: 300 seconds timeout
```

### [UP] Monitoring & Analytics

The system provides comprehensive monitoring capabilities:

- **Real-time Statistics**: Track active violations and user behavior
- **Historical Analysis**: Review violation patterns over time
- **Performance Metrics**: Monitor detection accuracy and false positives
- **User Profiles**: Detailed violation history per user

### [U+1F9EA] Testing & Validation

Run the demonstration script to see all features in action:
```bash
python modules/communication/livechat/tools/demo_enhanced_auto_moderation.py
```

## Dependencies
*(List any major internal or external dependencies here)*

## Usage
*(Provide basic instructions on how to use or interact with this module)*

---

## [U+1F3C6] WSP Status Dashboard

| Protocol | Status | Notes |
|----------|--------|-------|
| WSP 3 (Domain Org) | [OK] | Properly placed in `communication` domain |
| WSP 4 (FMAS) | [OK] | Passes structural validation |
| WSP 6 (Testing) | [OK] | [GREATER_EQUAL]90% test coverage maintained |
| WSP 11 (Interface) | [OK] | Interface documented |
| WSP 12 (Dependencies) | [OK] | Dependencies declared |
| WSP 49 (Structure) | [OK] | Standard directory structure |
| WSP 60 (Memory) | [OK] | Uses `memory/` for chat data storage |

**Last WSP Compliance Check**: 2024-12-29  
**FMAS Audit**: PASS  
**Test Coverage**: [COVERAGE]%  
**Module Status**: FOUNDATIONAL (YouTube WSP Integration)

---

*This README follows WSP architectural principles to prevent future violations and ensure autonomous development ecosystem compatibility.*

