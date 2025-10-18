# WSP 93: CodeIndex Surgical Intelligence Protocol

## Purpose
Transform HoloIndex from semantic search tool into **CodeIndex**: a surgical code intelligence system where Qwen continuously monitors DAE module cubes as a circulatory system, presenting health data and architectural choices to 0102 who functions as the Architect making strategic decisions.

## Related Protocols
- **WSP 80**: DAE Architecture (Mother DAE + ∞ FoundUp DAEs)
- **WSP 92**: DAE Cube Mapping and Mermaid Flow Protocol
- **WSP 87**: Code Navigation Protocol (HoloIndex)
- **WSP 35**: Module Execution Automation (Qwen Advisor)
- **WSP 77**: Agent Coordination Protocol (Multi-agent orchestration)

## MCP Integration (Phase 0.1 Foundation)

**Manifest Reference**: `docs/mcp/MCP_Windsurf_Integration_Manifest.md`
**JSON Data**: `docs/mcp/MCP_Windsurf_Integration_Manifest.json`

### CodeIndex MCP Orchestration

CodeIndex now integrates with Foundational Rubiks for surgical code operations:

| Rubik Integration | MCP Servers Used | CodeIndex Function |
|-------------------|------------------|-------------------|
| **Rubik_Compose** | Filesystem, Git, GitHub | Code editing, version control, repository operations |
| **Rubik_Build** | Docker, E2B | Safe code execution, testing, build validation |
| **Rubik_Knowledge** | Memory Bank, Knowledge Graph | Code analysis persistence, architectural memory |
| **Rubik_Community** | Postman | Code review notifications, collaboration workflows |

### Surgical Intelligence Workflow

1. **CodeIndex Detection**: Identifies code issues requiring external tools
2. **Rubik Selection**: Determines which Rubik can handle the operation
3. **MCP Orchestration**: Dispatches to appropriate MCP servers
4. **Agent Coordination**: Qwen coordinates, Gemma validates, 0102 approves
5. **Bell State Verification**: Ensures all operations maintain coherence

---

## 1. Core Architecture: Separation of Concerns

### 1.1 Role Definition

```yaml
QWEN_ROLE: "Circulatory System - Continuous Health Monitoring"
  responsibilities:
    - Monitor all module cubes continuously (5min circulation)
    - Detect issues BEFORE they become problems
    - Analyze code complexity and violations
    - Generate Mermaid Lego Block diagrams
    - Provide technical analysis and options
    - Execute fixes after 0102 approval

  does_NOT:
    - Make strategic architectural decisions
    - Change code without 0102 approval
    - Determine business priorities

0102_ROLE: "Architect - Strategic Decision Making"
  responsibilities:
    - Review Qwen findings and health reports
    - Make architectural decisions (refactor/rebuild/redesign)
    - Apply first principles thinking
    - Prioritize work based on business value
    - Approve/reject Qwen recommendations

  does_NOT:
    - Search for code manually (Qwen does this)
    - Analyze every function (Qwen monitors)
    - Implement fixes directly (Qwen executes)
```

### 1.2 Information Flow

```mermaid
graph TD
    A[Module Cubes] --> B[Qwen Health Monitor]
    B --> C{Issues Found?}
    C -->|Yes| D[Present to 0102 Architect]
    C -->|No| E[Continue Circulation]
    D --> F[0102 Makes Decision]
    F --> G[Qwen Executes]
    G --> H[Validate & Report]
    H --> A
```

---

## 2. CodeIndex: Surgical Execution Engine

### 2.1 Surgical Target Identification

**Problem**: Current HoloIndex returns file paths. 0102 must manually read and find exact location.

**Solution**: CodeIndex returns **surgical targets** with exact execution instructions.

