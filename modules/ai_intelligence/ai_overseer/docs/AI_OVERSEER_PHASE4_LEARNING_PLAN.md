# AI_Overseer Phase 4 Learning Feedback - Implementation Plan

**Date**: 2025-10-28
**Status**: Ready for Implementation
**Dependencies**: ✅ Gemma/Qwen wiring complete, ✅ PatternMemory infrastructure exists

---

## Current State

### ✅ Completed (Phases 1-3)
- **Phase 1 (Gemma)**: ML-validated bug detection - OPERATIONAL (lines 921-1007)
- **Phase 2 (Qwen)**: Strategic MPS classification - OPERATIONAL (lines 1009-1156)
- **Phase 3 (0102)**: Execution and oversight - ACTIVE
- **Models**: Both loaded from E:/HoloIndex/models/ and working

### ⏳ Phase 4 TODO: Learning Feedback Loop
**Goal**: Store successful detections → recall patterns → improve future inference

**Existing Infrastructure**:
- ✅ `PatternMemory` class exists: `modules/infrastructure/wre_core/src/pattern_memory.py`
- ✅ SQLite schema with `skill_outcomes`, `skill_variations`, `learning_events` tables
- ✅ Methods: `store_outcome()`, `recall_successful_patterns()`, `recall_failure_patterns()`
- ✅ `SkillOutcome` dataclass with all required fields

---

## Implementation Plan

### Step 1: Initialize PatternMemory in AI_Overseer

**File**: `modules/ai_intelligence/ai_overseer/src/ai_overseer.py`

**Location**: After line 227 (after `self._qwen_available = False`)

**Add**:
```python
# WSP 48: Pattern Memory for recursive learning
try:
    from modules.infrastructure.wre_core.src.pattern_memory import PatternMemory, SkillOutcome
    self.pattern_memory = PatternMemory()
    self._pattern_memory_available = True
    logger.info("[AI-OVERSEER] Pattern memory initialized for learning feedback")
except Exception as e:
    self.pattern_memory = None
    self._pattern_memory_available = False
    logger.warning(f"[AI-OVERSEER] Pattern memory unavailable: {e}")
```

**Why**: Graceful degradation - system works without pattern memory, but learns when available

### Step 2: Store Outcomes After Detection/Classification

**File**: `modules/ai_intelligence/ai_overseer/src/ai_overseer.py`

**Method**: Add new method after `_qwen_classify_bugs()` (~line 1157)

```python
def _store_detection_outcome(
    self,
    skill_name: str,
    agent: str,
    execution_id: str,
    detected_bugs: List[Dict],
    classified_bugs: List[Dict],
    execution_time_ms: int,
    success: bool
) -> None:
    """
    Store bug detection/classification outcome for learning

    Per WSP 48: Recursive self-improvement through pattern storage

    Args:
        skill_name: Skill used for detection (e.g., "youtube_daemon_monitor")
        agent: Which agent performed the work ("gemma" or "qwen")
        execution_id: Unique execution ID
        detected_bugs: Bugs detected by Gemma
        classified_bugs: Classifications from Qwen
        execution_time_ms: Total execution time
        success: Whether detection/classification succeeded
    """
    if not self._pattern_memory_available:
        return

    try:
        # Calculate pattern fidelity based on confidence scores
        if agent == "gemma":
            # Average Gemma confidence across all detections
            confidences = [b.get("gemma_confidence", 0.0) for b in detected_bugs if b.get("ml_validated")]
            pattern_fidelity = sum(confidences) / len(confidences) if confidences else 0.0
        elif agent == "qwen":
            # Average based on classification success
            pattern_fidelity = 1.0 if classified_bugs else 0.0
        else:
            pattern_fidelity = 0.5

        # Create outcome record
        outcome = SkillOutcome(
            execution_id=execution_id,
            skill_name=skill_name,
            agent=agent,
            timestamp=datetime.now().isoformat(),
            input_context=json.dumps({
                "detected_bugs_count": len(detected_bugs),
                "classified_bugs_count": len(classified_bugs)
            }),
            output_result=json.dumps({
                "detected": [b["pattern_name"] for b in detected_bugs],
                "classified": [{
                    "pattern": c["pattern_name"],
                    "action": c["qwen_action"],
                    "complexity": c.get("complexity", 0)
                } for c in classified_bugs]
            }),
            success=success,
            pattern_fidelity=pattern_fidelity,
            outcome_quality=1.0 if success else 0.0,
            execution_time_ms=execution_time_ms,
            step_count=2 if agent == "qwen" else 1,  # Gemma=1 step, Qwen=2 steps
            failed_at_step=None if success else 1,
            notes=f"{len(detected_bugs)} bugs detected, {len(classified_bugs)} classified"
        )

        # Store in pattern memory
        self.pattern_memory.store_outcome(outcome)

        logger.info(f"[AI-OVERSEER] Stored {agent} outcome - exec_id={execution_id}, "
                   f"fidelity={pattern_fidelity:.2f}, bugs={len(detected_bugs)}")

    except Exception as e:
        logger.warning(f"[AI-OVERSEER] Failed to store outcome: {e}")
```

