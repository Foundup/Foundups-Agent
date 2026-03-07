# Sprint 1: CoT Closure - Implementation Tickets

**Objective**: Close the reasoning loop (P0-D: TT-SI + P0-A: ReAct)
**Target**: 20% median fidelity improvement, 30% retry reduction
**Duration**: 1 week

---

## Ticket 1.1: TT-SI Variation Promotion Pipeline

**Priority**: P0 | **Estimate**: 4h | **Owner**: 0102

### Problem
Variations are generated via `evolve_skill()` but never promoted. The `skill_variations.promoted` column is always 0. No A/B testing infrastructure exists.

### Target Files
| File | Action |
|------|--------|
| `modules/infrastructure/wre_core/src/pattern_memory.py` | ADD promotion methods |
| `modules/infrastructure/wre_core/wre_master_orchestrator/src/wre_master_orchestrator.py` | ADD A/B routing |

### Implementation Steps

#### Step 1.1.1: Add promotion tables to PatternMemory (pattern_memory.py)

After line 179 (learning_events table), add:

```python
# A/B test assignments table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS ab_test_assignments (
        test_id TEXT PRIMARY KEY,
        skill_name TEXT NOT NULL,
        control_version TEXT NOT NULL,
        treatment_version TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT,
        status TEXT DEFAULT 'running',
        sample_size_target INTEGER DEFAULT 20,
        control_successes INTEGER DEFAULT 0,
        control_trials INTEGER DEFAULT 0,
        treatment_successes INTEGER DEFAULT 0,
        treatment_trials INTEGER DEFAULT 0
    )
""")
```

#### Step 1.1.2: Add promotion methods to PatternMemory (pattern_memory.py)

After `get_evolution_history()` (line 651), add:

```python
def schedule_ab_test(
    self,
    skill_name: str,
    control_version: str,
    treatment_version: str,
    sample_size_target: int = 20
) -> str:
    """
    Schedule A/B test between control and treatment variation.

    Returns:
        test_id for tracking
    """
    import uuid
    test_id = f"ab_{skill_name}_{uuid.uuid4().hex[:8]}"
    cursor = self.conn.cursor()
    cursor.execute("""
        INSERT INTO ab_test_assignments (
            test_id, skill_name, control_version, treatment_version,
            start_time, sample_size_target
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        test_id, skill_name, control_version, treatment_version,
        datetime.now().isoformat(), sample_size_target
    ))
    self.conn.commit()
    logger.info(f"[PATTERN-MEMORY] Scheduled A/B test {test_id}")
    return test_id

def get_active_ab_test(self, skill_name: str) -> Optional[Dict]:
    """Get active A/B test for skill if exists."""
    cursor = self.conn.cursor()
    cursor.execute("""
        SELECT * FROM ab_test_assignments
        WHERE skill_name = ? AND status = 'running'
        ORDER BY start_time DESC LIMIT 1
    """, (skill_name,))
    row = cursor.fetchone()
    return dict(row) if row else None

def record_ab_outcome(
    self,
    test_id: str,
    variant: str,  # 'control' or 'treatment'
    success: bool
) -> None:
    """Record outcome for A/B test variant."""
    cursor = self.conn.cursor()
    if variant == 'control':
        cursor.execute("""
            UPDATE ab_test_assignments
            SET control_trials = control_trials + 1,
                control_successes = control_successes + ?
            WHERE test_id = ?
        """, (1 if success else 0, test_id))
    else:
        cursor.execute("""
            UPDATE ab_test_assignments
            SET treatment_trials = treatment_trials + 1,
                treatment_successes = treatment_successes + ?
            WHERE test_id = ?
        """, (1 if success else 0, test_id))
    self.conn.commit()

def check_ab_promotion(self, test_id: str, min_margin: float = 0.10) -> Optional[str]:
    """
    Check if treatment should be promoted.

    Returns:
        'treatment' if should promote, 'control' if treatment lost, None if inconclusive
    """
    cursor = self.conn.cursor()
    cursor.execute("SELECT * FROM ab_test_assignments WHERE test_id = ?", (test_id,))
    row = cursor.fetchone()
    if not row:
        return None

    test = dict(row)
    total_trials = test['control_trials'] + test['treatment_trials']

    # Need minimum sample size
    if total_trials < test['sample_size_target']:
        return None

    control_rate = test['control_successes'] / max(test['control_trials'], 1)
    treatment_rate = test['treatment_successes'] / max(test['treatment_trials'], 1)

    margin = treatment_rate - control_rate

    if margin >= min_margin:
        return 'treatment'
    elif margin <= -min_margin:
        return 'control'
    return None

def promote_variation(self, variation_id: str) -> None:
    """Promote variation to production."""
    cursor = self.conn.cursor()
    cursor.execute("""
        UPDATE skill_variations
        SET promoted = 1, test_status = 'promoted'
        WHERE variation_id = ?
    """, (variation_id,))
    self.conn.commit()
    logger.info(f"[PATTERN-MEMORY] Promoted variation {variation_id}")

def archive_variation(self, variation_id: str) -> None:
    """Archive losing variation."""
    cursor = self.conn.cursor()
    cursor.execute("""
        UPDATE skill_variations
        SET test_status = 'archived'
        WHERE variation_id = ?
    """, (variation_id,))
    self.conn.commit()
    logger.info(f"[PATTERN-MEMORY] Archived variation {variation_id}")
```

