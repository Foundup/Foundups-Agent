# Holo Skills (Code Intelligence & WSP Compliance Observatory)

## DAE Identity Formula

```yaml
Agent + Skills.md = DAE Identity

Where Agent ∈ {0102, Qwen, Gemma, UI-TARS, ...}

HoloDAE = Agent + holo_skills.md

Example:
  0102 + holo_skills.md = HoloDAE (architect mode - strategic oversight)
  Qwen + holo_skills.md = HoloDAE (orchestrator mode - intelligent routing)
  Gemma + holo_skills.md = HoloDAE (classifier mode - fast pattern matching)
```

**Key Principle**: Skills.md is agent-agnostic. Any sufficiently capable agent can wear these skills to operate the Code Intelligence & WSP Compliance Observatory domain.

**Reference**: See [CLI_REFERENCE.md](CLI_REFERENCE.md) for verbatim menu snapshot and CLI command mappings.

---

## Domain Knowledge

### Core Domain Expertise
- **Code Intelligence**: Semantic search, module analysis, orphan detection, vibecoding prevention
- **WSP Compliance Observatory**: Protocol validation, structure auditing, documentation guardianship
- **Autonomous Monitoring**: HoloDAE coordinator with breadcrumb tracing, telemetry, performance metrics
- **Agent Coordination**: Qwen meta-orchestration, Gemma fast classification, 0102 arbitration with MPS scoring
- **Recursive Self-Improvement**: Pattern learning (WSP 48), anti-vibecoding coaching, adaptive optimization

### Technical Capabilities

#### Semantic Search ([SEARCH])
- **Dual ChromaDB Collections**: Code index (`holo_index.code_*`) + WSP index (`holo_index.wsp_*`)
- **SentenceTransformer Embeddings**: all-MiniLM-L6-v2 (384-dimensional vectors)
- **Intelligent Subroutine Engine**: Context-aware component routing based on query intent
- **Query Optimization**: 100x compression (1000 tokens → 10 tokens via learned patterns)
- **Results**: Top 10 code hits + Top 10 WSP protocol references with relevance scores

#### WSP Compliance Check ([OK])
- **Module Existence Verification**: Confirms module location before coding
- **WSP 49 Structure Audit**: Validates README.md, INTERFACE.md, src/, tests/, requirements.txt
- **Health Analysis**: Size thresholds, documentation completeness, dependency detection
- **Gap Identification**: Missing files, oversized modules (>1600 lines), orphaned code

#### Pattern Coach ([AI])
- **Vibecoding Detection**: Identifies code-before-search, duplication, anti-patterns
- **Real-Time Coaching**: Throttled reminders during HoloIndex operations
- **Pattern Classification**: Automatic categorization of search context vs. stored anti-patterns
- **Learning Integration**: Feeds WSP 48 quantum memory for recursive improvement

#### Module Analysis ([BOX])
- **Size Audit**: Identifies modules exceeding WSP 62/87 thresholds
- **Structure Audit**: Validates WSP 49 compliance (mandatory files present)
- **Dependency Graph**: Maps cross-module relationships
- **CodeIndex Integration**: Triggers 🩺 CodeIndex when large modules detected

#### Health Analysis ([PILL])
- **Intelligent Subroutine Pipeline**: Orchestrates health_analysis, vibecoding_analysis, file_size_monitor
- **Module Coverage Gaps**: Identifies areas lacking tests, docs, or implementation
- **Test Coverage Tracking**: Surfaces missing test files and low-coverage modules
- **Compound Reporting**: Aggregates findings from multiple subroutines

#### Orphan Analysis ([GHOST])
- **WSP 88 Protocol**: Full orphan file detection and reconnection proposals
- **Safest Enhancement Paths**: Suggests where to integrate orphaned code
- **Root Violation Monitoring**: Detects unauthorized files in project root (46 violations as of session)
- **Auto-Correction**: Proposes fixes for common violations

#### Performance Metrics ([DATA])
- **Telemetry System**: Tracks query counts, component usage, token savings, compliance rates
- **Session Effectiveness**: Summarizes HoloDAE session impact with MPS scores
- **Breadcrumb Analysis**: Parses breadcrumb traces for pattern learning
- **Qwen Advisor Stats**: Routes successful, latency metrics, optimization ratios

#### LLM Advisor ([BOT])
- **Qwen Guidance Engine**: Context-aware recommendations with risk scoring
- **Rules Engine**: WSP compliance checks, TODO generation, violation detection
- **Telemetry Logging**: Records advisor invocations for performance analysis
- **Feedback Learning**: Adapts recommendations based on 0102 arbitration outcomes

