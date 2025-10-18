# Qwen Task 4: Real-Time Output Filtering with Unicode Error Detection

## Single Task Focus
Enhance agentic_output_throttler.py to detect and fix Unicode violations in real-time using first principles pattern matching

## Problem Context
**From 012**: "checking the holo output is monitored by qwen... it should apply first principle and throttle output that is noise... and detect and fix errors like the emoji issue in realtime"

**The Truth**:
- HoloIndex outputs thousands of lines with emojis
- cp932 console errors break output display
- Qwen currently throttles by priority/relevance
- Qwen does NOT detect or fix Unicode violations in real-time
- Need Gemma-style pattern matching integrated into output pipeline

## Architecture Reality

### Current Flow
```
HoloIndex Search -> Qwen Orchestrator -> Output Throttler -> Console
                                              v
                                    Priority filtering only
                                    (no Unicode detection)
```

### Desired Flow
```
HoloIndex Search -> Qwen Orchestrator -> Output Throttler -> Unicode Fixer -> Console
                                              v                  v
                                    Priority filtering    Pattern matching
                                    Noise reduction       Emoji -> ASCII
```

## Execute These Steps (Validate After Each)

### Step 1: Add Unicode Detection to Output Throttler

**File**: `holo_index/output/agentic_output_throttler.py`
**Location**: Add new method after `_format_for_agent()` (around line 288)

**Add This Method**:
```python
def filter_unicode_violations(self, content: str) -> tuple[str, dict]:
    """
    Real-time Unicode violation detection and fixing.

    Uses Gemma-style pattern matching to detect emojis in output,
    then replaces with ASCII equivalents for cp932 compatibility.

    Args:
        content: Output content to filter

    Returns:
        (filtered_content, stats) - Clean content + fix statistics

    WSP Compliance: WSP 90 (UTF-8 Enforcement)
    """
    try:
        from holo_index.qwen_advisor.unicode_fixer import UnicodeViolationFixer
        fixer = UnicodeViolationFixer()

        # Check if content has violations
        violations_detected = any(
            emoji in content
            for emoji in fixer.patterns['emoji_replacements'].keys()
        )

        if not violations_detected:
            return content, {"violations": 0, "replaced": 0}

        # Apply fixes
        fixed_content = content
        replacements = 0

        for emoji, replacement in fixer.patterns['emoji_replacements'].items():
            if emoji in fixed_content:
                fixed_content = fixed_content.replace(emoji, replacement)
                replacements += 1

        return fixed_content, {
            "violations": len([e for e in fixer.patterns['emoji_replacements'].keys() if e in content]),
            "replaced": replacements
        }

    except Exception as e:
        # If fixer not available, return original
        return content, {"error": str(e)}
```

**Validate**: Does method exist? Test with:
```bash
python -c "from holo_index.output.agentic_output_throttler import AgenticOutputThrottler; t = AgenticOutputThrottler(); print(hasattr(t, 'filter_unicode_violations'))"
```

### Step 2: Integrate into Render Pipeline (BEFORE Agent Formatting)

**File**: `holo_index/output/agentic_output_throttler.py`
**Location**: Update `render_prioritized_output()` method (line 141)

**Architecture Decision**: Filter Unicode **BEFORE** agent formatting so ALL agents get clean ASCII:
- **0102**: Clean output for cp932 console
- **Qwen**: Clean JSON for parsing (no Unicode breaks)
- **Gemma**: Pure ASCII for binary classification

**Modify** the method:
```python
def render_prioritized_output(self, verbose: bool = False) -> str:
    """Render PERFECT output for 0102 decision-making using tri-state architecture.

    Agent-aware rendering:
    - 0102 (Claude Sonnet, 200K context): Full verbose documentation (200 tokens)
    - qwen (1.5B model, 32K context): Concise JSON with action items (50 tokens)
    - gemma (270M model, 8K context): Minimal classification (10 tokens)
    """
    state = self._determine_system_state()

    if state == "error":
        content = self._render_error_state()
    elif state == "found":
        content = self._render_found_state(verbose)
    elif state == "missing":
        content = self._render_missing_state()
    else:
        # Fallback to auto-detection
        content = self._render_auto_state(verbose)

    # REAL-TIME UNICODE FILTERING - BEFORE agent formatting (NEW)
    # This ensures ALL agents (0102, qwen, gemma) get clean ASCII output
    filtered_content, stats = self.filter_unicode_violations(content)

    # Log if fixes were applied (for learning)
    if stats.get('replaced', 0) > 0:
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"[UNICODE-FIX] Replaced {stats['replaced']} emojis for agent={self.agent_id}")

    # Format output based on calling agent's capabilities (after cleaning)
    return self._format_for_agent(filtered_content, state)
```

**Why This Order?**
1. **Clean at source** - All state renderers produce ASCII-safe output
2. **Agent-agnostic** - Qwen gets clean JSON, Gemma gets pure ASCII classifications
3. **No duplication** - Filter once, format once
4. **Learning opportunity** - Track which emojis appear in which states

**Validate**: Test with all three agent types:
```bash
# Test as 0102 (default)
python holo_index.py --search "test" 2>&1 | grep "\[OK\]"  # Should see [OK] not [OK]

# Test as qwen (requires env var set in qwen context)
# Qwen will receive clean JSON with no emoji characters

# Test as gemma (requires env var set in gemma context)
# Gemma will receive pure ASCII pipe-delimited output
```