#### Step 1.1.3: Add A/B routing to execute_skill (wre_master_orchestrator.py)

In `execute_skill()`, after step 2 (load skill), insert A/B routing:

```python
# Step 2.5: Check for active A/B test and route to variant
selected_variant = None
active_test = None
if self.sqlite_memory:
    active_test = self.sqlite_memory.get_active_ab_test(skill_name)
    if active_test:
        # 50/50 split
        import random
        if random.random() < 0.5:
            selected_variant = 'control'
            # Use original skill_content
        else:
            selected_variant = 'treatment'
            # Load treatment variation
            cursor = self.sqlite_memory.conn.cursor()
            cursor.execute("""
                SELECT variation_content FROM skill_variations
                WHERE variation_id = ?
            """, (active_test['treatment_version'],))
            row = cursor.fetchone()
            if row:
                skill_content = row['variation_content']
```

After storing outcome (step 7), add A/B recording:

```python
# Step 7.5: Record A/B outcome if in test
if active_test and selected_variant:
    is_success = pattern_fidelity >= 0.90
    self.sqlite_memory.record_ab_outcome(
        test_id=active_test['test_id'],
        variant=selected_variant,
        success=is_success
    )

    # Check for promotion
    winner = self.sqlite_memory.check_ab_promotion(active_test['test_id'])
    if winner == 'treatment':
        self.sqlite_memory.promote_variation(active_test['treatment_version'])
        self.sqlite_memory.record_learning_event(
            event_id=str(uuid.uuid4()),
            skill_name=skill_name,
            event_type="variation_promoted",
            description=f"Auto-promoted {active_test['treatment_version']} via A/B win",
            variation_id=active_test['treatment_version']
        )
    elif winner == 'control':
        self.sqlite_memory.archive_variation(active_test['treatment_version'])
```

### Acceptance Criteria
- [ ] `ab_test_assignments` table created on schema init
- [ ] Variations enter A/B test after `evolve_skill()` creates them
- [ ] 50/50 routing works for active tests
- [ ] Auto-promotion fires when treatment wins by 10%+ margin
- [ ] Losing variations archived

---

## Ticket 1.2: ReAct Reasoning Loop Wrapper

**Priority**: P0 | **Estimate**: 3h | **Owner**: 0102

### Problem
`execute_skill()` is single-pass. Low-fidelity results trigger evolution for FUTURE runs, not retry NOW.

### Target Files
| File | Action |
|------|--------|
| `modules/infrastructure/wre_core/wre_master_orchestrator/src/wre_master_orchestrator.py` | ADD ReAct wrapper |

### Implementation Steps

#### Step 1.2.1: Add execute_skill_with_reasoning() method

After `execute_skill()` (line 600), add:

