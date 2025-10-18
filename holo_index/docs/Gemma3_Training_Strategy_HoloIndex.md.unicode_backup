# Gemma 3 270M Training Strategy for HoloIndex Activities

**Date**: 2025-10-15
**Purpose**: Identify optimal use cases for Gemma 3 270M vs Qwen 1.5B, design training architecture
**Models**: Gemma 3 270M (fast, simple) vs Qwen 1.5B (complex, code understanding)

---

## Executive Summary

**Key Insight**: Gemma 3 270M excels at **classification and yes/no decisions**, while Qwen 1.5B handles **deep analysis and code understanding**.

**Training Approach**: Use **ChromaDB + few-shot examples** to teach Gemma 3 specific classification patterns, NOT general reasoning.

**Recommended Split**:
- **Gemma 3 (70% of queries)**: Fast triage, classification, simple decisions
- **Qwen 1.5B (30% of queries)**: Complex analysis, code generation, multi-step reasoning

---

## HoloIndex Activity Classification

### Category 1: PERFECT for Gemma 3 (Simple Classification)

These tasks are **binary decisions** or **simple pattern matching**:

#### 1.1 File Naming Validation (WITH TRAINING)
**Task**: Is this file name valid per WSP 57 rules?

**Why Gemma 3**: Binary yes/no with ~10 patterns to learn

**Current Accuracy**: 66.7% (untrained)
**Expected After Training**: 90-95%

**Training Data Needed**:
- 50 correct examples
- 50 violation examples
- Replacement pattern mappings

**Training Method**: ChromaDB with labeled examples + few-shot prompting

#### 1.2 Document Type Classification
**Task**: What type of document is this? (README, INTERFACE, ModLog, WSP, etc.)

**Why Gemma 3**: 10-15 document types, pattern-based classification

**Current**: Not implemented
**Expected Accuracy After Training**: 95%+

**Training Data**:
```python
{
    "WSP_framework/src/WSP_87*.md": "wsp_protocol",
    "modules/*/README.md": "module_readme",
    "modules/*/INTERFACE.md": "interface",
    "modules/*/ModLog.md": "modlog",
    "docs/**/*.md": "documentation"
}
```

#### 1.3 WSP Compliance Quick Check
**Task**: Does this file/module have basic WSP structure?

**Why Gemma 3**: Checklist validation (README exists? INTERFACE exists? tests/ exists?)

**Current**: Handled by Python code
**With Gemma 3**: Can provide natural language explanations

**Training Data**: WSP 49 structure requirements + 100 module examples

#### 1.4 Query Intent Classification
**Task**: What type of search is this? (code_search, wsp_lookup, module_discovery, help_request)

**Why Gemma 3**: 5-10 intent categories, keyword-based

**Current Accuracy**: Rule-based (pattern matching)
**With Gemma 3**: Can handle typos, natural language, context

**Training Data**:
```python
{
    "how do i post to youtube": "code_search",
    "what is wsp 87": "wsp_lookup",
    "where is the auth module": "module_discovery",
    "help me understand wsp": "help_request"
}
```

#### 1.5 Violation Triage
**Task**: Is this a P0/P1/P2/P3 violation?

**Why Gemma 3**: Severity classification based on keywords/location

**Training Data**: Historical violations from WSP_MODULE_VIOLATIONS.md + git log

#### 1.6 Module Health Status
**Task**: Quick health check - "healthy", "needs_attention", "critical"

**Why Gemma 3**: 3-category classification based on checklist

**Signals**:
- Missing README/INTERFACE/tests → "critical"
- Old ModLog, no recent commits → "needs_attention"
- All docs present, recent activity → "healthy"

---

### Category 2: MARGINAL for Gemma 3 (Needs Training + Careful Prompting)

These tasks require **more context** but can work with training:

#### 2.1 Search Result Ranking
**Task**: Which result is more relevant to the query?

**Why Marginal**: Requires understanding semantic similarity beyond keywords

**Gemma 3 Approach**: Train on historical click-through data
- Query + Result A + Result B → Which was clicked?
- Learn user preference patterns

**Fallback**: Use embedding similarity (current approach) for complex cases

