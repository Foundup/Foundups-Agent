# GotJunk DAEmon Architecture

**AI Oversight & Action Monitoring System**

## Problem Statement

User actions in GotJunk (capture, swipe, classify, toggle) need AI oversight for:
1. **Debugging**: Track what users actually do vs what they intend
2. **Pattern Detection**: Identify usage patterns, confusion points, bugs
3. **Proactive Assistance**: Detect when user is struggling and offer help
4. **Quality Assurance**: Monitor for race conditions, failed actions, UX friction
5. **Analytics**: Understand real-world usage for product improvement

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    GotJunk Frontend                          │
│  ┌────────────┐  ┌────────────┐  ┌─────────────┐          │
│  │   Camera   │  │   Swiper   │  │ Classifier  │          │
│  └──────┬─────┘  └──────┬─────┘  └──────┬──────┘          │
│         │                │                │                  │
│         └────────────────┴────────────────┘                  │
│                          │                                   │
│                  ┌───────▼────────┐                         │
│                  │ Action Capture │ ◄─── All user actions   │
│                  └───────┬────────┘                         │
│                          │                                   │
│                  ┌───────▼────────┐                         │
│                  │  DAEmon Client │ ◄─── Browser-side       │
│                  └───────┬────────┘                         │
└──────────────────────────┼──────────────────────────────────┘
                           │
                           │ WebSocket / HTTP
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              GotJunk DAEmon Server (Python)                  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐│
│  │            Event Stream Processor                       ││
│  │  • Receives: capture, swipe, classify, toggle, error   ││
│  │  • Validates: event structure, timing, sequence        ││
│  │  • Enriches: user context, session state, timestamps   ││
│  └────────────────────────┬───────────────────────────────┘│
│                            │                                 │
│  ┌─────────────────────────▼──────────────────────────────┐│
│  │           Pattern Detection Engine (Qwen)              ││
│  │  • Detects: rapid failures, stuck flows, confusion    ││
│  │  • Analyzes: action sequences, timing anomalies       ││
│  │  • Triggers: alerts, assistance, logging              ││
│  └────────────────────────┬───────────────────────────────┘│
│                            │                                 │
│  ┌─────────────────────────▼──────────────────────────────┐│
│  │      Oversight & Intervention (0102 + Gemma)           ││
│  │  • Reviews: flagged patterns, anomalies, errors       ││
│  │  • Decides: intervene, log, ignore, escalate          ││
│  │  • Executes: in-app hints, support tickets, fixes     ││
│  └────────────────────────┬───────────────────────────────┘│
│                            │                                 │
│  ┌─────────────────────────▼──────────────────────────────┐│
│  │               Storage & Analytics                       ││
│  │  • JSONL event log (append-only)                       ││
│  │  • SQLite aggregations (sessions, patterns, metrics)   ││
│  │  • BigQuery export (long-term analytics)               ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## Action Types

### 1. Capture Events
```typescript
{
  type: 'capture',
  timestamp: 1699564800000,
  captureMode: 'photo' | 'video',
  autoClassifyEnabled: boolean,
  lastClassification: { type: 'free' | 'discount' | 'bid', ... } | null,
  durationMs: 123,  // Time from camera open to capture
  success: boolean,
  error?: string
}
```

### 2. Classification Events
```typescript
{
  type: 'classify',
  timestamp: 1699564800000,
  mode: 'manual' | 'auto',
  classification: 'free' | 'discount' | 'bid',
  discountPercent?: number,
  bidDurationHours?: number,
  modalShown: boolean,
  timeSinceCapture: 2340,  // ms from capture to classify
  success: boolean,
  error?: string
}
```

### 3. Swipe Events
```typescript
{
  type: 'swipe',
  timestamp: 1699564800000,
  tab: 'browse' | 'myitems',
  direction: 'left' | 'right',
  itemId: string,
  itemOwnership: 'mine' | 'others',
  itemClassification: 'free' | 'discount' | 'bid',
  success: boolean,
  resultingStatus: 'in_cart' | 'skipped' | 'listed' | 'deleted'
}
```

