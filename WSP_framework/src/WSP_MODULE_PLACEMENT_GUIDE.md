# WSP Module Placement Guide - PREVENT WRONG PLACEMENT

## [U+1F6A8] CRITICAL: Before Creating ANY Module, Ask These Questions:

### 1. WHAT DOMAIN DOES IT BELONG TO?

| If the module is about... | It goes in... | NOT in... |
|---------------------------|---------------|-----------|
| **Gaming/Points/Levels** | `modules/gamification/` | [U+274C] chat_rules, livechat |
| **Chat Moderation** | `modules/communication/chat_rules/` | [U+274C] gamification |
| **YouTube Live Chat** | `modules/communication/livechat/` | [U+274C] chat_rules |
| **AI/LLM Integration** | `modules/ai_intelligence/` | [U+274C] communication |
| **OAuth/APIs** | `modules/platform_integration/` | [U+274C] communication |

### 2. EXAMPLES OF CORRECT PLACEMENT:

[U+2705] **CORRECT:**
```
modules/gamification/whack_a_magat/src/
[U+251C][U+2500][U+2500] whack.py                  # Game logic
[U+251C][U+2500][U+2500] timeout_announcer.py      # Game announcements
[U+251C][U+2500][U+2500] rpg_leveling_system.py    # Leveling logic
[U+2514][U+2500][U+2500] game_commands.py          # Game commands
```

[U+274C] **WRONG:**
```
modules/communication/chat_rules/src/
[U+251C][U+2500][U+2500] whack_a_magat.py         # WRONG! This is gaming!
[U+251C][U+2500][U+2500] rpg_leveling_system.py   # WRONG! This is gaming!
[U+2514][U+2500][U+2500] game_commands.py         # WRONG! This is gaming!
```

## [U+1F4CB] Module Type Checklist

### Is it GAMIFICATION?
- [ ] Points/XP system? -> `gamification/`
- [ ] Levels/Ranks? -> `gamification/`
- [ ] Game mechanics? -> `gamification/`
- [ ] Leaderboards? -> `gamification/`
- [ ] Achievements? -> `gamification/`
- [ ] Game commands (/score, /level)? -> `gamification/`

### Is it CHAT RULES?
- [ ] Message filtering? -> `chat_rules/`
- [ ] Spam detection? -> `chat_rules/`
- [ ] Bad word filtering? -> `chat_rules/`
- [ ] Rate limiting rules? -> `chat_rules/`
- [ ] Chat permissions? -> `chat_rules/`
- [ ] Moderation policies? -> `chat_rules/`

### Is it LIVE CHAT?
- [ ] YouTube API interaction? -> `livechat/`
- [ ] Message polling? -> `livechat/`
- [ ] Chat sending? -> `livechat/`
- [ ] Stream session management? -> `livechat/`
- [ ] YouTube-specific features? -> `livechat/`

## [U+1F3AF] Common Mistakes and How to Avoid Them

### Mistake 1: "It's used in chat, so it goes in chat_rules"
**WRONG!** Just because something is used in chat doesn't mean it belongs in chat_rules.
- Game commands used in chat -> Still goes in `gamification/`
- AI responses in chat -> Still goes in `ai_intelligence/`

### Mistake 2: "It handles timeouts, so it goes with moderation"
**WRONG!** Purpose matters, not trigger:
- Timeout for **points/gaming** -> `gamification/`
- Timeout for **rule violation** -> `chat_rules/`

### Mistake 3: "It's all related, so keep it together"
**WRONG!** Separate by domain:
- Even if tightly coupled, modules go in their proper domains
- Use imports to connect them, not co-location

## [U+1F50D] Before Creating a Module:

1. **CHECK IF IT EXISTS:**
   ```bash
   # Search for similar functionality
   grep -r "leveling" modules/
   grep -r "timeout" modules/
   ```

2. **IDENTIFY THE DOMAIN:**
   - What is the PRIMARY purpose?
   - What domain best describes this functionality?

3. **CHECK FOR DUPLICATES:**
   ```bash
   find modules/ -name "*timeout*" -type f
   find modules/ -name "*level*" -type f
   ```

4. **FOLLOW THE PATTERN:**
   ```
   modules/[DOMAIN]/[BLOCK]/src/[module].py
   ```

## [WARNING][U+FE0F] Red Flags You're in the Wrong Place:

1. **File named `game_*` in non-gamification folder**
2. **File named `*_leveling_*` in non-gamification folder**
3. **Points/XP logic outside gamification**
4. **Leaderboard code outside gamification**
5. **Chat API code outside livechat**
6. **OAuth code outside platform_integration**

## [U+1F4DD] Migration Checklist:

When you find misplaced modules:

1. [ ] Identify correct domain
2. [ ] Check for existing similar modules
3. [ ] Move file to correct location
4. [ ] Update ALL imports
5. [ ] Delete old file
6. [ ] Run tests
7. [ ] Update ModLog

## [U+1F6AB] NEVER DO THIS:

1. **NEVER** create gaming files in `chat_rules/`
2. **NEVER** create chat moderation in `gamification/`
3. **NEVER** mix domains in the same block
4. **NEVER** duplicate modules across domains
5. **NEVER** ignore WSP 3 structure

## [U+2705] ALWAYS DO THIS:

1. **ALWAYS** check if module already exists (WSP 84)
2. **ALWAYS** follow Domain->Block->Cube pattern (WSP 3)
3. **ALWAYS** keep files under 500 lines (WSP compliance)
4. **ALWAYS** put gaming in gamification
5. **ALWAYS** put chat rules in chat_rules
6. **ALWAYS** update imports when moving files

---

*Remember: Correct placement prevents technical debt and ensures clean architecture.*