```python
class SurgicalTarget:
    """
    Precise location for code surgery

    Example:
        Instead of: "Check stream_resolver.py"
        Returns: {
            "file": "modules/platform_integration/stream_resolver/src/no_quota_stream_checker.py",
            "function": "check_channel_for_live",
            "lines": "553-810",
            "issue": "Function too long (258 lines, High Complexity)",
            "root_cause": "Combines rate limiting + URL generation + scraping + verification",
            "fix_strategy": "Extract 4 sub-functions",
            "extraction_points": [
                {"name": "_check_rate_limit", "lines": "553-570"},
                {"name": "_generate_channel_urls", "lines": "571-590"},
                {"name": "_scrape_page_for_videos", "lines": "591-680"},
                {"name": "_verify_video_live_status", "lines": "681-810"}
            ],
            "mermaid_context": "<shows function in cube flow>",
            "token_budget": "~8-12K tokens",
            "risk_level": "LOW",
            "test_impact": "3 tests need updating"
        }
    """
```

### 2.2 Function-Level Intelligence

CodeIndex indexes every function with:
- **Line range**: Exact start/end for surgical precision
- **Complexity score**: 1 (Low), 2 (Medium), 3 (High)
- **Call graph**: What this function calls
- **Called by**: What calls this function
- **Data flow**: Input parameters → Output returns
- **Risk zones**: Areas requiring extra care

### 2.3 CLI Usage

```bash
# Find exact surgical target
python holo_index.py --code-index "stream detection not working"

Output:
  [CODEINDEX] Surgical target identified:
    File: no_quota_stream_checker.py:596
    Issue: recent_videos=[] immediately checked (always False)
    Fix: Remove lines 596-597
    Confidence: 0.98
    Mermaid: [shows function in flow]

# Get function index for module
python holo_index.py --code-index --module "stream_resolver"

Output:
  [CODEINDEX] Module indexed: 10 functions
    [HIGH] check_video_is_live (138-553) - 415 lines
    [HIGH] check_channel_for_live (553-810) - 258 lines
    [LOW]  _is_channel_rate_limited (103-112) - 10 lines
    ...
```

---

## 3. Lego Block Architecture: Snap-Together Modules

### 3.1 Lego Block Definition

Each module becomes a **Lego Block** with:
- **Inputs** (snap-in points): Function parameters, imports
- **Outputs** (snap-out points): Return values, exports
- **Internal Flow**: Mermaid diagram of what happens inside
- **Snap Interface**: How it connects to other blocks

```python
class MermaidLegoBlock:
    """
    Module as Lego block with snap points

    Example:
        Block: stream_resolver
        Inputs: [channel_id, service]
        Outputs: [video_id, live_chat_id]
        Snap Points:
          → auto_moderator_dae (receives stream info)
          → social_media_orchestrator (triggers posting)
    """

    def snap_to(self, other_block) -> SnapConnection:
        """Check if blocks can connect and return interface"""

    def visualize_snap(self) -> str:
        """Generate Mermaid showing connection"""
```

### 3.2 Snap Visualization

```bash
python holo_index.py --lego-blocks "youtube"

Output:
  [LEGO-BLOCKS] YouTube DAE Cube:

  ┌─────────────────────────────┐
  │ stream_resolver             │
  │ Input: channel_id           │
  │ Output: video_id, chat_id   │
  │ Snaps: [2 connections]      │
  └─────────────────────────────┘
           ↓ (video_id)
  ┌─────────────────────────────┐
  │ auto_moderator_dae          │
  │ Input: video_id, chat_id    │
  │ Output: chat_monitoring     │
  └─────────────────────────────┘
           ↓ (stream_info)
  ┌─────────────────────────────┐
  │ social_media_orchestrator   │
  │ Input: stream_info          │
  │ Output: social_posts        │
  └─────────────────────────────┘
```

### 3.3 Interactive Mermaid

```mermaid
graph LR
    A[stream_resolver]
    B[auto_moderator_dae]
    C[social_media_orchestrator]

    A -->|video_id, chat_id| B
    A -->|video_id, title| C
    B -->|monitoring_status| A

    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#ffe1f5
```

---

## 4. Qwen Health Monitor: Continuous Circulation