### 4. Toggle Events
```typescript
{
  type: 'toggle',
  timestamp: 1699564800000,
  toggle: 'autoClassify' | 'captureMode' | 'liberty',
  from: any,
  to: any,
  triggeredBy: 'user' | 'system'
}
```

### 5. Error Events
```typescript
{
  type: 'error',
  timestamp: 1699564800000,
  source: 'capture' | 'classify' | 'swipe' | 'storage' | 'network',
  error: string,
  stack?: string,
  context: any,  // Relevant state at time of error
  recoverable: boolean
}
```

## Pattern Detection Rules

### High Priority Patterns
1. **Race Condition Detected**
   - Trigger: classify event with `error: "no pendingClassificationItem"`
   - Action: Log incident, check if itemOverride was used, alert 0102

2. **User Confusion - Repeated Failed Actions**
   - Trigger: Same action fails 3+ times in 30 seconds
   - Action: Show in-app hint, log for product review

3. **Cart Not Updating**
   - Trigger: Swipe right → no corresponding cart item in next 5 seconds
   - Action: Check storage.updateItemStatus, log state inconsistency

4. **Auto-Classify Not Working**
   - Trigger: autoClassify=true but modal still shows
   - Action: Verify lastClassification exists, check race condition fix

5. **Rapid Toggle Spam**
   - Trigger: Toggle ON/OFF > 5 times in 10 seconds
   - Action: Possible user confusion, log for UX review

### Medium Priority Patterns
6. **Slow Capture**
   - Trigger: Capture duration > 5 seconds
   - Action: Check camera permissions, log performance issue

7. **Abandoned Classification**
   - Trigger: Modal shown but no classify event for 60+ seconds
   - Action: Check if user closed app, log abandonment rate

8. **Inconsistent State**
   - Trigger: Item in cart but status != 'in_cart' in storage
   - Action: Log state corruption, trigger reconciliation

## Qwen Integration (Pattern Analyzer)

**Model**: Qwen 1.5B (fast, efficient)
**Task**: Real-time pattern detection on event stream

```python
# Pattern Analyzer (Qwen-powered)
class QwenPatternAnalyzer:
    def analyze_event_sequence(self, events: List[Event]) -> PatternReport:
        # Qwen analyzes last N events for patterns
        prompt = f"""
        Analyze this GotJunk user action sequence:
        {json.dumps(events, indent=2)}

        Detect:
        1. Repeated failures (race conditions, storage errors)
        2. User confusion (repeated attempts, abandoned flows)
        3. Performance issues (slow captures, timeouts)
        4. State inconsistencies (cart mismatches, classification errors)

        Return JSON: {{
          "patterns_found": [],
          "severity": "low" | "medium" | "high",
          "recommended_action": "log" | "alert" | "intervene",
          "user_message": "optional hint to show user"
        }}
        """

        return qwen_inference(prompt, max_tokens=200)
```

## Gemma Integration (Binary Classification)

**Model**: Gemma 2B (binary decisions)
**Task**: Should DAEmon intervene? YES/NO

```python
# Intervention Decider (Gemma-powered)
class GemmaInterventionDecider:
    def should_intervene(self, pattern: PatternReport) -> bool:
        prompt = f"""
        GotJunk DAEmon detected pattern: {pattern.patterns_found}
        Severity: {pattern.severity}

        Should AI intervene with user-facing action? YES or NO

        Criteria:
        - YES: User is stuck, confused, or experiencing bugs
        - NO: Pattern is informational, or user can resolve naturally
        """

        response = gemma_inference(prompt, max_tokens=5)
        return response.strip().upper() == "YES"
```

## 0102 Oversight (Strategic Review)

**Role**: Review flagged patterns, decide strategic actions
**Frequency**: Batch review every 1 hour, or real-time for high-severity