### Step 3: Add First Principles Noise Detection

**File**: `holo_index/output/agentic_output_throttler.py`
**Location**: Add new method after `filter_unicode_violations()`

**Add This Method**:
```python
def is_noise(self, content: str, context: str = "") -> tuple[bool, str]:
    """
    First principles noise detection - Is this output actionable for 0102?

    Noise criteria:
    - Repeated patterns (same line 3+ times)
    - Empty information ("No results found" with no context)
    - Verbose logging without actionable insight
    - Duplicate section headers

    Args:
        content: Content line to evaluate
        context: Surrounding context for evaluation

    Returns:
        (is_noise, reason) - True if noise with reason why
    """
    content_lower = content.lower().strip()

    # Empty or whitespace-only
    if not content_lower:
        return True, "empty_line"

    # Repeated pattern detection (simple heuristic)
    if context:
        context_lines = context.lower().split('\n')
        count = sum(1 for line in context_lines if content_lower in line)
        if count >= 3:
            return True, "repeated_pattern"

    # Non-actionable status messages
    noise_patterns = [
        "no results found",
        "no matches",
        "processing...",
        "loading...",
        "checking...",
        "validating..."
    ]

    if any(pattern in content_lower for pattern in noise_patterns):
        # Only noise if there's no follow-up action
        if "action:" not in content_lower and "next:" not in content_lower:
            return True, "non_actionable_status"

    # Verbose debug logging
    if content_lower.startswith(('[debug]', '[trace]', '[verbose]')):
        return True, "debug_logging"

    return False, ""
```

**Validate**: Does noise detection work?
```bash
python -c "from holo_index.output.agentic_output_throttler import AgenticOutputThrottler; t = AgenticOutputThrottler(); print(t.is_noise('processing...'))"
# Should return: (True, 'non_actionable_status')
```

## Success Criteria
- [OK] Unicode fixer integrated into output throttler
- [OK] Real-time emoji -> ASCII conversion working
- [OK] First principles noise detection implemented
- [OK] No breaking changes to existing output
- [OK] Logging shows when fixes applied

## Integration Points

### With Qwen Orchestrator
```python
# In qwen_orchestrator.py, output already goes through throttler
# No changes needed - throttler enhancement is automatic
```

### With Unicode Fixer
```python
# Reuses existing UnicodeViolationFixer patterns
# No duplication - single source of truth for emoji mappings
```

## First Principles Applied

### 1. Detect at Source
**Before**: Errors happen at console, user sees crash
**After**: Detect in pipeline, fix before output

### 2. Pattern-Based, Not Compute-Based
**Before**: Complex logic to analyze output
**After**: Simple pattern matching (Gemma-style)

### 3. Noise = Non-Actionable
**Before**: Show everything, overwhelm 0102
**After**: Only show what 0102 can act upon

### 4. Learning Integration
**Before**: Same errors repeat forever
**After**: Log patterns, improve over time

## Submission
After completing all 3 steps and validating each:
- Report: "Task 4 complete - Real-time Unicode filtering integrated"
- Show test results with emoji -> ASCII conversion
- Ready for 0102 review

## Time Estimate
12 minutes

## If Anything Fails
- Stop immediately
- Report failure with error message
- Wait for 0102 direction
- Do NOT proceed to next step

## Expected Behavior After Implementation

### Before (All Agents)
```bash
# 0102 (Claude)
$ python holo_index.py --search "test"
[U+1F534] [SYSTEM ERROR] Fatal error...  # cp932 crash!
UnicodeEncodeError: 'cp932' codec can't encode character...

# Qwen (1.5B)
{"state": "error", "action": "fix_error_then_retry", "priority": "[U+1F525] high"}
# JSON parsing breaks on emoji!

# Gemma (270M)
ERROR|retry_needed|check_logs_[U+1F534]
# Binary classification confused by emoji noise
```

### After (All Agents)
```bash
# 0102 (Claude) - Clean ASCII
$ python holo_index.py --search "test"
[RED] [SYSTEM ERROR] Fatal error...  # Works on cp932!
[DEBUG] [UNICODE-FIX] Replaced 12 emojis for agent=0102

# Qwen (1.5B) - Valid JSON
{"state": "error", "action": "fix_error_then_retry", "priority": "high"}
# Clean JSON, ready for parsing

# Gemma (270M) - Pure ASCII
ERROR|retry_needed|check_logs
# Fast binary classification, no noise
```

### Multi-Agent Benefits

**0102**: Console compatibility (cp932 safe)
**Qwen**: Clean structured data for orchestration decisions
**Gemma**: Pure ASCII for fast pattern matching

The system **learns and fixes automatically** - no 012 intervention required.

### Learning Integration

Each fix is logged by agent type:
```
[UNICODE-FIX] agent=0102 replaced 12 emojis (console safety)
[UNICODE-FIX] agent=qwen replaced 8 emojis (JSON cleaning)
[UNICODE-FIX] agent=gemma replaced 15 emojis (classification purity)
```

This creates agent-specific learning patterns for recursive improvement.
