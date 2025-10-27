# AI_Overseer AI Wiring Architecture

**Status**: Design Phase
**Date**: 2025-10-28
**WSP Compliance**: WSP 77 (Agent Coordination), WSP 15 (MPS), WSP 96 (Skills), WSP 48 (Learning)

## Problem Statement

Current AI_overseer uses **static JSON lookups** instead of actual AI inference:

| Component | Current | Target |
|-----------|---------|--------|
| Gemma Detection | `re.findall()` regex | Gemma 270M ML inference |
| Qwen Classification | JSON value lookup | Qwen 1.5B strategic analysis |
| Learning Feedback | One-way storage | Adaptive pattern improvement |

**Consequence**: Cannot adapt to new error patterns, cannot dynamically assess complexity.

## Solution Architecture

### Phase 1: Gemma Pattern Detection (Micro-Sprint 1)

**Current** (`ai_overseer.py:913-932`):
```python
def _gemma_detect_errors(self, bash_output: str, skill: Dict) -> List[Dict]:
    """Phase 1 (Gemma): Fast error pattern detection using skill patterns"""
    import re
    detected = []

    error_patterns = skill.get("error_patterns", {})
    for pattern_name, pattern_config in error_patterns.items():
        regex = pattern_config.get("regex", "")
        matches = re.findall(regex, bash_output, re.IGNORECASE | re.MULTILINE)
        if matches:
            detected.append({"pattern_name": pattern_name, "matches": matches, "config": pattern_config})

    return detected
```

**Target** (using `GemmaRAGInference`):
```python
def _gemma_detect_errors(self, bash_output: str, skill: Dict) -> List[Dict]:
    """Phase 1 (Gemma): ML-based error pattern detection"""
    from holo_index.qwen_advisor.gemma_rag_inference import GemmaRAGInference

    if not hasattr(self, '_gemma_engine'):
        self._gemma_engine = GemmaRAGInference()

    detected = []
    error_patterns = skill.get("error_patterns", {})

    for pattern_name, pattern_config in error_patterns.items():
        # Step 1: Use regex as fast pre-filter (50-100ms)
        regex = pattern_config.get("regex", "")
        regex_matches = re.findall(regex, bash_output, re.IGNORECASE | re.MULTILINE)

        if regex_matches:
            # Step 2: Gemma ML validates if this is truly a bug (binary classification)
            prompt = f"""Error Pattern: {pattern_name}
Description: {pattern_config.get('description', '')}
Log Excerpt: {bash_output[-500:]}

Question: Is this a genuine bug requiring action? Answer YES or NO with confidence."""

            result = self._gemma_engine.infer(prompt)

            if result.response.upper().startswith("YES") and result.confidence > 0.7:
                detected.append({
                    "pattern_name": pattern_name,
                    "matches": regex_matches,
                    "config": pattern_config,
                    "gemma_confidence": result.confidence,
                    "ml_validated": True
                })

    return detected
```

**Performance Target**: 50-150ms (regex 50ms + Gemma 100ms)

### Phase 2: Qwen Strategic Classification (Micro-Sprint 2)

**Current** (`ai_overseer.py:934-972`):
```python
def _qwen_classify_bugs(self, detected_bugs: List[Dict], skill: Dict) -> List[Dict]:
    """Phase 2 (Qwen): Classify bugs with WSP 15 MPS scoring and determine actions"""
    for bug in detected_bugs:
        config = bug["config"]
        qwen_action = config.get("qwen_action", "ignore")  # ❌ JSON LOOKUP
        wsp_15_mps = config.get("wsp_15_mps", {})          # ❌ JSON LOOKUP
        complexity = wsp_15_mps.get("complexity", 3)       # ❌ JSON LOOKUP
        # ...
```

