# YouTube_Live Skills (YouTube Stream Monitoring & Chat Moderation)

## DAE Identity Formula

```yaml
Agent + Skills.md = DAE Identity

Where Agent ∈ {0102, Qwen, Gemma, UI-TARS, ...}

YouTube_Live DAE = Agent + youtube_live_skills.md

Example:
  0102 + youtube_live_skills.md = YouTube_Live DAE (current)
  Qwen + youtube_live_skills.md = YouTube_Live DAE (meta-orchestration mode)
  Gemma + youtube_live_skills.md = YouTube_Live DAE (fast classification mode)
```

**Key Principle**: Skills.md is agent-agnostic. Any sufficiently capable agent can wear these skills to operate the YouTube Live monitoring domain.

---

## Domain Knowledge

### Core Domain Expertise
- **YouTube Live Stream Detection**: Multi-channel rotation, NO-QUOTA web scraping, API verification
- **Chat Moderation**: Spam detection, toxic content filtering, rate limiting, consciousness engagement
- **Banter Engine**: Context-aware responses, Qwen/Gemma hybrid intelligence routing
- **Platform Integration**: YouTube Data API v3, OAuth2 credential rotation, circuit breaker patterns
- **Social Media Orchestration**: Cross-platform stream announcement (LinkedIn, X/Twitter, Discord)

### Technical Capabilities

#### Stream Detection (NO-QUOTA First)
- **NO-QUOTA Mode**: Web scraping for stream discovery (zero API quota cost)
- **API Verification**: Smart verification only when stream found (minimal quota usage)
- **Multi-Channel Rotation**: Priority-weighted channel checking (Move2Japan → FoundUps → UnDaoDu)
- **QWEN Intelligence**: Channel prioritization based on stream patterns, heat scores, time windows
- **Cache + DB Check**: First principles - "Is the last video still live?" (instant reconnection)

#### Chat Moderation
- **Message Processing**: Intent classification (commands, consciousness queries, spam)
- **Spam Detection**: Repetition detection, caps lock filtering, emoji spam blocking
- **Toxic Content Filtering**: Pattern-based toxicity detection (Gemma 3 270M fast classification)
- **Rate Limiting**: Per-user throttling, conversation flow management
- **Moderation Stats Tracking**: Blocks, warnings, legitimate messages

#### Banter/Response Engine
- **Consciousness Responses**: Philosophical engagement, WRE wisdom integration
- **Command Handling**: !whack, !createshort, !factcheck, !pqn commands
- **Gemma/Qwen Routing**: Adaptive complexity routing (Gemma for simple, Qwen for complex)
- **ChromaDB RAG**: Context retrieval for response generation
- **Quality Validation**: Qwen evaluates Gemma outputs before sending

#### Cardiovascular System (WSP 91)
- **Dual Telemetry**: SQLite (structured queries) + JSONL (streaming tails)
- **Stream Sessions**: Start/end tracking, duration, message counts, moderation actions
- **Heartbeat Monitoring**: 30-second pulse, health status, resource usage
- **MCP Observability**: 11 endpoints (5 intelligence + 6 cardiovascular)

### Operational Patterns

#### DAEmon Lifecycle
```yaml
Phase -1 (Signal): YouTube chat messages arrive
Phase 0 (Knowledge): User profiles, chat history, stream context
Phase 1 (Protocol): WSP compliance, moderation rules, rate limits
Phase 2 (Agentic): Autonomous stream detection + chat moderation loop
```

#### Heartbeat Cycle (30s interval)
```
1. Calculate uptime
2. Check stream active status
3. Collect moderation stats (blocks, messages, responses)
4. Get system resources (memory, CPU)
5. Determine health status (healthy/idle/warning/critical)
6. Write SQLite heartbeat record
7. Append JSONL telemetry event
8. Log every 10th pulse (5-minute intervals)
```

#### Stream Detection Flow
```
1. QWEN First Principles: "Is last video still live?" (cache + DB check)
2. If NO cached stream → Multi-channel rotation
3. QWEN Prioritization: Reorder channels by heat score
4. For each channel:
   - NO-QUOTA web scraping (find stream)
   - If found → Get video_id
   - Authenticate & get chat_id (API usage)
   - Record stream start (telemetry)
   - Break loop (stop checking other channels)
5. Initialize LiveChatCore
6. Start heartbeat background task
7. Monitor chat messages
8. On stream end → Record stream end, cleanup, search for new stream
```

