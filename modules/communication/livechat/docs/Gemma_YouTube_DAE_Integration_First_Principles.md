# Gemma YouTube DAE Integration - First Principles Analysis

**Status**: POC Architecture Complete
**Architect**: 0102
**Triggered By**: 012: "Apply 1st principles... to stream_resolver... robot brain emoji is Qwen lets add baby emoji so 012 can see gemma in daemon... is the daemon (DAE monitoring) logging MCP use?"

## Emoji System for DAEMON Logging

**WSP 91 Enhancement**: Visual DAE Model Notation

```
[BOT][AI] = Qwen 1.5B (Robot Brain - Architect, Complex reasoning)
[BOT][AI][BABY] = Gemma 3 270M (Robot Brain Baby - Fast classifier, Simple tasks)
```

**Rationale**: Gemma is the "baby" version of the robot brain - smaller, faster, simpler

**Example DAEMON Logs**:
```
[06:40:30] [BOT][AI] [QWEN-INTENT] [TARGET] Classified as GENERAL (confidence: 0.50)
[06:40:31] [BOT][AI][BABY] [GEMMA-CLASSIFY] Intent: command_whack (confidence: 0.92, latency: 87ms)
[06:40:32] [BOT][AI] [QWEN-EVALUATE] Quality score: 0.95 (APPROVED - Baby brain succeeded!)
```

## Current Architecture Discovery

### HoloIndex Search Results

**Modules Found**:
1. `modules/communication/livechat` (159 python files, 65 tests)
   - `message_processor.py` (1240 lines, 63 KB) - **TARGET**
   - `mcp_youtube_integration.py` (491 lines) - **MCP bridge exists!**
   - `qwen_youtube_integration.py` (500 lines) - **Qwen already integrated!**
   - `auto_moderator_dae.py` (795 lines) - Spam detection candidate

2. `modules/platform_integration/stream_resolver` (26 files, 10 tests)
   - `no_quota_stream_checker.py` (838 lines, 42 KB) - **Classification candidate**
   - `stream_resolver.py` (726 lines) - Status detection

### MCP Integration Status

**File**: `modules/communication/livechat/src/mcp_youtube_integration.py`

**Current State**:
- MCP bridge architecture complete (Lines 1-491)
- **Simulating calls** (Line 245-333) - NOT using real MCP yet
- Connects to 2 MCP servers:
  * `whack-a-magat-mcp` - Gamification
  * `youtube-quota-monitor` - Quota tracking

**Key Methods**:
```python
async def process_timeout_event(event: Dict) -> Dict:  # Line 113
    # Records timeout, returns points/combo
    # Currently uses simulated TimeoutManager

async def get_slash_command_response(command: str, user_id: str):  # Line 431
    # Handles /rank, /score, /leaderboard
    # Classification opportunity!

async def handle_mcp_event(event: Dict):  # Line 335
    # Routes whack, quota, magadoom events
    # Classification opportunity!
```

**Critical Insight**: This file is THE integration point! It already bridges MCP [U+2194] YouTube DAE.

## First Principles Analysis

### Problem Statement

**What do we need to classify?**

1. **Timeout Events** (Line 113-168):
   - Is this spam or legitimate moderation?
   - Is target actually a MAGA troll or false positive?
   - Should points be awarded?

2. **Slash Commands** (Line 431-455):
   - `/rank` vs `/score` vs `/leaderboard` vs typos
   - User intent: asking vs spamming
   - Context: during stream vs offline

3. **MCP Events** (Line 335-366):
   - Classify event type: whack, quota, magadoom
   - Priority: instant vs can wait
   - Validity: legit event vs spam

4. **Stream Status** (stream_resolver):
   - Is stream live? (complex API patterns)
   - Is stream starting? (pre-live detection)
   - Is stream ending? (post-live detection)

### Where Does Gemma Add Value?

**Replace Regex With Intelligence**:

| Current (Regex/Rules) | With Gemma 3 | Improvement |
|----------------------|--------------|-------------|
| `if command == "/rank":` | `classify_intent(command)` | Handles typos |
| `if "maga" in text.lower():` | `detect_spam(text, history)` | Context-aware |
| Manual event routing | `classify_mcp_event(event)` | Adaptive |
| Static status checks | `classify_stream_status(data)` | Pattern learning |

### Qwen as Architect

