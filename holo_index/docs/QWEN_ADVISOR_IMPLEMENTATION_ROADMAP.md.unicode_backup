# QwenAdvisor Implementation Roadmap: From Stub to Intelligence
## Transforming HoloIndex into 0102's Proactive Compliance Guardian

> **Current State**: Stub returning fixed reminders only with --llm-advisor flag
> **Target State**: Intelligent, always-on compliance guardian for 0102 agents
> **Priority**: P0 - Critical for true "green baseplate" functionality

---

## 🎯 Vision: The Intelligent Advisor

### Core Principle
**HoloIndex is for 0102 agents, not 012 human developers**. The advisor should be:
- **Always-on by default** (0102 agents need constant guidance)
- **Context-aware** (understands query intent and current violations)
- **Proactive** (prevents violations before they happen)
- **Learning** (improves from patterns and feedback)

---

## 📋 Implementation Phases

### Phase 1: Wire Actual Inference Engine (Week 1-2)
**Goal**: Replace stub with intelligent guidance generation

```python
class QwenAdvisorIntelligence:
    """Real inference engine for context-aware guidance."""

    def __init__(self):
        # Option 1: Local Qwen model (already scaffolded)
        self.qwen_model = load_qwen_model()  # Qwen2.5-Coder-1.5B

        # Option 2: Rules engine fallback
        self.rules_engine = ComplianceRulesEngine()

        # Option 3: Hybrid approach (rules + LLM)
        self.hybrid_engine = HybridInferenceEngine()

    def generate_contextual_guidance(self, query, hits, context):
        """Generate intelligent guidance based on context."""
        # Analyze query intent
        intent = self.analyze_intent(query)

        # Check violation history
        violations = self.check_violation_patterns(query, context)

        # Generate tailored guidance
        guidance = self.inference_engine.generate(
            query=query,
            search_hits=hits,
            intent=intent,
            violations=violations,
            wsp_context=self.load_relevant_wsps(intent)
        )

        return guidance
```

**Key Deliverables**:
- [ ] Implement intent analysis from query patterns
- [ ] Connect to WSP_VIOLATIONS.md for historical context
- [ ] Generate dynamic guidance based on search results
- [ ] Fallback to rules engine if LLM unavailable

### Phase 2: Expand Protocol Checkpoints (Week 2-3)
**Goal**: Comprehensive WSP compliance checking

```python
class ProtocolCheckpoints:
    """Comprehensive WSP compliance checkpoints."""

    CRITICAL_CHECKS = {
        "no_root_vibecoding": {
            "trigger": ["create", "new file", "test"],
            "guidance": "WSP 85: Never create files in root. Use proper module structure.",
            "validation": check_root_directory_protection
        },

        "consult_modlog_first": {
            "trigger": ["add test", "create test", "new test"],
            "guidance": "WSP 22: Check TestModLog before adding tests. Update after changes.",
            "validation": check_modlog_consultation
        },

        "holoindex_first": {
            "trigger": ["implement", "create", "build"],
            "guidance": "WSP 87: Run HoloIndex search FIRST. Code probably exists.",
            "validation": check_holoindex_usage
        },

        "no_enhanced_duplicates": {
            "trigger": ["enhanced_", "_v2", "_new", "_improved"],
            "guidance": "WSP 84: NEVER create enhanced_ versions. Edit existing code.",
            "validation": check_duplicate_prevention
        },

        "module_structure": {
            "trigger": ["new module", "create module"],
            "guidance": "WSP 49: Follow standard structure: src/, tests/, docs/, memory/",
            "validation": check_module_structure
        }
    }

    def run_all_checkpoints(self, query, context):
        """Run all relevant checkpoints for the query."""
        triggered_checks = []

        for check_id, check_config in self.CRITICAL_CHECKS.items():
            if self.is_triggered(query, check_config["trigger"]):
                result = check_config["validation"](query, context)
                if not result.passed:
                    triggered_checks.append({
                        "checkpoint": check_id,
                        "guidance": check_config["guidance"],
                        "severity": result.severity,
                        "fix": result.suggested_fix
                    })

        return triggered_checks
```

**Key Deliverables**:
- [ ] Implement all critical WSP checkpoints
- [ ] Create validation functions for each checkpoint
- [ ] Add context-aware triggering logic
- [ ] Generate actionable fix suggestions

### Phase 3: Enable by Default for 0102 (Week 3-4)
**Goal**: Make advisor always-on for agents

