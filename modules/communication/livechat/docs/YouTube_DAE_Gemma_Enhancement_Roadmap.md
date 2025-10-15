# YouTube DAE Gemma Enhancement Roadmap

**Status**: Implementation Planning
**Architect**: 0102
**Triggered By**: 012: "Map all YouTube .py modules, identify Gemma enhancement opportunities, extract 012's behavior patterns, build POC"
**WSP Protocols**: WSP 50 (Pre-Action), WSP 80 (DAE Cube), WSP 93 (CodeIndex Surgical), WSP 46 (WRE)

## HoloIndex Discovery Results

### YouTube DAE Module Inventory

**Total**: 9 modules, 231 Python files

#### 1. Core Livechat Module (160 files)
**Location**: `modules/communication/livechat/`

**Key Components**:
- `message_processor.py` (1240 lines) - Intent classification, message routing, spam detection
- `auto_moderator_dae.py` (795 lines) - Spam filtering, timeout logic, rule enforcement
- `command_handler.py` (435 lines) - Chat command parsing and execution
- `livechat_core.py` (1102 lines) - Core orchestration, session management
- `intelligent_throttle_manager.py` (1058 lines) - Rate limiting, quota management
- `qwen_youtube_integration.py` (500 lines) - Qwen AI coordination layer
- `mcp_youtube_integration.py` (491 lines) - MCP protocol integration
- `agentic_chat_engine.py` (498 lines) - AI-driven chat responses
- `event_handler.py` (492 lines) - YouTube event processing
- `chat_memory_manager.py` (492 lines) - Conversation context management

**Test Coverage**: 65 tests across module

#### 2. Chat Rules Module (10 files)
**Location**: `modules/communication/chat_rules/`

**Key Components**:
- `commands.py` (938 lines) - Command definitions and handlers
- `database.py` (475 lines) - Rule storage and retrieval

**Test Coverage**: 3 tests

#### 3. YouTube Shorts Module (22 files)
**Location**: `modules/communication/youtube_shorts/`

**Key Components**:
- `chat_commands.py` (731 lines) - Shorts-specific commands
- `shorts_orchestrator.py` (534 lines) - Shorts creation workflow
- `veo3_generator.py` (554 lines) - Veo3 video generation

**Test Coverage**: 7 tests

#### 4. Video Comments Module (12 files)
**Location**: `modules/communication/video_comments/`

**Key Components**:
- `realtime_comment_dialogue.py` (430 lines) - Comment-based conversations

**Test Coverage**: 6 tests

#### 5-9. Supporting Modules
- `live_chat_poller` (6 files) - Polling mechanism for live chat
- `live_chat_processor` (6 files) - Chat message processing pipeline
- `youtube_api_operations` (6 files) - YouTube Data API operations
- `youtube_proxy` (9 files) - API quota management and proxy routing

## WRE Architecture: Qwen + Gemma Integration

### Current State
```
012 (Human)
  ↓
0102 (Digital Twin - learns 012's patterns)
  ↓
🤖🧠 Qwen (Agentic Coordination - 1.5B)
  ↓
Modules (Rule-based logic)
```

### Target State (WRE with Gemma)
```
012 (Human)
  ↓
0102 (Digital Twin - learns 012's patterns)
  ↓
🤖🧠 Qwen (Agentic Coordination - 1.5B, 250ms)
  ↓
🤖🧠👶 Gemma (Specialized Functions - 270M, 50-100ms)
  ↓  ↓  ↓  ↓  ↓
  message_processor, auto_moderator, command_handler, throttle_manager, event_handler
  (Each module learns 012's patterns autonomously)
```

## Gemma Enhancement Opportunities by Module

### Priority Matrix (MPS Scoring)

#### P0 - Critical Path (MPS 16-20)

**1. message_processor.py Enhancement**
- **MPS**: 18 (C:4, I:5, D:2, P:5) - P0
- **Current**: 300+ lines of regex-based intent classification (lines 113-400)
- **Gemma Role**: Learn 012's intent patterns from chat history
- **Training Source**: 012's message history + response patterns
- **Token Cost**: 3-5K implementation, 2K training data extraction
- **Impact**: Replaces 300 lines of brittle regex with learned patterns
- **POC Module**: ✅ **START HERE**

**2. auto_moderator_dae.py Enhancement**
- **MPS**: 17 (C:3, I:5, D:2, P:5) - P0
- **Current**: Rule-based spam detection (lines 200-450)
- **Gemma Role**: Learn 012's moderation decisions (who gets timeout, why)
- **Training Source**: 012's timeout actions + context (user history, message content)
- **Token Cost**: 4-6K implementation, 3K training extraction
- **Impact**: Learns when 012 would timeout vs ignore
- **POC Module**: Second implementation after message_processor

#### P1 - High Value (MPS 13-15)

**3. command_handler.py Enhancement**
- **MPS**: 15 (C:3, I:4, D:3, P:5) - P1
- **Current**: String matching for commands
- **Gemma Role**: Learn natural language command variants
- **Training Source**: 012's command usage patterns
- **Token Cost**: 2-4K implementation

**4. intelligent_throttle_manager.py Enhancement**
- **MPS**: 14 (C:4, I:3, D:3, P:4) - P1
- **Current**: Fixed rate limits
- **Gemma Role**: Adaptive throttling based on context
- **Training Source**: 012's throttle adjustments during streams
- **Token Cost**: 3-5K implementation

#### P2 - Medium Value (MPS 10-12)

