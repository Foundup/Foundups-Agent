# HoloIndex Refactoring Supervision Checklist

## Supervisor: 0102 Claude
## Implementer: 0102 Grok
## Goal: Fix cli.py vibecoding using HoloIndex patterns

## Pre-Refactor Analysis (Using HoloIndex)

### ✅ Pattern Discovery Complete
Found existing patterns in codebase:
- **Command Handlers**: `modules/communication/livechat/src/command_handler.py`
- **Menu Handlers**: `modules/ai_intelligence/menu_handler/src/menu_handler.py`
- **Message Handlers**: `modules/communication/livechat/src/core/message_router.py`
- **Base Patterns**: Protocol-based handlers with clean interfaces

### ✅ Vibecoding Evidence
- cli.py: 1724 lines (WSP 87 CRITICAL)
- main(): 528 lines (should be <50)
- Features added inline instead of modules
- No separation of concerns

## Refactoring Supervision Guidelines

### Phase 1: Command Extraction Pattern
Follow the existing CommandHandler pattern from livechat:

```python
# Pattern from modules/communication/livechat/src/command_handler.py
class CommandHandler:
    def __init__(self, dependencies):
        self.deps = dependencies

    def handle_command(self, command: str, context: Dict) -> Result:
        # Clean, focused handling
        pass
```

Apply to HoloIndex:
```python
# holo_index/commands/search_handler.py
class SearchCommandHandler:
    def __init__(self, holo_index, throttler):
        self.holo = holo_index
        self.throttler = throttler

    def handle(self, args) -> None:
        # Extract from main() lines 1528-1700
        pass
```

### Phase 2: Output Management Pattern
Follow existing output patterns:

```python
# holo_index/output/throttler.py
class AgenticOutputThrottler:
    # Move entire class from cli.py (lines 214-442)
    # This is already well-structured, just needs extraction
```

### Phase 3: Monitoring Extraction
```python
# holo_index/monitoring/subroutines.py
class IntelligentSubroutineEngine:
    # Move from cli.py (lines 73-212)
    # Already well-structured
```

## Validation Checkpoints

### After Each Extraction:
1. **Import Check**: Does extracted module import correctly?
2. **Dependency Check**: Are all dependencies available?
3. **Test Check**: Do existing tests still pass?
4. **Size Check**: Is extracted module <500 lines?
5. **WSP Check**: Does structure follow WSP 49?

### Critical Rules for Grok:

#### DO NOT:
- ❌ Create new patterns - use existing ones
- ❌ Add features during refactoring
- ❌ Change functionality
- ❌ Create circular imports
- ❌ Leave dead code behind

#### MUST DO:
- ✅ Use `grep` to find existing patterns first
- ✅ Extract without modification (pure moves)
- ✅ Update imports immediately
- ✅ Test after each extraction
- ✅ Keep git commits atomic

## Supervision Metrics

### Success Criteria:
- [ ] cli.py < 200 lines
- [ ] main() < 50 lines
- [ ] All extracted modules < 500 lines
- [ ] No circular imports
- [ ] All tests passing
- [ ] No functionality change

### WSP Compliance:
- [ ] WSP 87: All files within size limits
- [ ] WSP 49: Proper module structure
- [ ] WSP 72: Block independence
- [ ] WSP 84: No code duplication
- [ ] WSP 50: Pre-action verification

## Current Status Tracking

### Files to Extract:
1. **AgenticOutputThrottler** (228 lines)
   - Source: cli.py lines 214-442
   - Target: output/throttler.py
   - Status: PENDING

2. **IntelligentSubroutineEngine** (169 lines)
   - Source: cli.py lines 73-212
   - Target: monitoring/subroutines.py
   - Status: PENDING

3. **HoloIndex class** (499 lines)
   - Source: cli.py lines 900-1399
   - Target: core/holoindex.py
   - Status: PENDING - NEEDS SPLITTING

4. **Search Command** (~200 lines)
   - Source: main() lines 1528-1700
   - Target: commands/search_cmd.py
   - Status: PENDING

5. **DAE Init Command** (~200 lines)
   - Source: main() lines 1300-1500
   - Target: commands/dae_init.py
   - Status: PENDING

6. **Doc Audit Command** (~200 lines)
   - Source: main() lines 1100-1300
   - Target: commands/doc_audit.py
   - Status: PENDING

## Supervision Notes

### For Grok:
1. Start with AgenticOutputThrottler - it's the cleanest extraction
2. Test imports after each move
3. Use existing patterns from livechat module
4. Don't improve code - just move it
5. Commit after each successful extraction

### Progress Tracking:
```
[PENDING] → [IN PROGRESS] → [EXTRACTED] → [TESTED] → [COMPLETE]
```

## Final Validation:

After all extractions:
```bash
# Size check
wc -l holo_index/cli.py  # Should be < 200

# Import check
python -c "from holo_index.cli import main"

# Test check
python holo_index.py --search "test query"

# WSP check
grep -r "class\|def" holo_index/ | wc -l
```

## Remember: Use HoloIndex to Find Patterns!

Before creating ANY new pattern:
```bash
python holo_index.py --search "handler pattern extraction"
grep -r "Handler\|handle_" modules/
```

The codebase already has the patterns - just follow them!