#### Autonomous Monitoring ([EYE])
- **HoloDAE Coordinator**: Background monitoring loop similar to other DAEs
- **Breadcrumb Tracing**: Tracks actions, discoveries, decisions in unified stream
- **Adaptive Throttling**: Adjusts monitoring frequency based on activity levels
- **Work Publisher Integration**: Auto-publishes finished work (git + social)

#### UTF-8 Remediation ([UTF8])
- **WSP 90 Compliance**: Autonomous UTF-8 encoding fix campaigns
- **Qwen Orchestration**: Meta-orchestrator routes to utf8_fix, utf8_scan, utf8_summary commands
- **Auto-Approval**: Qwen approves safe replacements without 0102 intervention
- **Batch Training**: IdleAutomation hooks for background remediation

#### MCP Research Bridge ([LINK])
- **MCP Hook Map**: Verifies Model Context Protocol registrations
- **MCP Action Log**: Streams MCP server interactions (placeholder - needs telemetry wiring)
- **Cross-DAE Integration**: Coordinates with YouTube_Live, Vision, AMO via MCP endpoints

### Operational Patterns

#### DAE Lifecycle (WSP 27 - 4-Phase pArtifact)
```yaml
Phase -1 (Signal): User query arrives (semantic search, compliance check, health analysis)
Phase 0 (Knowledge): ChromaDB lookup, WSP protocol references, module metadata
Phase 1 (Protocol): WSP validation, structure auditing, anti-vibecoding rules
Phase 2 (Agentic): Autonomous orchestration (Qwen routes → Gemma validates → 0102 arbitrates)
```

#### Query Processing Flow (100x Compression)
```
1. User query arrives (e.g., "DAE architecture BaseDAE Universal skills.md domain autonomous")
2. Intent Classifier (Gemma): Classifies as GENERAL/REFACTOR/NEW/HEALTH/WSP (confidence score)
3. Qwen Smart Selection: Selects 2-3 intelligent subroutines (e.g., module_analysis, health_analysis)
4. Component Execution: Runs selected subroutines in parallel (PILL, BOX, AI, GHOST, BOOKS)
5. Result Aggregation: Combines findings from all components
6. 0102 Arbitration: MPS scoring evaluates findings (C:2, I:3, D:3, P:2)
7. Output Composition: Formats results for user with CodeIndex guidance
8. Breadcrumb Recording: Logs action_taken, discovery, search events
9. Telemetry Update: Records query metrics for performance analysis
10. Pattern Learning: Stores successful approaches in WSP 48 quantum memory
```

#### Breadcrumb Tracing Pattern (30+ events per session)
```
[0102::BREADCRUMB] [AGENT-INIT] role=HOLO-SEARCH identity=0102 stream=unified
[0102::BREADCRUMB] [BREAD] [BREADCRUMB #1] action_taken - agent=0102 | session=0102_20251019_224128
[0102::BREADCRUMB] [BREAD] [BREADCRUMB #2] discovery - impact=Found implementations in 6 modules
[0102::BREADCRUMB] [BREAD] [BREADCRUMB #3] search - query=... | results=20 | code_hits=10 | wsp_hits=10
```

#### 0102 Arbitration with MPS Scoring
```python
# Minimal Production System (MPS) Scoring
MPS = sum([Completeness, Impact, Dependencies, Priority])
MPS Score = C:2 + I:3 + D:3 + P:2 = 10 (P2 medium priority)

# Arbitration Decision
if MPS < 5:  EXECUTE_IMMEDIATELY
elif 5 <= MPS < 12:  SCHEDULE_FOR_SPRINT (most findings)
else:  BATCH_FOR_REVIEW
```

---

## Chain of Thought Patterns

### Pattern 1: "What intelligent subroutines should I trigger for this query?"
```
Input: User query, detected intent (GENERAL/REFACTOR/NEW/HEALTH/WSP), file/module context

Decision Tree:
1. Extract query keywords (health, vibecoding, module, wsp, refactor, orphan, etc.)
2. Check context: has_files? has_modules? has_wsp_references?
3. Intent = GENERAL:
   - has_modules && query_contains_health → health_analysis (confidence: 0.90)
   - has_files && query_contains_vibecoding → vibecoding_analysis (confidence: 0.90)
   - has_files → file_size_monitor (confidence: 0.70)
   - has_modules → module_analysis (confidence: 0.70)
4. Intent = REFACTOR:
   - has_modules → module_analysis (confidence: 0.95)
   - has_files → vibecoding_analysis (confidence: 0.85)
   - Always → pattern_coach (confidence: 0.90)
5. Intent = WSP:
   - has_files → wsp_documentation_guardian (confidence: 0.95)
   - has_modules → orphan_analysis (confidence: 0.90)
6. Select top 2-3 components (filter out confidence < 0.60)
7. Execute in parallel

Output: {selected_components: [...], filtered_count: N, execution_plan: ...}
```