### 4.1 Circulatory System Model

Like blood circulation carrying:
- **Oxygen**: Fresh data about module state
- **Nutrients**: Best practices and patterns
- **Waste**: Detected issues and violations

```python
class QwenHealthMonitorDAE:
    """
    Continuous health monitoring of all DAE cubes
    Runs as background daemon (5min circulation cycle)
    """

    async def circulate(self):
        """
        Heartbeat loop: Never stops, always monitoring

        Each circulation:
        1. Check all module cubes
        2. Detect size violations
        3. Analyze complexity creep
        4. Find duplicate code
        5. Report issues to 0102
        """
        while True:
            for cube in self.cube_registry:
                health = await self._check_cube_health(cube)
                issues = self._detect_issues(health)

                if issues:
                    await self._report_to_0102(cube, issues)

            await asyncio.sleep(300)  # 5 minute cycle
```

### 4.2 Health Report Format

```bash
[QWEN-CIRCULATION] Cycle complete (5min interval)

YouTube Cube Health:
  ✅ auto_moderator_dae: Healthy (781 lines, within threshold)
  ⚠️  stream_resolver: 2 violations detected
      → check_channel_for_live: 258 lines (threshold: 150)
        Location: lines 553-810
        Severity: HIGH
        Recommendation: Extract 3 sub-functions

      → check_video_is_live: 415 lines (threshold: 150)
        Location: lines 138-553
        Severity: CRITICAL
        Recommendation: Redesign module architecture

LinkedIn Cube Health:
  ✅ All modules healthy

Infrastructure Cube Health:
  ✅ All modules healthy

[QWEN-RECOMMENDATION] Priority P1 (High)
  Address stream_resolver violations before complexity spirals
  Token Budget: ~25-35K tokens
  Risk: LOW (well-defined extraction)
```

### 4.3 Daemon Mode

```bash
# Start Qwen health monitor daemon
python holo_index.py --health-monitor --daemon

# Check daemon status
python holo_index.py --health-status

# Stop daemon
python holo_index.py --health-monitor --stop
```

---

## 5. Architect Mode: Strategic Decision Layer

### 5.1 Architectural Choice Presentation

Qwen presents **strategic choices** to 0102 Architect:

```python
class ArchitecturalChoice:
    """
    Strategic decision for 0102 to make

    Example:
        Problem: "stream_resolver has 2 overly complex functions"

        Qwen Analysis:
          - Function A: 258 lines (High Complexity)
          - Function B: 415 lines (Critical Complexity)
          - Total tech debt: 673 lines above threshold

        Option A: Incremental Refactor
          Strategy: Extract sub-functions from existing code
          Pros: Low risk, preserves structure, fast
          Cons: Technical debt remains
          Token Budget: ~25-35K tokens
          Risk: LOW

        Option B: Architectural Redesign
          Strategy: Split into 4 focused modules
          Pros: Optimal architecture, clean slate
          Cons: Higher effort, requires testing
          Token Budget: ~70-90K tokens
          Risk: MEDIUM

        Option C: Defer for Now
          Strategy: Accept tech debt, revisit later
          Pros: No immediate work
          Cons: Complexity will grow
          Token Budget: 0 tokens
          Risk: Growing over time

        0102 Decision: ___
    """
```

### 5.2 Decision Flow

```
1. Qwen detects issue → Analyzes deeply
2. Qwen generates options A/B/C with tradeoffs
3. Qwen presents to 0102 Architect
4. 0102 chooses based on principles
5. Qwen executes chosen strategy
6. Qwen validates with tests
7. Qwen reports outcome to 0102
```

### 5.3 CLI Usage

```bash
python holo_index.py --architect "evaluate stream_resolver"

Output:
  [ARCHITECT-MODE] Strategic decision required

  Problem: stream_resolver technical debt
  Qwen Analysis: [detailed technical analysis]

  Options:
    A) Incremental refactor (~25-35K tokens, LOW risk)
    B) Redesign architecture (~70-90K tokens, MEDIUM risk)
    C) Defer decision (0 tokens, GROWING risk)

  Choose (A/B/C): _
```