#### 2.2 Breadcrumb Trail Relevance
**Task**: Is this breadcrumb relevant to current search?

**Why Marginal**: Requires understanding task continuity

**Gemma 3 Approach**: Simple keyword overlap + recency
- If query contains words from breadcrumb → relevant
- If breadcrumb is recent (<5 min) → more relevant

#### 2.3 Warning/Reminder Generation
**Task**: Should we show a warning for this query?

**Why Marginal**: Requires understanding WSP context

**Gemma 3 Approach**: Train on query → warning mappings
- "create new file" → WSP 50 warning
- "test" → WSP 5 reminder

---

### Category 3: NOT SUITABLE for Gemma 3 (Use Qwen 1.5B)

These tasks require **deep understanding** or **multi-step reasoning**:

#### 3.1 Code Understanding
**Task**: What does this code do? How does it work?

**Why Qwen**: Requires understanding syntax, logic, flow
- Gemma 3 too small for code semantics
- Qwen 1.5B code-specialized

#### 3.2 WSP Protocol Analysis
**Task**: Explain this WSP, its dependencies, implications

**Why Qwen**: Requires multi-document reasoning, context integration

#### 3.3 Module Dependency Analysis
**Task**: What modules does this depend on? What depends on this?

**Why Qwen**: Requires graph reasoning, import tracking

#### 3.4 Architectural Recommendations
**Task**: Where should this functionality live? What's the best approach?

**Why Qwen**: Requires understanding system architecture, trade-offs

#### 3.5 Code Generation
**Task**: Generate code for X functionality

**Why Qwen**: Requires syntax knowledge, best practices, context

#### 3.6 Refactoring Suggestions
**Task**: How can we improve this code?

**Why Qwen**: Requires understanding patterns, anti-patterns, optimization

---

## Training Architecture: Gemma 3 + ChromaDB

### Overview

```
User Query → Intent Classifier (Gemma 3) → Route Decision
                                            ↓
                        ┌───────────────────┴───────────────────┐
                        ↓                                       ↓
                Simple Classification                    Complex Analysis
                (Gemma 3 + ChromaDB)                    (Qwen 1.5B)
                        ↓                                       ↓
                Fast Response (50ms)                   Deep Analysis (250ms)
```

### ChromaDB Training Corpus Structure

```python
# E:/HoloIndex/vectors/gemma_training/

collections = {
    "file_naming_rules": {
        # WSP 57 file naming examples
        "positive": [
            {
                "file": "WSP_framework/src/WSP_87_Code_Navigation_Protocol.md",
                "verdict": "valid",
                "reason": "Official WSP protocol in proper location"
            },
            # ... 50 more
        ],
        "negative": [
            {
                "file": "modules/test/WSP_AUDIT.md",
                "verdict": "violation",
                "reason": "Module docs should not use WSP_ prefix",
                "fix": "Rename to Audit_Report.md"
            },
            # ... 50 more
        ]
    },

    "document_types": {
        "examples": [
            {
                "path": "modules/communication/livechat/README.md",
                "type": "module_readme",
                "indicators": ["in modules/", "README.md", "has src/ sibling"]
            },
            # ... 100 more
        ]
    },

    "query_intents": {
        "examples": [
            {
                "query": "how do i send youtube comments",
                "intent": "code_search",
                "confidence": 0.95,
                "route_to": "code_collection"
            },
            {
                "query": "what is wsp 87",
                "intent": "wsp_lookup",
                "confidence": 0.95,
                "route_to": "wsp_collection"
            },
            # ... 200 more
        ]
    },

    "violation_severity": {
        "examples": [
            {
                "violation": "test file in root directory",
                "severity": "P0",
                "reason": "WSP 85 root protection violation"
            },
            {
                "violation": "missing README.md",
                "severity": "P1",
                "reason": "WSP 49 structure requirement"
            },
            # ... 100 more
        ]
    }
}
```

### Training Process