**Qwen's Role** ([BOT][AI]):
1. **Monitor Gemma output** (Line 245-333 in adaptive_router.py)
2. **Evaluate quality** (Is Gemma's classification correct?)
3. **Adjust threshold** (Should this query type use Qwen instead?)
4. **Handle complex cases** (Multi-step reasoning)

**Example**:
```python
# Gemma classifies
intent = gemma.classify("!creatshort my idea")  # Result: command_shorts (0.85)

# Qwen evaluates
quality = qwen.evaluate(original="!creatshort", gemma_result=intent)
# Quality: 0.92 (APPROVED - typo handling good)

# Threshold adjusts
# Success! Lower threshold (trust Gemma more)
```

## Integration Architecture

### Option A: Enhance mcp_youtube_integration.py

**Add Gemma to MCP bridge** (RECOMMENDED):

```python
from foundups_mcp_p1.servers.youtube_dae_gemma.adaptive_router import AdaptiveComplexityRouter

class YouTubeMCPIntegration:
    def __init__(self):
        self.connections = {}
        self.gemma_router = AdaptiveComplexityRouter()  # NEW!

    async def process_timeout_event(self, event: Dict) -> Dict:
        # Gemma: Is this spam or legit?
        classification = self.gemma_router.classify_intent(
            message=event["target_name"],
            role="MOD",
            context={"event_type": "timeout", "duration": event["duration"]}
        )

        if classification['intent'] == 'spam':
            # Award points! Legit timeout
            return await self._process_legit_timeout(event)
        else:
            # False positive - don't award points
            return {"error": "Not a MAGA troll, cancelled"}

    async def get_slash_command_response(self, command: str, user_id: str):
        # Gemma: Classify command (handles typos!)
        classification = self.gemma_router.classify_intent(
            message=command,
            role="USER",
            context={"command_context": True}
        )

        # Route based on Gemma's classification
        if classification['intent'] == 'command_whack':
            return await self._handle_whack_command(user_id)
        elif classification['intent'] == 'spam':
            return None  # Don't respond to spam
```

**Benefits**:
- Single integration point
- MCP already handles orchestration
- Minimal changes to existing code
- [BOT][AI]/[BABY] logging at MCP layer

### Option B: Separate Gemma MCP Server

**Use our new `youtube_dae_gemma` MCP server**:

```python
from mcp import Client

class YouTubeMCPIntegration:
    def __init__(self):
        self.connections = {}
        self.gemma_mcp = Client("youtube_dae_gemma")  # Our new server!

    async def process_timeout_event(self, event: Dict) -> Dict:
        # Call Gemma MCP server
        classification = await self.gemma_mcp.call_tool(
            "classify_intent",
            message=event["target_name"],
            role="MOD",
            context={"event_type": "timeout"}
        )

        # Log with emoji
        logger.info(f"[BOT][AI][BABY] [GEMMA] {classification['intent']} ({classification['confidence']:.2f})")

        if classification['processing_path'] == 'gemma->qwen':
            logger.info(f"[BOT][AI] [QWEN] Corrected baby brain classification")
```

**Benefits**:
- Clean separation of concerns
- MCP-native architecture
- Can be used by other DAEs
- Full adaptive routing with Qwen monitoring

## Stream Resolver Analysis

**File**: `modules/platform_integration/stream_resolver/src/no_quota_stream_checker.py` (838 lines)

**Current**: Rule-based stream detection
**Opportunity**: Gemma classification of stream status

**Pattern Matching Candidates**:
1. **Live stream detection**: Analyze API responses for "live" indicators
2. **Pre-live detection**: Classify stream as "starting soon"
3. **Post-live detection**: Classify stream as "ended"
4. **Error classification**: "quota exceeded" vs "not found" vs "private"

**Why Gemma**:
- YouTube API returns inconsistent patterns
- Rule-based detection misses edge cases
- Gemma can learn patterns from training data

**Example**:
```python
# Current (stream_resolver.py:726 lines)
if "activeLiveChatId" in response:
    return "LIVE"
elif "scheduledStartTime" in response:
    return "SCHEDULED"
else:
    return "NOT_LIVE"

# With Gemma
classification = gemma.classify_stream_status(
    api_response=response,
    channel_metadata=metadata,
    history=previous_checks
)
# Returns: "LIVE", "PRE_LIVE", "POST_LIVE", "ERROR", "PRIVATE"
# With confidence and reasoning
```

## WSP 77 Enhancement Required

**Current**: WSP 77 mentions "EmbeddingGemma" (Line 69) but this is outdated

**Needed**: Update to reflect Gemma 3 270M + Qwen 1.5B adaptive routing

**New Section**:
```markdown
## 11. Gemma/Qwen Adaptive Intelligence Layer (WSP 77.1)

The Intelligent Internet orchestration now includes adaptive model routing:

- **Gemma 3 270M** ([BABY]): Fast classification for simple queries (50-100ms)
- **Qwen 1.5B** ([BOT][AI]): Architect monitoring + complex reasoning (250ms)
- **Adaptive Threshold**: Learns optimal routing (starts 0.3, adjusts ±0.02)
- **0102 Architect**: Manual override for system tuning

**Integration Points**:
- YouTube DAE message classification
- MCP event routing
- Stream status detection
- Spam/troll identification

**DAEMON Logging**:
- [BOT][AI][BABY] = Gemma 3 inference (baby brain)
- [BOT][AI] = Qwen monitoring/evaluation (adult brain)
- Threshold adjustments logged for learning

**MPS Priorities**:
- P0: Message classification (replaces 300+ lines regex)
- P1: Stream status detection
- P2: MCP event routing
```

## WSP 80 Enhancement Required

**Current**: WSP 80 defines DAE cube architecture

**Needed**: Add Gemma/Qwen relationship to DAE definition

**New Section**:
```markdown
### 8.3. Gemma/Qwen DAE Intelligence Pattern

Each FoundUp DAE can integrate Gemma/Qwen adaptive routing:

**Architecture**:
```
FoundUp DAE (YouTube)
    v
[[BOT][AI][BABY] Gemma: Fast Classifier] (50ms, baby brain)
    v
[[BOT][AI] Qwen: Architect Monitor] (evaluates baby brain)
    v
[Adaptive Threshold] (learns optimal routing)
    v
[0102 Architect] (system-level tuning)
```

**Token Budgets**:
- Gemma inference: 50-200 tokens per operation
- Qwen evaluation: 100-500 tokens per evaluation
- Total per query: 150-700 tokens (vs 5K+ without routing)

**Evolution Path**:
- POC: Gemma + Qwen + manual threshold
- Proto: Training data + adaptive learning
- MVP: Autonomous threshold optimization
```

## Recommended Implementation Path

### P0: Enhance mcp_youtube_integration.py (MPS: 16)

**Complexity**: 3 (integrate existing components)
**Importance**: 5 (replaces 300+ lines regex)
**Deferability**: 3 (can work without it)
**Impact**: 5 (massive code reduction + new capabilities)

**Implementation**:
1. Import AdaptiveComplexityRouter
2. Add router instance to YouTubeMCPIntegration.__init__
3. Replace regex in process_timeout_event with Gemma classification
4. Replace command parsing with Gemma intent detection
5. Add [BABY]/[BOT][AI] emoji logging

**Token Cost**: 2-3K tokens (read + modify + test)

### P1: Stream Resolver Gemma Integration (MPS: 14)

**Complexity**: 3 (new classification domain)
**Importance**: 4 (improves stream detection)
**Deferability**: 4 (works currently)
**Impact**: 3 (incremental improvement)

**Implementation**:
1. Add classify_stream_status to adaptive_router.py
2. Extract training data from stream_resolver logs
3. Replace rule-based detection with Gemma
4. A/B test vs current system

**Token Cost**: 3-5K tokens

### P2: Update WSP 77 + WSP 80 (MPS: 13)

**Complexity**: 2 (documentation)
**Importance**: 4 (WSP compliance)
**Deferability**: 4 (can document later)
**Impact**: 3 (framework clarity)

**Implementation**:
1. Add Section 11 to WSP 77 (Gemma/Qwen layer)
2. Add Section 8.3 to WSP 80 (DAE intelligence pattern)
3. Update emoji notation in WSP 91
4. Update ModLog

**Token Cost**: 1-2K tokens

## Next Step Decision

**Question**: Which path?

**Option A**: Enhance mcp_youtube_integration.py directly (faster, monolithic)
**Option B**: Use youtube_dae_gemma MCP server (cleaner, MCP-native)
**Option C**: Hybrid (Gemma MCP server, integrate via client)

**Recommendation**: **Option C (Hybrid)**
- Use our new MCP server (youtube_dae_gemma)
- Integrate via MCP client in mcp_youtube_integration.py
- Best of both: clean separation + MCP architecture
- Allows other DAEs to use same Gemma intelligence

## DAEMON Logging Enhancement

**Add to all Gemma/Qwen operations**:

```python
# Gemma inference (baby brain)
logger.info(f"[BOT][AI][BABY] [GEMMA-CLASSIFY] Intent: {result['intent']} (confidence: {result['confidence']:.2f}, latency: {result['latency_ms']}ms)")

# Qwen evaluation (adult brain monitoring baby)
if result['processing_path'] == 'gemma->qwen':
    logger.info(f"[BOT][AI] [QWEN-CORRECT] Quality: {result['quality_score']:.2f} (Baby brain failed, adult re-routed)")
else:
    logger.info(f"[BOT][AI] [QWEN-APPROVE] Quality: {result['quality_score']:.2f} (Baby brain succeeded!)")

# Threshold adjustment (teaching baby brain)
logger.info(f"[U+2699]️ [THRESHOLD] {old:.3f} -> {new:.3f} ({'v trust baby more' if new < old else '^ use adult more'})")
```

**Benefits**:
- Visual distinction in logs
- 012 can instantly see which model is active
- Threshold learning visible in real-time
- Debug-friendly

---

**Status**: First principles analysis complete, ready for P0 implementation (MPS: 16)
