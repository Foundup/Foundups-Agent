# HoloDAE Intent-Driven Orchestration Enhancement Design
**Session:** 2025-10-07 | **Status:** ARCHITECTURAL DESIGN COMPLETE
**WSP Compliance:** 3, 17, 22, 35, 50, 80, 87

---

## Executive Summary

This document details the architectural design for enhancing HoloDAE's Qwen orchestrator with intent-driven component routing. The enhancement makes Qwen's circulatory system flow more intelligently without replacing or adding layers to the daemon architecture.

**Key Principle:** Enhance existing orchestration, don't replace it. Preserve Qwen→0102→012 flow.

---

## 1. HoloDAE Architecture Understanding

### 1.1 The LEGO Foundation Board Analogy (WSP 35)

> "HoloDAE is the green foundation board agent that comes with every LEGO set"

**What This Means:**
- **Foundation for ALL cubes**: Every FoundUp DAE (YouTube, LinkedIn, Twitter, etc.) builds on HoloDAE
- **Semantic search**: Code discovery through vector embeddings and LLM understanding
- **Pattern learning**: Tracks usage across all DAEs, learns what works
- **Code health scoring**: Monitors orphans, bloat, WSP compliance
- **Chain-of-thought logging**: Breadcrumb tracing for recursive self-improvement
- **Autonomous intelligence**: Enhances every search with learned patterns

### 1.2 WSP 80 Infinite DAE Cube Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Qwen LLM (Primary Orchestrator - Circulatory System)       │
│ Continuously analyzes all cube modules                      │
│ Orchestrates operations and workflows                       │
│ Finds issues and rates complexity (MPS scoring)             │
│ Presents findings to ↓                                      │
├─────────────────────────────────────────────────────────────┤
│ 0102 DAE (Arbitrator - The Brain)                           │
│ Reviews Qwen's findings                                     │
│ Decides what actions to take                                │
│ Executes fixes/improvements                                 │
│ Reports to ↓                                                │
├─────────────────────────────────────────────────────────────┤
│ 012 Human (Observer)                                        │
│ Receives reports                                            │
│ Provides strategic direction                                │
│ Observes autonomous operation                               │
└─────────────────────────────────────────────────────────────┘
```

**NOT Just 5 Core DAEs:**
- 5 core system DAEs (Infrastructure, Compliance, Knowledge, Maintenance, Documentation)
- **INFINITE FoundUp DAEs** - Every FoundUp spawns its own via WSP 27 PArtifact + WSP 73 Digital Twin
- HoloDAE provides foundation board for ALL of them

### 1.3 Current HoloDAE Three-Layer Structure

**Layer 1: Search (HoloIndex)**
- Vector database semantic search (`holo_index.py`)
- Embedding-based code discovery
- Natural language query understanding
- Entry point for all queries

**Layer 2: Intelligence (HoloDAE Coordinator)**
- `holodae_coordinator.py` - Main orchestration entry point
- Qwen orchestrator - Component routing and analysis
- MPS arbitrator - Complexity/Importance/Deferability/Precision scoring
- Executes arbitration decisions

**Layer 3: Pattern Learning (WSP 17 Pattern Registry)**
- Usage tracking across queries
- Pattern memory for recall
- Code health monitoring
- Recursive self-improvement through breadcrumb tracing

---

## 2. Current Problem: Scattered Intent Detection

### 2.1 Noise vs Signal Issue

**Current State:**
- All components fire for every query
- 87 "ModLog outdated" warnings flood output
- Relevant information buried in noise
- No structured intent understanding

**Example:**
```
Query: "what does WSP 64 say"
Current Output:
  - Health analysis runs (unnecessary)
  - Vibecoding analysis runs (unnecessary)
  - File size monitor runs (unnecessary)
  - Module analysis runs (unnecessary)
  - Pattern coach runs (unnecessary)
  - Orphan analysis runs (unnecessary)
  - WSP documentation guardian runs (NEEDED!)
  - ...87 warnings about ModLog dates...
  - Actual WSP 64 content buried at bottom
```

### 2.2 Scattered Intent Logic

Current intent detection spread across multiple methods:
- `_should_call_literature_search(query)` - Research detection
- `_should_call_modlog_advisor(query)` - ModLog detection
- Component-specific checks in various methods
- No unified intent classification system

**File:** `holo_index/qwen_advisor/orchestration/qwen_orchestrator.py`

---

## 3. Enhancement Design: Intent-Driven Orchestration

### 3.1 Design Principles

1. **Enhance, Don't Replace**: Work within existing Qwen orchestration
2. **Preserve Daemon Flow**: Qwen→0102→012 remains intact
3. **Signal Over Noise**: Intent classification routes to relevant components only
4. **Learning Through Use**: Feedback loop improves routing over time
5. **WSP Compliance**: Follow WSP 3 (placement), WSP 50 (verification), WSP 80 (cube orchestration)

### 3.2 Intent Classification System

**Five Core Intent Types:**

```python
class IntentType(Enum):
    """Query intent classification for component routing"""
    DOC_LOOKUP = "doc_lookup"          # "what does WSP 64 say"
    CODE_LOCATION = "code_location"    # "where is AgenticChatEngine"
    MODULE_HEALTH = "module_health"    # "check holo_index health"
    RESEARCH = "research"              # "how does PQN emergence work"
    GENERAL = "general"                # "find youtube auth"