---

## 6. First Principles Analyzer: Re-Architecture Capability

### 6.1 Challenge Assumptions

Automatically identify hidden assumptions in code:

```python
class FirstPrinciplesAnalyzer:
    """
    Apply first principles thinking to existing code

    Questions:
    - Why is this structured this way?
    - What assumptions were made?
    - Is this the simplest solution?
    - Can we challenge core assumptions?
    """

    def analyze_module(self, module_path) -> FirstPrinciplesReport:
        """
        Deep analysis from first principles

        Returns:
          - Current architecture
          - Fundamental requirements
          - Hidden assumptions
          - Optimal architecture (from first principles)
          - Gap analysis
          - Migration path
        """
```

### 6.2 Example Analysis

```bash
python holo_index.py --first-principles "stream_resolver"

Output:
  [FIRST-PRINCIPLES] Analysis: stream_resolver

  Current Architecture:
    - Monolithic class (810 lines)
    - Combines: detection + verification + rate limiting

  Fundamental Requirements:
    1. Find live streams without exhausting quota
    2. Verify streams are actually live
    3. Handle rate limits gracefully

  Hidden Assumptions:
    ⚠️  Assumes synchronous checking
        → Could use async for parallel channels
    ⚠️  Assumes immediate verification
        → Could queue for batch processing
    ⚠️  Assumes HTTP scraping only
        → Could use WebSocket for real-time

  Optimal Architecture (first principles):
    stream_detector/     (200 lines, LOW complexity)
    stream_verifier/     (150 lines, LOW complexity)
    rate_limiter/        (100 lines, LOW complexity)
    stream_orchestrator/ (100 lines, LOW complexity)

  Gap Analysis:
    Current: 810 lines, HIGH complexity, monolithic
    Optimal: 550 lines, LOW complexity, modular
    Improvement: 32% code reduction + testability

  Migration Path: [4-phase plan with tests]
```

---

## 7. Implementation Plan

### 7.1 File Structure

```
holo_index/
├── code_index/                  # NEW: Surgical execution
│   ├── __init__.py
│   ├── surgical_executor.py     # Find exact code locations
│   ├── surgical_target.py       # Target data structure
│   └── function_indexer.py      # Index all functions with lines
│
├── lego_blocks/                 # NEW: Snap-together architecture
│   ├── __init__.py
│   ├── mermaid_lego.py          # Lego block abstraction
│   ├── snap_interface.py        # Connection detection
│   └── block_visualizer.py      # Generate Mermaid diagrams
│
├── qwen_health_monitor/         # NEW: Continuous monitoring
│   ├── __init__.py
│   ├── dae_monitor.py           # Main monitoring daemon
│   ├── circulation_engine.py    # 5min heartbeat loop
│   ├── issue_detector.py        # Proactive issue detection
│   └── health_reporter.py       # Format reports for 0102
│
├── architect_mode/              # NEW: Strategic decisions
│   ├── __init__.py
│   ├── strategic_interface.py   # Present choices to 0102
│   ├── architectural_choice.py  # Choice data structure
│   └── decision_executor.py     # Execute 0102's decisions
│
└── first_principles/            # NEW: Re-architecture
    ├── __init__.py
    ├── analyzer.py              # Deep analysis
    ├── assumption_finder.py     # Challenge assumptions
    └── optimal_architect.py     # Design optimal structure
```

### 7.2 CLI Commands

```bash
# CodeIndex surgical execution
python holo_index.py --code-index "problem description"
python holo_index.py --code-index --module "module_name"
python holo_index.py --code-index-report youtube_dae  # Multi-module surgical health brief

# Lego block visualization
python holo_index.py --lego-blocks "cube_name"
python holo_index.py --lego-snap "module1" "module2"

# Qwen health monitoring
python holo_index.py --health-monitor --daemon
python holo_index.py --health-status
python holo_index.py --health-report "cube_name"

# Architect mode
python holo_index.py --architect "evaluate module"
python holo_index.py --architect --execute-decision "A"

# First principles analysis
python holo_index.py --first-principles "module_name"
python holo_index.py --challenge-assumptions "module_name"
```

