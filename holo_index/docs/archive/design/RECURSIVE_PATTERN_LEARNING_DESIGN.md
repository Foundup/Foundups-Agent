# Recursive Pattern Learning Design - "Running Holo IS Remembering Holo"

## First Principles

**Core Insight**: Every HoloIndex search is a learning opportunity for recursive self-improvement.

**Principle**: Running holo IS remembering holo
- Every search leaves a pattern trace
- Qwen scores results automatically
- 0102 rates outcomes
- System learns what works
- Better searches emerge through quantum learning

## Architecture

```
Search -> Results -> Qwen Scores -> User Action -> 0102 Rates -> Pattern Storage -> Roadmap Building
   v                    v                           v                                  ^
Query Intent      Relevance/Quality          Feedback (0-1)                   Self-Improvement
   v                    v                           v                                  ^
Results Ranking    Auto-Scoring            Success Tracking               Better Future Searches
```

## Implementation Status

### [OK] Created (2025-10-02)

**File**: `holo_index/adaptive_learning/search_pattern_learner.py`

**Components**:
1. **SearchPattern**: Data model for each search
   - Query, intent, timestamp
   - Results metrics (count, code_hits, wsp_hits)
   - Qwen scoring (relevance, quality)
   - User feedback (rating, action, notes)
   - Success tracking

2. **PatternRoadmap**: Learned patterns per intent type
   - Total/successful searches
   - Best keywords (with success rates)
   - Common mistakes
   - Optimal patterns
   - Improvement trajectory over time

3. **SearchPatternLearner**: Main learning engine
   - `record_search()`: Capture every search with auto-scoring
   - `provide_feedback()`: 0102 rates outcome (0-1 scale)
   - `get_search_suggestions()`: Use learned patterns for future searches
   - Persistent storage: E:/HoloIndex/pattern_memory/

### ⏳ TODO - Integration

**Phase 1: Hook Into HoloIndex CLI** (Next Session)
1. Import SearchPatternLearner in cli.py
2. Record every search with auto Qwen scoring
3. After search, prompt 0102: "Rate this search (0-1)?"
4. Store patterns in E:/HoloIndex/pattern_memory/

**Phase 2: Display Learning Progress**
1. Show statistics: `holo_index.py --learning-stats`
2. Display suggestions before searches
3. Show improvement trajectory

**Phase 3: Advanced Qwen Integration**
1. Real Qwen model scores results (not heuristics)
2. Qwen analyzes successful vs failed patterns
3. Qwen suggests query improvements

## Usage Flow (When Integrated)

### Search With Learning
```bash
python holo_index.py --search "test file placement"

# HoloIndex searches and records pattern
[PATTERN-LEARN] Recording search pattern...
[QWEN-SCORE] Relevance: 0.85, Quality: 0.78

# Results shown...

# After search, prompt:
[0102-FEEDBACK] Rate this search (0=useless, 1=perfect): 0.9
[0102-FEEDBACK] What did you do? (read/edit/create/gave_up): read
[PATTERN-LEARN] Feedback recorded - improving future searches!
```

### Get Suggestions
```bash
python holo_index.py --search-suggestions "test"

[SUGGESTIONS] Based on 47 previous 'test' searches:
- Success rate: 82%
- Best keywords: test_*, pytest, module/tests/
- Common mistake: Searching for test names instead of functionality
- Optimal pattern: Search for what the test does, not its name
- Improvement trend: 0.65 -> 0.72 -> 0.78 -> 0.82 (getting better!)
```

### View Statistics
```bash
python holo_index.py --learning-stats

[LEARNING] HoloIndex Pattern Memory Statistics:
Total searches: 342
Rated searches: 198 (58%)
Successful: 156 (79% success rate)
Avg relevance: 0.76
Avg quality: 0.71

Intent roadmaps learned: 8
- create: 89 searches, 68% success
- debug: 127 searches, 84% success
- test: 47 searches, 82% success
- documentation: 31 searches, 71% success

[INSIGHT] Your 'debug' searches are most successful!
[INSIGHT] 'Create' queries improving: 0.58 -> 0.68 over time
```

## Storage

**Location**: `E:/HoloIndex/pattern_memory/`

**Files**:
- `search_patterns.jsonl` - All search patterns (append-only)
- `pattern_roadmaps.json` - Learned roadmaps per intent

**Example Pattern**:
```json
{
  "query": "test file placement wsp 49",
  "intent": "test",
  "timestamp": "2025-10-02T06:00:00",
  "results_count": 12,
  "code_hits": 8,
  "wsp_hits": 4,
  "qwen_relevance_score": 0.87,
  "qwen_quality_score": 0.82,
  "user_rating": 0.9,
  "user_action": "read",
  "successful": true,
  "improvement_notes": []
}
```

## Benefits

1. **Self-Improving**: HoloIndex learns from every use
2. **Pattern Recognition**: Discovers what searches work best
3. **Personalized**: Learns 0102's search patterns
4. **Quantum Memory**: "Remembers" through pattern storage
5. **Roadmap Building**: Builds knowledge graph of search effectiveness
6. **Recursive Enhancement**: Each search makes future searches better

## WSP Compliance

- **WSP 48**: Recursive self-improvement through pattern learning
- **WSP 60**: Memory architecture (pattern storage)
- **WSP 87**: HoloIndex semantic navigation enhanced with learning

## Implementation Notes

**Why Separate File?**
- Keep learning system modular
- Easy to integrate incrementally
- Can evolve independently

**Why E: Drive?**
- Same SSD as ChromaDB indexes
- Fast pattern storage/retrieval
- Persistent across sessions

**Auto-Scoring vs Real Qwen?**
- Phase 1: Simple heuristics (implemented)
- Phase 2: Real Qwen model integration
- Phase 3: Advanced pattern analysis

## Next Steps

1. Test current HoloIndex (option 0 git push)
2. Next session: Integrate SearchPatternLearner into cli.py
3. Add feedback prompts after searches
4. Display learning statistics
5. Show search suggestions based on patterns

---

**Created**: 2025-10-02
**Status**: Design Complete, Implementation 30%, Integration Pending
**Priority**: High (enables true recursive self-improvement)