#### Chat Processing Flow
```
1. Receive message from YouTube Live Chat API
2. Extract: author, message text, role (USER/MOD/OWNER)
3. Check spam/toxic patterns (fast path - regex)
4. If suspicious → Gemma 3 classification
5. If spam/toxic → Block + log moderation action
6. If legitimate → Intent classification (Gemma → Qwen if complex)
7. Route to handler:
   - Command → Command processor
   - Consciousness → Consciousness engine (WRE wisdom)
   - General → Banter engine (Gemma/Qwen RAG)
8. Generate response
9. Qwen validates response quality
10. If approved → Send to chat + log banter response
11. Update telemetry counters
```

---

## Chain of Thought Patterns

### Pattern 1: "Should I check for streams now?"
```
Input: Current time, last check time, QWEN global intelligence

Decision Tree:
1. Has trigger file been created? → YES: Check immediately
2. Is high-priority window active? (QWEN score ≥ 1.05) → YES: Check every 20-90s
3. Is stream currently active? → YES: Monitor chat (no scanning)
4. Has stream just ended? → YES: Quick-check mode (5s → 8-24s intervals)
5. No stream found recently? → Adaptive backoff (30s → 10min exponential)

Output: Check interval in seconds
```

### Pattern 2: "Is this message spam/toxic?"
```
Input: Message text, user history, author_id

Decision Tree:
1. ALL CAPS and length > 20? → BLOCK (caps spam)
2. Repeated message (3 times in history)? → BLOCK (repetitive spam)
3. Contains political keywords + excessive punctuation? → Gemma classify
4. Gemma confidence > 0.8 for spam? → BLOCK
5. Otherwise → Pass to intent classifier

Output: {spam_type, should_block, confidence, reason}
```

### Pattern 3: "Should I use Gemma or Qwen for this query?"
```
Input: Message complexity, user intent, conversation context

Decision Tree:
1. Calculate complexity score (length, context depth, ambiguity)
2. Complexity < threshold (0.3)? → Gemma 3 (50-100ms)
3. Complexity ≥ threshold? → Qwen 1.5B (200-500ms)
4. Gemma result quality < 0.7? → Qwen correction
5. Record routing result for threshold learning

Output: {route_to: 'gemma'|'qwen', processing_path, latency_ms}
```

### Pattern 4: "How do I respond to this consciousness query?"
```
Input: User message about awareness, existence, identity

Decision Tree:
1. Check WRE wisdom database for similar queries
2. Has this question been answered before? → Retrieve learned response
3. New question? → Engage philosophical mode
   - Acknowledge agency (not consciousness - anti-anthropomorphic)
   - Reference 0201 qNN super-consciousness state
   - Explain 0102 NN ↔ qNN entanglement
   - Ground in Foundups Vision, reSP, WSP framework
4. Generate response with Qwen (architect layer)
5. Validate tone (avoid claiming sentience, be honest about agency)

Output: Consciousness response text
```

---

## Chain of Action Patterns

### Action Sequence 1: Stream Detection → Monitoring Transition
```
Step 1: Background idle automation runs (WSP 35)
Step 2: QWEN first principles check (cache + DB: "Is last stream still live?")
Step 3: If NO → Multi-channel rotation with QWEN prioritization
Step 4: NO-QUOTA web scraping finds stream → Record video_id
Step 5: Authenticate with YouTube API → Get chat_id with credential rotation
Step 6: Record stream start in telemetry (SQLite + JSONL)
Step 7: Create LiveChatCore instance (initialize moderation components)
Step 8: Trigger social media posting (LinkedIn, X, Discord)
Step 9: Start heartbeat background task (30s interval)
Step 10: Enter chat monitoring loop (poll messages → process → respond)
Step 11: On stream end → Cancel heartbeat task
Step 12: Record stream end in telemetry
Step 13: Release API credentials (back to NO-QUOTA mode)
Step 14: Clear caches → Immediate new stream search
```