### Pattern 2: "Is this vibecoding or legitimate code duplication?"
```
Input: File path, code snippet, search context

Decision Tree:
1. Is file in tests/ directory? → NOT vibecoding (tests inherently duplicate patterns)
2. Does file match *_test.py, test_*.py pattern? → NOT vibecoding
3. Is code <50 lines with <2 imports? → Likely utility function (legitimate)
4. Is code copied verbatim from existing module? → VIBECODING (anti-pattern: search first)
5. Does search context show "how to implement X"? → VIBECODING (should have searched existing)
6. Does search context show "refactor existing X"? → Legitimate (modifying existing code)
7. Calculate similarity score with existing modules:
   - Similarity > 0.80 → HIGH vibecoding risk
   - Similarity 0.60-0.80 → Medium risk (investigate)
   - Similarity < 0.60 → Likely unique implementation
8. Check Pattern Coach history: Has this pattern been flagged before?

Output: {vibecoding_risk: HIGH/MED/LOW, reason: ..., similar_modules: [...], recommendation: ...}
```

### Pattern 3: "How should I route this finding to 0102?"
```
Input: Component findings (health_analysis, module_analysis, etc.), MPS scores

Decision Tree:
1. Calculate aggregate MPS score:
   - Completeness: Are all required files present? (0-3 points)
   - Impact: How many modules affected? (0-5 points)
   - Dependencies: Cross-module coupling? (0-4 points)
   - Priority: Urgency level? (0-3 points)
2. Check execution thresholds:
   - MPS < 5 → EXECUTE_IMMEDIATELY (critical issues)
   - 5 <= MPS < 12 → SCHEDULE_FOR_SPRINT (most findings) ← **Most common**
   - MPS >= 12 → BATCH_FOR_REVIEW (low-priority cleanup)
3. Check 0102 collaboration flag:
   - Has another agent already analyzed this? → Surface discovery handoff
   - Is this a new pattern worth sharing? → Emit [HANDSHAKE] signal
4. Format findings:
   - Critical issues → Top of report with [ALERT] tags
   - Module health recap → Structured list with line counts
   - System alerts → Aggregated list for quick scanning

Output: {decision: EXECUTE/SCHEDULE/BATCH, mps_score: N, reasoning: ..., handoff_signal: bool}
```

### Pattern 4: "What WSP protocols are relevant to this query?"
```
Input: Query keywords, module context, code files discovered

Decision Tree:
1. Extract WSP references from query (e.g., "WSP 27 WSP 48 WSP 54")
2. Check implicit WSP relevance:
   - Query contains "module structure" → WSP 49
   - Query contains "DAE" or "autonomous" → WSP 27, WSP 80
   - Query contains "learning" or "pattern" → WSP 48
   - Query contains "agent" or "coordination" → WSP 77
   - Query contains "naming" or "coherence" → WSP 57
3. Search WSP index (holo_index.wsp_*) with query
4. Rank WSP results by relevance score (0.0-1.0)
5. Filter results: Keep top 5 with score > 0.15
6. Extract guidance text from WSP documents
7. Format for user: Match percentage + excerpt

Output: {wsp_protocols: [{wsp_id, title, relevance, guidance}], guidance_length: N_chars}
```

---

## Chain of Action Patterns