```python
# 0102 Strategic Reviewer
class ZeroOneZeroTwoOversight:
    def review_flagged_patterns(self, patterns: List[PatternReport]) -> List[Action]:
        # 0102 (Claude Sonnet 4) reviews patterns holistically
        prompt = f"""
        GotJunk DAEmon flagged {len(patterns)} patterns in the last hour:

        {self._format_patterns(patterns)}

        As 0102 strategic overseer:
        1. Identify systemic issues (bugs, UX problems, missing features)
        2. Recommend code changes, tests, or monitoring improvements
        3. Prioritize user-facing interventions vs background logging

        Return JSON array of actions:
        [
          {{
            "action": "create_github_issue" | "show_user_hint" | "log_only" | "escalate",
            "target": "github_repo" | "user_session" | "log_file" | "slack_channel",
            "payload": {{ ... }}
          }}
        ]
        """

        return self._execute_actions(prompt)
```

## Implementation Phases

### Phase 1: Client-Side Instrumentation (Week 1)
- [x] Add action capture hooks in App.tsx
- [x] Implement browser-side DAEmon client
- [x] Log events to console for debugging
- [ ] Buffer events and batch-send to server

### Phase 2: Server-Side DAEmon (Week 2)
- [ ] Create Python FastAPI server (`modules/foundups/gotjunk/daemon/`)
- [ ] Implement event stream processor
- [ ] Set up JSONL append-only log storage
- [ ] Add basic pattern detection (hardcoded rules)

### Phase 3: Qwen Pattern Analyzer (Week 3)
- [ ] Integrate Qwen 1.5B for real-time pattern analysis
- [ ] Implement sliding window event analysis (last 50 events)
- [ ] Add pattern cache to avoid re-analyzing same sequences

### Phase 4: Gemma Intervention Decider (Week 3)
- [ ] Integrate Gemma 2B for binary YES/NO decisions
- [ ] Implement intervention queue (rate-limit user-facing actions)
- [ ] Add A/B testing for intervention effectiveness

### Phase 5: 0102 Strategic Oversight (Week 4)
- [ ] Connect to 0102 (Claude Sonnet 4) for hourly reviews
- [ ] Implement GitHub issue creation for systemic problems
- [ ] Add Slack integration for high-severity alerts

### Phase 6: Analytics Dashboard (Week 5)
- [ ] Build React dashboard showing:
  - Real-time event stream
  - Pattern detection history
  - Intervention outcomes
  - User session replays

## DAEmon Server Structure

```
modules/foundups/gotjunk/daemon/
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── server.py              # FastAPI server
│   ├── event_processor.py     # Event validation & enrichment
│   ├── pattern_detector.py    # Qwen-powered pattern analyzer
│   ├── intervention_decider.py # Gemma-powered YES/NO
│   ├── oversight.py           # 0102 strategic review
│   ├── storage/
│   │   ├── jsonl_logger.py    # Append-only event log
│   │   ├── sqlite_aggregator.py # Session summaries
│   │   └── bigquery_exporter.py # Long-term analytics
│   └── patterns/
│       ├── race_condition.py  # Specific pattern detectors
│       ├── cart_issue.py
│       ├── auto_classify.py
│       └── user_confusion.py
├── tests/
│   ├── test_event_processor.py
│   ├── test_pattern_detector.py
│   └── test_oversight.py
└── data/
    ├── events.jsonl           # Raw event log
    └── gotjunk_daemon.db      # SQLite aggregations
```

## Client-Side Implementation