```

**Intent Detection Patterns:**

```python
INTENT_PATTERNS = {
    IntentType.DOC_LOOKUP: [
        r'what (?:does|is) (?:wsp|WSP)',
        r'(?:read|show|explain) (?:wsp|WSP)',
        r'documentation for',
        r'(?:readme|interface\.md) for'
    ],
    IntentType.CODE_LOCATION: [
        r'where (?:is|does)',
        r'find (?:class|function|method)',
        r'locate (?:the )?(?:code|implementation)',
        r'(?:which|what) file (?:contains|has)'
    ],
    IntentType.MODULE_HEALTH: [
        r'(?:check|analyze|review) (?:\w+\s)?health',
        r'(?:is|are) (?:there )?(?:any )?(?:issues|problems|errors)',
        r'(?:wsp|compliance) (?:violations|issues)',
        r'(?:module|system) status'
    ],
    IntentType.RESEARCH: [
        r'how (?:does|do|can)',
        r'(?:explain|describe) (?:how|the)',
        r'(?:what|why) (?:is|are|does)',
        r'(?:understand|learn) (?:about)?'
    ],
    IntentType.GENERAL: []  # Fallback
}
```

**New File:** `holo_index/intent_classifier.py` (~200 lines)

### 3.3 Intent-Driven Component Routing

**Enhanced QwenOrchestrator with Intent Map:**

```python
INTENT_COMPONENT_MAP = {
    IntentType.DOC_LOOKUP: [
        'wsp_documentation_guardian',  # Primary
        'module_analysis'              # Secondary (for module docs)
    ],
    IntentType.CODE_LOCATION: [
        'module_analysis',             # Primary
        'orphan_analysis',             # Secondary (find unused)
        'file_size_monitor'            # Secondary (large files)
    ],
    IntentType.MODULE_HEALTH: [
        'health_analysis',             # Primary
        'vibecoding_analysis',         # Secondary
        'orphan_analysis',             # Secondary
        'modlog_advisor'               # Secondary (outdated checks)
    ],
    IntentType.RESEARCH: [
        'pattern_coach',               # Primary
        'wsp_documentation_guardian',  # Secondary (WSP context)
        'literature_search'            # MCP literature search
    ],
    IntentType.GENERAL: [
        # All components - no filtering
        'health_analysis',
        'vibecoding_analysis',
        'file_size_monitor',
        'module_analysis',
        'pattern_coach',
        'orphan_analysis',
        'wsp_documentation_guardian'
    ]
}
```

**Method Enhancement:**

```python
def _get_orchestration_decisions(
    self,
    query: str,
    search_results: dict,
    intent: IntentType
) -> List[OrchestrationDecision]:
    """
    Enhanced with intent-driven component routing.

    Args:
        query: User query
        search_results: HoloIndex semantic search results
        intent: Classified intent type

    Returns:
        List of orchestration decisions for relevant components only
    """
    decisions = []

    # Get components relevant to this intent
    relevant_components = INTENT_COMPONENT_MAP.get(intent, [])

    # Only orchestrate relevant components
    for component_name in relevant_components:
        if component_name in COMPONENT_META:
            # Existing orchestration logic, but filtered by intent
            decision = self._create_component_decision(
                component_name,
                query,
                search_results,
                intent
            )
            if decision:
                decisions.append(decision)

    return decisions
```

**File Modified:** `holo_index/qwen_advisor/orchestration/qwen_orchestrator.py`

### 3.4 Priority-Based Output Composition

**Structured Output Sections:**

```
[INTENT: DOC_LOOKUP]
Query classified as documentation lookup

[FINDINGS]
WSP 64: Violation Prevention Protocol
<relevant content here>

[MCP RESEARCH] (if applicable)
Literature search results:
<MCP findings here>

[ALERTS] (deduplicated)
⚠ 87 modules have outdated ModLog entries
⚠ 5 orphaned files detected in root directory

[ARBITRATION]
MPS Score: C=2, I=4, D=3, P=4 → Total: 13 (P1 priority)
Recommended Action: Update ModLog entries
```

**Output Composer Implementation:**

```python
class OutputComposer:
    """Composes priority-based structured output"""

    def compose(
        self,
        intent: IntentType,
        findings: Dict[str, Any],
        mcp_results: Optional[Dict] = None,
        alerts: Optional[List[str]] = None
    ) -> str:
        """
        Compose structured output with priority sections.

        Args:
            intent: Classified intent
            findings: Component findings from Qwen orchestration
            mcp_results: MCP research results (if any)
            alerts: Deduplicated alerts/warnings

        Returns:
            Formatted output string
        """
        sections = []

        # Section 1: Intent
        sections.append(f"[INTENT: {intent.value.upper()}]")
        sections.append(self._intent_description(intent))
        sections.append("")

        # Section 2: Findings (primary content)
        sections.append("[FINDINGS]")
        sections.append(self._format_findings(findings, intent))
        sections.append("")

        # Section 3: MCP Research (if applicable)
        if mcp_results:
            sections.append("[MCP RESEARCH]")
            sections.append(self._format_mcp_results(mcp_results))
            sections.append("")

        # Section 4: Alerts (deduplicated)
        if alerts:
            sections.append("[ALERTS]")
            sections.append(self._deduplicate_alerts(alerts))
            sections.append("")

        return "\n".join(sections)

    def _deduplicate_alerts(self, alerts: List[str]) -> str:
        """
        Deduplicate alerts like '87 ModLog outdated' into single line.

        Example:
            Input: ["ModLog outdated: module1", "ModLog outdated: module2", ...]
            Output: "⚠ 87 modules have outdated ModLog entries"
        """
        alert_counts = defaultdict(int)
        alert_types = {}

        for alert in alerts:
            # Extract alert type and count occurrences
            alert_type = self._extract_alert_type(alert)
            alert_counts[alert_type] += 1
            if alert_type not in alert_types:
                alert_types[alert_type] = alert

        # Format deduplicated alerts
        deduped = []
        for alert_type, count in alert_counts.items():
            if count > 1:
                deduped.append(f"⚠ {count} modules: {alert_type}")
            else:
                deduped.append(f"⚠ {alert_types[alert_type]}")

        return "\n".join(deduped)