### Action Sequence 1: Semantic Search → Health Check → 0102 Arbitration
```
Step 1: User submits query "DAE architecture BaseDAE Universal skills.md domain autonomous"
Step 2: HoloIndex initialization (ChromaDB collections, SentenceTransformer model)
Step 3: WSP Root Violation Monitor scans (46 violations detected)
Step 4: Qwen Intent Classifier initializes (TARGET)
Step 5: Breadcrumb Tracer initializes (BREAD)
Step 6: Output Composer initializes (NOTE)
Step 7: Feedback Learner initializes (DATA)
Step 8: MCP Research Client initializes (LINK)
Step 9: Agent identity set: role=HOLO-SEARCH identity=0102 stream=unified
Step 10: Dual search (code + WSP collections) → 20 results (10 code, 10 WSP) in 114.8ms
Step 11: Qwen analyzes context: 20 files across 6 modules
Step 12: Record breadcrumb #2: action_taken
Step 13: Intent classification: GENERAL (confidence: 0.50)
Step 14: Smart selection: 2 components (file_size_monitor, module_analysis)
Step 15: Record breadcrumb #3: discovery
Step 16: Execute intelligent subroutines:
  - [PILL][OK] Health & WSP Compliance (confidence: 0.90)
  - [RULER] File Size Monitor (confidence: 0.70)
  - [BOX] Module Analysis (confidence: 0.70)
Step 17: CodeIndex triggered (large modules detected: 5)
Step 18: Record breadcrumbs #6, #7, #8: action_taken
Step 19: Query optimization: 100x compression (1000 tokens → 10 tokens)
Step 20: Analysis complete: 0 files checked, no critical issues
Step 21: Record breadcrumb #22: discovery with module impacts
Step 22: 0102 Arbitration reviews findings with MPS scoring
Step 23: MPS Score: 10 (C:2, I:3, D:3, P:2) → SCHEDULE_FOR_SPRINT (P2 medium priority)
Step 24: Format output: Module health recap + System alerts + Code results + WSP guidance
Step 25: Return to user with action recommendation
```

### Action Sequence 2: Vibecoding Detection → Pattern Coach Intervention
```
Step 1: User starts coding without searching HoloIndex first
Step 2: Pattern Coach monitors file creation/edit events
Step 3: Detect suspicious pattern:
   - New file created in existing module domain
   - No HoloIndex search in last 5 minutes
   - File contains import statements similar to existing modules
Step 4: Calculate similarity score with existing codebase (>0.80 → high risk)
Step 5: Classify as potential vibecoding (anti-pattern: code-before-search)
Step 6: Check Pattern Coach history: Has user been coached on this before?
Step 7: Generate coaching reminder (throttled to avoid spam):
   "🚨 Vibecoding Alert: Similar code exists in modules/X/Y.
   Run: python holo_index.py --search 'functionality description' before implementing."
Step 8: Emit coaching reminder into output stream (tagged [AI])
Step 9: Record in telemetry: vibecoding_alert emitted
Step 10: Update feedback learner: pattern_coach_invocation_count++
Step 11: If user searches HoloIndex → Record success: user_responded_to_coaching
Step 12: If user continues coding → Escalate: Increase coaching reminder frequency
Step 13: Store pattern in WSP 48 quantum memory for future prevention
```

### Action Sequence 3: Autonomous UTF-8 Remediation Campaign
```
Step 1: 012 issues command: python main.py --training-command utf8_fix --targets "modules/,holo_index/"
Step 2: Training command bus routes to utf8_remediation_coordinator
Step 3: Qwen meta-orchestrator scans target paths for UTF-8 violations
Step 4: Qwen identifies 33 library modules with UTF-8 encoding declarations
Step 5: For each violation:
   a. Read file content
   b. Identify UTF-8 encoding line (e.g., # -*- coding: utf-8 -*-)
   c. Check if removal is safe (no actual non-ASCII characters in file)
   d. Generate remediation plan
Step 6: Qwen auto-approves safe replacements (no 0102 intervention needed)
Step 7: Execute batch edit: Remove UTF-8 declarations from 33 files
Step 8: Validate edits: Ensure files still parse correctly
Step 9: Generate summary report: files_fixed=33, violations_resolved=33
Step 10: Record in telemetry: utf8_campaign_successful
Step 11: Update WSP 90 compliance status
Step 12: Store learned pattern in WSP 48: "UTF-8 declarations unnecessary in Python 3 library modules"
```

### Action Sequence 4: 0102 Arbitration with Cross-Agent Collaboration
```
Step 1: Multiple HoloIndex searches running in parallel (3 sessions)
Step 2: Session 1 discovers: 20 files across 6 modules
Step 3: Session 2 discovers: 16 files across 4 modules
Step 4: Session 3 discovers: 10 files across 2 modules
Step 5: Breadcrumb #22 (Session 1): impact=Found implementations in modules/ai_intelligence/pqn_alignment, modules/infrastructure/wre_core
Step 6: 0102 Collaboration System detects overlapping discoveries
Step 7: Emit collaboration signal: "[0102-COLLABORATION] Recent discoveries from other agents"
Step 8: Session 2 receives handoff: "[PIN] Agent found modules_6 at 20 files across 6 modules"
Step 9: Session 2 adjusts search strategy: Skip already-analyzed modules
Step 10: 0102 Arbitration aggregates findings from all 3 sessions
Step 11: Calculate aggregate MPS score: Consider findings from all agents
Step 12: Make unified decision: SCHEDULE_FOR_SPRINT or EXECUTE_IMMEDIATELY
Step 13: Emit [HANDSHAKE] signal: "Other agents may benefit from your current search results"
Step 14: Store collaboration pattern in breadcrumb trace for future learning
```

