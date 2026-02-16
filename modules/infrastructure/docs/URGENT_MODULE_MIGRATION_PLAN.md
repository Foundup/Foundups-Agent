# [ALERT] URGENT: Module Migration Plan

## Files to Move from chat_rules -> gamification

### 1. Create new RPG block in gamification:
```bash
modules/gamification/rpg_system/
+-- src/
[U+2502]   +-- rpg_leveling_system.py (from chat_rules, 594 lines - NEEDS SPLIT)
[U+2502]   +-- game_commands.py (from chat_rules, 341 lines)
+-- tests/
```

### 2. Move whack_a_magat.py:
- FROM: `modules/communication/chat_rules/src/whack_a_magat.py` (750 lines)
- TO: DELETE - We already have better implementation in `gamification/whack_a_magat/`

### 3. Delete duplicate timeout_announcer:
- DELETE: `modules/communication/chat_rules/src/timeout_announcer.py` (177 lines)
- KEEP: `modules/gamification/whack_a_magat/src/timeout_announcer.py` (438 lines)

### 4. Split oversized files:
- `chat_rules/src/commands.py` (938 lines) -> Split into:
  - `moderation_commands.py` (<500 lines)
  - `utility_commands.py` (<500 lines)

## Import Updates Required:

### Files importing from wrong location:
1. `modules/communication/chat_rules/src/enhanced_commands.py`
2. `modules/communication/chat_rules/src/game_commands.py`
3. `modules/communication/chat_rules/tests/test_timeout_points.py`
4. `modules/communication/chat_rules/tests/test_chat_rules.py`

### Update imports:
```python
# OLD (WRONG):
from modules.communication.chat_rules.src.rpg_leveling_system import RPGLevelingSystem
from modules.communication.chat_rules.src.whack_a_magat import WhackGame

# NEW (CORRECT):
from modules.gamification.rpg_system.src.rpg_leveling_system import RPGLevelingSystem
from modules.gamification.whack_a_magat.src.whack import apply_whack, get_profile
```

## Execution Steps:

1. **Create RPG block structure**
   ```bash
   mkdir -p modules/gamification/rpg_system/src
   mkdir -p modules/gamification/rpg_system/tests
   ```

2. **Move RPG files**
   ```bash
   mv modules/communication/chat_rules/src/rpg_leveling_system.py \
      modules/gamification/rpg_system/src/
   
   mv modules/communication/chat_rules/src/game_commands.py \
      modules/gamification/rpg_system/src/
   ```

3. **Delete duplicates**
   ```bash
   rm modules/communication/chat_rules/src/whack_a_magat.py
   rm modules/communication/chat_rules/src/timeout_announcer.py
   ```

4. **Update all imports**
   - Search and replace import paths
   - Test each module after update

5. **Split oversized files**
   - Break commands.py into smaller modules
   - Ensure each <500 lines

## Testing Checklist:
- [ ] All imports resolve
- [ ] No circular dependencies
- [ ] All tests pass
- [ ] Bot runs without errors
- [ ] Commands still work

## Prevention:
- Follow `WSP_framework/docs/annexes/MODULE_PLACEMENT_GUIDE.md` for ALL future modules
- ALWAYS check correct domain before creating files
- NEVER mix gaming and moderation in same domain

---
**Priority: HIGH - These violations break WSP compliance and create confusion**