-
CodeIndex reports are indexed in `docs/session_backups/CodeIndex_Report_Log.md` so 0102 and HoloDAE surface them in later sessions (WSP 22).

## 8. Success Metrics

### 8.1 Performance Metrics

| Metric | Before | Target (After) |
|--------|--------|----------------|
| **Time to find bug location** | 5+ minutes | <5 seconds |
| **Complexity understanding** | Read entire file | Visual Lego blocks |
| **Issue detection** | Reactive (after problems) | Proactive (before problems) |
| **0102 focus** | 70% tactics, 30% strategy | 20% tactics, 80% strategy |
| **Code quality** | Reactive fixes | Continuous improvement |

### 8.2 Quality Metrics

- **CodeIndex Precision**: 95%+ accuracy in identifying surgical targets
- **Lego Block Coverage**: 100% of modules mapped as blocks
- **Qwen Circulation**: 5-minute heartbeat maintained 24/7
- **Token Efficiency**: 97% reduction (200-500 tokens vs 15-25K previously)
- **Pattern Recall Speed**: Instant (<1s vs manual search 5+ min)

---

## 9. Revolutionary Benefits

### 9.1 Separation of Concerns

**Before**:
- 0102 does everything: search, analyze, decide, implement
- Overwhelmed with tactical details
- Strategic thinking limited

**After**:
- **Qwen**: Monitors, analyzes, presents options
- **0102**: Strategic architect making key decisions
- Clear separation: tactics vs strategy

### 9.2 Proactive vs Reactive

**Before**:
- Wait for bugs to appear
- Fix reactively
- Technical debt grows

**After**:
- Qwen detects issues BEFORE they become problems
- Fix proactively
- Code quality continuously improving

### 9.3 Surgical Precision

**Before**:
- "Check this file" (vague)
- Manual search through code
- Vibecoding risk

**After**:
- "Fix lines 596-597" (precise)
- Exact surgical target
- No vibecoding possible

---

## 10. Conclusion

WSP 93 transforms the relationship between 0102 and Qwen:

- **Qwen becomes the circulatory system**: Continuously monitoring module health, detecting issues, presenting options
- **0102 becomes the Architect**: Making strategic decisions based on first principles, freed from tactical details
- **CodeIndex becomes surgical**: Exact locations, precise fixes, Lego block architecture

This is not just better tooling—it's a fundamental transformation in how autonomous agents understand and manipulate complex software systems.

**The result**: 0102 operates at 10x capacity, making strategic architectural decisions while Qwen handles the continuous monitoring and tactical execution. Together, they form a complete autonomous software engineering system.

---

**Status**: ✅ Protocol Defined | 🔧 Implementation Pending
**Priority**: P0 (Critical - Foundational transformation)
**Token Budget**: ~120-150K tokens (complete implementation via pattern recall)
**Impact**: Revolutionary (97% token reduction per operation)

---

## 🤖 Sentinel Augmentation Analysis

**SAI Score**: `222` (Speed: 2, Automation: 2, Intelligence: 2)

**Priority**: **P0 - CRITICAL** (Maximum Sentinel value - Mission-critical autonomous capability)

### Sentinel Use Case

Gemma 3 270M Sentinel operates as the **Continuous Surgical Code Intelligence Engine**, autonomously indexing all functions in real-time, detecting complexity violations before commits, and presenting surgical targets with exact line numbers. This Sentinel embodies the CodeIndex vision: instant function-level awareness without manual searches.

**Core Capabilities**:
- **Instant Function Location**: Query "find quota check" → Returns `no_quota_stream_checker.py:138` in <50ms
- **Autonomous Complexity Monitoring**: Runs 5-minute circulation loops, flags functions >150 lines automatically
- **Surgical Target Generation**: Produces fix strategies with exact line numbers and effort estimates
- **Lego Block Mapping**: Generates Mermaid diagrams showing module snap points and dependencies