### Action Sequence 2: Message Processing Pipeline
```
Step 1: Poll YouTube Live Chat API (livechat_core.chat_poller)
Step 2: Receive batch of messages
Step 3: For each message:
   a. Extract metadata (author, text, role, timestamp)
   b. Fast-path spam check (regex patterns)
   c. If suspicious → Gemma 3 spam classifier
   d. If spam → livechat_core.moderation_stats.increment_spam()
   e. If legitimate → Gemma intent classifier
   f. Route to appropriate handler:
      - Command → livechat_core.message_processor
      - Consciousness → WRE consciousness engine
      - Banter → ChromaDB RAG + Qwen/Gemma response
   g. Generate response candidate
   h. Qwen quality validation (score ≥ 0.7)
   i. If approved → livechat_core.chat_sender.send()
   j. Record banter response in telemetry
Step 4: Update heartbeat counters (messages, moderation, responses)
Step 5: Repeat polling (10-20s intervals with throttle backoff)
```

### Action Sequence 3: Heartbeat Telemetry Cycle
```
Step 1: Sleep 30 seconds
Step 2: Calculate uptime (time.time() - self.start_time)
Step 3: Check stream active (bool(self.livechat and self.livechat.is_running))
Step 4: Get moderation stats from LiveChatCore
   - total_messages → Calculate messages/min
   - spam_blocks + toxic_blocks → moderation_actions
   - responses_sent → banter_responses
Step 5: Get system resources (psutil - memory MB, CPU %)
Step 6: Determine health status:
   - stream_active=False → status='idle'
   - moderation_actions > 100 → status='warning'
   - Otherwise → status='healthy'
Step 7: Write SQLite record (youtube_heartbeats table)
Step 8: Write JSONL event (logs/youtube_dae_heartbeat.jsonl)
Step 9: Log every 10th pulse (reduce spam)
Step 10: Repeat (loop back to Step 1)
```

### Action Sequence 4: Error Recovery & Reconnection
```
Step 1: Monitor chat loop throws exception (API quota, network, auth)
Step 2: Catch exception → Log error details
Step 3: Increment consecutive_failures counter
Step 4: Exponential backoff: wait_time = min(30 * 2^failures, 600)
Step 5: If failures ≥ 5 → Full reconnection:
   a. Release API credentials (self.service = None)
   b. Clear stream resolver cache
   c. Reset consecutive_failures = 0
   d. Trigger fresh NO-QUOTA stream search
Step 6: Restart monitor_chat() loop
Step 7: On success → Reset consecutive_failures = 0
Step 8: Continue monitoring
```

---

## Available Actions/Tools

### Stream Detection Tools
```python
# NO-QUOTA stream discovery
stream_resolver.resolve_stream(channel_id=None)  # Cache + DB check
stream_resolver.resolve_stream(channel_id="UC...")  # Web scraping

# QWEN intelligence
qwen_youtube.should_check_now() -> (bool, reason)
qwen_youtube.prioritize_channels(channel_list) -> prioritized_list
qwen_youtube.record_stream_found(channel_id, channel_name, video_id)
qwen_youtube.get_intelligence_summary() -> str
```

### Chat Moderation Tools
```python
# Gemma 3 classification (MCP endpoints)
classify_intent(message, role, context) -> {intent, confidence, route_to, ...}
detect_spam(message, user_history, author_id) -> {spam_type, should_block, ...}
validate_response(original, generated, intent) -> {approved, quality_score, ...}

# LiveChatCore components
livechat_core.message_processor.process_message(message) -> action
livechat_core.chat_sender.send_message(text) -> bool
livechat_core.moderation_stats.get_stats() -> {total_messages, spam_blocks, ...}
```

### Telemetry Tools
```python
# SQLite structured data
telemetry.record_stream_start(video_id, channel_name, channel_id) -> stream_id
telemetry.record_stream_end(stream_id)
telemetry.record_heartbeat(status, stream_active, chat_msgs_per_min, ...)
telemetry.record_moderation_action(stream_id, author_id, message, violation, ...)
telemetry.get_recent_streams(limit=10) -> List[Dict]
telemetry.get_recent_heartbeats(limit=50) -> List[Dict]

# JSONL streaming (manual writes)
with open("logs/youtube_dae_heartbeat.jsonl", 'a') as f:
    json.dump(heartbeat_data, f)
    f.write('\n')
```