### Step 3: Recall Patterns Before Inference

**File**: `modules/ai_intelligence/ai_overseer/src/ai_overseer.py`

**Enhance**: `_gemma_detect_errors()` method (~line 937)

**Before line 960** (before Gemma ML validation), add:

```python
# Step 2: HoloIndex research - Recall successful patterns
if self._pattern_memory_available:
    try:
        successful_patterns = self.pattern_memory.recall_successful_patterns(
            skill_name=skill.get("daemon_name", "unknown"),
            min_fidelity=0.90,
            limit=3
        )

        if successful_patterns:
            # Add pattern context to prompt
            pattern_context = "\\n\\nLearned from past successful detections:\\n"
            for p in successful_patterns:
                pattern_context += f"- Pattern '{p['skill_name']}' validated with {p['pattern_fidelity']:.0%} confidence\\n"

            prompt = prompt + pattern_context

            logger.debug(f"[GEMMA] Enhanced prompt with {len(successful_patterns)} learned patterns")
    except Exception as e:
        logger.debug(f"[GEMMA] Pattern recall failed: {e}")
```

**Enhance**: `_qwen_classify_bugs()` method (~line 1055)

**Before line 1068** (before Qwen classification), add:

```python
# Step 1+2: Deep think + HoloIndex research - Recall learned patterns
if self._pattern_memory_available:
    try:
        successful_patterns = self.pattern_memory.recall_successful_patterns(
            skill_name=skill.get("daemon_name", "unknown"),
            min_fidelity=0.90,
            limit=5
        )

        if successful_patterns:
            pattern_context = "\\n\\nLearned from past classifications:\\n"
            for p in successful_patterns:
                output = json.loads(p['output_result'])
                pattern_context += f"- Successfully classified {len(output.get('classified', []))} bugs\\n"

            prompt = prompt.format(bug=bug, config=config) + pattern_context

            logger.debug(f"[QWEN] Enhanced prompt with {len(successful_patterns)} learned patterns")
    except Exception as e:
        logger.debug(f"[QWEN] Pattern recall failed: {e}")
```

### Step 4: Call Outcome Storage After Each Cycle

**File**: `modules/ai_intelligence/ai_overseer/src/ai_overseer.py`

**Method**: Update `monitor_daemon()` method (~line 700)

**After Gemma detection** (~line 760), add:

```python
# Store Gemma detection outcome
if detected_bugs:
    execution_id = f"gemma_detect_{int(time.time() * 1000)}"
    self._store_detection_outcome(
        skill_name=skill.get("daemon_name", "unknown"),
        agent="gemma",
        execution_id=execution_id,
        detected_bugs=detected_bugs,
        classified_bugs=[],
        execution_time_ms=int((time.time() - detection_start) * 1000),
        success=True
    )
```

**After Qwen classification** (~line 780), add:

```python
# Store Qwen classification outcome
if classified_bugs:
    execution_id = f"qwen_classify_{int(time.time() * 1000)}"
    self._store_detection_outcome(
        skill_name=skill.get("daemon_name", "unknown"),
        agent="qwen",
        execution_id=execution_id,
        detected_bugs=detected_bugs,
        classified_bugs=classified_bugs,
        execution_time_ms=int((time.time() - classification_start) * 1000),
        success=True
    )
```