**Target** (using `QwenInferenceEngine`):
```python
def _qwen_classify_bugs(self, detected_bugs: List[Dict], skill: Dict) -> List[Dict]:
    """Phase 2 (Qwen): Strategic MPS scoring and action determination"""
    from holo_index.qwen_advisor.llm_engine import QwenInferenceEngine

    if not hasattr(self, '_qwen_engine'):
        self._qwen_engine = QwenInferenceEngine(
            model_path=Path("E:/LLM_Models/qwen-coder-1.5b.gguf"),
            max_tokens=512,
            temperature=0.2
        )
        self._qwen_engine.initialize()

    classified = []

    for bug in detected_bugs:
        config = bug["config"]

        # Qwen performs WSP 15 MPS scoring dynamically
        prompt = f"""Bug Classification Task (WSP 15 MPS Scoring):

Pattern: {bug['pattern_name']}
Description: {config.get('description', '')}
Matches Found: {len(bug['matches'])}
Daemon Context: {skill.get('daemon_name', 'unknown')}

WSP 15 Scoring Criteria (1-5 scale):
1. Complexity (1=trivial, 5=architectural)
2. Importance (1=optional, 5=critical)
3. Deferability (1=urgent, 5=can wait)
4. Impact (1=minimal, 5=transformative)

Provide JSON response:
{{
    "complexity": <1-5>,
    "importance": <1-5>,
    "deferability": <1-5>,
    "impact": <1-5>,
    "total_mps": <sum>,
    "priority": "<P0|P1|P2|P3|P4>",
    "action": "<auto_fix|bug_report|ignore>",
    "rationale": "<1 sentence>"
}}"""

        response = self._qwen_engine.generate_response(prompt)

        # Parse Qwen's JSON response
        import json
        try:
            qwen_analysis = json.loads(response)

            classification = {
                "pattern_name": bug["pattern_name"],
                "complexity": qwen_analysis["complexity"],
                "auto_fixable": (qwen_analysis["action"] == "auto_fix"),
                "needs_0102": (qwen_analysis["action"] == "bug_report"),
                "qwen_action": qwen_analysis["action"],
                "mps_score": qwen_analysis["total_mps"],
                "priority": qwen_analysis["priority"],
                "rationale": qwen_analysis["rationale"],
                "matches": bug["matches"],
                "config": config,
                "ml_classified": True
            }

            classified.append(classification)

        except Exception as e:
            logger.error(f"[QWEN-ERROR] Failed to parse response: {e}")
            # Fallback to static config
            classified.append(self._fallback_static_classification(bug, config))

    return classified
```

**Performance Target**: 200-500ms per bug (Qwen strategic analysis)

### Phase 3: WRE Libido Monitor Integration (Micro-Sprint 3)

Wire `GemmaLibidoMonitor` to control pattern execution frequency:

```python
from modules.infrastructure.wre_core.src.libido_monitor import GemmaLibidoMonitor, LibidoSignal

class AIIntelligenceOverseer:
    def __init__(self, repo_root: Path):
        # ... existing init ...

        # WRE Libido Monitor for pattern frequency control
        self.libido_monitor = GemmaLibidoMonitor(
            history_size=100,
            default_min_frequency=1,
            default_max_frequency=5,
            default_cooldown_seconds=300  # 5 minutes
        )

        # Set daemon-specific thresholds
        self.libido_monitor.set_thresholds(
            skill_name="youtube_daemon_monitor",
            min_frequency=1,
            max_frequency=10,  # Allow more frequent YouTube monitoring
            cooldown_seconds=30  # 30 second cooldown
        )

    def monitor_daemon(self, bash_output: str, skill_path: Path, ...) -> Dict:
        """Ubiquitous daemon monitor with WRE libido control"""

        skill_name = skill.get("daemon_name", "unknown_daemon")
        exec_id = f"monitor_{int(time.time())}"

        # Check libido signal before monitoring
        signal = self.libido_monitor.should_execute(skill_name, exec_id, force=False)

        if signal == LibidoSignal.THROTTLE:
            logger.info(f"[LIBIDO] THROTTLE - skipping {skill_name} (pattern frequency too high)")
            return {"success": True, "throttled": True}

        # Proceed with monitoring...
        detected_bugs = self._gemma_detect_errors(bash_output, skill)
        classified_bugs = self._qwen_classify_bugs(detected_bugs, skill)

        # Record execution for libido tracking
        avg_fidelity = sum(b.get("gemma_confidence", 0) for b in detected_bugs) / len(detected_bugs) if detected_bugs else 0.0
        self.libido_monitor.record_execution(
            skill_name=skill_name,
            agent="ai_overseer",
            execution_id=exec_id,
            fidelity_score=avg_fidelity
        )

        # ... rest of monitoring ...
```

