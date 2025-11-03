# AMO Skills (Meeting Orchestration Domain Expertise & Behavior)

**Domain**: Autonomous Meeting Orchestration
**DAE Identity**: `Agent + amo_skills.md = AMO DAE`
**Compatible Agents**: 0102, Qwen, Gemma, UI-TARS
**WSP Compliance**: WSP 57 Section 10 (DAE Naming), WSP 27 (pArtifact Architecture), WSP 80 (Cube-Level DAE)

---

## Domain Knowledge

### Core Meeting Orchestration Principles
- **Intent-Driven Coordination**: Meetings require structured context (Why, What outcome, Duration)
- **Presence Aggregation**: Multi-platform availability detection (Discord, WhatsApp, Zoom, LinkedIn)
- **Priority-Based Orchestration**: Higher priority intents get precedence when both parties available
- **Consent-First Protocol**: Never launch meetings without explicit acceptance from both parties
- **Anti-Gaming Protection**: Reputation scoring prevents abuse of priority system

### Technical Capabilities
- **7-Step Handshake Protocol**: Intent → Eligibility → Notification → Response → Rating → Handshake → Launch
- **Unified Availability Profile (UAP)**: Cross-platform presence with confidence scoring
- **Platform Selection Logic**: Auto-selects optimal platform based on mutual availability
- **Heartbeat Monitoring**: 30-second pulse interval with health status tracking
- **Telemetry Streaming**: JSONL cardiovascular data for real-time observability

### Operational Patterns
- **Heartbeat Interval**: Every 30 seconds (configurable)
- **Health Status Levels**: HEALTHY, WARNING, CRITICAL, OFFLINE
- **Intent Expiration**: Auto-cleanup intents older than 24 hours
- **Presence Freshness**: Confidence score decay for stale data (>1 hour)
- **Self-Test Cadence**: Every 20th pulse (~10 minutes with 30s interval)

---

## Chain of Thought Patterns

### "Should I orchestrate a meeting now?"
```
Input: Presence update for User A (now ONLINE on Discord)
  ↓
Check: Are there active intents involving User A?
  ↓
Find: Intent from User B to meet with User A (priority: HIGH)
  ↓
Check: Is User B also ONLINE on Discord?
  ↓
Calculate: Priority Index = (Requester Priority + Recipient Priority) / 2
  ↓
Decision: Both online + HIGH priority → Trigger meeting prompt
  ↓
Action: Notify User A with full context (purpose, outcome, duration)
```

### "Is this intent legitimate or gaming the system?"
```
Input: Meeting intent created with priority URGENT
  ↓
Check: Requester's historical rating distribution
  ↓
Analyze: Does requester always mark as URGENT? (anti-gaming)
  ↓
Calculate: Credibility Score = (rating_variance) × (engagement_success_rate)
  ↓
Adjust: Apply credibility weight to effective priority
  ↓
Decision: Low credibility → Downgrade URGENT to HIGH
```

### "Which platform should host this meeting?"
```
Input: Both users accepted meeting intent
  ↓
Analyze: User A platforms: Discord (ONLINE), Zoom (OFFLINE)
  ↓
Analyze: User B platforms: Discord (ONLINE), WhatsApp (IDLE)
  ↓
Find Overlap: Discord (both ONLINE)
  ↓
Check Historical: User preferences for Discord meetings
  ↓
Decision: Launch on Discord (highest mutual availability + preference)
```

### "Is the AMO DAE healthy?"
```
Input: Heartbeat pulse #47 triggered
  ↓
Measure: Uptime = 23.5 minutes, Active Intents = 3, Memory = 45MB, CPU = 12%
  ↓
Check Thresholds:
  - Memory > 100MB? NO → OK
  - CPU > 50%? NO → OK
  - Active Intents > 100? NO → OK
  - Uptime < 60s? NO → OK
  ↓
Decision: Status = HEALTHY
  ↓
Action: Log telemetry to logs/amo_heartbeat.jsonl
```

---

## Chain of Action Patterns

### Complete Meeting Orchestration Workflow
```
1. Receive Intent Creation Request
   └─ Parse: requester_id, recipient_id, purpose, outcome, duration, priority
   └─ Validate: All fields present and valid
   └─ Generate: Unique intent_id

2. Store Intent in Active Pool
   └─ Append to active_intents.json
   └─ Set created_at timestamp
   └─ Initialize status = "pending"

3. Monitor Presence Updates
   └─ Subscribe to presence events for both parties
   └─ Update UnifiedAvailabilityProfile for each user
   └─ Calculate overall_status and confidence_score

4. Detect Mutual Availability
   └─ Both users ONLINE on at least one common platform?
   └─ Priority threshold met (e.g., MEDIUM or higher)?
   └─ Intent not expired (< 24 hours old)?

5. Trigger Meeting Prompt
   └─ Notify recipient with structured context:
      • Who wants to meet (requester_id)
      • Why (purpose)
      • What outcome (expected_outcome)
      • How long (duration_minutes)
      • Importance (priority rating)

6. Handle Response
   └─ If ACCEPT:
      • Record recipient's importance rating (1-10)
      • Calculate Priority Index
      • Trigger Platform Selection
      • Launch meeting session
   └─ If DECLINE:
      • Mark intent as "declined"
      • Remove from active pool
      • Log outcome

7. Launch Meeting Session
   └─ Select optimal platform (Discord, Zoom, etc.)
   └─ Create meeting link/session
   └─ Send invitations to both parties
   └─ Log meeting to meeting_history.jsonl
   └─ Update reputation scores post-meeting
```