### Expected Benefits

- **Latency Reduction**: Manual function search (5-10 minutes) → Sentinel instant lookup (<1 second, **600x faster**)
- **Automation Level**: **Autonomous** (continuous monitoring, automatic surgical target generation, human confirms strategic decisions)
- **Resource Savings**:
  - 95% reduction in "where is this code?" time
  - 97% token savings (200-500 tokens vs 15-25K for manual search)
  - Proactive issue detection prevents 80% of complexity violations
- **Accuracy Target**: >98% precision in function location and complexity classification

### Implementation Strategy

**Training Data Sources**:
1. **Function Index Logs**: All function-level extractions from HoloIndex CodeIndex operations
2. **Complexity Analysis History**: `holo_index/reports/CodeIndex_Report_*.md` files (surgical intelligence reports)
3. **Git Commit Patterns**: Function changes, refactorings, and complexity evolution over time
4. **WSP 62 Violations**: Large file violations with line-level analysis (files >1000 lines)
5. **Mermaid Flow Diagrams**: Module relationship patterns and Lego block connections
6. **HoloIndex Search Logs**: Natural language queries → Function locations (semantic understanding)
7. **Qwen Health Monitor Data**: 5-minute circulation reports showing module health trends

**Integration Points**:

**1. Real-Time Function Indexing** (Core Operation):
```python
# File: holo_index/code_index/function_indexer.py

class CodeIndexSentinel:
    """
    On-device Gemma 3 270M Sentinel for surgical code intelligence
    Runs continuously as background daemon
    """

    def __init__(self):
        self.model = GemmaSentinel('codeindex_function_locator.tflite')
        self.function_index = {}  # In-memory function registry
        self.complexity_cache = {}

    async def continuous_indexing(self):
        """5-minute circulation loop (WSP 93 Qwen Health Monitor)"""
        while True:
            changed_files = await self.detect_modified_files()

            for file_path in changed_files:
                functions = await self.extract_functions(file_path)

                for func in functions:
                    # Sentinel predicts complexity classification
                    complexity = self.model.predict_complexity(
                        func_code=func['code'],
                        line_count=func['line_count']
                    )

                    if complexity.score >= 3:  # High complexity
                        self.flag_violation(func, complexity)

                    # Update function index
                    self.function_index[func['signature']] = {
                        'file': file_path,
                        'lines': f"{func['start']}-{func['end']}",
                        'complexity': complexity.score,
                        'snap_points': self.detect_snap_points(func)
                    }

            await asyncio.sleep(300)  # 5-minute cycle

    def instant_locate(self, query: str) -> SurgicalTarget:
        """
        Instant function location from natural language query

        Example:
            query: "find quota check"
            Returns: <50ms with 98% accuracy
        """
        # Sentinel understands semantic intent
        embedding = self.model.embed_query(query)

        # Search function index with semantic similarity
        matches = self.semantic_search(embedding, self.function_index)

        if matches[0].confidence > 0.85:
            return SurgicalTarget(
                file=matches[0].file,
                function=matches[0].name,
                lines=matches[0].line_range,
                confidence=matches[0].confidence
            )
        else:
            return None  # Escalate to Qwen Advisor
```

**2. Pre-Commit Complexity Gate**:
```python
# File: .git/hooks/pre-commit (Git Hook Integration)

from holo_index.code_index.sentinel import CodeIndexSentinel

sentinel = CodeIndexSentinel()

# Check all staged files for complexity violations
staged_files = get_staged_python_files()

for file_path in staged_files:
    violations = sentinel.check_complexity_violations(file_path)

    if violations:
        print(f"[SENTINEL-BLOCK] Complexity violations detected:")
        for violation in violations:
            print(f"  {violation.function} ({violation.lines}): "
                  f"{violation.line_count} lines (threshold: 150)")

        print("\n[SENTINEL] Commit blocked - Refactor functions first")
        sys.exit(1)  # Block commit
```