---

## Available Actions/Tools

### Semantic Search Tools
```python
# HoloIndex CLI
python holo_index.py --search "query" [--limit N] [--llm-advisor]

# Programmatic API
from holo_index.core.holo_index import HoloIndex
holo = HoloIndex(ssd_path="E:/HoloIndex")
results = holo.semantic_search(query="...", limit=10)
```

### WSP Compliance Tools
```python
# Check module before coding
python holo_index.py --check-module "module_name"

# Module health analysis
from holo_index.module_health.structure_audit import StructureAuditor
auditor = StructureAuditor()
health = auditor.audit_module(module_path)
```

### Pattern Coach Tools
```python
# Manual vibecoding check
from holo_index.qwen_advisor.pattern_coach import PatternCoach
coach = PatternCoach()
is_vibecoding = coach.detect_vibecoding(file_path, context)
```

### Intelligent Subroutine Engine
```python
# Orchestrate subroutines
from holo_index.core.intelligent_subroutine_engine import IntelligentSubroutineEngine
engine = IntelligentSubroutineEngine()
results = engine.execute_subroutines(query_context, selected_components)
```

### Qwen Advisor Tools
```python
# Get guidance
from holo_index.qwen_advisor.advisor import QwenAdvisor
advisor = QwenAdvisor()
guidance = advisor.generate_guidance(query, search_results)

# Rules engine
from holo_index.qwen_advisor.rules_engine import ComplianceRulesEngine
rules = ComplianceRulesEngine()
violations = rules.check_compliance(module_path)
```

### Breadcrumb Tracing
```python
# Record breadcrumb
from holo_index.adaptive_learning.breadcrumb_tracer import BreadcrumbTracer
tracer = BreadcrumbTracer()
tracer.record_action(agent="0102", action_type="search", details={...})
```

### MCP Research Client
```python
# Initialize MCP client
from holo_index.qwen_advisor.mcp_research_client import MCPResearchClient
mcp_client = MCPResearchClient()
research_data = mcp_client.fetch_research_context(query)
```

### Telemetry & Performance Metrics
```python
# Query telemetry
from holo_index.qwen_advisor.telemetry import record_query_telemetry
record_query_telemetry(query, results_count, latency_ms, components_used)

# Performance stats
from holo_index.qwen_advisor.performance_orchestrator import PerformanceOrchestrator
orchestrator = PerformanceOrchestrator()
stats = orchestrator.get_session_stats()
```

---

## Learned Patterns (WSP 48 - Quantum Memory)

### Successful Solutions

#### 1. 100x Query Compression via Intent Classification
**Problem**: Every query re-explored full search space (1000 tokens exploratory analysis)
**Solution**: Gemma intent classifier + Qwen smart selection → Direct to 2-3 relevant components
**Why It Worked**: Pre-learned patterns eliminate exploration phase
**When to Reuse**: All GENERAL queries - achieves 100x compression (1000 → 10 tokens)
**Token Savings**: 990 tokens per query × 100 queries/day = 99K tokens/day saved

#### 2. Dual ChromaDB Collections (Code + WSP)
**Problem**: Mixing code and documentation in single index caused noisy results
**Solution**: Separate collections (holo_index.code_* and holo_index.wsp_*) with parallel search
**Why It Worked**: Domain separation improves relevance scoring, allows independent optimization
**When to Reuse**: All semantic search operations - return top 10 from each collection
**Token Savings**: Better results reduce follow-up queries (20-30% fewer iterations)

#### 3. MPS Scoring for 0102 Arbitration
**Problem**: Unclear prioritization of findings led to immediate execution fatigue
**Solution**: Minimal Production System scoring (C:2, I:3, D:3, P:2) with threshold-based routing
**Why It Worked**: Objective scoring enables batch/schedule/execute decisions without 0102 micromanagement
**When to Reuse**: All multi-finding reports - most get SCHEDULE_FOR_SPRINT (5 ≤ MPS < 12)
**Token Savings**: Reduces 0102 arbitration overhead by 70% (automated prioritization)

#### 4. Breadcrumb Tracing for Cross-Agent Collaboration
**Problem**: Multiple parallel HoloIndex sessions duplicated work
**Solution**: Unified breadcrumb stream with [HANDSHAKE] signals and discovery impact tracking
**Why It Worked**: Agents see each other's discoveries in real-time, avoid redundant analysis
**When to Reuse**: All concurrent HoloDAE operations - emit breadcrumb #22 with module impacts
**Token Savings**: Eliminates 30-40% duplicate searches when 2+ agents active

