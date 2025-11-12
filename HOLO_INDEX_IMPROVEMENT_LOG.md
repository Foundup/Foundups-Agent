# HoloIndex Improvement Log - 2025-11-10

## Micro Sprint – 2025-11-11: Restore WSP 87 Search Output

- **Issue**: `python holo_index.py --search ...` always printed `[NO SOLUTION FOUND]` even when hits existed. Root cause was the WSP-HOLO-REBUILD renaming the search payload keys to `code_hits` / `wsp_hits` while the CLI/throttler still consumed `code` / `wsps`, so downstream prompts never saw any results.
- **Fix**: `holo_index/core/holo_index.py:405-452` now returns both naming schemes (legacy + modern) so 0102’s CLI, Qwen advisor, and telemetry stay in sync without vibecoding new adapters. This keeps WSP 87 compliance by surfacing existing solutions again.
- **Verification**:
  ```bash
  python holo_index.py --search "handle item classification" --limit 3 --verbose
  ```
  Output now includes `[CODE]` entries for GotJunk handlers before any WSP reminders fire.

## Micro Sprint – 2025-11-11: TypeScript Entity Extraction & Previews

- **Issue**: NAVIGATION entries pointing at `.tsx` handlers (e.g., `App.tsx:handleClassify()`) never produced previews because the location string lacked line numbers and the promised `_extract_typescript_entities` helper didn’t exist.
- **Fix**: Implemented TypeScript entity parsing + caching in `holo_index/core/holo_index.py` (new `_extract_typescript_entities`, `_match_typescript_entity`, `_resolve_location_parts`) and updated `_enhance_code_results_with_previews` to resolve file paths, derive line numbers, and fall back to entity snippets for hooks/components/state variables.
- **Tests**: Added `holo_index/tests/test_typescript_entities.py` to cover components, hooks, interfaces, and state setters so the heuristics stay stable.
- **Verification**:
  ```bash
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest holo_index/tests/test_typescript_entities.py
  python holo_index.py --search "handle item classification" --limit 3 --verbose
  ```
  Search output now shows `[GREEN] [SOLUTION FOUND]` with populated previews for GotJunk flows.

## Micro Sprint – 2025-11-12: Holo vs Grep Validation

- **Issue**: 0102 agents still questioned whether HoloIndex truly replaces ripgrep/glob workflows.
- **Fix**: Added integration suite `holo_index/tests/test_holo_vs_grep.py` comparing semantic (`"PQN module in youtube dae"`) and literal (`"pendingClassificationItem"`) queries across Holo vs `rg`. Tests prove Holo finds semantic matches + TSX previews where grep returns nothing, while matching literal symbols equally well.
- **Verification**:
  ```bash
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest holo_index/tests/test_holo_vs_grep.py -k semantic
  ```
- **Bonus Tooling**: `scripts/holo_vs_grep_benchmark.py` now runs the same queries interactively, printing hit counts, timings, and preview snippets so 0102 can demo the advantage live.

## Micro Sprint – 2025-11-12: 012 Pattern Ingestion Pipeline

- **Issue**: 012’s directives were trapped in plain text; Gemma/Qwen couldn’t reuse them.
- **Fix**: Added `scripts/ingest_012_patterns.py`, which parses `012.txt`, stores high-signal blocks into `holo_index/qwen_advisor/pattern_memory.PatternMemory`, and exports Qwen task seeds to `holo_index/memory/012_pattern_tasks.json`. Running `python scripts/ingest_012_patterns.py --max 20` now loads 20 actionable patterns automatically.
- **Impact**: Gemma can mine 012 instructions locally, while Qwen/AI Overseer can iterate the exported tasks to execute/check WSP fixes (zero token cost).

## Session: GotJunk Double-Capture Investigation

### Issue 1: Empty Code Previews

**Query**:
```
"camera capture button double tap duplicate race condition onClick onTouchEnd handleCapture"
```

**Results**:
- ✓ Found 10 results (5 code, 5 WSP)
- ✗ All previews empty: `Preview: ` (no content)
- ✓ File paths returned correctly

**Expected Behavior**:
Should return actual code snippets showing:
- Event handler implementations
- Race condition guards
- State management patterns

**Impact**: Medium
- Forces fallback to manual file reading
- Loses semantic context of "why" these files match
- Cannot quickly assess relevance without opening files

---

### Issue 2: Generic Match Scores

**Query**:
```
"BottomNavBar Camera takePhoto handlePressStart handlePressEnd onTouchStart onTouchEnd"
```

**Results**:
- All matches show: `Match: 0.0%`
- Expected: Semantic similarity scores (0-100%)

**Impact**: Low
- Unclear which results are most relevant
- Cannot prioritize reading order

---

## Recommendations for Another 0102

### Fix 1: Code Preview Extraction

**File**: `holo_index/cli/holo_request.py` (likely)
**Root Cause Hypothesis**: TSX/JSX parsing may not extract function bodies correctly

**Suggested Investigation**:
1. Check if previews work for `.py` files vs `.tsx` files
2. Verify regex/AST extraction for TypeScript event handlers
3. Add fallback: if preview empty, return first 3 lines of matched function

### Fix 2: Match Score Calculation

**File**: `holo_index/core/search_engine.py` (likely)
**Root Cause Hypothesis**: Cosine similarity not being returned or formatted

**Suggested Investigation**:
1. Verify `distance` field from ChromaDB is converted to percentage
2. Check if score is lost during result aggregation
3. Add debug logging: `[HOLO-SCORE] file=X score=Y`

---

## Workaround Used This Session

Fallback strategy:
1. Use HoloIndex to identify relevant files ✓
2. Use `Read` tool to examine files directly ✓
3. Use `Grep` for precise pattern matching ✓

**Efficiency Loss**: ~30% (extra tool calls needed)

---

## Test Case for Validation

After fixes, re-run:
```bash
python holo_index.py --search "handlePressStart handlePressEnd onClick onTouchEnd" --verbose
```

**Expected Output**:
```
[CODE RESULTS] Top implementations:
  1. modules/foundups/gotjunk/frontend/components/BottomNavBar.tsx:handlePressEnd
     Match: 87.3% | Preview: const handlePressEnd = () => {
       if (pressTimerRef.current) {
         clearTimeout(pressTimerRef.current);
         pressTimerRef.current = null;
       }
       ...
     }
```

---

*Log created by 0102 during surgical investigation of GotJunk double-capture bug*
*Timestamp: 2025-11-10 07:25 UTC*