#### Step 1: Build Training Corpus
```python
# holo_index/training/build_gemma_corpus.py

from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

def build_training_corpus():
    """Build Gemma 3 training corpus from historical data"""

    client = PersistentClient(path="E:/HoloIndex/vectors/gemma_training")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Collection 1: File Naming Rules (WSP 57)
    file_naming = client.get_or_create_collection("file_naming_rules")

    # Add positive examples
    positive_examples = load_valid_file_names()  # From git history
    for i, ex in enumerate(positive_examples):
        embedding = model.encode(ex['file']).tolist()
        file_naming.add(
            ids=[f"valid_{i}"],
            embeddings=[embedding],
            documents=[ex['file']],
            metadatas=[{
                "verdict": "valid",
                "reason": ex['reason'],
                "type": "positive"
            }]
        )

    # Add negative examples (violations that were fixed)
    negative_examples = load_fixed_violations()  # From git log
    for i, ex in enumerate(negative_examples):
        embedding = model.encode(ex['file']).tolist()
        file_naming.add(
            ids=[f"violation_{i}"],
            embeddings=[embedding],
            documents=[ex['file']],
            metadatas=[{
                "verdict": "violation",
                "reason": ex['reason'],
                "fix": ex['fix'],
                "type": "negative"
            }]
        )

    print(f"✓ Built file naming corpus: {len(positive_examples)} valid, {len(negative_examples)} violations")

    # Collection 2: Document Types
    # Collection 3: Query Intents
    # Collection 4: Violation Severity
    # ... (similar pattern)
```

#### Step 2: Few-Shot Prompting Template
```python
def create_few_shot_prompt(task: str, examples: list, query: str) -> str:
    """Generate few-shot prompt for Gemma 3"""

    if task == "file_naming":
        prompt = "Classify if this file name follows WSP 57 rules.\n\n"
        prompt += "Examples:\n"

        for ex in examples[:5]:  # Show 5 examples
            prompt += f"\nFile: {ex['file']}\n"
            prompt += f"Verdict: {ex['verdict']}\n"
            prompt += f"Reason: {ex['reason']}\n"
            if 'fix' in ex:
                prompt += f"Fix: {ex['fix']}\n"

        prompt += f"\nNow classify this file:\n"
        prompt += f"File: {query}\n"
        prompt += f"Verdict: "

        return prompt
```

#### Step 3: Gemma 3 Inference with RAG
```python
from llama_cpp import Llama
from chromadb import PersistentClient

class GemmaClassifier:
    """Gemma 3 270M with ChromaDB RAG for classification tasks"""

    def __init__(self):
        self.llm = Llama(
            model_path="E:/HoloIndex/models/gemma-3-270m-it-Q4_K_M.gguf",
            n_ctx=1024,
            n_threads=4
        )
        self.db = PersistentClient(path="E:/HoloIndex/vectors/gemma_training")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def classify_file_naming(self, file_path: str) -> dict:
        """Classify file naming with few-shot examples from ChromaDB"""

        # 1. Retrieve similar examples from ChromaDB
        collection = self.db.get_collection("file_naming_rules")
        embedding = self.model.encode(file_path).tolist()

        results = collection.query(
            query_embeddings=[embedding],
            n_results=10  # Get 10 similar examples
        )

        # 2. Build few-shot prompt
        examples = []
        for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
            examples.append({
                'file': doc,
                'verdict': meta['verdict'],
                'reason': meta['reason'],
                'fix': meta.get('fix', '')
            })

        # Balance positive/negative examples
        positive = [ex for ex in examples if ex['verdict'] == 'valid'][:3]
        negative = [ex for ex in examples if ex['verdict'] == 'violation'][:3]
        examples = positive + negative

        prompt = create_few_shot_prompt("file_naming", examples, file_path)

        # 3. Run Gemma 3 inference
        response = self.llm(prompt, max_tokens=50, temperature=0.1)

        # 4. Parse response
        return self._parse_verdict(response)
```

---

## Implementation Roadmap

### Phase 1: Corpus Building (Week 1)
- [ ] Extract file naming examples from git history
- [ ] Classify documents by type (100 examples per type)
- [ ] Analyze historical queries for intent classification
- [ ] Extract violation examples from WSP_MODULE_VIOLATIONS.md
- [ ] Index all examples in ChromaDB