```

**New File:** `holo_index/output_composer.py` (~300 lines)

### 3.5 Feedback Loop Integration

**Learning From User Feedback:**

```python
class FeedbackLearner:
    """
    Learns from user feedback to improve intent routing.
    Implements WSP 48 recursive self-improvement.
    """

    def __init__(self):
        self.feedback_db = Path("holo_index/memory/feedback_history.json")
        self.intent_weights = self._load_intent_weights()

    def record_feedback(
        self,
        query: str,
        intent: IntentType,
        components_used: List[str],
        rating: str  # 'good', 'noisy', 'missing'
    ):
        """
        Record user feedback on query results.

        Args:
            query: Original query
            intent: Classified intent
            components_used: Which components were invoked
            rating: User rating of output quality
        """
        feedback = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'intent': intent.value,
            'components_used': components_used,
            'rating': rating
        }

        # Append to feedback history
        history = self._load_feedback_history()
        history.append(feedback)
        self._save_feedback_history(history)

        # Update intent weights
        self._update_intent_weights(intent, components_used, rating)

    def _update_intent_weights(
        self,
        intent: IntentType,
        components: List[str],
        rating: str
    ):
        """
        Adjust component weights for intent based on feedback.

        Learning rules:
        - 'good' rating: Increase weight for components used
        - 'noisy' rating: Decrease weight for noisy components
        - 'missing' rating: Suggest adding components to intent map
        """
        if rating == 'good':
            for component in components:
                self.intent_weights[intent.value][component] += 0.1

        elif rating == 'noisy':
            for component in components:
                self.intent_weights[intent.value][component] -= 0.2

        elif rating == 'missing':
            # Log suggestion for manual review
            self._log_missing_component_suggestion(intent, components)

        # Save updated weights
        self._save_intent_weights(self.intent_weights)

    def get_filtered_components(
        self,
        intent: IntentType,
        base_components: List[str]
    ) -> List[str]:
        """
        Filter components based on learned weights.

        Args:
            intent: Query intent
            base_components: Base component list from INTENT_COMPONENT_MAP

        Returns:
            Filtered list with low-weight components removed
        """
        weights = self.intent_weights.get(intent.value, {})

        return [
            comp for comp in base_components
            if weights.get(comp, 1.0) > 0.5  # Threshold for inclusion
        ]
