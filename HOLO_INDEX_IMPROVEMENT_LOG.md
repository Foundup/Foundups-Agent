# HoloIndex Improvement Log - 2025-11-10

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
