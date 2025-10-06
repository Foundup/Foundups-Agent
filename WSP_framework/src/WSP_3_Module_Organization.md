# WSP 3: Module Organization Protocol

## Core Principle: Domain -> Block -> Cube Pattern

### Structure Hierarchy

```
modules/                          # Root
[U+251C][U+2500][U+2500] [domain]/                     # Enterprise Domain (communication, gamification, etc.)
[U+2502]   [U+251C][U+2500][U+2500] __init__.py              # Domain-level exports
[U+2502]   [U+2514][U+2500][U+2500] [block]/                 # Specific Feature/Component Block
[U+2502]       [U+251C][U+2500][U+2500] __init__.py          # Block-level exports
[U+2502]       [U+251C][U+2500][U+2500] src/                 # The Cube - Implementation
[U+2502]       [U+2502]   [U+251C][U+2500][U+2500] __init__.py      # Cube exports
[U+2502]       [U+2502]   [U+2514][U+2500][U+2500] *.py             # Implementation files (<500 lines each)
[U+2502]       [U+251C][U+2500][U+2500] tests/               # Block-specific tests
[U+2502]       [U+251C][U+2500][U+2500] docs/                # Block documentation
[U+2502]       [U+2514][U+2500][U+2500] ModLog.md            # Block change log
```

### [U+274C] WRONG Pattern (Domain-level src)
```
modules/gamification/
[U+251C][U+2500][U+2500] src/                # [U+274C] WRONG - No src at domain level!
[U+2502]   [U+2514][U+2500][U+2500] whack.py       
[U+2514][U+2500][U+2500] whack_a_magat/     
    [U+2514][U+2500][U+2500] src/           
```

### [U+2705] CORRECT Pattern (Block->Cube)
```
modules/gamification/           # Domain
[U+2514][U+2500][U+2500] whack_a_magat/             # Block (specific game)
    [U+2514][U+2500][U+2500] src/                   # Cube (implementation)
        [U+251C][U+2500][U+2500] whack.py          
        [U+251C][U+2500][U+2500] timeout_tracker.py
        [U+2514][U+2500][U+2500] timeout_announcer.py
```

## Examples of Correct Implementation

### 1. Communication Domain
```
modules/communication/
[U+251C][U+2500][U+2500] livechat/                  # Block: YouTube Live Chat
[U+2502]   [U+2514][U+2500][U+2500] src/                   # Cube: Implementation
[U+2502]       [U+251C][U+2500][U+2500] livechat_core.py
[U+2502]       [U+251C][U+2500][U+2500] message_processor.py
[U+2502]       [U+2514][U+2500][U+2500] chat_sender.py
[U+251C][U+2500][U+2500] discord/                   # Block: Discord Bot
[U+2502]   [U+2514][U+2500][U+2500] src/                   # Cube: Implementation
[U+2514][U+2500][U+2500] slack/                     # Block: Slack Integration
    [U+2514][U+2500][U+2500] src/                   # Cube: Implementation
```

### 2. Gamification Domain
```
modules/gamification/
[U+251C][U+2500][U+2500] whack_a_magat/            # Block: Whack-a-MAGA Game
[U+2502]   [U+2514][U+2500][U+2500] src/                  # Cube: Implementation
[U+251C][U+2500][U+2500] chess/                    # Block: Chess Game
[U+2502]   [U+2514][U+2500][U+2500] src/                  # Cube: Implementation
[U+2514][U+2500][U+2500] poker/                    # Block: Poker Game
    [U+2514][U+2500][U+2500] src/                  # Cube: Implementation
```

### 3. Platform Integration Domain
```
modules/platform_integration/
[U+251C][U+2500][U+2500] youtube_auth/             # Block: YouTube Authentication
[U+2502]   [U+2514][U+2500][U+2500] src/                  # Cube: Implementation
[U+251C][U+2500][U+2500] twitter_api/              # Block: Twitter/X API
[U+2502]   [U+2514][U+2500][U+2500] src/                  # Cube: Implementation
[U+2514][U+2500][U+2500] linkedin_api/             # Block: LinkedIn API
    [U+2514][U+2500][U+2500] src/                  # Cube: Implementation
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
2. **Easy Discovery**: Domain->Block->Cube makes finding code intuitive
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