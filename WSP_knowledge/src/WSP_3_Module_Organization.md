# WSP 3: Module Organization Protocol

## Core Principle: Domain → Block → Cube Pattern

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

### ❌ WRONG Pattern (Domain-level src)
```
modules/gamification/
├── src/                # ❌ WRONG - No src at domain level!
│   └── whack.py       
└── whack_a_magat/     
    └── src/           
```

### ✅ CORRECT Pattern (Block→Cube)
```
modules/gamification/           # Domain
└── whack_a_magat/             # Block (specific game)
    └── src/                   # Cube (implementation)
        ├── whack.py          
        ├── timeout_tracker.py
        └── timeout_announcer.py
```

## Examples of Correct Implementation

### 1. Communication Domain
```
modules/communication/
├── livechat/                  # Block: YouTube Live Chat
│   └── src/                   # Cube: Implementation
│       ├── livechat_core.py
│       ├── message_processor.py
│       └── chat_sender.py
├── discord/                   # Block: Discord Bot
│   └── src/                   # Cube: Implementation
└── slack/                     # Block: Slack Integration
    └── src/                   # Cube: Implementation
```

### 2. Gamification Domain
```
modules/gamification/
├── whack_a_magat/            # Block: Whack-a-MAGA Game
│   └── src/                  # Cube: Implementation
├── chess/                    # Block: Chess Game
│   └── src/                  # Cube: Implementation
└── poker/                    # Block: Poker Game
    └── src/                  # Cube: Implementation
```

### 3. Platform Integration Domain
```
modules/platform_integration/
├── youtube_auth/             # Block: YouTube Authentication
│   └── src/                  # Cube: Implementation
├── twitter_api/              # Block: Twitter/X API
│   └── src/                  # Cube: Implementation
└── linkedin_api/             # Block: LinkedIn API
    └── src/                  # Cube: Implementation
```

## Import Patterns

### Importing from Within Same Block
```python
# Inside whack_a_magat/src/timeout_announcer.py
from modules.gamification.whack_a_magat.src.whack import get_profile
```

### Importing from Another Block
```python
# Inside livechat/src/command_handler.py
from modules.gamification.whack_a_magat.src.whack import get_profile
```

### Domain-Level Exports
```python
# modules/gamification/__init__.py
from .whack_a_magat import get_profile, get_leaderboard
# Re-export for convenience
```

## Key Rules

1. **No src/ at Domain Level**: The `src/` directory only exists within blocks, never at the domain level
2. **Block = Feature**: Each block represents a distinct feature or component
3. **Cube = Implementation**: The src/ folder within a block is the "cube" containing actual code
4. **<500 Lines Per File**: Each file in src/ must be under 500 lines (WSP compliance)
5. **Tests Mirror Structure**: Test files should mirror the src/ structure

## Benefits

1. **Clear Ownership**: Each block owns its implementation
2. **Easy Discovery**: Domain→Block→Cube makes finding code intuitive
3. **Scalability**: New blocks can be added without affecting existing ones
4. **Modularity**: Blocks can be moved/deleted as complete units
5. **Import Clarity**: Full paths make dependencies explicit

## Migration Example

When migrating from incorrect structure:

```bash
# WRONG: Domain-level src
modules/gamification/src/whack.py

# Step 1: Move to correct location
mv modules/gamification/src/whack.py modules/gamification/whack_a_magat/src/

# Step 2: Update imports
# From: from modules.gamification.src.whack import ...
# To:   from modules.gamification.whack_a_magat.src.whack import ...

# Step 3: Remove empty domain-level src
rmdir modules/gamification/src
```

## Compliance Check

Use this checklist to verify WSP 3 compliance:

- [ ] No `src/` directories at domain level
- [ ] All implementations are in `[domain]/[block]/src/`
- [ ] Each block has its own `__init__.py`
- [ ] Imports use full paths from module root
- [ ] All files under 500 lines
- [ ] Tests mirror the src/ structure

---

*This WSP defines the canonical module organization pattern for the entire codebase.*