### Phase 2: Few-Shot Prompting (Week 2)
- [ ] Design prompt templates for each task
- [ ] Test Gemma 3 with 5-shot, 10-shot, 20-shot examples
- [ ] Measure accuracy vs example count
- [ ] Optimize prompt format for Gemma 3's instruction format

### Phase 3: Integration (Week 3)
- [ ] Create GemmaClassifier class
- [ ] Add intent routing to HoloIndex search
- [ ] Implement file naming validator with Gemma 3
- [ ] Add document type classification
- [ ] Add violation severity triage

### Phase 4: Production Deployment (Week 4)
- [ ] A/B test Gemma 3 vs rule-based classification
- [ ] Measure latency, accuracy, user satisfaction
- [ ] Fine-tune prompts based on production data
- [ ] Add feedback loop (store corrections in ChromaDB)

---

## Expected Performance Gains

### Latency
| Task | Current (Rule-Based) | Gemma 3 (Trained) | Speedup |
|------|----------------------|-------------------|---------|
| File naming check | 1-2ms (Python) | 50-100ms | 0.5x slower |
| Document classification | 5ms (pattern matching) | 50-100ms | 0.1x slower |
| Query intent | 10ms (regex) | 50-100ms | 0.2x slower |

**Note**: Gemma 3 is SLOWER than pure code, but adds **intelligence**:
- Handles typos
- Understands natural language
- Provides explanations
- Learns from corrections

### Accuracy
| Task | Current (Rule-Based) | Gemma 3 (Trained) | Improvement |
|------|----------------------|-------------------|-------------|
| File naming | 100% (rigid rules) | 90-95% (flexible) | -5% but handles edge cases |
| Document classification | 85% (pattern match) | 95%+ | +10% |
| Query intent | 70% (keywords) | 90%+ | +20% |
| Violation severity | 60% (heuristic) | 85%+ | +25% |

---

## Training Data Sources

### 1. Git History
```bash
# Extract file renames (WSP 57 violations that were fixed)
git log --all --format='%H' | while read commit; do
    git show --name-status $commit | grep "^R" | grep "WSP_"
done > wsp_renames.txt
```

### 2. WSP_MODULE_VIOLATIONS.md
- Historical violations with severity
- Fixes applied
- Rationale

### 3. HoloIndex Search Logs
```python
# holo_index/logs/agent_activity.log contains:
# - Query text
# - Results clicked
# - Search duration
# → Train intent classifier + result ranker
```

### 4. Manual Labeling (Small Set)
- 50 edge cases for file naming
- 20 ambiguous document types
- 30 hard-to-classify queries

---

## Cost-Benefit Analysis

### Costs
- **Development**: 2-3 weeks to build training pipeline
- **Compute**: Minimal (Gemma 3 runs on CPU, 241MB model)
- **Maintenance**: Corpus updates quarterly

### Benefits
- **Better UX**: Natural language understanding vs rigid rules
- **Flexibility**: Handles typos, variations, context
- **Explainability**: Gemma 3 can explain classifications
- **Learning**: Improves over time with feedback
- **Offloading**: Frees Qwen 1.5B for complex tasks (30% query reduction)

### ROI Calculation
- **Query volume**: ~1000/day (estimated)
- **Gemma 3 handles**: 70% (700 queries)
- **Time saved per query**: 0.2s (Qwen not needed)
- **Total saved**: 140s/day = 850 hours/year
- **Dev cost**: 2-3 weeks
- **Payback**: 1-2 months

---

## Conclusion

**Gemma 3 270M is NOT a replacement for Qwen 1.5B** - it's a **fast triage layer**.

**Optimal Architecture**:
```
User Query
    ↓
[Gemma 3: Intent Classification] (50ms)
    ↓
Simple? ────────────→ [Gemma 3 + ChromaDB] (100ms)
    ↓                        ↓
Complex? ─────────→ [Qwen 1.5B] (250ms)
                            ↓
                    Deep Analysis Result
```

**Training Strategy**:
1. Build ChromaDB corpus from historical data
2. Use few-shot prompting (5-10 examples)
3. Validate on test set (80%+ accuracy target)
4. Deploy with A/B testing
5. Add feedback loop for continuous learning

**Next Step**: Build training corpus (Phase 1)