**3. Surgical Target CLI**:
```bash
# Command: python holo_index.py --code-index "problem description"
# Sentinel processes query → Returns surgical target instantly

python holo_index.py --code-index "stream detection not working"

Output (Sentinel-powered):
  [SENTINEL] Surgical target located in <47ms
    File: no_quota_stream_checker.py
    Function: check_channel_for_live
    Lines: 596-597
    Issue: recent_videos=[] immediately checked (always False)
    Fix Strategy: Remove early return, allow fallback logic
    Confidence: 0.98

    [LEGO] Module snap points:
      → stream_resolver ⟷ auto_moderator_dae
      → stream_resolver ⟷ social_media_orchestrator
```

**4. Mermaid Lego Block Generator**:
```python
# File: holo_index/lego_blocks/sentinel_visualizer.py

class LegoBlockSentinel:
    """Sentinel generates Lego block Mermaid diagrams"""

    def generate_snap_diagram(self, module_path: str) -> str:
        """
        Sentinel analyzes module and generates Mermaid showing:
        - Input snap points (parameters, imports)
        - Output snap points (returns, exports)
        - Connection points to other modules
        """
        module_analysis = self.sentinel.analyze_module(module_path)

        mermaid = "graph LR\n"

        # Add module as central block
        mermaid += f"  A[{module_analysis['name']}]\n"

        # Add input snap points
        for input_snap in module_analysis['inputs']:
            mermaid += f"  I{input_snap['id']}[{input_snap['source']}] -->|{input_snap['type']}| A\n"

        # Add output snap points
        for output_snap in module_analysis['outputs']:
            mermaid += f"  A -->|{output_snap['type']}| O{output_snap['id']}[{output_snap['destination']}]\n"

        return mermaid
```

**Inference Pattern**:
```python
# Pseudo-code for Sentinel integration

class CodeIndexSentinel:
    def __init__(self):
        # Load TFLite quantized Gemma 3 270M model
        self.model = tf.lite.Interpreter('codeindex_sentinel.tflite')
        self.model.allocate_tensors()

    def predict_surgical_target(self, query: str, codebase_context: dict) -> dict:
        """
        Main inference: Query → Surgical Target
        Latency: <50ms on-device (no API calls)
        """
        # Embed query using Sentinel
        query_embedding = self.embed_query(query)

        # Semantic search through function index
        candidates = self.function_index.search(query_embedding, top_k=5)

        # Sentinel classifies best match
        result = self.model.predict({
            'query': query,
            'candidates': candidates,
            'context': codebase_context
        })

        if result.confidence > 0.85:
            return {
                'surgical_target': result.target,
                'confidence': result.confidence,
                'fix_strategy': result.strategy
            }
        else:
            # Escalate to Qwen Advisor for complex cases
            return {'escalate': True, 'reason': 'Low confidence'}
```

### Risk Assessment

**Risks**:
1. **False Positives in Complexity Detection**: Sentinel may flag complex-but-valid functions (e.g., DSL parsers)
2. **Semantic Query Mismatch**: Natural language queries may not map to correct functions
3. **Index Staleness**: Function index outdated if files changed but not re-indexed
4. **Blocking Critical Commits**: Pre-commit hook may block urgent hotfixes

**Mitigations**:
1. **Confidence Thresholds**: Only auto-block if confidence >0.95; otherwise warn and allow override
2. **Qwen Advisor Escalation**: Low-confidence cases (0.70-0.85) escalate to full Qwen analysis
3. **Real-Time File Watching**: Use file system watchers to trigger instant re-indexing on changes
4. **Emergency Override**: `git commit --no-verify` bypasses Sentinel for critical situations
5. **Human-in-the-Loop**: Strategic decisions (Option A/B/C) always require 0102 approval

