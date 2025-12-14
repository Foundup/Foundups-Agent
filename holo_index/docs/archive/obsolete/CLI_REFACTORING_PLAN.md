# HoloIndex CLI Refactoring Plan - WSP 87 Compliance

## Problem
- **cli.py**: 1724 lines (CRITICAL VIOLATION)
- **WSP 87 Threshold**: 800-1000 lines WARNING, >1000 CRITICAL
- **Required Action**: Split into logical components

## Analysis of Current Structure

### Line Distribution in cli.py
```
1-200:    Imports and initialization
201-400:  HoloIndex core class
401-800:  Search and display logic
801-1200: AgenticOutputThrottler class
1201-1400: DAE initialization logic
1401-1600: Documentation audit logic
1601-1724: Main function and entry point
```

## Refactoring Strategy (WSP 87 + WSP 72)

### 1. Core Principle: Functional Separation
Following WSP 72 (Block Independence), split into independent, composable modules:

### 2. Proposed Structure

```
holo_index/
+-- cli.py                          # Main entry (< 200 lines)
+-- core/
[U+2502]   +-- __init__.py
[U+2502]   +-- holoindex.py               # HoloIndex class (~400 lines)
[U+2502]   +-- search_engine.py           # Search logic (~300 lines)
[U+2502]   +-- indexer.py                 # Indexing logic (~200 lines)
+-- output/
[U+2502]   +-- __init__.py
[U+2502]   +-- throttler.py               # AgenticOutputThrottler (~400 lines)
[U+2502]   +-- formatter.py               # Result formatting (~200 lines)
[U+2502]   +-- display.py                 # Display utilities (~150 lines)
+-- commands/
[U+2502]   +-- __init__.py
[U+2502]   +-- dae_init.py                # DAE initialization (~200 lines)
[U+2502]   +-- doc_audit.py               # Documentation audit (~200 lines)
[U+2502]   +-- search_cmd.py              # Search command (~150 lines)
+-- utils/
    +-- __init__.py
    +-- telemetry.py               # Telemetry and rewards (~100 lines)
    +-- config.py                  # Configuration (~100 lines)
```

### 3. Extraction Plan

#### Phase 1: Extract Core Components
```python
# core/holoindex.py
class HoloIndex:
    """Core semantic search engine"""
    def __init__(self, ssd_path)
    def search(self, query, limit)
    def index_code_entries()
    def index_wsp_entries()
```

#### Phase 2: Extract Output Management
```python
# output/throttler.py
class AgenticOutputThrottler:
    """Intelligent output management"""
    def __init__(self)
    def add_section()
    def render_prioritized_output()
```

#### Phase 3: Extract Commands
```python
# commands/dae_init.py
def handle_dae_initialization(args, organizer)

# commands/doc_audit.py
def handle_documentation_audit(args, holo)

# commands/search_cmd.py
def handle_search_command(args, holo, throttler)
```

#### Phase 4: Slim CLI Entry
```python
# cli.py (< 200 lines)
def main():
    """Main entry point - route to command handlers"""
    args = parse_args()

    if args.init_dae:
        from .commands import handle_dae_initialization
        return handle_dae_initialization(args)

    if args.audit_docs:
        from .commands import handle_documentation_audit
        return handle_documentation_audit(args)

    if args.search:
        from .commands import handle_search_command
        return handle_search_command(args)
```

## Benefits

1. **WSP 87 Compliance**: All files < 500 lines (OPTIMAL)
2. **WSP 72 Block Independence**: Each module independent
3. **WSP 49 Module Structure**: Proper sub-packages
4. **Maintainability**: Clear separation of concerns
5. **Testability**: Each component independently testable
6. **Performance**: Lazy imports reduce startup time

## Implementation Steps

1. **Create directory structure**
2. **Extract HoloIndex class** -> core/holoindex.py
3. **Extract AgenticOutputThrottler** -> output/throttler.py
4. **Extract command handlers** -> commands/
5. **Update imports** in all files
6. **Test each component** independently
7. **Update cli.py** to routing-only
8. **Update ModLog** with refactoring

## Risk Mitigation

- **Import paths**: Update all imports carefully
- **Circular dependencies**: Use lazy imports where needed
- **Testing**: Run full test suite after each extraction
- **Backwards compatibility**: Keep cli.py as main entry
- **Documentation**: Update README and INTERFACE

## Success Metrics

- cli.py < 200 lines [OK]
- All extracted files < 500 lines [OK]
- No circular dependencies [OK]
- All tests passing [OK]
- Performance unchanged or improved [OK]

## WSP Compliance

- **WSP 87**: Code Navigation Protocol (size limits)
- **WSP 72**: Block Independence Architecture
- **WSP 49**: Module Directory Structure
- **WSP 84**: Code Memory (no duplication)
- **WSP 50**: Pre-Action Verification