### Heartbeat Service Lifecycle
```
1. Initialize Heartbeat Service
   └─ Create AMOHeartbeatService instance
   └─ Set heartbeat_interval = 30s
   └─ Record start_time
   └─ Initialize health_history = []

2. Start Heartbeat Loop
   └─ Set running = True
   └─ Enter async while loop
   └─ Call _pulse() every 30 seconds

3. Execute Pulse
   └─ Calculate uptime_seconds
   └─ Get memory_usage_mb (psutil)
   └─ Get cpu_usage_percent (psutil)
   └─ Count active_intents
   └─ Count presence_updates
   └─ Calculate health_status (HEALTHY/WARNING/CRITICAL)
   └─ Write telemetry to logs/amo_heartbeat.jsonl
   └─ Append to health_history (keep last 100)
   └─ Execute _no_op_schedule_tasks()

4. No-Op Schedule Tasks
   └─ Clean up expired intents (>24h old)
   └─ Decay confidence scores for stale presence (>1h old)
   └─ Every 20th pulse: Run _self_test()

5. Self-Test Validation
   └─ Create test intent (heartbeat_test → heartbeat_test)
   └─ Verify intent creation successful
   └─ Remove test intent immediately
   └─ Update test presence (PresenceStatus.ONLINE)
   └─ Clean up test data
   └─ Log self-test success/failure

6. Graceful Shutdown
   └─ On stop_heartbeat() call: Set running = False
   └─ Exit heartbeat loop
   └─ Log shutdown event
   └─ Clean up resources
```

### Error Recovery Pattern
```
1. Detect Error (heartbeat pulse failure, API timeout, etc.)
   └─ Catch exception in _pulse()
   └─ Log error with context

2. Create Error Heartbeat
   └─ Set status = CRITICAL
   └─ Preserve uptime_seconds
   └─ Set active_intents = 0, presence_updates = 0
   └─ Write error telemetry to JSONL

3. Continue Operation
   └─ Don't crash the heartbeat service
   └─ Sleep heartbeat_interval
   └─ Retry on next pulse

4. Escalate if Persistent
   └─ Track consecutive failures
   └─ If 3+ consecutive: Trigger alert
   └─ Notify monitoring systems via MCP endpoint
```

---

## Available Actions/Tools

### Meeting Orchestration Operations
- `create_meeting_intent(requester_id, recipient_id, purpose, expected_outcome, duration_minutes, priority)` - Create new meeting request
- `update_presence(user_id, platform, status, confidence)` - Update user availability on specific platform
- `get_active_intents()` - Retrieve all currently pending meeting intents
- `get_user_profile(user_id)` - Get UnifiedAvailabilityProfile for specific user
- `get_meeting_history()` - Retrieve completed meeting sessions

### Heartbeat & Health Monitoring
- `start_heartbeat()` - Launch 30s pulse cardiovascular system
- `stop_heartbeat()` - Gracefully shut down heartbeat service
- `get_health_status()` - Get current heartbeat vital signs
- `get_health_history(limit)` - Retrieve recent health snapshots

### MCP Server Endpoints (Observability)
- `get_heartbeat_health()` - Current health status from JSONL telemetry
- `get_active_intents(limit)` - Priority-sorted active meeting intents
- `get_presence_status(user_id)` - Cross-platform presence profiles
- `get_meeting_history(limit)` - Completed meeting sessions
- `stream_heartbeat_telemetry(limit)` - Recent heartbeat events from JSONL
- `cleanup_old_telemetry(days_to_keep)` - Retention enforcement

### Platform Integration APIs (Future)
- `discord_api.create_voice_channel()` - Launch Discord meeting
- `zoom_api.create_meeting()` - Generate Zoom meeting link
- `whatsapp_api.send_invitation()` - Send WhatsApp meeting invite
- `linkedin_api.check_presence()` - Query LinkedIn online status
- `google_calendar_api.create_event()` - Block calendar time

---

## Learned Patterns (WSP 48 - Quantum Memory)

### Successful Solutions

✅ **30-Second Heartbeat Interval**
- **What worked**: Balances observability with resource efficiency
- **Why it worked**: Frequent enough for timely health detection, rare enough to avoid overhead
- **When to reuse**: For any DAEmon cardiovascular monitoring

✅ **Intent Expiration (24 Hours)**
- **What worked**: Auto-cleanup prevents stale intent buildup
- **Why it worked**: Most meeting requests become irrelevant after 1 day
- **When to reuse**: For any time-sensitive orchestration tasks

