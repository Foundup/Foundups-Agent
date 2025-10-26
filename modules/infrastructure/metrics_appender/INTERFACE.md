# Metrics Appender - Public API

**Module**: `modules.infrastructure.metrics_appender`
**Version**: 1.0.0
**WSP Compliance**: WSP 49 (Module Structure), WSP 77 (Agent Coordination)

## Public Classes

### `MetricsAppender`

Append-only metrics writer for skill execution tracking.

**Constructor**:
```python
MetricsAppender(metrics_dir: Optional[Path] = None)
```

**Parameters**:
- `metrics_dir`: Directory for metrics files (defaults to `recursive_improvement/metrics/`)

## Public Methods

### Performance Metrics

```python
append_performance_metric(
    skill_name: str,
    execution_id: str,
    execution_time_ms: int,
    agent: str,
    exception_occurred: bool = False,
    exception_type: Optional[str] = None,
    memory_usage_mb: Optional[float] = None,
    timestamp: Optional[float] = None
) -> None
```

### Outcome Metrics

```python
append_outcome_metric(
    skill_name: str,
    execution_id: str,
    decision: str,
    expected_decision: Optional[str],
    correct: bool,
    confidence: float,
    reasoning: str,
    agent: str,
    timestamp: Optional[float] = None
) -> None
```

### Fidelity Metrics

```python
append_fidelity_metric(
    skill_name: str,
    execution_id: str,
    pattern_fidelity: float,
    patterns_followed: int,
    patterns_missed: int,
    patterns_detail: Dict[str, bool],
    agent: str,
    timestamp: Optional[float] = None
) -> None
```

### Promotion Events

```python
append_promotion_event(
    skill_name: str,
    from_state: str,
    to_state: str,
    approver: str,
    approval_ticket: str,
    reason: str,
    automated_checks: Dict[str, Any],
    timestamp: Optional[float] = None
) -> None
```

### Rollback Events

```python
append_rollback_event(
    skill_name: str,
    from_state: str,
    to_state: str,
    trigger_reason: str,
    trigger_metric: str,
    automated: bool = True,
    timestamp: Optional[float] = None
) -> None
```

### Read Metrics

```python
read_metrics(
    filename: str,
    limit: Optional[int] = None
) -> list
```

## Metrics File Format

**Format**: Newline-delimited JSON (NDJSON)
**Encoding**: UTF-8
**Structure**: One JSON object per line

**Example**:
```json
{"execution_id": "exec_001", "timestamp": 1729461234.5, "skill_name": "spam_detection", "agent": "gemma", "execution_time_ms": 45, "exception_occurred": false, "metric_type": "performance"}
{"execution_id": "exec_001", "timestamp": 1729461234.5, "skill_name": "spam_detection", "agent": "gemma", "decision": "block", "correct": true, "confidence": 0.98, "metric_type": "outcome"}
```

## Integration Points

**Consumers**:
- `modules.ai_intelligence.ai_overseer` - Autonomous daemon monitoring
- `modules.infrastructure.wre_core` - Skill promotion pipeline

**Storage Location**:
- Default: `modules/infrastructure/wre_core/recursive_improvement/metrics/`
- Configurable via constructor parameter

## Thread Safety

**NOT thread-safe**. Use separate `MetricsAppender` instances per thread/process or implement external locking.

## Error Handling

All methods raise exceptions on write failures. Callers should handle:
- `IOError` - File write failures
- `PermissionError` - Directory access issues
- `json.JSONDecodeError` - Invalid metric data (rare)