### Phase 4: Learning Feedback Loop (Micro-Sprint 3)

Wire pattern memory to improve Gemma/Qwen over time:

```python
def _store_monitoring_patterns(self, skill_path: Path, results: Dict) -> None:
    """Phase 4: Store outcomes to improve future detection"""
    skill = self._load_daemon_skill(skill_path)
    skill_name = skill.get("daemon_name", "unknown_daemon")

    # Update skill learning stats
    stats = skill.get("learning_stats", {})
    stats["total_bugs_detected"] = stats.get("total_bugs_detected", 0) + results["bugs_detected"]
    stats["total_bugs_fixed"] = stats.get("total_bugs_fixed", 0) + results["bugs_fixed"]
    stats["last_detection"] = datetime.now().isoformat()

    if results["bugs_fixed"] > 0:
        stats["last_fix"] = datetime.now().isoformat()

    # Calculate pattern accuracy (successful fixes / total detections)
    if stats["total_bugs_detected"] > 0:
        stats["pattern_accuracy"] = stats["total_bugs_fixed"] / stats["total_bugs_detected"]

    skill["learning_stats"] = stats
    skill["last_monitoring_run"] = time.time()

    # Write updated skill back to disk
    with open(skill_path, 'w', encoding='utf-8') as f:
        json.dump(skill, f, indent=2)

    logger.info(f"[LEARNING] Updated skill stats - accuracy={stats.get('pattern_accuracy', 0):.2%}")

    # TODO: Feed learning stats back to Gemma/Qwen for improved inference
    # This requires pattern memory integration (ChromaDB)
```

## Micro-Sprint Implementation Plan

### Sprint 1: Gemma Pattern Detection (Day 1)
- [ ] Add `GemmaRAGInference` initialization to `__init__`
- [ ] Replace `_gemma_detect_errors()` with ML validation
- [ ] Test with live YouTube daemon logs
- [ ] Measure performance (target: <150ms)
- [ ] WSP validation

### Sprint 2: Qwen Strategic Classification (Day 2)
- [ ] Add `QwenInferenceEngine` initialization to `__init__`
- [ ] Replace `_qwen_classify_bugs()` with strategic analysis
- [ ] Test MPS scoring accuracy
- [ ] Fallback to static config if Qwen fails
- [ ] WSP validation

### Sprint 3: WRE + Learning Integration (Day 3)
- [ ] Add `GemmaLibidoMonitor` initialization
- [ ] Wire `should_execute()` checks
- [ ] Implement learning feedback storage
- [ ] Test pattern accuracy improvement
- [ ] WSP validation

### Sprint 4: End-to-End Testing (Day 4)
- [ ] Live YouTube daemon monitoring
- [ ] Verify Gemma → Qwen → 0102 → Learning flow
- [ ] Performance benchmarks
- [ ] Documentation updates

## Success Criteria

| Metric | Target |
|--------|--------|
| Gemma Detection Latency | <150ms |
| Qwen Classification Latency | <500ms |
| Pattern Accuracy | >85% after 10 iterations |
| False Positive Rate | <10% |
| Libido Throttling | Prevents spam loops |
| Learning Improvement | Measurable over 24h |

## WSP Compliance

- **WSP 77**: 4-phase agent coordination (Gemma → Qwen → 0102 → Learning)
- **WSP 15**: Dynamic MPS scoring by Qwen
- **WSP 96**: WRE skills architecture with libido control
- **WSP 48**: Pattern memory and adaptive learning
- **WSP 91**: Structured DAEMON observability

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Qwen/Gemma models not available | Graceful fallback to static config |
| Inference too slow | Cache Qwen responses for repeated patterns |
| Pattern accuracy regression | A/B test new vs old before deployment |
| Over-throttling | Configurable libido thresholds per daemon |

## Next Steps

1. ✅ Complete architecture design
2. 🔄 Execute Micro-Sprint 1 (Gemma wiring)
3. ⏳ Execute Micro-Sprint 2 (Qwen wiring)
4. ⏳ Execute Micro-Sprint 3 (WRE + Learning)
5. ⏳ End-to-end testing
6. ⏳ Documentation + ModLog updates

---

**Architecture Status**: READY FOR IMPLEMENTATION
**Next Action**: Execute Micro-Sprint 1 (Gemma Pattern Detection)