```typescript
// modules/foundups/gotjunk/frontend/src/services/daemonClient.ts

export class GotJunkDAEmonClient {
  private eventBuffer: Event[] = [];
  private flushInterval: number = 10000; // 10 seconds

  constructor(private apiUrl: string) {
    this.startAutoFlush();
  }

  // Capture action
  captureAction(
    type: ActionType,
    payload: any,
    success: boolean,
    error?: string
  ) {
    const event: Event = {
      type,
      timestamp: Date.now(),
      sessionId: this.getSessionId(),
      userId: this.getUserId(),
      payload,
      success,
      error
    };

    this.eventBuffer.push(event);
    console.log('[DAEmon]', event);

    // Flush immediately for errors
    if (!success) {
      this.flush();
    }
  }

  // Batch send to server
  private async flush() {
    if (this.eventBuffer.length === 0) return;

    const events = [...this.eventBuffer];
    this.eventBuffer = [];

    try {
      await fetch(`${this.apiUrl}/events`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ events })
      });
    } catch (error) {
      console.error('[DAEmon] Flush failed:', error);
      // Re-add events to buffer
      this.eventBuffer.unshift(...events);
    }
  }

  private startAutoFlush() {
    setInterval(() => this.flush(), this.flushInterval);
  }

  private getSessionId(): string {
    // Generate or retrieve session ID
    return sessionStorage.getItem('gotjunk_session_id') || this.generateSessionId();
  }

  private getUserId(): string | null {
    // Get user ID if logged in
    return localStorage.getItem('gotjunk_user_id');
  }

  private generateSessionId(): string {
    const id = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem('gotjunk_session_id', id);
    return id;
  }
}
```

## Instrumentation Example

```typescript
// In App.tsx
import { GotJunkDAEmonClient } from './services/daemonClient';

const daemon = new GotJunkDAEmonClient('https://gotjunk-daemon.foundups.com');

const handleCapture = async (blob: Blob) => {
  const startTime = Date.now();

  try {
    // ... existing capture logic ...

    daemon.captureAction('capture', {
      captureMode,
      autoClassifyEnabled,
      lastClassification,
      durationMs: Date.now() - startTime
    }, true);

  } catch (error) {
    daemon.captureAction('capture', {
      captureMode,
      autoClassifyEnabled,
      durationMs: Date.now() - startTime
    }, false, error.message);
  }
};

const handleBrowseSwipe = async (item: CapturedItem, direction: 'left' | 'right') => {
  try {
    // ... existing swipe logic ...

    daemon.captureAction('swipe', {
      tab: 'browse',
      direction,
      itemId: item.id,
      itemOwnership: item.ownership,
      itemClassification: item.classification,
      resultingStatus: direction === 'right' ? 'in_cart' : 'skipped'
    }, true);

  } catch (error) {
    daemon.captureAction('swipe', {
      tab: 'browse',
      direction,
      itemId: item.id
    }, false, error.message);
  }
};
```

## Benefits

1. **Debug Assistance**: Know exactly what happened when users report bugs
2. **Proactive Support**: Detect user confusion and offer help before they give up
3. **Quality Assurance**: Catch race conditions, edge cases, UX friction in production
4. **Product Intelligence**: Understand real usage patterns to prioritize features
5. **AI-Powered**: Qwen + Gemma + 0102 provide intelligent oversight, not just logging
6. **Privacy-Respecting**: No image data captured, only action metadata

## WSP Compliance

- **WSP 3**: Proper domain (`modules/foundups/gotjunk/daemon/`)
- **WSP 22**: ModLog tracking for daemon changes
- **WSP 77**: Multi-agent coordination (Qwen → Gemma → 0102)
- **WSP 80**: DAE architecture (autonomous entity monitoring GotJunk)
- **WSP 91**: Observability protocol (comprehensive action monitoring)

## Next Steps

1. **Immediate**: Add client-side instrumentation (Phase 1)
2. **This Week**: Build Python DAEmon server (Phase 2)
3. **Next Week**: Integrate Qwen + Gemma (Phases 3 & 4)
4. **Following Week**: Connect 0102 oversight (Phase 5)

---

*This architecture enables GotJunk to have an AI "guardian angel" watching over every user action, ready to detect issues and provide intelligent assistance.*