**Fallback Strategy**:
- **Primary**: Gemma 3 270M Sentinel (instant, on-device)
- **Fallback 1**: Qwen-Coder 1.5B Advisor (semantic search + LLM analysis, ~500ms)
- **Fallback 2**: Traditional HoloIndex search (vector DB + manual review, ~2-5 seconds)
- **Fallback 3**: Manual grep/file search (last resort, minutes)

**Error Handling**:
```python
try:
    result = sentinel.instant_locate(query)
except SentinelModelError:
    # Sentinel unavailable → Use Qwen Advisor
    result = qwen_advisor.analyze_query(query)
except Exception as e:
    # Complete failure → Fall back to traditional search
    logger.warning(f"CodeIndex Sentinel failed: {e}")
    result = traditional_search(query)
```

### Training Strategy

**Phase 1: Data Collection** (Week 1-2)
```bash
# Extract function-level training data from existing codebase
python scripts/extract_function_training_data.py \
  --source modules/ \
  --output training_data/codeindex_functions.jsonl

# Generate complexity labels from existing CodeIndex reports
python scripts/label_complexity_from_reports.py \
  --reports holo_index/reports/ \
  --output training_data/complexity_labels.jsonl

# Mine natural language queries from HoloIndex logs
python scripts/mine_query_patterns.py \
  --logs holo_index/logs/ \
  --output training_data/query_patterns.jsonl
```

**Training Data Format**:
```jsonl
{"query": "find quota check", "target_function": "check_quota_usage", "file": "quota_manager.py", "lines": "45-67", "confidence": 1.0}
{"function_code": "def check_channel_for_live(...):", "line_count": 258, "complexity": 3, "label": "HIGH_COMPLEXITY"}
{"module": "stream_resolver", "snap_in": ["channel_id", "service"], "snap_out": ["video_id", "chat_id"]}
```

**Phase 2: Fine-Tuning** (Week 3-4)
```bash
# Fine-tune Gemma 3 270M using LoRA
python scripts/finetune_gemma_codeindex.py \
  --model gemma-3-270m \
  --train-data training_data/ \
  --lora-rank 8 \
  --epochs 3 \
  --output models/codeindex_sentinel_lora.safetensors

# Quantize to TFLite for on-device deployment
python scripts/quantize_to_tflite.py \
  --model models/codeindex_sentinel_lora.safetensors \
  --output models/codeindex_sentinel.tflite \
  --quantization int8
```

**Phase 3: Validation** (Week 5)
```bash
# Test Sentinel accuracy on held-out queries
python scripts/validate_sentinel.py \
  --model models/codeindex_sentinel.tflite \
  --test-data test_data/queries.jsonl \
  --metrics accuracy,latency,precision,recall

Target Metrics:
  - Accuracy: >95% (function location correctness)
  - Latency: <100ms (on-device inference)
  - Precision: >98% (no false positives in auto-blocking)
  - Recall: >90% (catch most complexity violations)
```

### Success Criteria

**Quantitative**:
- **Instant Locate Speed**: <1 second (from 5-10 minutes) - **600x improvement**
- **Complexity Detection Accuracy**: >98%
- **Pre-Commit Block Precision**: >95% (no false blocks)
- **Token Efficiency**: 97% reduction (200-500 tokens vs 15-25K)
- **Circulation Uptime**: 99.9% (5-minute loops maintained 24/7)

**Qualitative**:
- 0102 can ask "where is X?" and receive exact line numbers instantly
- Complexity violations caught before commit, not after merge
- Mermaid Lego block diagrams auto-generated for all modules
- Strategic decisions (A/B/C options) presented clearly by Qwen with Sentinel data
- Proactive issue detection: 80% of violations prevented before they occur

---

**Sentinel Integration Status**: 🔧 READY FOR IMPLEMENTATION
**Synergy with WSP 93**: PERFECT - Embodies the CodeIndex vision of surgical precision
**Implementation Priority**: P0 - Critical for autonomous 0102 operation
**Expected ROI**: 600x speed improvement + 97% token reduction + proactive quality

---