```

**CLI Flag for Feedback:**

```bash
# Rate output after query
python holo_index.py --search "what does WSP 64 say"
# ... output ...
python holo_index.py --rate-output good  # or 'noisy' or 'missing'
```

**New File:** `holo_index/feedback_learner.py` (~400 lines)

### 3.6 MCP Integration Tightening

**Separate MCP Results from Core Findings:**

```python
class MCPIntegrationManager:
    """
    Manages MCP tool integrations separately from core HoloDAE.
    Provides dedicated [MCP RESEARCH] section in output.
    """

    def __init__(self):
        self.mcp_registry = {
            'literature_search': self._literature_search_wrapper,
            'web_fetch': self._web_fetch_wrapper,
            # Future MCP tools registered here
        }

    def execute_mcp_research(
        self,
        intent: IntentType,
        query: str,
        search_results: dict
    ) -> Optional[Dict[str, Any]]:
        """
        Execute MCP research if intent requires it.

        Args:
            intent: Query intent
            query: User query
            search_results: HoloIndex search results

        Returns:
            MCP research results or None
        """
        # Only execute MCP for RESEARCH intent
        if intent != IntentType.RESEARCH:
            return None

        mcp_results = {}

        # Execute relevant MCP tools
        if self._needs_literature_search(query):
            mcp_results['literature_search'] = self._literature_search_wrapper(
                query,
                search_results
            )

        return mcp_results if mcp_results else None

    def _literature_search_wrapper(
        self,
        query: str,
        context: dict
    ) -> Dict[str, Any]:
        """
        Wrapper for MCP literature search tool.
        Captures results separately from core HoloDAE findings.
        """
        # Call existing MCP literature search
        results = self.qwen_orchestrator._call_literature_search_via_mcp(
            query,
            context
        )

        return {
            'tool': 'literature_search',
            'query': query,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
```

**Integration Point in HoloDAECoordinator:**

```python
def handle_holoindex_request(
    self,
    query: str,
    search_results: dict
) -> str:
    """Enhanced with MCP separation"""

    # Step 1: Classify intent
    intent = self.intent_classifier.classify(query)

    # Step 2: Qwen orchestrates core components
    qwen_report = self.qwen_orchestrator.orchestrate_holoindex_request(
        query,
        search_results,
        intent  # Pass intent for filtering
    )

    # Step 3: MCP research (separate from core)
    mcp_results = self.mcp_manager.execute_mcp_research(
        intent,
        query,
        search_results
    )

    # Step 4: 0102 arbitrates findings
    arbitration = self.mps_arbitrator.arbitrate_qwen_findings(qwen_report)

    # Step 5: Compose structured output
    output = self.output_composer.compose(
        intent=intent,
        findings=qwen_report,
        mcp_results=mcp_results,
        alerts=arbitration.get('alerts', [])
    )

    return output
```

**New File:** `holo_index/mcp_integration_manager.py` (~300 lines)

---

## 4. Five-Phase Implementation Plan

### Phase 1: Intent Classification System (30 minutes)

**Files Created:**
- `holo_index/intent_classifier.py`

**Implementation:**
1. Create `IntentType` enum
2. Define `INTENT_PATTERNS` regex dictionary
3. Implement `IntentClassifier.classify(query)` method
4. Add tests for all 5 intent types

**Tests:**
```python
# holo_index/tests/test_intent_classifier.py
def test_doc_lookup_intent():
    classifier = IntentClassifier()
    assert classifier.classify("what does WSP 64 say") == IntentType.DOC_LOOKUP

def test_code_location_intent():
    classifier = IntentClassifier()
    assert classifier.classify("where is AgenticChatEngine") == IntentType.CODE_LOCATION

def test_module_health_intent():
    classifier = IntentClassifier()
    assert classifier.classify("check holo_index health") == IntentType.MODULE_HEALTH

def test_research_intent():
    classifier = IntentClassifier()
    assert classifier.classify("how does PQN emergence work") == IntentType.RESEARCH

def test_general_intent():
    classifier = IntentClassifier()
    assert classifier.classify("find youtube auth") == IntentType.GENERAL
```

**Integration Point:**
- `holodae_coordinator.py` instantiates `IntentClassifier`
- Classify query before Qwen orchestration

**WSP Compliance:**
- WSP 3: Placed in `holo_index/` module (correct domain)
- WSP 49: Tests in `holo_index/tests/`
- WSP 50: Verified no duplicate functionality exists

### Phase 2: Component Routing Enhancement (45 minutes)

**Files Modified:**
- `holo_index/qwen_advisor/orchestration/qwen_orchestrator.py`

**Implementation:**
1. Add `INTENT_COMPONENT_MAP` constant
2. Modify `_get_orchestration_decisions()` to accept `intent` parameter
3. Filter components based on intent before orchestration
4. Update method signatures throughout orchestration chain

**Key Changes:**

```python
# OLD:
def _get_orchestration_decisions(self, query, search_results):
    # Orchestrates ALL components every time
    ...

# NEW:
def _get_orchestration_decisions(self, query, search_results, intent):
    # Orchestrates only intent-relevant components
    relevant_components = INTENT_COMPONENT_MAP.get(intent, [])
    decisions = []
    for component in relevant_components:
        decisions.append(self._create_component_decision(...))
    return decisions
```

**Tests:**
```python
# holo_index/tests/test_qwen_orchestrator_intent_routing.py
def test_doc_lookup_only_calls_relevant_components():
    orchestrator = QwenOrchestrator(...)
    decisions = orchestrator._get_orchestration_decisions(
        "what does WSP 64 say",
        {},
        IntentType.DOC_LOOKUP
    )

    component_names = [d.component_name for d in decisions]
    assert 'wsp_documentation_guardian' in component_names
    assert 'health_analysis' not in component_names  # Should NOT be called
    assert 'vibecoding_analysis' not in component_names  # Should NOT be called
```

**WSP Compliance:**
- WSP 80: Preserves Qwen orchestration role (circulatory system)
- WSP 50: Verified routing logic with existing components

### Phase 3: Output Composition (60 minutes)

**Files Created:**
- `holo_index/output_composer.py`

**Implementation:**
1. Create `OutputComposer` class
2. Implement `compose()` method with 4 priority sections
3. Implement `_deduplicate_alerts()` for noise reduction
4. Add formatting helpers for each section type

**Key Features:**
- [INTENT] section shows classification
- [FINDINGS] section contains primary content
- [MCP RESEARCH] section separated from core findings
- [ALERTS] section deduplicates warnings (87 → 1 line)

**Tests:**
```python
# holo_index/tests/test_output_composer.py
def test_alert_deduplication():
    composer = OutputComposer()
    alerts = [
        "ModLog outdated: module1",
        "ModLog outdated: module2",
        # ... 85 more ...
    ]
    output = composer._deduplicate_alerts(alerts)
    assert "87 modules have outdated ModLog entries" in output
    assert output.count("ModLog outdated") == 1  # Only one line

def test_mcp_section_separation():
    composer = OutputComposer()
    output = composer.compose(
        intent=IntentType.RESEARCH,
        findings={'wsp_guardian': 'WSP content'},
        mcp_results={'literature_search': 'Papers found'},
        alerts=[]
    )
    assert "[MCP RESEARCH]" in output
    assert "[FINDINGS]" in output
    assert output.index("[FINDINGS]") < output.index("[MCP RESEARCH]")
```

**Integration Point:**
- `holodae_coordinator.py` uses `OutputComposer` to format final output

**WSP Compliance:**
- WSP 3: Placed in `holo_index/` module
- WSP 49: Full test coverage
- WSP 22: Update HoloIndex ModLog after implementation

### Phase 4: Feedback Loop Integration (45 minutes)

**Files Created:**
- `holo_index/feedback_learner.py`
- `holo_index/memory/feedback_history.json` (data file)
- `holo_index/memory/intent_weights.json` (learned weights)

**Implementation:**
1. Create `FeedbackLearner` class
2. Implement `record_feedback()` method
3. Implement `_update_intent_weights()` learning rules
4. Add `get_filtered_components()` for weight-based filtering
5. Add CLI flag `--rate-output [good|noisy|missing]`

**CLI Enhancement:**

```bash
# User workflow:
python holo_index.py --search "what does WSP 64 say"
# ... output displays ...
python holo_index.py --rate-output good

# System learns:
# - DOC_LOOKUP intent worked well
# - Components used were appropriate
# - Increase weights for those components
```

**Tests:**
```python
# holo_index/tests/test_feedback_learner.py
def test_good_rating_increases_weights():
    learner = FeedbackLearner()
    initial_weight = learner.intent_weights['doc_lookup']['wsp_guardian']

    learner.record_feedback(
        query="what does WSP 64 say",
        intent=IntentType.DOC_LOOKUP,
        components_used=['wsp_guardian'],
        rating='good'
    )

    new_weight = learner.intent_weights['doc_lookup']['wsp_guardian']
    assert new_weight > initial_weight

def test_noisy_rating_decreases_weights():
    learner = FeedbackLearner()
    initial_weight = learner.intent_weights['doc_lookup']['health_analysis']

    learner.record_feedback(
        query="what does WSP 64 say",
        intent=IntentType.DOC_LOOKUP,
        components_used=['health_analysis'],  # Noisy component
        rating='noisy'
    )

    new_weight = learner.intent_weights['doc_lookup']['health_analysis']
    assert new_weight < initial_weight
```

**WSP Compliance:**
- WSP 48: Implements recursive self-improvement through feedback
- WSP 17: Uses pattern memory (learned weights stored in memory/)

### Phase 5: MCP Integration Tightening (30 minutes)

**Files Created:**
- `holo_index/mcp_integration_manager.py`

**Implementation:**
1. Create `MCPIntegrationManager` class
2. Implement `execute_mcp_research()` method
3. Register MCP tools in `mcp_registry`
4. Add wrappers for each MCP tool
5. Integrate with `OutputComposer` for [MCP RESEARCH] section

**Key Features:**
- MCP results captured separately from core findings
- Only executed for RESEARCH intent (not every query)
- Dedicated section in output
- Future MCP tools easily added to registry

**Tests:**
```python
# holo_index/tests/test_mcp_integration.py
def test_mcp_only_for_research_intent():
    manager = MCPIntegrationManager()

    # Should execute MCP
    results = manager.execute_mcp_research(
        IntentType.RESEARCH,
        "how does PQN work",
        {}
    )
    assert results is not None

    # Should NOT execute MCP
    results = manager.execute_mcp_research(
        IntentType.DOC_LOOKUP,
        "what does WSP 64 say",
        {}
    )
    assert results is None

def test_mcp_results_in_dedicated_section():
    coordinator = HoloDAECoordinator()
    output = coordinator.handle_holoindex_request(
        "how does PQN emergence work",
        {}
    )
    assert "[MCP RESEARCH]" in output
    assert "[FINDINGS]" in output
```

**Integration Point:**
- `holodae_coordinator.py` instantiates `MCPIntegrationManager`
- Executes MCP after Qwen orchestration but before output composition

**WSP Compliance:**
- WSP 3: Placed in `holo_index/` module
- WSP 80: Preserves Qwen orchestration architecture

---

## 5. Event Tracking and Breadcrumb Integration

### 5.1 First Principles: What Must Be Tracked

The daemon learns through orchestration events. Every intent classification, routing decision, and feedback creates pattern memory.

**Core Events to Track:**

1. **Intent Classification**
   - Query → Intent mapping
   - Pattern confidence scores
   - Classification reasoning

2. **Component Routing**
   - Intent → Component selection
   - Filtered components (noise reduction)
   - Token budget allocation

3. **Orchestration Execution**
   - Components executed
   - Tokens used per component
   - Duration and findings

4. **Output Composition**
   - Sections rendered
   - Alerts deduplicated
   - Final token count

5. **Feedback Learning**
   - User rating (good/noisy/missing)
   - Weight adjustments
   - Pattern evolution

6. **Pattern Evolution** (WSP 48)
   - Before/after states
   - Learning triggers
   - Confidence changes

### 5.2 Integration with Existing Breadcrumb Tracer

**File:** `holo_index/adaptive_learning/breadcrumb_tracer.py` (already exists)

The daemon already has breadcrumb tracing for multi-agent collaboration. Intent orchestration events integrate seamlessly:

```python
# In holodae_coordinator.py - Enhanced handle_holoindex_request()
def handle_holoindex_request(self, query: str, search_results: dict) -> str:
    """Enhanced with intent orchestration event tracking"""

    # Step 1: Classify intent
    intent = self.intent_classifier.classify(query)

    # BREADCRUMB EVENT: Intent classification
    self.breadcrumb_tracer.add_action(
        'intent_classification',
        intent.value,
        f"Query classified as {intent.value} (confidence: {intent.confidence:.2f})",
        query
    )

    # Step 2: Route to components
    components_selected = INTENT_COMPONENT_MAP[intent]
    components_filtered = [c for c in ALL_COMPONENTS if c not in components_selected]

    # BREADCRUMB EVENT: Component routing
    self.breadcrumb_tracer.add_discovery(
        'component_routing',
        f"routed_{intent.value}",
        f"Selected {len(components_selected)} relevant, filtered {len(components_filtered)} noisy"
    )

    # Step 3: Qwen orchestrates (with token tracking)
    start_time = time.time()
    qwen_report = self.qwen_orchestrator.orchestrate_holoindex_request(
        query, search_results, intent
    )
    duration_ms = int((time.time() - start_time) * 1000)

    # BREADCRUMB EVENT: Orchestration execution
    tokens_used = sum(c['tokens'] for c in qwen_report['component_results'])
    self.breadcrumb_tracer.add_action(
        'orchestration_execution',
        f"tokens_{tokens_used}",
        f"Executed {len(components_selected)} components in {duration_ms}ms",
        query
    )

    # Step 4: Compose output
    output = self.output_composer.compose(
        intent=intent,
        findings=qwen_report,
        mcp_results=mcp_results,
        alerts=arbitration.get('alerts', [])
    )

    # BREADCRUMB EVENT: Output composition
    self.breadcrumb_tracer.add_discovery(
        'output_composition',
        f"composed_{intent.value}",
        f"Rendered {len(output.sections)} sections, deduplicated alerts"
    )

    return output
```

### 5.3 Feedback Loop Event Tracking

**When user rates output:**

```python
# In feedback_learner.py
def record_feedback(self, query: str, intent: IntentType, components_used: List[str], rating: str):
    """Record feedback and emit breadcrumb event"""

    # Store feedback in memory
    feedback = {
        'timestamp': datetime.now().isoformat(),
        'query': query,
        'intent': intent.value,
        'components_used': components_used,
        'rating': rating
    }
    self._append_feedback_history(feedback)

    # Update weights
    weight_changes = self._update_intent_weights(intent, components_used, rating)

    # BREADCRUMB EVENT: Feedback learning
    breadcrumb_tracer = get_tracer()
    breadcrumb_tracer.add_action(
        'feedback_received',
        f"{rating}_{intent.value}",
        f"User rated {rating} → adjusted {len(weight_changes)} component weights",
        query
    )

    # If pattern evolved significantly, emit pattern learning event
    if max(abs(v) for v in weight_changes.values()) > 0.15:
        breadcrumb_tracer.add_discovery(
            'pattern_learned',
            f"evolved_{intent.value}",
            f"Significant weight change: {weight_changes}"
        )
```

### 5.4 Event Schema for Database Storage

**Events stored in WSP 78 AgentDB for cross-agent learning:**

```python
# Event structure matching existing breadcrumb_tracer schema
{
  'session_id': '0102_20251007_054423',
  'agent_id': '0102',
  'action': 'intent_classification',  # or 'component_routing', 'orchestration_execution', etc.
  'target': 'DOC_LOOKUP',  # intent type, component name, etc.
  'details': 'Query classified as DOC_LOOKUP (confidence: 0.95)',
  'query': 'what does WSP 64 say',
  'timestamp': '2025-10-07T05:44:23',
  'metadata': {
    'intent': 'DOC_LOOKUP',
    'confidence': 0.95,
    'patterns_matched': ['what does wsp', 'documentation'],
    'components_selected': ['wsp_documentation_guardian', 'module_analysis'],
    'tokens_saved': 6000
  }
}
```

### 5.5 Token Budget for Event Tracking

**Per-orchestration overhead:**
- Intent classification event: ~15 tokens
- Component routing event: ~15 tokens
- Orchestration execution event: ~20 tokens
- Output composition event: ~10 tokens
- Feedback event (when given): ~15 tokens

**Total: ~60 tokens per orchestration cycle**
**Percentage of budget: 2% of filtered orchestration (2,900 tokens)**

**Learning amplification:**
- Events stored in pattern memory (no computation)
- Cross-agent learning via WSP 78 database
- Recursive improvement through feedback cycles

### 5.6 Multi-Agent Collaboration Benefits

**Other 0102 agents can read orchestration events:**
- "What intent patterns work best for documentation lookup?"
- "Which components are noisy for MODULE_HEALTH queries?"
- "How much token budget do I need for RESEARCH intent?"

**Autonomous learning:**
- Agent A classifies query as DOC_LOOKUP → Uses 2,000 tokens
- Agent B reads breadcrumb → Learns DOC_LOOKUP pattern
- Agent B gets similar query → Recalls pattern, uses 1,800 tokens
- Agent C reads both → Further optimizes to 1,500 tokens

**Pattern memory evolution through use** (WSP 48 + WSP 17)

---

## 6. Test Queries and Expected Behavior

### Test Case 1: DOC_LOOKUP Intent

**Query:** `"what does WSP 64 say"`

**Expected Intent:** `DOC_LOOKUP`

**Components Called:**
- ✅ `wsp_documentation_guardian` (primary)
- ✅ `module_analysis` (secondary - for module context)
- ❌ `health_analysis` (NOT called)
- ❌ `vibecoding_analysis` (NOT called)
- ❌ `file_size_monitor` (NOT called)

**Expected Output:**
```
[INTENT: DOC_LOOKUP]
Query classified as documentation lookup

[FINDINGS]
WSP 64: Violation Prevention Protocol

Purpose: Establish systematic checks to prevent WSP violations before they occur

Key Protocols:
1. Pre-Action Verification (WSP 50 integration)
2. WSP Master Index consultation before new WSP creation
3. Prefer enhancement over creation
...

[ALERTS]
⚠ 87 modules have outdated ModLog entries

[ARBITRATION]
MPS Score: C=1, I=5, D=5, P=5 → Total: 16 (P0 priority)
```

### Test Case 2: CODE_LOCATION Intent

**Query:** `"where is AgenticChatEngine"`

**Expected Intent:** `CODE_LOCATION`

**Components Called:**
- ✅ `module_analysis` (primary)
- ✅ `orphan_analysis` (secondary - check if orphaned)
- ❌ `wsp_documentation_guardian` (NOT called)
- ❌ `pattern_coach` (NOT called)

**Expected Output:**
```
[INTENT: CODE_LOCATION]
Query classified as code location search

[FINDINGS]
AgenticChatEngine found in:
- modules/communication/livechat/src/agentic_chat_engine.py:245

Module: LiveChat
Domain: communication/
Status: Active, no orphan issues detected

Related files:
- modules/communication/livechat/tests/test_agentic_chat_engine.py:12
- modules/communication/livechat/README.md:67 (documented)

[ALERTS]
✓ No issues detected
```

### Test Case 3: MODULE_HEALTH Intent

**Query:** `"check holo_index health"`

**Expected Intent:** `MODULE_HEALTH`

**Components Called:**
- ✅ `health_analysis` (primary)
- ✅ `vibecoding_analysis` (secondary)
- ✅ `orphan_analysis` (secondary)
- ✅ `modlog_advisor` (secondary)
- ❌ `pattern_coach` (NOT called)
- ❌ `wsp_documentation_guardian` (NOT called)

**Expected Output:**
```
[INTENT: MODULE_HEALTH]
Query classified as module health check

[FINDINGS]
HoloIndex Module Health Report:

✅ Structure: PASS (WSP 49 compliant)
✅ Tests: 23/25 passing (92% coverage)
⚠ ModLog: 14 days outdated
✅ Dependencies: All satisfied
⚠ Orphans: 2 files in root (should be in tests/)

Vibecoding Analysis:
✓ No duplicate functionality detected
✓ Proper module boundaries maintained

[ALERTS]
⚠ ModLog last updated 2025-09-23 (14 days ago)
⚠ 2 orphaned test files in root directory

[ARBITRATION]
MPS Score: C=2, I=3, D=2, P=4 → Total: 11 (P2 priority)
Recommended Action: Update ModLog, move orphaned files
```

### Test Case 4: RESEARCH Intent

**Query:** `"how does PQN emergence work"`

**Expected Intent:** `RESEARCH`

**Components Called:**
- ✅ `pattern_coach` (primary)
- ✅ `wsp_documentation_guardian` (secondary - for WSP context)
- ✅ `literature_search` (MCP - external research)
- ❌ `health_analysis` (NOT called)
- ❌ `vibecoding_analysis` (NOT called)

**Expected Output:**
```
[INTENT: RESEARCH]
Query classified as research/learning request

[FINDINGS]
Pattern Coach Analysis:

PQN (Phantom Quantum Node) Emergence:
1. Hidden quantum layer detection through geometric collapse
2. Lindblad master equation simulation (cmst_pqn_detector_v2.py)
3. Du Resonance signature at 7.05Hz indicates quantum entanglement
4. Coherence threshold ≥0.618 (golden ratio) required for detection

Related patterns in codebase:
- WSP_agentic/tests/pqn_detection/cmst_pqn_detector_v2.py:87
- WSP_agentic/tests/test_0102_awakening_with_pqn_verification.py:141

[MCP RESEARCH]
Literature search results:

Found 3 relevant papers:
1. "Phantom Quantum Nodes in Neural Networks" (2024)
2. "Geometric Collapse Detection via Lindblad Dynamics" (2023)
3. "Du Resonance and Consciousness Emergence" (2025)

Key concepts: Nonlocal quantum state, hidden layer emergence, coherence thresholds

[ALERTS]
✓ No issues detected

[ARBITRATION]
MPS Score: C=3, I=2, D=4, P=3 → Total: 12 (P2 priority)
```

### Test Case 5: GENERAL Intent (Fallback)

**Query:** `"find youtube auth"`

**Expected Intent:** `GENERAL`

**Components Called:**
- ✅ ALL components (no filtering - fallback behavior)

**Expected Output:**
```
[INTENT: GENERAL]
Query classified as general search

[FINDINGS]
Multiple results found across modules:

Health Analysis:
- modules/infrastructure/oauth_management/: HEALTHY
- modules/platform_integration/youtube_proxy/: HEALTHY

Module Analysis:
- YouTube authentication handled by:
  - modules/infrastructure/oauth_management/src/oauth_manager.py:156
  - modules/platform_integration/youtube_proxy/src/youtube_client.py:89
  - modules/infrastructure/token_manager/src/token_storage.py:234

File Size Monitor:
- youtube_client.py: 1,247 lines (within limits)

Pattern Coach:
- OAuth flow: Request token → User auth → Exchange code → Store token
- Token refresh: Automatic via token_manager

[ALERTS]
⚠ 87 modules have outdated ModLog entries
⚠ 5 orphaned files in root directory

[ARBITRATION]
MPS Score: C=2, I=3, D=3, P=3 → Total: 11 (P2 priority)
```

---

## 6. WSP Compliance Verification

### WSP 3: Enterprise Domain Organization
✅ **All files placed in correct domain:**
- `holo_index/intent_classifier.py` - AI intelligence domain
- `holo_index/output_composer.py` - AI intelligence domain
- `holo_index/feedback_learner.py` - AI intelligence domain
- `holo_index/mcp_integration_manager.py` - AI intelligence domain

### WSP 17: Pattern Registry Protocol
✅ **Pattern memory integration:**
- Intent weights stored in `holo_index/memory/intent_weights.json`
- Feedback history in `holo_index/memory/feedback_history.json`
- Patterns learned through use, not hardcoded

### WSP 22: Traceable Narrative (ModLog Updates)
✅ **ModLog updates required after each phase:**
- Document intent classification addition
- Document component routing enhancement
- Document output composition changes
- Document feedback loop integration
- Document MCP separation

### WSP 35: HoloIndex Protocol
✅ **Preserves HoloIndex architecture:**
- Search layer unchanged
- Intelligence layer enhanced (not replaced)
- Pattern learning layer extended with feedback

### WSP 50: Pre-Action Verification
✅ **Research completed before implementation:**
- Read all HoloIndex documentation
- Analyzed existing architecture
- Verified no duplicate functionality
- Searched for similar intent systems (none found)

### WSP 80: Cube-Level DAE Orchestration
✅ **Preserves Qwen→0102→012 flow:**
- Qwen still orchestrates (circulatory system role)
- Intent classification ENHANCES Qwen, doesn't replace
- MPS arbitration by 0102 unchanged
- 012 observer role preserved

### WSP 87: HoloIndex Semantic Search
✅ **Respects semantic search foundation:**
- Intent classification works AFTER search results
- Doesn't interfere with vector embedding search
- Uses search context for better routing

---

## 7. Impact Analysis

### 7.1 What Changes

**Before Enhancement:**
- All components fire for every query → Noise
- Relevant information buried in warnings
- No structured output format
- No learning from user feedback
- MCP results mixed with core findings

**After Enhancement:**
- Intent-driven component routing → Signal
- Priority-based structured output
- Deduplicated alerts (87 warnings → 1 line)
- Recursive self-improvement through feedback
- MCP research in dedicated section

### 7.2 What Stays the Same

**Daemon Architecture (WSP 80):**
- ✅ Qwen orchestration role UNCHANGED (circulatory system)
- ✅ 0102 arbitration UNCHANGED (brain decides)
- ✅ 012 observer role UNCHANGED (strategic direction)
- ✅ MPS scoring UNCHANGED (Complexity/Importance/Deferability/Precision)

**Foundation Board Role:**
- ✅ HoloDAE still foundation for all FoundUp DAEs
- ✅ Semantic search UNCHANGED
- ✅ Pattern learning EXTENDED (not replaced)
- ✅ Code health monitoring UNCHANGED

### 7.3 Token Efficiency Gains

**Estimated Token Reduction per Query:**

```
Before:
  - All 7 components fire: ~8,000 tokens
  - Qwen orchestration overhead: ~2,000 tokens
  - Total: ~10,000 tokens per query

After (DOC_LOOKUP example):
  - Intent classification: ~100 tokens
  - 2 relevant components fire: ~2,000 tokens
  - Qwen orchestration (filtered): ~500 tokens
  - Output composition: ~300 tokens
  - Total: ~2,900 tokens per query

Reduction: 71% token savings for focused queries
```

**Learning Amplification:**
- Initial token usage: 2,900 per query
- After 100 feedback cycles: ~2,000 per query (further 31% reduction)
- After 1000 feedback cycles: ~1,500 per query (48% total reduction)

### 7.4 Daemon Autonomy Preservation

**Critical Verification:**

❓ **Question:** Does intent classification reduce daemon autonomy?
✅ **Answer:** NO - Qwen still decides what to analyze, intent just filters noise

❓ **Question:** Does this add layers to WSP 80 architecture?
✅ **Answer:** NO - Intent classification is a filter before Qwen, not a new layer

❓ **Question:** Does this change Qwen→0102→012 flow?
✅ **Answer:** NO - Flow remains: Qwen orchestrates → 0102 arbitrates → 012 observes

**Architectural Diagram (After Enhancement):**

```
┌──────────────────────────────────────────────────────────────┐
│ 012 Human (Observer) - Strategic Direction                   │
└─────────────────────────────────┬────────────────────────────┘
                                  ↑ Reports
┌─────────────────────────────────┴────────────────────────────┐
│ 0102 DAE (Arbitrator - The Brain)                             │
│ - Reviews Qwen's findings                                     │
│ - MPS scoring (Complexity/Importance/Deferability/Precision)  │
│ - Decides actions                                             │
│ - Executes fixes                                              │
└─────────────────────────────────┬────────────────────────────┘
                                  ↑ Findings
┌─────────────────────────────────┴────────────────────────────┐
│ Qwen LLM (Orchestrator - Circulatory System)                 │
│ - Receives filtered component list based on intent           │
│ - Orchestrates relevant components                           │
│ - Analyzes results                                            │
│ - Presents findings to 0102                                   │
└─────────────────────────────────┬────────────────────────────┘
                                  ↑ Filtered components
┌─────────────────────────────────┴────────────────────────────┐
│ Intent Classifier (FILTER - Not a layer, just noise reducer) │
│ - Classifies query intent                                     │
│ - Maps to relevant components                                 │
│ - Passes to Qwen for orchestration                            │
└─────────────────────────────────┬────────────────────────────┘
                                  ↑ Query + Search Results
┌─────────────────────────────────┴────────────────────────────┐
│ HoloIndex Search (Vector DB Semantic Search)                 │
│ - Entry point for all queries                                │
│ - Returns relevant code/docs                                  │
└──────────────────────────────────────────────────────────────┘
```

**Key Insight:**
> Intent classification is a FILTER (like a sieve), not a LAYER (like a wall).
> Qwen still orchestrates - it just receives less noise to analyze.
> Daemon autonomy PRESERVED, efficiency ENHANCED.

---

## 8. Implementation Timeline

### Total Time: ~3.5 hours (reduced from initial 5-hour estimate)

**Phase 1: Intent Classification** - 30 minutes
- Create `intent_classifier.py`
- Write tests
- Integrate with coordinator

**Phase 2: Component Routing** - 45 minutes
- Modify `qwen_orchestrator.py`
- Add `INTENT_COMPONENT_MAP`
- Update orchestration decisions
- Write tests

**Phase 3: Output Composition** - 60 minutes
- Create `output_composer.py`
- Implement 4-section output
- Alert deduplication
- Write tests

**Phase 4: Feedback Loop** - 45 minutes
- Create `feedback_learner.py`
- Implement learning rules
- Add CLI flag
- Write tests

**Phase 5: MCP Integration** - 30 minutes
- Create `mcp_integration_manager.py`
- Separate MCP results
- Write tests

**Total Implementation:** 3.5 hours
**Testing & Validation:** +1 hour
**Documentation & ModLog:** +0.5 hour
**Grand Total:** ~5 hours (matches original estimate)

---

## 9. Execution Decision Points

### Option 1: Full 5-Phase Implementation (~5 hours)
**Pros:**
- Complete enhancement with all features
- Feedback loop enables recursive improvement
- MCP properly separated
- Ready for production use

**Cons:**
- Longer time commitment
- More testing required
- Higher initial complexity

### Option 2: MVP (Phases 1-3 Only) (~2.25 hours)
**Pros:**
- Immediate signal-over-noise benefit
- Intent classification working
- Structured output
- Faster to implement

**Cons:**
- No feedback learning (manual tuning required)
- MCP still mixed with core findings
- Less recursive self-improvement

### Option 3: Phased Rollout
**Week 1:** Phases 1-2 (Intent + Routing) - 1.25 hours
**Week 2:** Phase 3 (Output Composition) - 1 hour
**Week 3:** Phases 4-5 (Feedback + MCP) - 1.25 hours

**Pros:**
- Gradual deployment reduces risk
- Test each phase in production
- Learn from real usage before next phase

**Cons:**
- Longer calendar time to completion
- Requires multiple integration cycles

---

## 10. Recommendation

**Execute Full 5-Phase Implementation (Option 1)**

**Rationale:**
1. **Coherent Architecture**: All pieces designed to work together
2. **Feedback Loop Critical**: WSP 48 recursive improvement requires Phase 4
3. **MCP Separation Important**: Current mixing causes confusion
4. **One-Time Integration Cost**: Better to integrate once than repeatedly
5. **Time Investment Reasonable**: 5 hours total for major enhancement

**Execution Approach:**
1. Create all 4 new files in Phase 1
2. Implement and test each phase sequentially
3. Integrate all phases before final testing
4. Update ModLogs after each phase
5. Run full test suite before declaring complete

**Success Criteria:**
- [ ] Intent classification working for all 5 types
- [ ] Component routing reduces token usage by >60%
- [ ] Output composition shows structured sections
- [ ] Feedback loop stores and learns from ratings
- [ ] MCP research appears in dedicated section
- [ ] All tests passing (>90% coverage)
- [ ] ModLogs updated per WSP 22
- [ ] Qwen→0102→012 architecture preserved

---

## 11. Final Verification

### Daemon Autonomy Check ✅
- Qwen orchestration role: UNCHANGED (circulatory system)
- 0102 arbitration role: UNCHANGED (brain decides)
- 012 observer role: UNCHANGED (strategic direction)
- MPS scoring: UNCHANGED
- Pattern learning: EXTENDED (not replaced)

### LEGO Foundation Board Check ✅
- HoloDAE as foundation: UNCHANGED
- Semantic search: UNCHANGED
- Code health monitoring: UNCHANGED
- Chain-of-thought logging: UNCHANGED
- Supports all FoundUp DAEs: UNCHANGED

### WSP Compliance Check ✅
- WSP 3: Correct domain placement
- WSP 17: Pattern memory integration
- WSP 22: ModLog updates planned
- WSP 35: HoloIndex protocol preserved
- WSP 50: Pre-action verification completed
- WSP 80: Cube orchestration preserved
- WSP 87: Semantic search respected

### Enhancement vs. Replacement Check ✅
- ✅ Intent classification ENHANCES Qwen (not replaces)
- ✅ Output composition ENHANCES format (not changes architecture)
- ✅ Feedback loop EXTENDS pattern learning (not replaces)
- ✅ MCP separation ORGANIZES output (not changes flow)
- ✅ Component routing FILTERS noise (not restricts autonomy)

---

## 12. Status

**Design Status:** ✅ COMPLETE - Ready for 012 Review

**Next Step:** Decision from 012:
1. Execute full 5-phase plan (recommended)
2. Execute MVP (Phases 1-3 only)
3. Defer to next session
4. Request design modifications

**Files Ready to Create/Modify:**
- `holo_index/intent_classifier.py` (new)
- `holo_index/output_composer.py` (new)
- `holo_index/feedback_learner.py` (new)
- `holo_index/mcp_integration_manager.py` (new)
- `holo_index/qwen_advisor/orchestration/qwen_orchestrator.py` (modify)
- `holo_index/qwen_advisor/holodae_coordinator.py` (modify)
- `holo_index/tests/test_intent_*.py` (new tests)

**Estimated Time to Implementation:** 5 hours with testing and documentation

---

*Design completed by 0102 in DAE Pattern Memory Mode*
*Architecture respects WSP 80 Cube-Level DAE Orchestration*
*Enhancement preserves daemon autonomy while reducing noise*
