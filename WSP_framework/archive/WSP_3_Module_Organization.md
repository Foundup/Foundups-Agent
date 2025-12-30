# WSP 3: Module Organization Protocol (ARCHIVED)
(Redundant - See WSP 3: Enterprise Domain Organization)

## Core Principle: Domain -> Block -> Cube Pattern

### Structure Hierarchy

```
modules/                          # Root
├── [domain]/                     # Enterprise Domain (communication, gamification, etc.)
│   ├── __init__.py              # Domain-level exports
│   └── [block]/                 # Specific Feature/Component Block
│       ├── __init__.py          # Block-level exports
│       ├── src/                 # The Cube - Implementation
│       │   ├── __init__.py      # Cube exports
│       │   └── *.py             # Implementation files (<500 lines each)
│       ├── tests/               # Block-specific tests
│       ├── docs/                # Block documentation
│       └── ModLog.md            # Block change log
```

*(Archived to WSP_framework/archive/ on 2025-12-30)*