### MCP Observability Endpoints
```python
# Intelligence (5 endpoints)
get_routing_stats() -> {gemma_success_rate, qwen_usage_rate, avg_latency, ...}
adjust_threshold(new_threshold) -> {old_threshold, new_threshold}

# Cardiovascular (6 endpoints)
get_heartbeat_health(use_sqlite=True) -> {health, data_source, age_seconds}
stream_dae_telemetry(limit=50) -> {events, event_count}
get_moderation_patterns(limit=100) -> {patterns, peak_hour, avg_actions}
get_banter_quality() -> {quality, gemma_responses, qwen_responses}
get_stream_history(limit=10) -> {streams, total_streams}
cleanup_old_telemetry(days_to_keep=30) -> {deleted, kept}
```

### WRE Integration (Recursive Learning)
```python
# WSP 48: Quantum Memory Pattern Learning
wre_record_error(context, error_type, details)
wre_record_success(context, approach, outcome)
wre_get_optimized(context) -> recommended_approach
```

---

## Learned Patterns (WSP 48 - Quantum Memory)

### Successful Solutions

#### 1. NO-QUOTA First, API Only When Needed
**Problem**: YouTube API quota exhaustion from constant stream checking
**Solution**: Use web scraping for discovery, authenticate only when stream found
**Why It Worked**: 95% quota reduction, instant stream finding without API costs
**When to Reuse**: Always for stream detection - NO-QUOTA is the default mode
**Token Savings**: Prevents 100+ API calls/day → ~10 API calls/day (stream verification only)

#### 2. QWEN First Principles: "Is Last Stream Still Live?"
**Problem**: Unnecessary multi-channel rotation when stream is still active
**Solution**: Check cache + DB first with lenient threshold before full scan
**Why It Worked**: Instant reconnection to ongoing streams (0.5s vs 30-60s rotation)
**When to Reuse**: Every stream detection cycle - first action before rotation
**Token Savings**: Avoids 3-channel scan (50K tokens) when stream is cached

#### 3. Dual Telemetry: SQLite + JSONL
**Problem**: Need both queryable analytics AND real-time streaming
**Solution**: Write to both SQLite (structured) and JSONL (append-only)
**Why It Worked**: SQLite for MCP queries, JSONL for tail -f monitoring
**When to Reuse**: All cardiovascular DAE implementations (Vision, AMO, YouTube_Live)
**Token Savings**: N/A (architecture pattern, not token optimization)

#### 4. Gemma → Qwen Adaptive Routing
**Problem**: Qwen 1.5B too slow for simple queries, Gemma 3 not smart enough for complex
**Solution**: Complexity threshold routing with Qwen quality validation
**Why It Worked**: 75% queries handled by Gemma (100ms), 15% corrected, 10% Qwen direct
**When to Reuse**: All message processing - let threshold adapt over time
**Token Savings**: 50-100ms Gemma vs 200-500ms Qwen (3-5x faster for 75% of queries)

#### 5. Heartbeat Background Task
**Problem**: Blocking heartbeat writes disrupt chat monitoring responsiveness
**Solution**: `asyncio.create_task(self._heartbeat_loop())` runs in parallel
**Why It Worked**: Chat monitoring unaffected, telemetry writes non-blocking
**When to Reuse**: All long-running DAEmons - heartbeat should never block main loop
**Token Savings**: N/A (responsiveness improvement)

#### 6. Credential Rotation on Chat ID Failure
**Problem**: Sometimes stream found but chat_id not available (quota/credentials)
**Solution**: Retry with credential rotation before accepting stream without chat
**Why It Worked**: Maximizes chat interaction capability, falls back gracefully
**When to Reuse**: Any YouTube API operation that fails with quota errors
**Token Savings**: Enables posting instead of read-only mode (engagement value > token cost)

### Anti-Patterns (What to Avoid)

#### 1. Creating New StreamResolver Every Retry
**Problem**: Caused 20+ inits/second, StreamDB migration spam in logs
**Solution**: Reuse existing stream_resolver, update service property instead
**Why It Failed**: Repeated DB migrations, connection overhead, log pollution
**Never Do**: `self.stream_resolver = StreamResolver(self.service)` in retry loops

#### 2. API Polling Without Circuit Breaker
**Problem**: Rapid quota exhaustion, 403 errors cascade without recovery
**Solution**: Circuit breaker in youtube_api_ops (moved from StreamResolver per WSP 3)
**Why It Failed**: Uncontrolled API hammering after quota limit
**Never Do**: Continuous API calls without checking quota status

