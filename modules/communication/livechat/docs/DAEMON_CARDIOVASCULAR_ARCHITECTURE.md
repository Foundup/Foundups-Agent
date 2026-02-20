# DAEmon as Cardiovascular System

**Module**: communication/livechat  
**WSP Reference**: WSP 91 (DAEmon Observability), WSP 77 (Agent Coordination)  
**Status**: Active  
**Date**: 2026-01-19

---

## Concept

The **DAEmon** (LiveChat) is the cardiovascular system for all DAEs:
- **Heart**: Pumps logs/vitals to 012 (human operator)
- **Arteries**: breadcrumb_telemetry.db carries events from all DAEs
- **Veins**: 012 queries telemetry, pastes to 0102 for analysis

```
┌────────────────────────────────────────────────┐
│  DAEmon (LiveChat) - Cardiovascular System     │
├────────────────────────────────────────────────┤
│                                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │Scheduler │ │ Indexer  │ │Comments  │       │
│  │  DAE     │ │   DAE    │ │  DAE     │       │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘       │
│       │            │            │              │
│       └────────────┴────────────┘              │
│                    ↓                           │
│       breadcrumb_telemetry.db                  │
│                    ↓                           │
│       AI Overseer (monitors patterns)          │
│                    ↓                           │
│       LiveChat display (012 sees logs)         │
└────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. DAEs Emit Vitals (Logged for 012)
```python
# Example from youtube_shorts_scheduler
print(vitals.to_dashboard())  # Console: 012 sees this
vitals.emit_to_telemetry(phase="channel_move2japan")  # SQLite: 0102 queries this
```

### 2. 012 Sees Logs → Pastes to 0102
```
[VITALS] ✅ | ❤️ 12.0 ops/min | 🩸 2.0% errors | 📂 2/2 channels | 🧠 5min
```
012 copies this from terminal/LiveChat → pastes to 0102.

### 3. 0102/AI Overseer Query Telemetry
```python
# 0102 or AI Overseer queries programmatically
vitals = telemetry.get_recent_breadcrumbs(minutes=30, source_dae="youtube_shorts_scheduler")
patterns = telemetry.get_repeated_patterns(minutes=5, min_occurrences=3)
```

### 4. AI Overseer Monitors Patterns
```python
# BreadcrumbMonitor detects anomalies, alerts via LiveChat
if pattern.is_critical():
    livechat.send_chat_message(alert)  # 012 sees in chat
```

---

## Vitals Schema

| Vital | Normal | Warning | Critical |
|-------|--------|---------|----------|
| Heart Rate (ops/min) | 5-20 | <2 or >50 | 0 or >100 |
| Error Rate | <5% | 5-15% | >15% |
| Oops Events | 0 | 1-2 | >2 |
| Session Age | <2h | 2-4h | >4h |

---

## Integration Points

### DAEVitals → Telemetry
`modules/platform_integration/youtube_shorts_scheduler/src/dae_vitals.py`
- `emit_to_telemetry()` stores vitals as breadcrumbs

### BreadcrumbMonitor → AI Overseer  
`modules/ai_intelligence/ai_overseer/src/breadcrumb_monitor.py`
- Monitors patterns, Gemma classifies, Qwen generates alerts

### Telemetry Store
`modules/communication/livechat/src/breadcrumb_telemetry.py`
- SQLite storage for all DAE events
- Queryable by 012 for 0102 handoff

---

## WSP Compliance

- **WSP 91**: DAEmon Observability Protocol
- **WSP 77**: Agent Coordination (Qwen/Gemma/0102)
- **WSP 94**: Agent Specialization by Capability
