# Sprint 2: Context & Transfer - Implementation Tickets

**Objective**: Add context enrichment (P1-F: Agentic RAG) + cross-skill transfer (P1-C: Graph edges)
**Target**: 80% of executions include retrieval with relevance checks
**Duration**: 1 week
**Depends On**: Sprint 1 complete (ReAct + TT-SI)

---

## Ticket 2.1: Agentic RAG Pre-Execution Hook

**Priority**: P1 | **Estimate**: 4h | **Owner**: 0102

### Problem
Skills run with insufficient context. Retrieval exists (HoloIndex) but is not consistently inserted as a first-class execution step. Agent doesn't choose when/how to retrieve or validate quality.

### Target Files
| File | Action |
|------|--------|
| `modules/infrastructure/wre_core/wre_master_orchestrator/src/wre_master_orchestrator.py` | ADD retrieval preflight |
| `modules/infrastructure/wre_core/src/pattern_memory.py` | ADD retrieval quality tracking |

### Implementation Steps

#### Step 2.1.1: Add retrieval quality table to PatternMemory

In `_initialize_schema()`, after telemetry_counters table:

```python
# Retrieval quality tracking (Sprint 2 - Agentic RAG)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS retrieval_quality (
        retrieval_id TEXT PRIMARY KEY,
        execution_id TEXT NOT NULL,
        skill_name TEXT NOT NULL,
        query TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        results_count INTEGER,
        relevance_score REAL,
        used_in_execution INTEGER DEFAULT 0,
        retrieval_time_ms INTEGER
    )
""")
```

#### Step 2.1.2: Add retrieval tracking methods to PatternMemory

```python
def record_retrieval(
    self,
    retrieval_id: str,
    execution_id: str,
    skill_name: str,
    query: str,
    results_count: int,
    relevance_score: float,
    retrieval_time_ms: int
) -> None:
    """Record retrieval event for quality tracking."""
    cursor = self.conn.cursor()
    cursor.execute("""
        INSERT INTO retrieval_quality (
            retrieval_id, execution_id, skill_name, query,
            timestamp, results_count, relevance_score, retrieval_time_ms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        retrieval_id, execution_id, skill_name, query,
        datetime.now().isoformat(), results_count, relevance_score, retrieval_time_ms
    ))
    self.conn.commit()

def get_retrieval_stats(self, skill_name: str, days: int = 7) -> Dict:
    """Get retrieval quality stats for a skill."""
    cursor = self.conn.cursor()
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    cursor.execute("""
        SELECT
            COUNT(*) as total_retrievals,
            AVG(relevance_score) as avg_relevance,
            AVG(results_count) as avg_results,
            AVG(retrieval_time_ms) as avg_time_ms
        FROM retrieval_quality
        WHERE skill_name = ? AND timestamp >= ?
    """, (skill_name, cutoff))
    row = cursor.fetchone()
    return dict(row) if row else {}
```

#### Step 2.1.3: Add retrieval preflight to execute_skill

In `execute_skill()`, after Step 2.5 (A/B routing), add Step 2.6:

```python
# Step 2.6: Agentic RAG pre-execution (Sprint 2 - Gap F)
retrieval_context = None
retrieval_relevance = 0.0
if self.sqlite_memory and os.getenv("WRE_AGENTIC_RAG", "1").strip() == "1":
    try:
        retrieval_start = datetime.now()

        # Build retrieval query from skill + input context
        query = f"{skill_name} {json.dumps(input_context)[:200]}"

        # Retrieve from HoloIndex
        from holo_index.qwen_advisor.orchestration.autonomous_refactoring import (
            AutonomousRefactoringOrchestrator
        )
        holo = AutonomousRefactoringOrchestrator(self.repo_root)
        results = holo.search_codebase(query, limit=3)

        retrieval_time_ms = int((datetime.now() - retrieval_start).total_seconds() * 1000)

        # Calculate relevance score (simple heuristic)
        if results:
            retrieval_relevance = min(1.0, len(results) / 3.0)
            retrieval_context = {
                "retrieved_files": [r.get("path", "") for r in results[:3]],
                "relevance_score": retrieval_relevance
            }

            # Record retrieval
            retrieval_id = f"ret_{execution_id[:8]}"
            self.sqlite_memory.record_retrieval(
                retrieval_id=retrieval_id,
                execution_id=execution_id,
                skill_name=skill_name,
                query=query[:500],
                results_count=len(results),
                relevance_score=retrieval_relevance,
                retrieval_time_ms=retrieval_time_ms
            )

            # Inject into input context
            input_context["_retrieval_context"] = retrieval_context

            self.sqlite_memory.increment_counter("rag_retrievals")
            if retrieval_relevance >= 0.5:
                self.sqlite_memory.increment_counter("rag_high_relevance")

        logger.info(
            f"[WRE-RAG] Retrieved {len(results)} results for {skill_name}, "
            f"relevance={retrieval_relevance:.2f}"
        )

    except Exception as exc:
        logger.warning(f"[WRE-RAG] Retrieval failed: {exc}")
```

### Acceptance Criteria
- [ ] `retrieval_quality` table created
- [ ] Retrieval happens before skill execution
- [ ] Relevance score calculated and stored
- [ ] Context injected into `input_context["_retrieval_context"]`
- [ ] Telemetry: `rag_retrievals`, `rag_high_relevance` counters

---

## Ticket 2.2: Graph Edges for Cross-Skill Transfer

**Priority**: P1 | **Estimate**: 4h | **Owner**: 0102

### Problem
Learning from one skill does not reliably transfer to related skills. Flat outcome records without explicit cross-skill causal edges.

### Target Files
| File | Action |
|------|--------|
| `modules/infrastructure/wre_core/src/pattern_memory.py` | ADD graph edge storage |

### Implementation Steps

#### Step 2.2.1: Add skill_edges table

In `_initialize_schema()`:

```python
# Skill relationship edges (Sprint 2 - Graph-of-Thought)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS skill_edges (
        edge_id TEXT PRIMARY KEY,
        source_skill TEXT NOT NULL,
        target_skill TEXT NOT NULL,
        edge_type TEXT NOT NULL,
        weight REAL DEFAULT 1.0,
        created_at TEXT NOT NULL,
        evidence TEXT
    )
""")

cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_skill_edges_source
    ON skill_edges(source_skill)
""")

cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_skill_edges_target
    ON skill_edges(target_skill)
""")
```

#### Step 2.2.2: Add edge management methods