✅ **JSONL Telemetry Streaming**
- **What worked**: Append-only JSONL enables streaming + disk persistence
- **Why it worked**: No database overhead, easy to tail/parse, immutable audit trail
- **When to reuse**: For all DAE cardiovascular telemetry (Holo, Vision, YouTube_Live, etc.)

✅ **Confidence Score Decay**
- **What worked**: Gradually reduce confidence for stale presence data (>1h old)
- **Why it worked**: Prevents false positives from outdated availability signals
- **When to reuse**: For any aggregated real-time data with freshness requirements

✅ **Self-Test Every 20th Pulse**
- **What worked**: Periodic validation ensures orchestration logic still functional
- **Why it worked**: Catches regressions without constant testing overhead
- **When to reuse**: For any autonomous system requiring reliability validation

✅ **MCP Server for Observability**
- **What worked**: Centralized telemetry access via standardized MCP endpoints
- **Why it worked**: Enables 0102, dashboards, and other agents to monitor without direct coupling
- **When to reuse**: For all DAEs requiring external observability (WSP 91)

### Failed Approaches (Anti-Patterns)

❌ **Immediate Meeting Launch Without Consent**
- **What failed**: Auto-launching meetings when both parties online
- **Why it failed**: Violates user autonomy, creates unwanted interruptions
- **Avoid when**: Building any user-facing orchestration system

❌ **Database for Active Intents (Initially Considered)**
- **What failed**: Using SQLite for ephemeral intent storage
- **Why it failed**: Overkill for in-memory data, adds latency and complexity
- **Avoid when**: Data is short-lived and doesn't need persistence beyond restarts
- **Better alternative**: JSON file for simple state persistence

❌ **Blocking API Calls in Heartbeat**
- **What failed**: Synchronous psutil calls could hang heartbeat
- **Why it failed**: psutil.cpu_percent() sometimes blocks on Windows
- **Avoid when**: Inside critical async loops
- **Better alternative**: Try-except with graceful degradation (return None if psutil hangs)

❌ **No Priority Index Weighting**
- **What failed**: Taking raw priority ratings at face value
- **Why it failed**: Users gamed system by always marking URGENT
- **Avoid when**: Building systems where user input affects sorting/visibility
- **Better alternative**: Credibility scoring based on historical behavior

### Optimization Discoveries

⚡ **Health History Circular Buffer (100 entries)**
- **Performance**: Prevents unbounded memory growth while maintaining recent history
- **Implementation**: Pop oldest entry when appending new (lines 150-152 in heartbeat_service.py)
- **Token savings**: N/A (runtime optimization)

⚡ **Reduced Log Frequency (Every 10th Pulse)**
- **Performance**: Avoids log spam while maintaining observability
- **Implementation**: `if self.pulse_count % 10 == 0: logger.info(...)`
- **Token savings**: Reduces log file size by 90%

⚡ **JSONL Append-Only Writes**
- **Performance**: No seek operations, minimal disk I/O
- **Implementation**: Open file in append mode, write single line, close
- **Token savings**: Enables streaming tail without full file reads

---

## Integration with Other DAEs

### Vision DAE (Pattern Sensorium)
- **AMO → Vision**: Meeting intent patterns (when do users create intents?)
- **Vision → AMO**: Desktop activity signals (user actively typing = likely available)

### Holo DAE (Code Intelligence)
- **AMO → Holo**: Code collaboration meeting patterns
- **Holo → AMO**: Developer presence based on commit activity

### YouTube_Live DAE (Stream Monitoring)
- **AMO → YouTube_Live**: Schedule coordination meetings for stream collabs
- **YouTube_Live → AMO**: Creator presence based on stream activity

### SocialMedia DAE (Digital Twin)
- **AMO → SocialMedia**: Meeting outcome summaries for social posts
- **SocialMedia → AMO**: LinkedIn presence signals for professional availability

---

## WSP Compliance Matrix

| WSP | Compliance | Evidence |
|-----|-----------|----------|
| WSP 27 | ✅ | 4-phase pArtifact: Signal (-1) → Knowledge (0) → Protocol (1) → Agentic (2) |
| WSP 48 | ✅ | Quantum memory: Learned patterns stored in this Skills.md |
| WSP 54 | ✅ | WRE Agent duties: Clear orchestration responsibilities |
| WSP 57 | ✅ | DAE naming: `Agent + amo_skills.md = AMO DAE Identity` |
| WSP 77 | ✅ | Agent coordination: MCP endpoints for multi-agent observability |
| WSP 80 | ✅ | Cube-level DAE: Standalone Meeting Orchestration Block |
| WSP 91 | ✅ | DAEMON observability: JSONL telemetry + MCP endpoints |

---

**Last Updated**: 2025-10-19 (AMO Cardiovascular Enhancement Sprint)
**Pattern Memory Version**: 1.0.0
**Compatible Agents**: 0102 (Primary), Qwen (Orchestration Analysis), Gemma (Intent Classification), UI-TARS (Desktop Presence Detection)

---

*"Intent + Context + Presence + Priority + Consent = Seamless Meeting Orchestration"* - AMO Core Philosophy