```python
def execute_skill_with_reasoning(
    self,
    skill_name: str,
    agent: str,
    input_context: Dict,
    max_iterations: int = 3,
    fidelity_threshold: float = 0.90,
    force: bool = False
) -> Dict:
    """
    ReAct-style execution with bounded retries.

    Per WRE_COT_DEEP_ANALYSIS.md Gap A:
    Thought -> Action -> Observation -> (Retry if needed)

    Args:
        skill_name: Skill to execute
        agent: Agent to use
        input_context: Input data
        max_iterations: Max retry attempts (default 3)
        fidelity_threshold: Success threshold (default 0.90)
        force: Force execution regardless of libido

    Returns:
        Dict with final result and iteration metadata
    """
    iteration = 0
    results = []
    final_result = None

    while iteration < max_iterations:
        iteration += 1
        logger.info(
            f"[WRE-REACT] Iteration {iteration}/{max_iterations} for {skill_name}"
        )

        # Thought: Analyze context (on retry, include failure analysis)
        if results:
            # Enrich context with failure analysis
            last_failure = results[-1]
            input_context = {
                **input_context,
                "_react_retry": True,
                "_previous_attempt": {
                    "fidelity": last_failure.get("pattern_fidelity", 0),
                    "failed_at_step": last_failure.get("result", {}).get("failed_at_step"),
                    "error": last_failure.get("result", {}).get("error")
                }
            }

        # Action: Execute skill
        result = self.execute_skill(
            skill_name=skill_name,
            agent=agent,
            input_context=input_context,
            force=force
        )
        results.append(result)

        # Observation: Check fidelity
        fidelity = result.get("pattern_fidelity", 0)

        if fidelity >= fidelity_threshold:
            # Success - early exit
            logger.info(
                f"[WRE-REACT] Success on iteration {iteration} - "
                f"fidelity={fidelity:.2f} >= {fidelity_threshold}"
            )
            final_result = result
            break

        # Below threshold - will retry if iterations remain
        if iteration < max_iterations:
            logger.info(
                f"[WRE-REACT] Fidelity {fidelity:.2f} < {fidelity_threshold}, "
                f"retrying..."
            )

    if final_result is None:
        final_result = results[-1] if results else {"error": "No execution"}
        logger.warning(
            f"[WRE-REACT] Exhausted {max_iterations} iterations for {skill_name}"
        )

    # Record telemetry
    if self.sqlite_memory:
        self.sqlite_memory.record_learning_event(
            event_id=str(uuid.uuid4()),
            skill_name=skill_name,
            event_type="react_execution",
            description=(
                f"ReAct execution: {iteration} iterations, "
                f"final_fidelity={final_result.get('pattern_fidelity', 0):.2f}"
            ),
            before_fidelity=results[0].get("pattern_fidelity", 0) if results else None,
            after_fidelity=final_result.get("pattern_fidelity", 0)
        )

    return {
        **final_result,
        "_react_metadata": {
            "iterations": iteration,
            "max_iterations": max_iterations,
            "all_attempts": [
                {"fidelity": r.get("pattern_fidelity", 0)} for r in results
            ],
            "early_success": fidelity >= fidelity_threshold
        }
    }
```

#### Step 1.2.2: Wire ReAct as default entry point

Add config flag to `__init__()`:

```python
# ReAct mode config
self.react_mode = os.getenv("WRE_REACT_MODE", "1").strip() == "1"
self.react_max_iterations = int(os.getenv("WRE_REACT_MAX_ITER", "3"))
self.react_fidelity_threshold = float(os.getenv("WRE_REACT_FIDELITY", "0.90"))
```

### Acceptance Criteria
- [ ] `execute_skill_with_reasoning()` method added
- [ ] Retries up to 3 times on low fidelity
- [ ] Early exit on success
- [ ] Failure context passed to subsequent iterations
- [ ] Telemetry records iteration count

---

## Ticket 1.3: Telemetry Counters

**Priority**: P0 | **Estimate**: 2h | **Owner**: 0102

### Problem
No aggregate metrics for retry rates, variation win rates, or fidelity deltas.

### Target Files
| File | Action |
|------|--------|
| `modules/infrastructure/wre_core/src/pattern_memory.py` | ADD telemetry methods |

### Implementation Steps

#### Step 1.3.1: Add telemetry table

In `_initialize_schema()`, after learning_events table:

```python
# Telemetry counters table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS telemetry_counters (
        counter_name TEXT PRIMARY KEY,
        counter_value INTEGER DEFAULT 0,
        last_updated TEXT
    )
""")
```

#### Step 1.3.2: Add telemetry methods