```python
# ------------------------------------------------------------------ #
#  Graph-of-Thought Edges (Sprint 2 - Cross-Skill Transfer)          #
# ------------------------------------------------------------------ #

def add_skill_edge(
    self,
    source_skill: str,
    target_skill: str,
    edge_type: str,
    weight: float = 1.0,
    evidence: Optional[str] = None
) -> str:
    """
    Add edge between skills for knowledge transfer.

    Edge types:
    - caused_by: source caused target to fail/succeed
    - improved_by: source improvement helped target
    - similar_to: skills share patterns
    - depends_on: source depends on target
    """
    import uuid
    edge_id = f"edge_{uuid.uuid4().hex[:8]}"
    cursor = self.conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO skill_edges (
            edge_id, source_skill, target_skill, edge_type,
            weight, created_at, evidence
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        edge_id, source_skill, target_skill, edge_type,
        weight, datetime.now().isoformat(), evidence
    ))
    self.conn.commit()
    logger.info(
        f"[PATTERN-MEMORY] Added edge {source_skill} --{edge_type}--> {target_skill}"
    )
    return edge_id

def get_related_skills(
    self,
    skill_name: str,
    edge_types: Optional[List[str]] = None,
    min_weight: float = 0.5
) -> List[Dict]:
    """Get skills related to source skill via edges."""
    cursor = self.conn.cursor()

    if edge_types:
        placeholders = ",".join(["?"] * len(edge_types))
        cursor.execute(f"""
            SELECT * FROM skill_edges
            WHERE source_skill = ?
              AND edge_type IN ({placeholders})
              AND weight >= ?
            ORDER BY weight DESC
        """, (skill_name, *edge_types, min_weight))
    else:
        cursor.execute("""
            SELECT * FROM skill_edges
            WHERE source_skill = ?
              AND weight >= ?
            ORDER BY weight DESC
        """, (skill_name, min_weight))

    return [dict(row) for row in cursor.fetchall()]

def get_skill_graph(self, skill_name: str, depth: int = 2) -> Dict:
    """
    Get skill subgraph centered on skill_name.

    Returns nodes and edges for visualization/analysis.
    """
    visited = set()
    nodes = []
    edges = []

    def traverse(skill: str, current_depth: int):
        if skill in visited or current_depth > depth:
            return
        visited.add(skill)
        nodes.append({"id": skill, "depth": current_depth})

        related = self.get_related_skills(skill)
        for rel in related:
            edges.append({
                "source": rel["source_skill"],
                "target": rel["target_skill"],
                "type": rel["edge_type"],
                "weight": rel["weight"]
            })
            traverse(rel["target_skill"], current_depth + 1)

    traverse(skill_name, 0)
    return {"nodes": nodes, "edges": edges}

def transfer_learning(
    self,
    source_skill: str,
    target_skill: str
) -> Optional[Dict]:
    """
    Transfer successful patterns from source to target skill.

    Returns transferred pattern info or None if no transferable patterns.
    """
    # Find successful patterns from source
    source_successes = self.recall_successful_patterns(source_skill, min_fidelity=0.90, limit=3)

    if not source_successes:
        return None

    # Check if skills are related
    edges = self.get_related_skills(source_skill, edge_types=["similar_to", "improved_by"])
    target_related = any(e["target_skill"] == target_skill for e in edges)

    if not target_related:
        # Create similarity edge based on pattern overlap
        self.add_skill_edge(
            source_skill=source_skill,
            target_skill=target_skill,
            edge_type="similar_to",
            weight=0.5,
            evidence="Auto-detected during transfer_learning"
        )

    return {
        "source_skill": source_skill,
        "target_skill": target_skill,
        "patterns_transferred": len(source_successes),
        "best_source_fidelity": source_successes[0]["pattern_fidelity"]
    }
```

#### Step 2.2.3: Auto-create edges on successful evolution

In `wre_master_orchestrator.py`, after variation promotion in Step 7.5:

```python
# Auto-create improvement edge
if winner == 'treatment':
    # ... existing promotion code ...

    # Sprint 2: Create improvement edge
    self.sqlite_memory.add_skill_edge(
        source_skill=skill_name,
        target_skill=skill_name,
        edge_type="improved_by",
        weight=pattern_fidelity,
        evidence=f"Variation {active_test['treatment_version']} promoted"
    )
```

### Acceptance Criteria
- [ ] `skill_edges` table created with indexes
- [ ] `add_skill_edge()` supports 4 edge types
- [ ] `get_related_skills()` filters by type and weight
- [ ] `get_skill_graph()` traverses to depth 2
- [ ] `transfer_learning()` finds and applies patterns
- [ ] Auto-edge creation on promotion

---

## Ticket 2.3: Retrieval Quality Dashboard Extension

**Priority**: P1 | **Estimate**: 2h | **Owner**: 0102

### Problem
No visibility into retrieval effectiveness across skills.

### Target Files
| File | Action |
|------|--------|
| `modules/infrastructure/wre_core/src/pattern_memory.py` | EXTEND dashboard |

### Implementation Steps

#### Step 2.3.1: Extend get_telemetry_dashboard()

Add retrieval and graph metrics:

```python
def get_telemetry_dashboard(self) -> Dict:
    """Get telemetry dashboard with Sprint 1 + Sprint 2 metrics."""
    # ... existing Sprint 1 code ...

    # Sprint 2: Retrieval metrics
    cursor.execute("""
        SELECT
            COUNT(*) as total_retrievals,
            AVG(relevance_score) as avg_relevance,
            SUM(CASE WHEN relevance_score >= 0.5 THEN 1 ELSE 0 END) as high_relevance_count
        FROM retrieval_quality
    """)
    row = cursor.fetchone()
    retrieval_total = row['total_retrievals'] or 0
    high_relevance = row['high_relevance_count'] or 0
    retrieval_coverage = high_relevance / max(retrieval_total, 1)

    # Sprint 2: Graph metrics
    cursor.execute("SELECT COUNT(*) as edge_count FROM skill_edges")
    edge_count = cursor.fetchone()['edge_count'] or 0

    cursor.execute("""
        SELECT COUNT(DISTINCT source_skill) as connected_skills
        FROM skill_edges
    """)
    connected_skills = cursor.fetchone()['connected_skills'] or 0

    return {
        # Sprint 1
        "retry_count": counters.get("react_retry_count", 0),
        "total_executions": counters.get("total_executions", 0),
        "variation_win_rate": round(win_rate, 3),
        "avg_fidelity_delta": round(avg_delta, 3),
        "variations_tested": total_tested,
        "variations_promoted": promoted,

        # Sprint 2
        "retrieval_coverage": round(retrieval_coverage, 3),
        "avg_retrieval_relevance": round(row['avg_relevance'] or 0, 3),
        "total_retrievals": retrieval_total,
        "skill_edges": edge_count,
        "connected_skills": connected_skills
    }
```

### Acceptance Criteria
- [ ] Dashboard includes `retrieval_coverage`, `avg_retrieval_relevance`
- [ ] Dashboard includes `skill_edges`, `connected_skills`
- [ ] 80% retrieval coverage target trackable

---

## Sprint 2 Execution Order

```
2.2.1 → 2.1.1 → 2.2.2 → 2.1.2 → 2.3.1 → 2.1.3 → 2.2.3
   ↓       ↓       ↓       ↓       ↓       ↓       ↓
 edges  retrieval edge    retrieval dash   RAG    auto
 table   table   methods  methods  extend  hook   edge
```

**Rationale**: Schema first, then methods, then wiring. Edge table before retrieval since edge methods are simpler to validate.

---

## Validation Plan

### Unit Tests
```python
# test_agentic_rag.py
def test_retrieval_recorded():
    """Verify retrieval events are stored."""

def test_retrieval_context_injected():
    """Verify _retrieval_context appears in input_context."""

def test_relevance_score_calculation():
    """Verify relevance heuristic works."""

# test_skill_edges.py
def test_add_edge():
    """Verify edge creation."""

def test_get_related_skills():
    """Verify edge traversal."""

def test_transfer_learning():
    """Verify pattern transfer works."""
```

### Integration Test
```bash
WRE_AGENTIC_RAG=1 python -c "
from modules.infrastructure.wre_core.wre_master_orchestrator import WREMasterOrchestrator
m = WREMasterOrchestrator()
result = m.execute_skill('qwen_gitpush', 'qwen', {'files': ['test.py']})
print('Retrieval context:', result.get('result', {}).get('_retrieval_context'))
"
```

---

## Success Metrics (CTO Gate)

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Retrieval coverage | 0% | 80% | `retrieval_coverage` from dashboard |
| Avg relevance | N/A | >= 0.5 | `avg_retrieval_relevance` |
| Cross-skill edge reuse | 0 | >10 edges | `skill_edges` count |
| First-pass fidelity improvement | baseline | +10% | Compare with/without transfer |

---

*Created: 2026-02-24 | Sprint 2 of WRE CoT Closure*