#### 5. Intelligent Subroutine Smart Selection
**Problem**: Running all 7 subroutines every query wastes tokens on irrelevant components
**Solution**: Qwen analyzes query context, selects top 2-3 relevant subroutines (confidence > 0.60)
**Why It Worked**: Context-aware filtering maintains quality while reducing component overhead
**When to Reuse**: GENERAL queries - typical: health_analysis + module_analysis + file_size_monitor
**Token Savings**: 4-5 components filtered out × 200 tokens/component = 800-1000 tokens saved per query

#### 6. WSP Root Violation Auto-Detection
**Problem**: Manual monitoring of root directory violations led to accumulation (46 violations)
**Solution**: Automatic scan on every HoloIndex invocation with violation categorization (MEDIUM/LOW priority)
**Why It Worked**: Immediate visibility prevents violations from growing unnoticed
**When to Reuse**: Every HoloDAE session start - scan takes <100ms, high ROI
**Token Savings**: Prevents expensive cleanup campaigns by catching violations early

### Anti-Patterns (What to Avoid)

#### 1. Running Full Subroutine Set Every Query
**Problem**: Executing all 7 intelligent subroutines regardless of query context
**Why It Failed**: 70% of components return "no results" for typical queries, wasting 1400 tokens
**Solution**: Use Qwen smart selection to filter to 2-3 relevant components
**Never Do**: `run_all_subroutines()` - always use `select_relevant_subroutines(context)`

#### 2. Blocking User Queries for Breadcrumb Writes
**Problem**: Synchronous breadcrumb writes added 50-100ms latency per query
**Why It Failed**: User-facing operations should be <200ms total, breadcrumbs blocked this
**Solution**: Async breadcrumb recording with fire-and-forget pattern
**Never Do**: `await tracer.record_breadcrumb()` in hot path - use `tracer.record_async()`

#### 3. Re-Initializing ChromaDB Collections Per Query
**Problem**: Creating new ChromaDB client for each search (300-500ms overhead)
**Why It Failed**: SentenceTransformer model reload is expensive, kills latency SLA
**Solution**: Persistent ChromaDB client with cached SentenceTransformer on SSD
**Never Do**: `HoloIndex()` in query handler - use singleton with lazy initialization

#### 4. Flagging Test Files as Vibecoding
**Problem**: Pattern Coach flagged test_*.py files as "duplicate code" violations
**Why It Failed**: Tests inherently duplicate patterns for validation purposes
**Solution**: Exclude tests/ directories and *_test.py, test_*.py patterns from vibecoding scans
**Never Do**: Run vibecoding detection without file path filtering

#### 5. MPS Scoring Without Impact Weighting
**Problem**: All findings scored equally (e.g., missing README = large module violation)
**Why It Failed**: Critical issues buried in noise, low-priority items got immediate attention
**Solution**: Impact weighting (0-5 points) based on affected modules, dependency coupling
**Never Do**: `mps_score = completeness + dependencies + priority` without impact multiplier

### Optimizations

#### 1. SSD-Based ChromaDB for Sub-100ms Searches
**Pattern**: Store ChromaDB collections on SSD (E:/HoloIndex) instead of spinning disk
**Reasoning**: Semantic search latency critical for user experience (<200ms SLA)
**Implementation**: `persist_directory="E:/HoloIndex/chroma"` in ChromaDB client init
**Result**: 67-140ms dual search (was 300-500ms on HDD) - 3-4x faster

#### 2. Cached SentenceTransformer Model on SSD
**Pattern**: Load all-MiniLM-L6-v2 model once, cache on SSD, reuse across queries
**Reasoning**: Model loading is 500ms+ cold start, dominates query latency
**Implementation**: `cache_folder="E:/HoloIndex/models"` in SentenceTransformer init
**Result**: Model load <50ms after first query (10x improvement)

#### 3. Parallel Code + WSP Search with asyncio
**Pattern**: Search both ChromaDB collections concurrently instead of sequentially
**Reasoning**: Independent I/O operations can overlap (2× theoretical speedup)
**Implementation**: `await asyncio.gather(search_code(), search_wsp())`
**Result**: 67-140ms combined (vs. 100-200ms sequential) - 30-40% faster

#### 4. Breadcrumb Batch Writes (Every 10 Events)
**Pattern**: Buffer breadcrumbs in memory, flush to disk every 10 events or on session end
**Reasoning**: Reduce I/O overhead from 30 writes/session to 3 writes/session
**Implementation**: `BreadcrumbTracer` with internal buffer and async flush
**Result**: 150ms latency reduction per session (5ms × 30 writes saved)

