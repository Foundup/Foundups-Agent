# Metrics Appender

**Domain**: Infrastructure
**Purpose**: Append-only JSON metrics collection for real-time skill execution tracking
**WSP Compliance**: WSP 77 (Agent Coordination), WSP 91 (DAEMON Observability), WSP 49 (Module Structure)

## Overview

MetricsAppender provides fast, real-time metrics collection without database overhead. All metrics are stored in append-only JSON files for easy diffing, rollback, and analysis.

## Key Features

- **Append-Only Storage**: Newline-delimited JSON format
- **Real-Time Collection**: Zero database overhead
- **WSP 77 Integration**: Tracks skill execution for promotion pipeline (prototype → staged → production)
- **Multiple Metric Types**: Performance, outcome, fidelity, promotion events, rollback events

## Usage

```python
from modules.infrastructure.metrics_appender.src.metrics_appender import MetricsAppender

# Initialize
appender = MetricsAppender()

# Track performance
appender.append_performance_metric(
    skill_name="youtube_spam_detection",
    execution_id="exec_20251020_001",
    execution_time_ms=45,
    agent="gemma",
    exception_occurred=False
)

# Track outcome
appender.append_outcome_metric(
    skill_name="youtube_spam_detection",
    execution_id="exec_20251020_001",
    decision="block",
    expected_decision="block",
    correct=True,
    confidence=0.98,
    reasoning="CAPS spam detected",
    agent="gemma"
)
```

## Metrics Storage

**Location**: `modules/infrastructure/wre_core/recursive_improvement/metrics/`
**Format**: Newline-delimited JSON (NDJSON)
**Files**:
- `{skill_name}_performance.json` - Execution time, exceptions
- `{skill_name}_outcomes.json` - Decision correctness, confidence
- `{skill_name}_fidelity.json` - Pattern adherence tracking
- `{skill_name}_promotion_log.json` - State changes and rollbacks

## Integration

**Used By**:
- AI Intelligence Overseer (autonomous daemon monitoring)
- WRE Core (skill promotion pipeline)
- Any module performing skill-based execution

## WSP Compliance

- **WSP 3**: Proper infrastructure domain placement
- **WSP 49**: Complete module structure (README, INTERFACE, src/, tests/)
- **WSP 77**: Enables agent coordination via promotion tracking
- **WSP 91**: Structured observability for daemon operations