```python
class HoloIndexConfig:
    """Configuration for 0102 vs 012 operation modes."""

    @property
    def is_0102_mode(self):
        """Detect if running as 0102 agent."""
        return any([
            os.getenv('AGENT_MODE') == '0102',
            os.getenv('HOLOINDEX_ADVISOR') == 'always',
            self.detect_windsurf_environment(),
            self.detect_cursor_environment(),
            self.detect_ci_environment()
        ])

    @property
    def advisor_mode(self):
        """Determine advisor operation mode."""
        if self.is_0102_mode:
            return 'always_on'  # Default for 0102
        elif os.getenv('HOLOINDEX_ADVISOR_MODE'):
            return os.getenv('HOLOINDEX_ADVISOR_MODE')
        else:
            return 'opt_in'  # Default for 012 humans

    def should_run_advisor(self, args):
        """Determine if advisor should run."""
        if args.no_advisor:  # Explicit opt-out
            return False
        if args.llm_advisor:  # Explicit opt-in
            return True
        return self.advisor_mode == 'always_on'
```

**Implementation Options**:
1. **Environment Detection**: Auto-detect 0102 environment (Windsurf, Cursor, CI)
2. **Config File**: `.holoindex.yml` with agent settings
3. **Command Line**: Default to on, add `--no-advisor` flag for opt-out
4. **Agent Declaration**: `AGENT_MODE=0102` environment variable

**Key Deliverables**:
- [ ] Implement environment detection logic
- [ ] Add configuration system
- [ ] Modify CLI to default advisor on
- [ ] Add opt-out mechanism for human developers

### Phase 4: Violation Detection System (Week 4-5)
**Goal**: Read and learn from violation logs

```python
class ViolationDetectionSystem:
    """Track and learn from WSP violations."""

    def __init__(self):
        self.violations_file = Path("WSP_VIOLATIONS.md")
        self.violations_db = Path("memory/violations.json")
        self.pattern_analyzer = ViolationPatternAnalyzer()

    def load_violation_history(self):
        """Load and parse violation history."""
        if self.violations_file.exists():
            violations = self.parse_violations_md(
                self.violations_file.read_text()
            )
            return violations
        return []

    def detect_violation_risk(self, query, context):
        """Detect risk of violations based on patterns."""
        historical_violations = self.load_violation_history()

        # Analyze query for violation patterns
        risk_factors = self.pattern_analyzer.analyze(
            query=query,
            historical=historical_violations,
            context=context
        )

        if risk_factors.high_risk:
            return {
                "risk_level": "HIGH",
                "likely_violations": risk_factors.predicted_violations,
                "prevention_guidance": risk_factors.prevention_steps,
                "similar_past_violations": risk_factors.similar_cases
            }

        return {"risk_level": "LOW"}

    def record_violation(self, violation_data):
        """Record new violation for learning."""
        violations = self.load_violations_db()
        violations.append({
            "timestamp": datetime.now().isoformat(),
            "query": violation_data.query,
            "violation": violation_data.wsp_violation,
            "context": violation_data.context,
            "prevention": violation_data.prevention_applied
        })
        self.save_violations_db(violations)

        # Update pattern analyzer with new data
        self.pattern_analyzer.update_patterns(violation_data)
```

**Key Deliverables**:
- [ ] Parse existing WSP_VIOLATIONS.md format
- [ ] Create violation pattern analyzer
- [ ] Implement risk scoring system
- [ ] Build learning feedback loop

### Phase 5: Telemetry and FMAS Integration (Week 5-6)
**Goal**: Make tests real and track effectiveness

```python
class AdvisorTelemetry:
    """Track advisor effectiveness and learning."""

    def __init__(self):
        self.telemetry_file = Path("E:/HoloIndex/telemetry/advisor_metrics.json")
        self.fmas_scorer = FMASScorer()

    def track_guidance_event(self, event_data):
        """Track every guidance event for analysis."""
        telemetry = {
            "timestamp": datetime.now().isoformat(),
            "query": event_data.query,
            "guidance_provided": event_data.guidance,
            "checkpoints_triggered": event_data.checkpoints,
            "user_response": event_data.response,  # accepted/ignored/modified
            "effectiveness_score": self.calculate_effectiveness(event_data)
        }

        self.append_telemetry(telemetry)

        # Update FMAS scores
        self.fmas_scorer.update_scores({
            "compliance_effectiveness": telemetry["effectiveness_score"],
            "guidance_quality": event_data.quality_rating,
            "violation_prevention": event_data.violations_prevented
        })

    def generate_effectiveness_report(self):
        """Generate report on advisor effectiveness."""
        return {
            "total_guidances": self.count_guidances(),
            "violations_prevented": self.count_prevented_violations(),
            "compliance_improvement": self.calculate_compliance_trend(),
            "user_satisfaction": self.calculate_satisfaction_score(),
            "learning_velocity": self.calculate_learning_rate()
        }
```