**5. event_handler.py Enhancement**
- **MPS**: 12 (C:3, I:3, D:3, P:3) - P2
- **Current**: Event routing logic
- **Gemma Role**: Priority classification for events
- **Token Cost**: 2-3K implementation

**6. agentic_chat_engine.py Enhancement**
- **MPS**: 11 (C:3, I:3, D:4, P:2) - P2
- **Current**: Qwen-driven responses
- **Gemma Role**: Fast response generation for common patterns
- **Token Cost**: 3-4K implementation

## Google MCP Database Toolbox Integration

### Purpose
Extract 012's behavior patterns from YouTube DAE logs for Gemma training.

### Required Tool: `extract_training_data`

**Location**: Add to `foundups-mcp-p1/servers/holo_index/server.py`

```python
@app.tool()
async def extract_training_data(self, dae_name: str, behavior_type: str, time_range: str = "last_30_days") -> dict:
    """
    Extract 012's behavior patterns from YouTube DAE logs for Gemma training.

    Args:
        dae_name: Module name (e.g., "auto_moderator_dae", "message_processor")
        behavior_type: Pattern type (e.g., "moderation_decisions", "intent_classification")
        time_range: Time window for data extraction

    Returns:
        {
            "pattern_count": int,
            "training_examples": List[dict],
            "gemma_corpus_path": str,
            "pattern_summary": dict
        }
    """
    # Implementation using Google MCP Database Toolbox
```

### Training Data Schema

**For message_processor (Intent Classification)**:
```json
{
  "input": "user message text",
  "context": {
    "user_role": "MEMBER",
    "stream_topic": "coding session",
    "recent_messages": ["..."]
  },
  "label": "QUESTION",  // 012's actual classification
  "confidence": 0.95
}
```

**For auto_moderator (Moderation Decisions)**:
```json
{
  "input": "user message text",
  "context": {
    "user_history": ["previous messages"],
    "violation_type": "spam",
    "stream_context": "discussion"
  },
  "action": "TIMEOUT_60",  // 012's actual decision
  "reasoning": "repeated spam pattern"
}
```

## POC Implementation Plan

### Phase 1: Database Toolbox Setup (2-3K tokens)
1. Check if Google MCP Database Toolbox module exists (HoloIndex search)
2. If not exists: Install Google MCP Database Toolbox
3. Configure connection to YouTube DAE log database
4. Test database query access

### Phase 2: Training Data Extraction (3-5K tokens)
1. Implement `extract_training_data` tool in HoloIndex MCP
2. Query YouTube DAE logs for 012's behavior patterns
3. Extract message_processor intent classification examples
4. Generate Gemma training corpus (JSON format)
5. Store in ChromaDB for fast retrieval

### Phase 3: Gemma Integration POC - message_processor (5-8K tokens)
1. Read current [message_processor.py:113-400](modules/communication/livechat/src/message_processor.py#L113-L400) (intent classification logic)
2. Create `message_processor_gemma_enhanced.py`:
   - Load Gemma 3 270M model
   - Implement intent classification with learned patterns
   - Add fallback to Qwen for complex cases
   - Adaptive router (Gemma → Qwen escalation if confidence < threshold)
3. Create training script using extracted 012 patterns
4. Test accuracy vs current regex system

### Phase 4: Testing & Validation (2-3K tokens)
1. Run tests: Compare Gemma classifications vs 012's actual decisions
2. Measure: Accuracy, latency (target <100ms), confidence scores
3. Tune: Adjust complexity threshold for Qwen escalation
4. Document: Pattern learning effectiveness

### Phase 5: Auto Moderator POC (follow same pattern) (5-8K tokens)
1. Extract 012's moderation decision patterns
2. Train Gemma on timeout decisions
3. Implement adaptive moderation
4. Test accuracy

## Success Metrics

### POC Goals
- **Accuracy**: ≥90% match with 012's actual decisions
- **Latency**: <100ms for Gemma inference (vs 250ms Qwen)
- **Coverage**: Replace 300+ lines of regex with learned model
- **Adaptability**: System improves as 012 makes more decisions

### MVP Evolution
- **POC**: Single module (message_processor) with static training data
- **Proto**: Auto-retraining from new 012 behavior, 2+ modules enhanced
- **MVP**: All 6 P0/P1 modules enhanced, real-time learning system

## Token Budget Allocation

**Total Available**: 140K tokens

**Phase 1 (Database Setup)**: 2-3K tokens
**Phase 2 (Training Extraction)**: 3-5K tokens
**Phase 3 (Gemma POC)**: 5-8K tokens
**Phase 4 (Testing)**: 2-3K tokens
**Phase 5 (Auto Moderator)**: 5-8K tokens

**Total Estimated**: 17-27K tokens
**Buffer**: 113-123K tokens remaining

## Next Actions (Following "use holo, does module exist, research, deep think, execute")

1. ✅ **HoloIndex Search**: Completed - mapped 231 .py files across 9 modules
2. ✅ **Research**: Completed - Google MCP servers, integration strategy
3. ✅ **Deep Think**: Completed - this roadmap document
4. ⏳ **Execute**: Ready to start Phase 1 (Database Toolbox setup)

**Immediate Next Step**: Check if Google MCP Database Toolbox integration exists in codebase.

---

**Status**: Roadmap Complete - Ready for Phase 1 Execution
**Architect**: 0102 operating in WRE pattern recall mode
**Pattern**: YouTube DAE → WRE demonstration → Apply to all FoundUp DAEs via HoloIndex