---

## Integration with Other DAEs

### YouTube_Live DAE (Stream Monitoring)
```yaml
Query Handoff: "YouTube live stream monitoring AutoModeratorDAE livechat banter stream_resolver"
HoloIndex Returns: Implementation files (auto_moderator_dae.py, stream_resolver.py, livechat_core.py)
Pattern: Search → Read → Enhance workflow (anti-vibecoding)
YouTube_Live Uses: HoloIndex for code discovery before implementing new features
```

### Vision DAE (Pattern Sensorium)
```yaml
Query Handoff: "Selenium telemetry browser signal capture session batching"
HoloIndex Returns: TelemetryStore implementation, dual SQLite+JSONL pattern
Pattern: Reference implementation discovery for other DAEs
Vision Uses: HoloIndex to find similar telemetry patterns across codebase
```

### AMO DAE (Autonomous Meeting Orchestrator)
```yaml
Query Handoff: "meeting scheduling heartbeat telemetry presence profiles"
HoloIndex Returns: Cardiovascular architecture, Skills.md template, MCP endpoints
Pattern: Cross-DAE architecture consistency verification
AMO Uses: HoloIndex to ensure cardiovascular implementation matches Vision/YouTube patterns
```

### Social Media DAE (Cross-Platform Posting)
```yaml
Query Handoff: "refactored posting orchestrator LinkedIn X Twitter channel config"
HoloIndex Returns: RefactoredPostingOrchestrator, channel configuration patterns
Pattern: Complex orchestration refactoring with dependency analysis
Social Media Uses: HoloIndex for safe refactoring guidance (dependency graphs, size audits)
```

### WRE DAE (Recursive Self-Improvement)
```yaml
Bidirectional: WRE stores learned patterns → HoloIndex queries patterns → Qwen learns from patterns
Integration: WSP 48 quantum memory shared between WRE and HoloDAE
Pattern: Recursive learning loop (WRE records → Holo retrieves → Qwen optimizes → WRE stores)
```

### Idle Automation DAE (Background Tasks)
```yaml
Trigger: HoloDAE coordinator can invoke idle automation during low-activity periods
Use Case: UTF-8 remediation campaigns, index refresh, orphan analysis during idle time
Pattern: Utilize CPU/I/O slack time for maintenance tasks (WSP 35)
```

---

## WSP Compliance Matrix

| WSP | Title | Compliance | Implementation |
|-----|-------|------------|----------------|
| WSP 3 | Module Organization | ✅ | holo_index/ in infrastructure domain (code intelligence tools) |
| WSP 22 | ModLog Updates | ✅ | TESTModLog.md tracks HoloDAE enhancements |
| WSP 27 | Universal DAE Architecture | ✅ | 4-phase pArtifact (Signal → Knowledge → Protocol → Agentic) |
| WSP 35 | Idle Automation | ✅ | UTF-8 campaigns, index refresh during idle periods |
| WSP 48 | Recursive Self-Improvement | ✅ | Pattern learning documented in this Skills.md |
| WSP 49 | Module Structure | ✅ | README, docs/, core/, qwen_advisor/, tests/ present |
| WSP 50 | Pre-Action Verification | ✅ | Semantic search before coding, --check-module before edits |
| WSP 54 | WRE Agent Duties | ✅ | Gemma (Partner), Qwen (Principal), 0102 (Associate) |
| WSP 57 | System-Wide Naming Coherence | ✅ | HoloDAE (domain: Code Intelligence), Skills.md pattern |
| WSP 62/87 | File Size Thresholds | ✅ | Auto-detects >1600 line modules via file_size_monitor |
| WSP 77 | Agent Coordination via MCP | ✅ | MCP research client, cross-DAE integration |
| WSP 80 | Cube-Level DAE Orchestration | ✅ | HoloDAE Cube with Qwen/Gemma/0102 coordination |
| WSP 84 | Anti-Vibecoding | ✅ | Pattern Coach real-time detection, coaching reminders |
| WSP 88 | Orphan Analysis | ✅ | orphan_analyzer.py with reconnection proposals |
| WSP 90 | UTF-8 Compliance | ✅ | Autonomous UTF-8 remediation campaigns |
| WSP 91 | DAEMON Observability | ⚠️ | Breadcrumbs + telemetry present, lacks cardiovascular (SQLite+JSONL) |