---

## Testing Plan

### Unit Test

**File**: `modules/ai_intelligence/ai_overseer/tests/test_pattern_learning.py`

```python
def test_pattern_memory_integration():
    """Test that AI_overseer stores and recalls patterns"""
    overseer = AIIntelligenceOverseer(Path("O:/Foundups-Agent"))

    # Verify pattern memory initialized
    assert overseer._pattern_memory_available
    assert overseer.pattern_memory is not None

    # Test storing outcome
    outcome = SkillOutcome(
        execution_id="test_exec_001",
        skill_name="test_daemon",
        agent="gemma",
        timestamp=datetime.now().isoformat(),
        input_context="{}",
        output_result='{"detected": ["test_bug"]}',
        success=True,
        pattern_fidelity=0.95,
        outcome_quality=1.0,
        execution_time_ms=150,
        step_count=1
    )

    overseer.pattern_memory.store_outcome(outcome)

    # Test recalling patterns
    patterns = overseer.pattern_memory.recall_successful_patterns(
        skill_name="test_daemon",
        min_fidelity=0.90
    )

    assert len(patterns) >= 1
    assert patterns[0]['execution_id'] == "test_exec_001"
    assert patterns[0]['pattern_fidelity'] >= 0.90
```

### Integration Test

**Test with Live Daemon**:
1. Run YouTube DAE with AI monitoring (menu option 5)
2. Let run for 5-10 detection cycles
3. Check pattern_memory.db has records:
   ```bash
   sqlite3 modules/infrastructure/wre_core/data/pattern_memory.db \
     "SELECT COUNT(*) FROM skill_outcomes WHERE agent IN ('gemma', 'qwen');"
   ```
4. Verify logs show pattern recall:
   ```
   [GEMMA] Enhanced prompt with 3 learned patterns
   [QWEN] Enhanced prompt with 5 learned patterns
   ```

---

## Expected Improvements

### Accuracy Over Time

| Metric | Week 1 | Week 2 | Week 4 | Target |
|--------|--------|--------|--------|--------|
| **False Positives** | 20% | 15% | 10% | <8% |
| **Detection Accuracy** | 75% | 82% | 88% | >85% |
| **Pattern Fidelity** | 0.70 | 0.80 | 0.92 | >0.90 |

### Token Efficiency

- **Before Learning**: 500 tokens/prompt (no context)
- **After Learning**: 650 tokens/prompt (+150 for pattern context)
- **Net Benefit**: Higher accuracy outweighs 30% token increase

---

## Success Criteria

✅ PatternMemory initializes without errors
✅ Outcomes stored after each detection/classification cycle
✅ Patterns recalled and injected into Gemma/Qwen prompts
✅ SQLite database populated with skill_outcomes records
✅ Logs confirm "Enhanced prompt with N learned patterns"
✅ Detection accuracy improves >5% after 1 week

---

## WSP Compliance

- ✅ **WSP 48** (Recursive Self-Improvement): Pattern storage enables continuous learning
- ✅ **WSP 60** (Module Memory): SQLite database in module data directory
- ✅ **WSP 91** (DAEMON Observability): All learning events logged
- ✅ **WSP 96** (Skills Wardrobe): Foundation for specialized model training

---

## Next Steps

1. **Implement** (Est: 1-2 hours):
   - Add PatternMemory initialization
   - Create `_store_detection_outcome()` method
   - Enhance Gemma/Qwen prompts with pattern recall
   - Add outcome storage calls in monitor_daemon()

2. **Test** (Est: 30 minutes):
   - Run unit tests
   - Live daemon test with 5-10 cycles
   - Verify SQLite database population

3. **Document** (Est: 15 minutes):
   - Update ModLog.md with Phase 4 completion
   - Update README.md with learning capabilities
   - Add example to docs showing pattern recall

4. **Monitor** (Ongoing):
   - Track accuracy improvements over 1 week
   - Measure false positive rate reduction
   - Analyze pattern fidelity trends

---

**Status**: 📋 Implementation plan complete - Ready to code Phase 4
**Estimated Time**: 2-3 hours total
**Risk**: Low (graceful degradation if pattern memory fails)
**Value**: High (enables continuous accuracy improvement)