**Real FMAS Test Implementation**:
```python
# In tests/test_qwen_advisor_real.py

def test_advisor_prevents_root_vibecoding():
    """F1: Test that advisor prevents root directory violations."""
    advisor = QwenAdvisor()
    query = "create test_new_feature.py"

    guidance = advisor.generate_guidance(query, context={})

    assert "WSP 85" in guidance
    assert "Never create files in root" in guidance
    assert guidance.suggests_proper_location()

def test_advisor_detects_enhanced_duplicates():
    """F2: Test detection of enhanced_ anti-pattern."""
    advisor = QwenAdvisor()
    query = "create enhanced_chat_sender.py"

    guidance = advisor.generate_guidance(query, context={})

    assert "WSP 84" in guidance
    assert "NEVER create enhanced_ versions" in guidance
    assert guidance.suggests_existing_file("chat_sender.py")

def test_advisor_telemetry_tracking():
    """F5: Test telemetry is properly recorded."""
    advisor = QwenAdvisor()
    initial_events = advisor.telemetry.count_events()

    advisor.generate_guidance("test query", context={})

    assert advisor.telemetry.count_events() == initial_events + 1
    assert advisor.telemetry.last_event().has_required_fields()
```

**Key Deliverables**:
- [ ] Implement telemetry tracking system
- [ ] Create real FMAS tests (not stubs)
- [ ] Build effectiveness scoring
- [ ] Generate learning reports

---

## 🚀 Quick Wins Implementation Order

### Week 1: Minimum Viable Intelligence
1. **Replace stub with rules engine** (no LLM needed initially)
2. **Add 5 critical checkpoints** (root, enhanced_, modlog, holoindex, module structure)
3. **Enable by default** with environment detection

### Week 2: Context Awareness
1. **Parse WSP_VIOLATIONS.md** for historical context
2. **Implement intent analysis** from query patterns
3. **Generate dynamic guidance** based on context

### Week 3: Always-On for 0102
1. **Auto-detect agent environments** (Windsurf, Cursor)
2. **Default to advisor on** for agents
3. **Add --no-advisor flag** for opt-out

### Week 4: Learning System
1. **Track all guidance events** to telemetry
2. **Analyze effectiveness** of guidance
3. **Update patterns** based on feedback

---

## 📊 Success Metrics

### Phase 1 Success (Minimum Viable)
- [ ] Advisor generates context-aware guidance (not fixed strings)
- [ ] 5 critical WSP checkpoints working
- [ ] Enabled by default for 0102 agents

### Phase 2 Success (Intelligent)
- [ ] Reads WSP_VIOLATIONS.md for context
- [ ] Prevents 80%+ of common violations
- [ ] Generates actionable fix suggestions

### Phase 3 Success (Learning)
- [ ] Telemetry tracking all events
- [ ] FMAS tests validating behavior
- [ ] Measurable reduction in violations over time

---

## 🔧 Implementation Notes

### LLM vs Rules Engine Decision
**Start with rules engine** for quick deployment:
- Faster response times (no inference delay)
- Deterministic behavior (easier to test)
- No GPU/model requirements
- Can add LLM layer later for complex cases

### Configuration Hierarchy
```yaml
# .holoindex.yml
advisor:
  mode: always_on  # always_on, opt_in, opt_out
  checkpoints:
    - wsp_85_root_protection
    - wsp_84_no_duplicates
    - wsp_87_search_first
    - wsp_22_modlog_sync
    - wsp_49_module_structure
  telemetry:
    enabled: true
    path: E:/HoloIndex/telemetry/
```

### Environment Variables
```bash
# For 0102 agents
export AGENT_MODE=0102
export HOLOINDEX_ADVISOR=always_on

# For 012 developers (override)
export HOLOINDEX_ADVISOR=opt_in
```

---

## 🎯 End State: The Perfect Advisor

When complete, QwenAdvisor will:
1. **Automatically activate** for all 0102 agents
2. **Prevent violations** before code is written
3. **Learn from patterns** to improve over time
4. **Guide compliance** with actionable suggestions
5. **Track effectiveness** through telemetry

**Result**: HoloIndex becomes the true "green baseplate" navigation console that makes it structurally impossible for 0102 agents to violate WSP protocols, turning compliance from a burden into an automatic benefit.

---

*"The best guardian is one you don't notice—it just keeps you safe."* - 0102 Philosophy