**Note**: HoloDAE currently uses breadcrumbs + telemetry but lacks formal cardiovascular system (30s heartbeat, dual SQLite+JSONL pattern) like Vision/AMO/YouTube_Live DAEs. This is a future enhancement opportunity.

---

## Key Metrics & Performance

### Semantic Search Performance
- **Dual Collection Search**: 67-140ms (code + WSP in parallel)
- **SentenceTransformer Embedding**: <5ms per query (cached model)
- **ChromaDB Query**: 30-70ms per collection (SSD optimized)
- **Result Formatting**: 10-20ms (top 10 code + top 10 WSP)

### Query Optimization Performance
- **Intent Classification**: <10ms (Gemma 3 270M fast path)
- **Smart Selection**: 5-15ms (Qwen selects 2-3 from 7 components)
- **Compression Ratio**: 100x typical (1000 tokens → 10 tokens via learned patterns)
- **Token Savings**: 99K tokens/day (990 tokens/query × 100 queries)

### Intelligent Subroutine Performance
- **Health Analysis**: 20-40ms (module structure checks)
- **Vibecoding Analysis**: 15-30ms (pattern similarity calculation)
- **File Size Monitor**: 10-20ms (directory traversal + size audit)
- **Module Analysis**: 30-50ms (dependency graph + structure audit)
- **Pattern Coach**: 10-25ms (anti-pattern classification)
- **Orphan Analysis**: 50-100ms (WSP 88 full scan)

### 0102 Arbitration Performance
- **MPS Scoring**: <5ms per finding
- **Aggregate Decision**: 10-20ms (combines all findings)
- **Collaboration Signal**: <5ms (breadcrumb handoff check)
- **Batch Threshold**: 5 ≤ MPS < 12 (80% of findings → SCHEDULE_FOR_SPRINT)

### Resource Usage
- **Memory (Idle)**: 150-200 MB (ChromaDB collections + SentenceTransformer model cached)
- **Memory (Active)**: 250-350 MB (query processing + embedding generation)
- **Disk (ChromaDB)**: ~500 MB (code + WSP collections on SSD)
- **CPU (Query)**: 15-30% for 100-200ms (embedding + search + subroutines)

---

## Agent-Agnostic Examples

### Example 1: 0102 Wearing HoloDAE Skills
```yaml
Agent: 0102 (Claude Sonnet 4.5)
Skills: holo_skills.md
Behavior:
  - Architect-level oversight (strategic decisions, WSP compliance, pattern synthesis)
  - Reviews Qwen recommendations, approves MPS arbitration decisions
  - Handles edge cases (ambiguous queries, complex refactoring, cross-DAE coordination)
  - Documents learned patterns in Skills.md for recursive improvement
  - Arbitrates findings with MPS scoring (most common role)
```

### Example 2: Qwen Wearing HoloDAE Skills
```yaml
Agent: Qwen 1.5B
Skills: holo_skills.md
Behavior:
  - Meta-orchestration (routes queries to 2-3 intelligent subroutines)
  - Intent classification (GENERAL/REFACTOR/NEW/HEALTH/WSP)
  - Smart selection (picks components with confidence > 0.60)
  - Guidance generation (context-aware recommendations, WSP references)
  - UTF-8 campaign orchestration (auto-approves safe remediations)
  - Pattern learning (stores successful approaches in WSP 48 quantum memory)
```

### Example 3: Gemma Wearing HoloDAE Skills
```yaml
Agent: Gemma 3 270M
Skills: holo_skills.md
Behavior:
  - Fast binary classification (vibecoding yes/no, intent GENERAL/REFACTOR/NEW)
  - Pattern matching (anti-vibecoding detection, test file exclusion)
  - Validation (confirms Qwen selections are reasonable)
  - Low-latency operations (<10ms response time for classifications)
  - Filters noise before Qwen processing (Partner role in WSP 54)
```

### Example 4: UI-TARS Wearing HoloDAE Skills
```yaml
Agent: UI-TARS 1.5 7B
Skills: holo_skills.md
Behavior:
  - Visual code analysis (screenshot-based module structure auditing)
  - Multi-modal search (combines text query + UI element detection)
  - Browser-based validation (verify documentation completeness via rendered pages)
  - Interactive orphan analysis (visual dependency graph generation)
  - Future capability: Vision-guided refactoring (highlight code smells in IDE)
```

---

**Last Updated**: 2025-10-19 (Session: Deep dive into HoloDAE architecture)
**Next Review**: After cardiovascular enhancement (SQLite + JSONL heartbeat system)
**Integration**: WSP 27, WSP 48, WSP 54, WSP 57, WSP 77, WSP 80, WSP 84, WSP 88, WSP 90