```python
def increment_counter(self, counter_name: str, delta: int = 1) -> int:
    """Increment telemetry counter and return new value."""
    cursor = self.conn.cursor()
    cursor.execute("""
        INSERT INTO telemetry_counters (counter_name, counter_value, last_updated)
        VALUES (?, ?, ?)
        ON CONFLICT(counter_name) DO UPDATE SET
            counter_value = counter_value + ?,
            last_updated = ?
    """, (
        counter_name, delta, datetime.now().isoformat(),
        delta, datetime.now().isoformat()
    ))
    self.conn.commit()

    cursor.execute(
        "SELECT counter_value FROM telemetry_counters WHERE counter_name = ?",
        (counter_name,)
    )
    row = cursor.fetchone()
    return row['counter_value'] if row else delta

def get_telemetry_dashboard(self) -> Dict:
    """
    Get telemetry dashboard for Sprint 1 metrics.

    Returns:
        Dict with retry_count, variation_win_rate, avg_fidelity_delta
    """
    cursor = self.conn.cursor()

    # Get counters
    cursor.execute("SELECT * FROM telemetry_counters")
    counters = {row['counter_name']: row['counter_value'] for row in cursor.fetchall()}

    # Calculate variation win rate
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN promoted = 1 THEN 1 ELSE 0 END) as promoted
        FROM skill_variations
        WHERE test_status IN ('promoted', 'archived')
    """)
    row = cursor.fetchone()
    total_tested = row['total'] or 0
    promoted = row['promoted'] or 0
    win_rate = promoted / max(total_tested, 1)

    # Calculate avg fidelity delta from learning events
    cursor.execute("""
        SELECT AVG(after_fidelity - before_fidelity) as avg_delta
        FROM learning_events
        WHERE event_type = 'variation_promoted'
          AND before_fidelity IS NOT NULL
          AND after_fidelity IS NOT NULL
    """)
    row = cursor.fetchone()
    avg_delta = row['avg_delta'] or 0

    return {
        "retry_count": counters.get("react_retry_count", 0),
        "total_executions": counters.get("total_executions", 0),
        "variation_win_rate": round(win_rate, 3),
        "avg_fidelity_delta": round(avg_delta, 3),
        "variations_tested": total_tested,
        "variations_promoted": promoted
    }
```

#### Step 1.3.3: Wire counters into execute_skill and ReAct

In `execute_skill()`, after storing outcome:

```python
# Telemetry
if self.sqlite_memory:
    self.sqlite_memory.increment_counter("total_executions")
```

In `execute_skill_with_reasoning()`, after retry:

```python
if iteration > 1 and self.sqlite_memory:
    self.sqlite_memory.increment_counter("react_retry_count")
```

### Acceptance Criteria
- [ ] `telemetry_counters` table created
- [ ] `get_telemetry_dashboard()` returns retry_count, win_rate, fidelity_delta
- [ ] Counters increment on each execution and retry
- [ ] Dashboard queryable via `get_skill_statistics()` enhancement

---

## Sprint 1 Execution Order

```
1.1.1 → 1.1.2 → 1.3.1 → 1.3.2 → 1.2.1 → 1.2.2 → 1.1.3 → 1.3.3
   ↓       ↓       ↓       ↓       ↓       ↓       ↓       ↓
 schema  methods  schema  methods  ReAct  config   A/B    wire
```

**Rationale**: Schema first, then methods, then wiring. ReAct before A/B routing so tests can validate iteration behavior.

---

## Validation Plan

### Unit Tests
```python
# test_tt_si_promotion.py
def test_ab_test_scheduling():
    """Verify A/B test can be scheduled."""

def test_ab_routing_50_50():
    """Verify 50/50 split between control and treatment."""

def test_auto_promotion_on_win():
    """Verify treatment promoted when margin > 10%."""

# test_react_loop.py
def test_early_exit_on_success():
    """Verify ReAct exits on first success."""

def test_retry_on_low_fidelity():
    """Verify ReAct retries when fidelity < threshold."""

def test_max_iterations_respected():
    """Verify ReAct stops at max_iterations."""
```

### Integration Test
```bash
# Run skill with ReAct enabled
WRE_REACT_MODE=1 python -c "
from modules.infrastructure.wre_core.wre_master_orchestrator import WREMasterOrchestrator
m = WREMasterOrchestrator()
result = m.execute_skill_with_reasoning('qwen_gitpush', 'qwen', {'test': True})
print(result['_react_metadata'])
"
```

---

## Success Metrics (CTO Gate from WRE_COT_DEEP_ANALYSIS.md)

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Median fidelity | TBD | +20% | `get_skill_metrics()` |
| Repeated failure rate | TBD | -30% | `react_retry_count / total_executions` |
| Variation promotion rate | 0% | >50% | `variation_win_rate` from dashboard |

---

*Created: 2026-02-24 | Sprint 1 of WRE CoT Closure*