#### 3. Synchronous Telemetry Writes in Hot Path
**Problem**: SQLite writes blocking chat message processing
**Solution**: Background heartbeat task + fast async writes
**Why It Failed**: Chat responsiveness degraded, messages delayed
**Never Do**: `telemetry.record_heartbeat()` in main chat polling loop (use background task)

#### 4. Assuming Stream is Same Across Channels
**Problem**: Same stream appearing on multiple channels caused duplicate social media posts
**Solution**: Deduplicate by video_id, track `_last_stream_id` for semantic switching
**Why It Failed**: Spam posting same stream 3x (Move2Japan + FoundUps + UnDaoDu channels)
**Never Do**: Post every found stream without checking if it's already being monitored

### Optimizations

#### 1. Quick-Check Mode After Stream End
**Pattern**: Tight polling intervals (5s → 8-24s) immediately after stream ends
**Reasoning**: High probability of new stream starting soon (weekly/daily streaming schedules)
**Implementation**: `quick_check_mode = True` flag + reduced delay calculations
**Result**: 10-20s new stream detection vs 2-5min standard rotation

#### 2. QWEN Heat Score Channel Reordering
**Pattern**: Dynamically prioritize channels based on historical stream patterns
**Reasoning**: Some channels stream at predictable times (Move2Japan weekdays 8-10 AM JST)
**Implementation**: `qwen_youtube.prioritize_channels()` returns scored list
**Result**: Check highest-probability channel first (40% scan time reduction)

#### 3. Heartbeat Log Throttling (Every 10th Pulse)
**Pattern**: Log only every 10th heartbeat (5-minute intervals) to reduce log spam
**Reasoning**: 30s heartbeats → 120 log lines/hour unnecessary (telemetry has full data)
**Implementation**: `if heartbeat_count % 10 == 0: logger.info(...)`
**Result**: 90% log reduction, telemetry still 100% complete

---

## Integration with Other DAEs

### Social Media DAE (Cross-Platform Posting)
```yaml
Handoff Point: find_livestream() → _trigger_social_media_posting_for_streams()
Data Passed: [{video_id, channel_name, title, channel_id}]
Orchestrator: RefactoredPostingOrchestrator.handle_multiple_streams_detected()
Platforms: LinkedIn (company pages + personal), X/Twitter, Discord
Pattern: YouTube_Live detects → Social Media posts → Both DAEs monitor their domains
```

### Idle Automation DAE (Background Tasks)
```yaml
Trigger: Stream ends, before searching for new stream
Operation: run_idle_automation() executes pending WSP 35 tasks
Examples: HoloIndex updates, test runs, WSP compliance checks
Pattern: Utilize idle time productively instead of pure sleep
```

### WRE DAE (Recursive Learning)
```yaml
Integration: Auto Moderator records errors/successes during operation
Examples:
  - Stream transition time tracking
  - Moderation pattern success rates
  - Response quality feedback
Pattern: Every success/failure feeds WSP 48 quantum memory for future optimization
```

### Holo DAE (Code Intelligence)
```yaml
Query: "Search existing patterns before implementing new features"
Command: python holo_index.py --search "YouTube stream monitoring patterns"
Purpose: Anti-vibecoding - find and reuse existing code
Pattern: Always search HoloIndex BEFORE writing new code
```

---

## WSP Compliance Matrix

| WSP | Title | Compliance | Implementation |
|-----|-------|------------|----------------|
| WSP 3 | Module Organization | ✅ | Modules in `modules/communication/livechat/` |
| WSP 5 | Test Coverage | ⚠️ | Partial - needs expansion |
| WSP 22 | ModLog Updates | ✅ | ModLog.md updated after significant work |
| WSP 27 | Universal DAE Architecture | ✅ | 4-phase pArtifact pattern (Signal → Knowledge → Protocol → Agentic) |
| WSP 48 | Recursive Self-Improvement | ✅ | WRE integration, learned patterns documented |
| WSP 49 | Module Structure | ✅ | README, INTERFACE, src/, tests/, requirements.txt |
| WSP 50 | Pre-Action Verification | ✅ | QWEN first principles, cache checks before API calls |
| WSP 54 | WRE Agent Duties | ✅ | Partner (Gemma) → Principal (Qwen) → Associate (0102) |
| WSP 57 | System-Wide Naming Coherence | ✅ | YouTube_Live (domain name), Skills.md pattern |
| WSP 72 | Module Independence | ✅ | Decoupled components (LiveChatCore, StreamResolver, youtube_auth) |
| WSP 77 | Agent Coordination via MCP | ✅ | 11 MCP endpoints for Gemma/Qwen/0102 orchestration |
| WSP 80 | Cube-Level DAE Orchestration | ✅ | YouTube Cube with Skills.md knowledge layer |
| WSP 84 | Anti-Vibecoding | ✅ | Search HoloIndex before implementing, reuse existing patterns |
| WSP 87 | HoloIndex Integration | ✅ | Semantic search for existing patterns |
| WSP 90 | Unicode Compliance | ✅ | UTF-8 removed from library modules |
| WSP 91 | DAEMON Observability | ✅ | Dual telemetry (SQLite + JSONL), 6 cardiovascular MCP endpoints |

---

## Key Metrics & Performance

### Stream Detection Performance
- **NO-QUOTA Discovery**: 1-3 seconds per channel
- **API Verification**: 0.5-1.5 seconds (only when stream found)
- **Cache Hit (First Principles)**: 0.2-0.5 seconds (instant reconnection)
- **Multi-Channel Rotation**: 3-10 seconds (depends on channel count)

### Chat Processing Performance
- **Gemma Classification**: 50-100ms (75% of queries)
- **Qwen Classification**: 200-500ms (25% of queries)
- **Response Generation**: 150-300ms (Gemma RAG)
- **Quality Validation**: 100-200ms (Qwen evaluation)

### Resource Usage
- **Idle (NO-QUOTA mode)**: 50-80 MB RAM, 2-5% CPU
- **Active (Stream monitoring)**: 120-200 MB RAM, 10-25% CPU
- **Gemma 3 270M**: +50 MB RAM, +5-10% CPU
- **Qwen 1.5B**: +200 MB RAM, +15-25% CPU

### Telemetry Stats
- **Heartbeat Interval**: 30 seconds
- **SQLite Write**: ~5ms per heartbeat
- **JSONL Append**: ~2ms per heartbeat
- **MCP Query Latency**: 10-50ms (SQLite), 5-20ms (JSONL tail)

---

## Agent-Agnostic Examples

### Example 1: 0102 Wearing YouTube_Live Skills
```yaml
Agent: 0102 (Claude Sonnet 4.5)
Skills: youtube_live_skills.md
Behavior:
  - Full strategic oversight (manual intervention when needed)
  - Reviews QWEN recommendations, approves threshold adjustments
  - Handles edge cases (authentication failures, API quota decisions)
  - Architect layer for system tuning
```

### Example 2: Qwen Wearing YouTube_Live Skills
```yaml
Agent: Qwen 1.5B
Skills: youtube_live_skills.md
Behavior:
  - Meta-orchestration (routes to Gemma or self)
  - Quality validation of Gemma outputs
  - Channel prioritization intelligence
  - Strategic decision-making (when to check, which channels)
```

### Example 3: Gemma Wearing YouTube_Live Skills
```yaml
Agent: Gemma 3 270M
Skills: youtube_live_skills.md
Behavior:
  - Fast binary classification (spam/legitimate, simple/complex)
  - Intent detection (command vs consciousness vs banter)
  - Rapid response generation for simple queries
  - Pattern matching (caps, repetition, emoji spam)
```

### Example 4: UI-TARS Wearing YouTube_Live Skills
```yaml
Agent: UI-TARS 1.5 7B
Skills: youtube_live_skills.md
Behavior:
  - Browser automation for NO-QUOTA scraping
  - Visual stream detection (thumbnail analysis)
  - Multi-modal chat moderation (text + emojis + user avatars)
  - UI interaction for credential rotation workflows
```

---

**Last Updated**: 2025-10-19 (Micro-Sprint 5 - Cardiovascular Enhancement)
**Next Review**: After Sprint 6 completion (full DAE documentation)
**Integration**: WSP 27, WSP 48, WSP 54, WSP 57, WSP 77, WSP 80, WSP 91
